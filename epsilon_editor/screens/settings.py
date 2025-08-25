from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Switch
from textual.containers import VerticalScroll

from epsilon_editor.ui.material_components import Card


class SettingsScreen(Screen):
    """A screen for configuring application settings."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        with VerticalScroll(id="settings-body"):
            yield Card(
                "Appearance",
                Static("Dark Mode"),
                Switch(value=self.app.dark, id="dark-mode-switch"),
                id="appearance-card"
            )
            # Placeholder for keybindings - will be implemented later
            yield Card(
                "Keybindings",
                Static("Keybinding customization is not yet available."),
                id="keybindings-card"
            )
        yield Footer()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes."""
        if event.switch.id == "dark-mode-switch":
            self.app.action_toggle_dark()
