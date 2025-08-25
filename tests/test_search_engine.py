import unittest
from unittest.mock import MagicMock

from epsilon_editor.core.search_engine import SearchEngine
from epsilon_editor.core.epub_model import EpubBook, ManifestItem


class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        """Set up a mock EpubBook and SearchEngine for testing."""
        self.mock_book = MagicMock(spec=EpubBook)
        self.mock_book.manifest = {
            "item1": ManifestItem(
                id="item1",
                href="content/page1.xhtml",
                media_type="application/xhtml+xml",
            ),
            "item2": ManifestItem(
                id="item2",
                href="content/page2.xhtml",
                media_type="application/xhtml+xml",
            ),
            "item3": ManifestItem(
                id="item3", href="styles/style.css", media_type="text/css"
            ),
        }

        self.mock_content_manager = MagicMock()
        self.mock_book.content_manager = self.mock_content_manager

        # Define what the mock content manager returns
        self.page1_content = (
            b"<html><body><p>This is a sample page with the word Test.</p></body></html>"
        )
        self.page2_content = (
            b"<html><body><p>Another page, without the keyword.</p></body></html>"
        )

        def get_content_side_effect(href):
            if href == "content/page1.xhtml":
                return self.page1_content
            if href == "content/page2.xhtml":
                return self.page2_content
            return b""

        self.mock_content_manager.get_content.side_effect = get_content_side_effect

        self.search_engine = SearchEngine(self.mock_book)

    def test_simple_search(self):
        """Test a simple case-insensitive search."""
        results = list(
            self.search_engine.search(
                query="test", case_sensitive=False, whole_word=True, regex=False
            )
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].match_text, "Test")

    def test_case_sensitive_search(self):
        """Test a case-sensitive search."""
        results = list(
            self.search_engine.search(
                query="Test", case_sensitive=True, whole_word=True, regex=False
            )
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].match_text, "Test")

        results_lower = list(
            self.search_engine.search(
                query="test", case_sensitive=True, whole_word=True, regex=False
            )
        )
        self.assertEqual(len(results_lower), 0)

    def test_whole_word_search(self):
        """Test the whole word search functionality."""
        results = list(
            self.search_engine.search(
                query="sam", case_sensitive=False, whole_word=True, regex=False
            )
        )
        self.assertEqual(len(results), 0)

        results_full = list(
            self.search_engine.search(
                query="sample", case_sensitive=False, whole_word=True, regex=False
            )
        )
        self.assertEqual(len(results_full), 1)

    def test_regex_search(self):
        """Test a search using a regular expression."""
        results = list(
            self.search_engine.search(
                query=r"T..t", case_sensitive=True, whole_word=False, regex=True
            )
        )
        # Should find "Test"
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].match_text, "Test")

    def test_no_results(self):
        """Test a search that should return no results."""
        results = list(
            self.search_engine.search(
                query="nonexistent",
                case_sensitive=False,
                whole_word=False,
                regex=False,
            )
        )
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
