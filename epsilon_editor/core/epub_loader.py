import logging
import zipfile
from pathlib import Path
from typing import Optional, Dict, List
from lxml import etree

from epsilon_editor.core.epub_model import EpubBook, EpubMetadata, ManifestItem, SpineItem

log = logging.getLogger(__name__)


class EpubLoaderError(Exception):
    """Base exception for EpubLoader errors."""
    pass


class InvalidEpubFileError(EpubLoaderError):
    """Exception raised for invalid EPUB files."""
    pass


class EpubLoader:
    """
    Loads and parses an EPUB file, providing access to its contents.
    """
    def __init__(self, file_path: Path):
        """
        Initializes the EpubLoader with the path to an EPUB file.

        Args:
            file_path: The path to the EPUB file.
        """
        self.file_path = file_path
        self.epub: Optional[zipfile.ZipFile] = None
        self.opf_path: Optional[str] = None
        self.opf_dir: Optional[Path] = None

    def _get_opf_path(self) -> str:
        """
        Parses container.xml to find the path to the OPF file.
        """
        if not self.epub:
            raise EpubLoaderError("EPUB file is not loaded.")

        container_xml = self.epub.read('META-INF/container.xml')

        # Define the namespace for container.xml
        namespaces = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}

        try:
            tree = etree.fromstring(container_xml)
            # Find the rootfile element and get its full-path attribute
            rootfile_element = tree.find('c:rootfiles/c:rootfile', namespaces)
            if rootfile_element is None:
                raise InvalidEpubFileError("Could not find rootfile element in container.xml.")

            opf_path = rootfile_element.get('full-path')
            if not opf_path:
                raise InvalidEpubFileError("Rootfile element in container.xml is missing the 'full-path' attribute.")

            return opf_path
        except etree.XMLSyntaxError:
            raise InvalidEpubFileError("META-INF/container.xml is not well-formed XML.")

    def _parse_metadata(self, metadata_element, ns) -> EpubMetadata:
        """Parses the metadata element from the OPF file."""
        metadata = EpubMetadata()
        metadata_mapping = {
            "title": "title",
            "creator": "creator",
            "language": "language",
            "identifier": "identifier",
            "publisher": "publisher",
            "date": "date",
            "rights": "rights",
        }
        for item in metadata_element:
            tag_name = etree.QName(item.tag).localname
            if tag_name in metadata_mapping:
                setattr(metadata, metadata_mapping[tag_name], item.text)

            # Store all metadata
            if item.text:
                if tag_name not in metadata.all_metadata:
                    metadata.all_metadata[tag_name] = []
                metadata.all_metadata[tag_name].append(item.text)
        return metadata

    def _parse_manifest(self, manifest_element, ns) -> Dict[str, ManifestItem]:
        """Parses the manifest element from the OPF file."""
        manifest = {}
        for item in manifest_element.findall('opf:item', ns):
            manifest_item = ManifestItem(
                id=item.get('id'),
                href=item.get('href'),
                media_type=item.get('media-type'),
                properties=item.get('properties')
            )
            manifest[manifest_item.id] = manifest_item
        return manifest

    def _parse_spine(self, spine_element, ns) -> List[SpineItem]:
        """Parses the spine element from the OPF file."""
        spine = []
        for itemref in spine_element.findall('opf:itemref', ns):
            spine_item = SpineItem(
                idref=itemref.get('idref'),
                linear=(itemref.get('linear', 'yes') == 'yes')
            )
            spine.append(spine_item)
        return spine

    def _parse_opf(self) -> EpubBook:
        """
        Parses the OPF file to extract metadata, manifest, and spine.
        """
        if not self.epub or not self.opf_path:
            raise EpubLoaderError("EPUB not loaded or OPF path not found.")

        opf_content = self.epub.read(self.opf_path)
        try:
            tree = etree.fromstring(opf_content)
        except etree.XMLSyntaxError:
            raise InvalidEpubFileError(f"OPF file at {self.opf_path} is not well-formed XML.")

        # Define namespaces for OPF
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        metadata_element = tree.find('opf:metadata', ns)
        manifest_element = tree.find('opf:manifest', ns)
        spine_element = tree.find('opf:spine', ns)

        if metadata_element is None or manifest_element is None or spine_element is None:
            raise InvalidEpubFileError("OPF file is missing one or more required elements: metadata, manifest, spine.")

        metadata = self._parse_metadata(metadata_element, ns)
        manifest = self._parse_manifest(manifest_element, ns)
        spine = self._parse_spine(spine_element, ns)

        return EpubBook(
            filepath=str(self.file_path),
            opf_dir=str(self.opf_dir),
            metadata=metadata,
            manifest=manifest,
            spine=spine
        )

    def _validate_epub(self):
        """
        Validates the basic structure of the EPUB file.
        - Checks for mimetype file and its content.
        - Checks for container.xml.
        """
        if not self.epub:
            raise EpubLoaderError("EPUB file is not loaded.")

        # Check for mimetype file and its content
        try:
            mimetype_content = self.epub.read('mimetype').decode('ascii').strip()
            if mimetype_content != 'application/epub+zip':
                raise InvalidEpubFileError("Mimetype file has incorrect content: must be 'application/epub+zip'.")
        except KeyError:
            raise InvalidEpubFileError("Required 'mimetype' file not found in the EPUB archive.")
        except UnicodeDecodeError:
            raise InvalidEpubFileError("Mimetype file is not ASCII encoded.")

        # Check that mimetype is the first file in the archive and is not compressed
        file_list = self.epub.infolist()
        if not file_list or file_list[0].filename != 'mimetype':
            raise InvalidEpubFileError("'mimetype' must be the first file in the EPUB archive.")
        if file_list[0].compress_type != zipfile.ZIP_STORED:
            raise InvalidEpubFileError("'mimetype' file must not be compressed.")

        # Check for container.xml
        try:
            self.epub.getinfo('META-INF/container.xml')
        except KeyError:
            raise InvalidEpubFileError("Required 'META-INF/container.xml' file not found.")

    def load(self) -> EpubBook:
        """
        Loads the EPUB file, validates it, and parses its structure.
        Returns an EpubBook instance.
        """
        if not self.file_path.is_file():
            raise FileNotFoundError(f"EPUB file not found at: {self.file_path}")

        try:
            self.epub = zipfile.ZipFile(self.file_path, 'r')
        except zipfile.BadZipFile:
            raise InvalidEpubFileError(f"File at {self.file_path} is not a valid ZIP file.")

        self._validate_epub()
        self.opf_path = self._get_opf_path()
        self.opf_dir = Path(self.opf_path).parent

        book = self._parse_opf()

        return book

    def close(self):
        """
        Closes the EPUB file if it's open.
        """
        if self.epub:
            self.epub.close()
            self.epub = None
