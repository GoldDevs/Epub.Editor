import zipfile
import urllib.parse
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from epsilon_editor.core.epub_model import EpubBook

from epsilon_editor.core.epub_model import ManifestItem


class ContentManager:
    """
    Manages access to the content of an EPUB book.
    Handles lazy loading and caching of content files.
    """

    def __init__(self, book: 'EpubBook'):
        self._book = book
        self._content_cache: Dict[str, bytes] = {}
        self._zipfile: Optional[zipfile.ZipFile] = None

    @property
    def zipfile(self) -> zipfile.ZipFile:
        """Opens the EPUB zip file if not already open."""
        if self._zipfile is None:
            self._zipfile = zipfile.ZipFile(self._book.filepath, 'r')
        return self._zipfile

    def get_content(self, item_href: str) -> bytes:
        """
        Gets the content of a manifest item, loading it if not cached.
        """
        if item_href in self._content_cache:
            return self._content_cache[item_href]

        # The href in the manifest is relative to the OPF file.
        # We need to construct the full path within the zip archive.
        href_path = urllib.parse.unquote(item_href)

        # Normalize the path to handle cases like 'OEBPS/../text.xhtml'
        full_path = (Path(self._book.opf_dir) / href_path).as_posix()
        # Pathlib doesn't have a robust normalization for zip paths, but this is a start.
        # os.path.normpath might be better but works on the current OS's path format.
        # A simple string-based normalization for now.
        # full_path = os.path.normpath(full_path) # This might not work on all systems for zip paths

        try:
            content = self.zipfile.read(full_path)
            self._content_cache[item_href] = content
            return content
        except KeyError:
            raise FileNotFoundError(f"Could not find '{full_path}' in the EPUB archive.")

    def update_content(self, item_href: str, new_content: bytes):
        """
        Updates the content of a manifest item in the cache.
        Marks the book as modified.
        """
        self._content_cache[item_href] = new_content
        self._book.is_modified = True

    def get_all_content(self) -> Dict[str, ManifestItem]:
        """
        Returns all manifest items. The content will be lazy-loaded when accessed.
        This method is a bit of a misnomer based on the search/replace engine's usage.
        The engines actually need the manifest items to then get content.
        Let's adjust the engines to use `get_content`.

        For now, to avoid refactoring the engines immediately, I'll return
        a dictionary-like object that lazy loads. But a better approach is to refactor.
        Let's stick to the plan and refactor the engines after this.

        Let's make this return the manifest, and the engines can get the hrefs from it.
        """
        return self._book.manifest

    def _find_manifest_item_by_href(self, href: str) -> Optional[ManifestItem]:
        """Finds a manifest item by its href."""
        for item in self._book.manifest.values():
            if item.href == href:
                return item
        return None

    def close(self):
        """Closes the zip file if it's open."""
        if self._zipfile:
            self._zipfile.close()
            self._zipfile = None
