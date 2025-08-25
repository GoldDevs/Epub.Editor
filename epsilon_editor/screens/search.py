from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Checkbox, Button
from textual.containers import VerticalScroll, Horizontal
from textual.message import Message

from epsilon_editor.ui.material_components import Card


class SearchScreen(Screen):
    """A screen for searching text within the EPUB."""

    class SearchInitiated(Message):
        """Posted when a search is initiated."""
        def __init__(self, query: str, case_sensitive: bool, whole_word: bool, regex: bool) -> None:
            self.query = query
            self.case_sensitive = case_sensitive
            self.whole_word = whole_word
            self.regex = regex
            super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        with VerticalScroll(id="search-body"):
            yield Card(
                "Search",
                Input(placeholder="Enter text to search...", id="search-input"),
                Horizontal(
                    Checkbox("Case-sensitive", id="case-sensitive-checkbox"),
                    Checkbox("Whole word", id="whole-word-checkbox"),
                    Checkbox("Regex", id="regex-checkbox"),
                    id="search-options"
                ),
                Horizontal(
                    Button("Search", id="search-button", variant="primary"),
                    Button("Cancel", id="cancel-button"),
                    id="search-actions"
                ),
                id="search-card"
            )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search-button":
            query = self.query_one("#search-input", Input).value
            if query:
                case_sensitive = self.query_one("#case-sensitive-checkbox", Checkbox).value
                whole_word = self.query_one("#whole-word-checkbox", Checkbox).value
                regex = self.query_one("#regex-checkbox", Checkbox).value
                self.post_message(self.SearchInitiated(query, case_sensitive, whole_word, regex))
            else:
                self.app.notify("Please enter a search query.", title="Warning", severity="warning")
        elif event.button.id == "cancel-button":
            self.app.pop_screen()
