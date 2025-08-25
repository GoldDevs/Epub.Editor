import unittest
from unittest.mock import MagicMock

from epsilon_editor.core.replace_engine import ReplaceEngine
from epsilon_editor.core.epub_model import EpubBook, ManifestItem


class TestReplaceEngine(unittest.TestCase):

    def setUp(self):
        """Set up a mock EpubBook and ReplaceEngine for testing."""
        self.mock_book = MagicMock(spec=EpubBook)
        self.mock_book.manifest = {
            'item1': ManifestItem(id='item1', href='content/page1.xhtml', media_type='application/xhtml+xml'),
        }

        self.mock_content_manager = MagicMock()
        self.mock_book.content_manager = self.mock_content_manager

        self.initial_content = b'<html><body><p>This is a test to test replacement.</p></body></html>'

        # This will be called by the engine to get the content
        self.mock_content_manager.get_content.return_value = self.initial_content

        self.replace_engine = ReplaceEngine(self.mock_book)

    def test_simple_replace_all(self):
        """Test a simple 'replace all' operation."""
        replacements = self.replace_engine.replace_all(
            find='test',
            replace='sample',
            case_sensitive=False,
            whole_word=True,
            regex=False
        )
        self.assertEqual(replacements, 2)

        # Check that update_content was called with the correct new content
        self.mock_content_manager.update_content.assert_called_once()
        call_args = self.mock_content_manager.update_content.call_args[0]
        href_arg = call_args[0]
        content_arg = call_args[1]

        self.assertEqual(href_arg, 'content/page1.xhtml')
        self.assertIn(b'a sample to sample replacement', content_arg)
        self.assertNotIn(b'a test to test replacement', content_arg)

    def test_batch_replace_all(self):
        """Test a batch 'replace all' operation."""
        # Make the mock content manager more realistic for this test
        self.mock_content_manager.reset_mock()

        # Simulate a content store that gets updated
        content_store = {'content/page1.xhtml': self.initial_content}

        def mock_get_content(href):
            return content_store[href]

        def mock_update_content(href, new_content):
            content_store[href] = new_content

        self.mock_content_manager.get_content.side_effect = mock_get_content
        self.mock_content_manager.update_content.side_effect = mock_update_content

        operations = [
            ('test', 'sample'),
            ('replacement', 'substitution')
        ]

        total_replacements = self.replace_engine.batch_replace_all(
            operations=operations,
            case_sensitive=False,
            whole_word=True,
            regex=False
        )

        self.assertEqual(total_replacements, 3)  # 2 for 'test', 1 for 'replacement'

        # Check the final state of the content
        final_content = content_store['content/page1.xhtml']
        self.assertIn(b'a sample to sample substitution', final_content)


if __name__ == '__main__':
    unittest.main()
