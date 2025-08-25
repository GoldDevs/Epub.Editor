from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label
from textual.containers import VerticalScroll
from textual.binding import Binding

from epsilon_editor.ui.material_components import Card, Button
from epsilon_editor.ui.layout_manager import LayoutManager, ResponsiveGrid


class Dashboard(Screen):
    """The main dashboard screen."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+q", "save_and_quit", "Save & Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        book = self.app.book
        with ResponsiveGrid():
            if book:
                yield Card(
                    "File Information",
                    Label(f"Title: {book.metadata.title}"),
                    Label(f"Author(s): {', '.join(book.metadata.creator) if book.metadata.creator else 'N/A'}"),
                    Label(f"Identifier: {book.metadata.identifier}"),
                    Label(f"Language: {book.metadata.language}"),
                    Label(f"Publisher: {book.metadata.publisher}"),
                    id="file-info-card"
                )

                num_content_files = sum(1 for item in book.manifest.values() if "xhtml" in item.media_type)

                yield Card(
                    "Statistics",
                    Label(f"Total Files: {len(book.manifest)}"),
                    Label(f"Content Files: {num_content_files}"),
                    Label(f"Spine Items: {len(book.spine)}"),
                    Label(f"TOC Entries: {len(book.toc)}"),
                    id="stats-card"
                )

                yield Card(
                    "Quick Actions",
                    Button("Search", id="search-button"),
                    Button("Replace", id="replace-button"),
                    Button("Batch Operations", id="batch-operations-button"),
                    Button("Settings", id="settings-button"),
                    Button("Help", id="help-button"),
                    id="quick-actions-card"
                )

                yield Card(
                    "File Operations",
                    Button("Save", id="save-button", variant="primary", disabled=not book.is_modified),
                    Button("Save & Quit", id="save-quit-button"),
                    id="file-ops-card"
                )
            else:
                yield Card("File Information", Label("No EPUB loaded."), id="file-info-card")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted to update button state."""
        if self.app.book:
            self.query_one("#save-button", Button).disabled = not self.app.book.is_modified

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search-button":
            self.app.push_screen("search")
        elif event.button.id == "replace-button":
            self.app.push_screen("replace")
        elif event.button.id == "batch-operations-button":
            self.app.push_screen("batch_operations")
        elif event.button.id == "settings-button":
            self.app.push_screen("settings")
        elif event.button.id == "help-button":
            self.app.push_screen("help")
        elif event.button.id == "save-button":
            self.action_save()
        elif event.button.id == "save-quit-button":
            self.action_save_and_quit()

    def action_save(self) -> None:
        """Action to save the book."""
        self.app.action_save_book()
        # Re-disable the button after saving
        self.query_one("#save-button", Button).disabled = not self.app.book.is_modified

    def action_save_and_quit(self) -> None:
        """Action to save the book and then quit."""
        self.app.action_save_book()
        self.app.action_quit()
