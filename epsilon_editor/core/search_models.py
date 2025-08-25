from dataclasses import dataclass


@dataclass
class SearchResult:
    """Represents a single search result."""
    file_path: str
    item_href: str  # To identify the EPUB item
    node_index: int  # The index of the text node in the document
    match_start: int  # The start index of the match in the node's text
    match_end: int  # The end index of the match in the node's text
    match_text: str
    context: str  # The text of the node containing the match
