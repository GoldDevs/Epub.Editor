from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.containers import VerticalScroll

from epsilon_editor.core.search_models import SearchResult


class SearchResultItem(ListItem):
    """A widget to display a single search result."""

    def __init__(self, result: SearchResult) -> None:
        super().__init__()
        self.result = result

    def compose(self) -> ComposeResult:
        """Create child widgets for the list item."""
        yield Label(f"{self.result.file_path}", classes="file-path")

        context_before = self.result.context[:self.result.match_start]
        match_text = self.result.match_text
        context_after = self.result.context[self.result.match_end:]

        # Use Textual's rich text markup for highlighting
        highlighted_context = (
            f"{context_before}[b u reverse]{match_text}[/b u reverse]{context_after}"
        )

        yield Label(highlighted_context, classes="context")


class SearchResultsScreen(Screen):
    """A screen to display search results."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        with VerticalScroll(id="results-body"):
            yield ListView(id="results-list")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        results = self.app.search_results
        list_view = self.query_one(ListView)
        for result in results:
            list_view.append(SearchResultItem(result))
