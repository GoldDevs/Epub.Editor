from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import VerticalScroll

from epsilon_editor.ui.material_components import Card


class HelpScreen(Screen):
    """A screen that displays help information."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        with VerticalScroll(id="help-body"):
            yield Card(
                "About",
                Static("Epsilon Editor is a powerful, terminal-based EPUB editor, "
                       "designed for efficiency and ease of use, especially on mobile devices with Termux."),
                id="about-card"
            )

            yield Card(
                "How to Use",
                Static("1. Start by selecting an EPUB file from the File Manager.\n"
                       "2. Use the Dashboard to see an overview of your file and access quick actions.\n"
                       "3. Use Search, Replace, or Batch Operations to modify your book.\n"
                       "4. Your changes are saved in memory. Use the 'Save' button or Ctrl+S to write changes to the file.\n"
                       "5. A backup of your original file is created with a .bak extension upon first save."),
                id="how-to-use-card"
            )

            keybindings_text = "Global Keybindings:\n"
            for binding in self.app.BINDINGS:
                keybindings_text += f"- {binding[0]}: {binding[2]}\n"

            # It's better to manage bindings in a more central way, but for now,
            # we will also list the dashboard bindings as they are important.
            from epsilon_editor.screens.dashboard import Dashboard
            keybindings_text += "\nDashboard Keybindings:\n"
            for binding in Dashboard.BINDINGS:
                keybindings_text += f"- {binding.key}: {binding.description}\n"

            yield Card(
                "Keybindings",
                Static(keybindings_text),
                id="keybindings-card"
            )
        yield Footer()
