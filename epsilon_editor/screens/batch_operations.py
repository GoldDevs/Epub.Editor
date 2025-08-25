from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, ListView, ListItem, Input, Checkbox
from textual.containers import VerticalScroll, Horizontal
from textual.message import Message
from typing import List, Tuple


class BatchOperationItem(ListItem):
    """A widget for a single find/replace operation in a batch."""
    def __init__(self, find: str = "", replace: str = "") -> None:
        super().__init__()
        self.find_text = find
        self.replace_text = replace

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Input(value=self.find_text, placeholder="Find..."),
            Input(value=self.replace_text, placeholder="Replace with..."),
        )

    @property
    def values(self) -> Tuple[str, str]:
        inputs = self.query(Input)
        return inputs[0].value, inputs[1].value


class BatchOperationsScreen(Screen):
    """A screen for performing batch find/replace operations."""

    class BatchOperationsInitiated(Message):
        """Posted when batch operations are initiated."""
        def __init__(
            self,
            operations: List[Tuple[str, str]],
            case_sensitive: bool,
            whole_word: bool,
            regex: bool,
        ) -> None:
            self.operations = operations
            self.case_sensitive = case_sensitive
            self.whole_word = whole_word
            self.regex = regex
            super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        with VerticalScroll(id="batch-body"):
            yield ListView(id="batch-list")
            yield Horizontal(
                Checkbox("Case-sensitive", id="case-sensitive-checkbox"),
                Checkbox("Whole word", id="whole-word-checkbox"),
                Checkbox("Regex", id="regex-checkbox"),
                id="batch-options"
            )
        yield Footer()
        yield Horizontal(
            Button("Add Row", id="add-row-button"),
            Button("Remove Row", id="remove-row-button"),
            Button("Start Batch", id="start-batch-button", variant="primary"),
            Button("Cancel", id="cancel-button"),
            id="batch-actions"
        )

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Add an initial empty row
        self.query_one(ListView).append(BatchOperationItem())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        list_view = self.query_one(ListView)
        if event.button.id == "add-row-button":
            list_view.append(BatchOperationItem())
            list_view.scroll_end()
        elif event.button.id == "remove-row-button":
            if list_view.children:
                list_view.children[-1].remove()
        elif event.button.id == "start-batch-button":
            operations = [item.values for item in list_view.query(BatchOperationItem)]
            # Filter out empty operations
            operations = [op for op in operations if op[0]]
            if operations:
                case_sensitive = self.query_one("#case-sensitive-checkbox", Checkbox).value
                whole_word = self.query_one("#whole-word-checkbox", Checkbox).value
                regex = self.query_one("#regex-checkbox", Checkbox).value
                self.post_message(
                    self.BatchOperationsInitiated(
                        operations, case_sensitive, whole_word, regex
                    )
                )
            else:
                self.app.notify("No operations to perform.", title="Warning", severity="warning")
        elif event.button.id == "cancel-button":
            self.app.pop_screen()
