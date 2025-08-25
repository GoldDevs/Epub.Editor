import re
from typing import TYPE_CHECKING
from bs4 import BeautifulSoup

from epsilon_editor.core.epub_model import EpubBook

if TYPE_CHECKING:
    from epsilon_editor.core.search_models import SearchResult


class ReplaceEngine:
    """A class to perform find and replace operations within an EPUB."""

    def __init__(self, book: EpubBook):
        self.book = book

    def _replace_in_file(self, item, search_pattern, replace) -> int:
        content_manager = self.book.content_manager
        try:
            content = content_manager.get_content(item.href)
            soup = BeautifulSoup(content, "lxml")
            text_nodes = soup.find_all(string=True)
            file_replacements = 0
            for node in text_nodes:
                if node.parent.name in ["style", "script"]:
                    continue
                new_content, num_subs = search_pattern.subn(replace, node.string)
                if num_subs > 0:
                    node.string.replace_with(new_content)
                    file_replacements += num_subs
            if file_replacements > 0:
                new_html = soup.prettify(encoding="utf-8")
                content_manager.update_content(item.href, new_html)
            return file_replacements
        except (FileNotFoundError, KeyError):
            return 0

    def replace_all(
        self, find: str, replace: str, case_sensitive: bool, whole_word: bool, regex: bool
    ) -> int:
        """
        Replaces all occurrences of a string in the EPUB content.

        Args:
            find: The text to search for.
            replace: The text to replace with.
            case_sensitive: Whether the search is case-sensitive.
            whole_word: Whether to match whole words only.
            regex: Whether the query is a regular expression.

        Returns:
            The total number of replacements made.
        """
        flags = 0 if case_sensitive else re.IGNORECASE
        if not regex:
            find = re.escape(find)
        if whole_word:
            find = r"\b" + find + r"\b"

        try:
            search_pattern = re.compile(find, flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}") from e

        total_replacements = 0
        for item in self.book.manifest.values():
            if "html" in item.media_type:
                total_replacements += self._replace_in_file(
                    item, search_pattern, replace
                )
        return total_replacements

    def batch_replace_all(self, operations: list[tuple[str, str]], case_sensitive: bool, whole_word: bool, regex: bool) -> int:
        """
        Performs a batch of replace all operations.

        For simplicity, this implementation iterates through the operations and calls
        replace_all for each. A more optimized version might process all replacements
        in a single pass over the content.

        Args:
            operations: A list of (find, replace) tuples.
            case_sensitive: Whether the search is case-sensitive for all operations.
            whole_word: Whether to match whole words for all operations.
            regex: Whether the queries are regular expressions for all operations.

        Returns:
            The total number of replacements made across all operations.
        """
        total_replacements = 0
        for find, replace in operations:
            total_replacements += self.replace_all(find, replace, case_sensitive, whole_word, regex)
        return total_replacements

    def replace_single(self, search_result: "SearchResult", replace_text: str) -> int:
        """
        Replaces a single occurrence of a match in the EPUB content.

        Args:
            search_result: The SearchResult object for the match to replace.
            replace_text: The text to replace with.

        Returns:
            The number of replacements made (should be 1 if successful).
        """
        content_manager = self.book.content_manager
        try:
            content = content_manager.get_content(search_result.item_href)
            soup = BeautifulSoup(content, "lxml")
            text_nodes = soup.find_all(string=True)

            if search_result.node_index >= len(text_nodes):
                return 0  # Node index out of bounds

            node_to_replace = text_nodes[search_result.node_index]

            original_text = node_to_replace.string

            # Re-verify that the match is still present at the expected location
            if original_text[search_result.match_start:search_result.match_end] != search_result.match_text:
                # The content might have changed since the search.
                # A more robust implementation might re-search the node.
                return 0

            new_text = (
                original_text[:search_result.match_start] +
                replace_text +
                original_text[search_result.match_end:]
            )

            node_to_replace.string.replace_with(new_text)

            new_html = soup.prettify(encoding="utf-8")
            content_manager.update_content(search_result.item_href, new_html)
            self.book.is_modified = True
            return 1

        except (FileNotFoundError, KeyError, IndexError):
            return 0
