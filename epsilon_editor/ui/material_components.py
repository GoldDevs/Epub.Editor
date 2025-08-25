from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button as TextualButton


class Card(VerticalScroll):
    """A card widget for the UI."""

    DEFAULT_CSS = """
    Card {
        border: round #666;
        padding: 1;
        margin: 1 2;
        border-title-align: center;
    }
    """

    def __init__(
        self,
        title: str,
        *children,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.border_title = title

    def compose(self) -> ComposeResult:
        """Create child widgets for the card."""
        yield from self.children


class Button(TextualButton):
    """A Material Design inspired button."""
    DEFAULT_CSS = """
    Button {
        width: 100%;
        text-align: center;
        background: #444;
        border: none;
        padding: 1;
        margin: 1 0;
    }
    Button:hover {
        background: #666;
    }
    """
    pass
