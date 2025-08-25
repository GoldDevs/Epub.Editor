import unittest
import zipfile
import shutil
from pathlib import Path

from epsilon_editor.core.epub_loader import EpubLoader, InvalidEpubFileError


class TestEpubLoader(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory and create test EPUB files."""
        self.test_dir = Path("tests/temp_test_files")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

        self.valid_epub_path = self.test_dir / "valid.epub"
        self.no_mimetype_epub_path = self.test_dir / "no_mimetype.epub"
        self.not_a_zip_path = self.test_dir / "not_a_zip.txt"
        self.mimetype_not_first_path = self.test_dir / "mimetype_not_first.epub"
        self.mimetype_compressed_path = self.test_dir / "mimetype_compressed.epub"
        self.no_container_path = self.test_dir / "no_container.epub"
        self.no_opf_path = self.test_dir / "no_opf.epub"

        self.not_a_zip_path.write_text("This is not a zip file.")
        self._create_test_epubs()

    def tearDown(self):
        """Remove the temporary directory."""
        shutil.rmtree(self.test_dir)

    def _create_test_epubs(self):
        # Common content for our test EPUBs
        mimetype_content = "application/epub+zip"
        container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        content_opf = """<?xml version="1.0"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="pub-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Title</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="pub-id">my-unique-id</dc:identifier>
  </metadata>
  <manifest>
    <item id="text" href="text.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="text"/>
  </spine>
</package>"""
        text_xhtml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test Title</title></head>
<body><p>Hello World</p></body>
</html>"""

        # 1. Create a valid EPUB
        with zipfile.ZipFile(self.valid_epub_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", mimetype_content, compress_type=zipfile.ZIP_STORED)
            zf.writestr("META-INF/container.xml", container_xml)
            zf.writestr("OEBPS/content.opf", content_opf)
            zf.writestr("OEBPS/text.xhtml", text_xhtml)

        # 2. Create an EPUB with no mimetype file
        with zipfile.ZipFile(self.no_mimetype_epub_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("META-INF/container.xml", container_xml)

        # 3. Create an EPUB where mimetype is not the first file
        with zipfile.ZipFile(self.mimetype_not_first_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("META-INF/container.xml", container_xml)
            zf.writestr("mimetype", mimetype_content, compress_type=zipfile.ZIP_STORED)

        # 4. Create an EPUB where mimetype is compressed
        with zipfile.ZipFile(self.mimetype_compressed_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", mimetype_content, compress_type=zipfile.ZIP_DEFLATED)
            zf.writestr("META-INF/container.xml", container_xml)

        # 5. Create an EPUB with no container.xml
        with zipfile.ZipFile(self.no_container_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", mimetype_content, compress_type=zipfile.ZIP_STORED)

        # 6. Create an EPUB with no OPF file (referenced by container.xml)
        with zipfile.ZipFile(self.no_opf_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", mimetype_content, compress_type=zipfile.ZIP_STORED)
            zf.writestr("META-INF/container.xml", container_xml)

    def test_load_valid_epub(self):
        """Test loading a well-formed EPUB file."""
        loader = EpubLoader(self.valid_epub_path)
        book = loader.load()
        self.assertIsNotNone(book)
        self.assertEqual(book.metadata.title, "Test Title")
        self.assertEqual(book.metadata.creator, "Test Author")
        self.assertEqual(book.metadata.language, "en")
        self.assertEqual(len(book.manifest), 1)
        self.assertEqual(book.manifest['text'].href, "text.xhtml")

        # Test content manager
        content = book.content_manager.get_content("text.xhtml")
        self.assertTrue(content.strip().endswith(b"Hello World</p></body>\n</html>"))

        loader.close()

    def test_file_not_found(self):
        """Test loading a non-existent file."""
        loader = EpubLoader(Path("non/existent/file.epub"))
        with self.assertRaises(FileNotFoundError):
            loader.load()

    def test_not_a_zip_file(self):
        """Test loading a file that is not a zip archive."""
        loader = EpubLoader(self.not_a_zip_path)
        with self.assertRaisesRegex(InvalidEpubFileError, "not a valid ZIP file"):
            loader.load()

    def test_no_mimetype(self):
        """Test EPUB validation fails if mimetype is missing."""
        loader = EpubLoader(self.no_mimetype_epub_path)
        with self.assertRaisesRegex(InvalidEpubFileError, "mimetype' file not found"):
            loader.load()

    def test_mimetype_not_first(self):
        """Test EPUB validation fails if mimetype is not the first file."""
        loader = EpubLoader(self.mimetype_not_first_path)
        with self.assertRaisesRegex(InvalidEpubFileError, "'mimetype' must be the first file"):
            loader.load()

    def test_mimetype_compressed(self):
        """Test EPUB validation fails if mimetype is compressed."""
        loader = EpubLoader(self.mimetype_compressed_path)
        with self.assertRaisesRegex(InvalidEpubFileError, "'mimetype' file must not be compressed"):
            loader.load()

    def test_no_container_xml(self):
        """Test EPUB validation fails if container.xml is missing."""
        loader = EpubLoader(self.no_container_path)
        with self.assertRaisesRegex(InvalidEpubFileError, "'META-INF/container.xml' file not found"):
            loader.load()

    def test_missing_opf_file_content(self):
        """Test error when OPF file listed in container.xml is not in the archive."""
        loader = EpubLoader(self.no_opf_path)
        # This will raise a KeyError when trying to read the OPF content
        with self.assertRaises(KeyError):
            loader.load()


if __name__ == "__main__":
    unittest.main()
