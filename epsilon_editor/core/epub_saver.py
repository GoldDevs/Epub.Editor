import zipfile
import os
from pathlib import Path

from epsilon_editor.core.epub_model import EpubBook


class EpubSaver:
    """
    Saves the changes in an EpubBook object back to an EPUB file.
    """

    def __init__(self, book: EpubBook):
        self.book = book

    def _write_mimetype(self, new_zip, original_zip):
        mimetype_info = original_zip.getinfo("mimetype")
        mimetype_content = original_zip.read(mimetype_info)
        new_zip.writestr(
            mimetype_info, mimetype_content, compress_type=zipfile.ZIP_STORED
        )

    def _write_unmodified_files(self, new_zip, original_zip, modified_files):
        for item in original_zip.infolist():
            if item.filename == "mimetype":
                continue

            is_modified = False
            for href in modified_files:
                if item.filename.endswith(href):
                    is_modified = True
                    break

            if not is_modified:
                new_zip.writestr(item, original_zip.read(item.filename))

    def _write_modified_files(self, new_zip, original_zip):
        for href, content in self.book.content_manager._content_cache.items():
            found_info = None
            for info in original_zip.infolist():
                if info.filename.endswith(href):
                    found_info = info
                    break

            if found_info:
                new_zip.writestr(found_info, content)
            else:
                new_zip.writestr(href, content)

    def save(self, backup=True):
        """
        Saves the EPUB file.

        Args:
            backup: If True, creates a backup of the original file.
        """
        if not self.book.is_modified:
            return

        original_path = Path(self.book.filepath)
        temp_path = original_path.with_suffix(original_path.suffix + ".tmp")
        backup_path = original_path.with_suffix(original_path.suffix + ".bak")

        try:
            with zipfile.ZipFile(self.book.filepath, "r") as original_zip:
                with zipfile.ZipFile(
                    temp_path, "w", zipfile.ZIP_DEFLATED
                ) as new_zip:
                    self._write_mimetype(new_zip, original_zip)
                    modified_files = self.book.content_manager._content_cache.keys()
                    self._write_unmodified_files(
                        new_zip, original_zip, modified_files
                    )
                    self._write_modified_files(new_zip, original_zip)

            if backup and original_path.exists():
                os.replace(original_path, backup_path)

            os.replace(temp_path, original_path)

            self.book.is_modified = False
            self.book.content_manager._content_cache.clear()

        except Exception as e:
            if temp_path.exists():
                os.remove(temp_path)
            raise IOError(f"Failed to save EPUB file: {e}") from e
