from textual.app import App
from textual.widgets import ListView

from epsilon_editor.core.epub_model import EpubBook
from epsilon_editor.screens.file_manager import FileManager
from epsilon_editor.screens.dashboard import Dashboard
from epsilon_editor.screens.search import SearchScreen
from epsilon_editor.screens.search_results import SearchResultsScreen
from epsilon_editor.screens.replace import ReplaceScreen
from epsilon_editor.screens.settings import SettingsScreen
from epsilon_editor.screens.batch_operations import BatchOperationsScreen
from epsilon_editor.screens.help import HelpScreen
from epsilon_editor.core.search_engine import SearchEngine
from epsilon_editor.core.replace_engine import ReplaceEngine
from epsilon_editor.core.epub_saver import EpubSaver


class EpsilonApp(App):
    """A Textual app to edit EPUBs."""

    SCREENS = {
        "file_manager": FileManager,
        "dashboard": Dashboard,
        "search": SearchScreen,
        "search_results": SearchResultsScreen,
        "replace": ReplaceScreen,
        "settings": SettingsScreen,
        "batch_operations": BatchOperationsScreen,
        "help": HelpScreen,
    }

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("f1", "show_help", "Help"),
        ("ctrl+s", "save_book", "Save Book"),
    ]

    def action_show_help(self) -> None:
        """Show the help screen."""
        self.push_screen("help")

    def __init__(self):
        super().__init__()
        self.book: EpubBook | None = None
        self.search_results = []

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        self.push_screen("file_manager")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_file_manager_file_selected(self, event: FileManager.FileSelected) -> None:
        """Handle file selection from the FileManager."""
        from epsilon_editor.core.epub_loader import EpubLoader, InvalidEpubFileError
        try:
            loader = EpubLoader(event.path)
            self.book = loader.load()
            self.push_screen("dashboard")
        except InvalidEpubFileError as e:
            self.notify(f"Error loading EPUB: {e}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"An unexpected error occurred: {e}", title="Error", severity="error")

    def on_search_screen_search_initiated(self, event: SearchScreen.SearchInitiated) -> None:
        """Handle search initiation from the SearchScreen."""
        if not self.book:
            self.notify("No EPUB loaded.", title="Error", severity="error")
            return

        try:
            search_engine = SearchEngine(self.book)
            self.search_results = list(search_engine.search(
                event.query,
                event.case_sensitive,
                event.whole_word,
                event.regex
            ))
            self.notify(f"Found {len(self.search_results)} results.", title="Search Complete")
            if self.search_results:
                self.push_screen("search_results")
            else:
                self.pop_screen()  # Go back to dashboard if no results
        except ValueError as e:
            self.notify(str(e), title="Search Error", severity="error")
        except Exception as e:
            self.notify(
                f"An unexpected error occurred during search: {e}",
                title="Error",
                severity="error",
            )

    def on_replace_screen_replace_initiated(self, event: ReplaceScreen.ReplaceInitiated) -> None:
        """Handle replace initiation from the ReplaceScreen."""
        if not self.book:
            self.notify("No EPUB loaded.", title="Error", severity="error")
            return

        try:
            replace_engine = ReplaceEngine(self.book)
            if event.replace_all:
                num_replacements = replace_engine.replace_all(
                    event.find,
                    event.replace,
                    event.case_sensitive,
                    event.whole_word,
                    event.regex
                )
                self.notify(f"Made {num_replacements} replacements.", title="Replace Complete")
                self.pop_screen()  # Go back to dashboard
            else:
                # Handle single replace
                if not isinstance(self.app.screen_stack[-2], SearchResultsScreen):
                    self.notify("Single replace can only be used from the search results screen.", title="Error", severity="error")
                    return

                search_results_screen = self.app.screen_stack[-2]
                list_view = search_results_screen.query_one("#results-list", ListView)
                if list_view.highlighted is None:
                    self.notify("No search result selected.", title="Warning", severity="warning")
                    return

                selected_item = list_view.highlighted
                search_result = selected_item.result

                num_replacements = replace_engine.replace_single(search_result, event.replace)

                if num_replacements > 0:
                    self.notify("Replacement successful.", title="Success")
                    # Remove the item from the list view and the search results
                    list_view.remove_child(selected_item.id)
                    self.search_results.remove(search_result)
                else:
                    self.notify("Replacement failed. The content may have changed.", title="Error", severity="error")

        except ValueError as e:
            self.notify(str(e), title="Replace Error", severity="error")
        except Exception as e:
            self.notify(f"An unexpected error occurred during replace: {e}", title="Error", severity="error")

    def on_batch_operations_screen_batch_operations_initiated(
        self, event: BatchOperationsScreen.BatchOperationsInitiated
    ) -> None:
        """Handle batch operations initiation."""
        if not self.book:
            self.notify("No EPUB loaded.", title="Error", severity="error")
            return

        try:
            replace_engine = ReplaceEngine(self.book)
            num_replacements = replace_engine.batch_replace_all(
                operations=event.operations,
                case_sensitive=event.case_sensitive,
                whole_word=event.whole_word,
                regex=event.regex,
            )
            self.notify(
                f"Made {num_replacements} replacements in batch operation.",
                title="Batch Replace Complete",
            )
            self.pop_screen()  # Go back to dashboard
        except ValueError as e:
            self.notify(str(e), title="Batch Replace Error", severity="error")
        except Exception as e:
            self.notify(
                f"An unexpected error occurred during batch replace: {e}",
                title="Error",
                severity="error",
            )

    def action_save_book(self) -> None:
        """Saves the current book."""
        if not self.book:
            self.notify("No book loaded to save.", title="Warning", severity="warning")
            return

        if not self.book.is_modified:
            self.notify("No changes to save.", title="Info", severity="information")
            return

        try:
            saver = EpubSaver(self.book)
            saver.save()
            self.notify("Book saved successfully.", title="Success", severity="information")
        except Exception as e:
            self.notify(f"Error saving book: {e}", title="Error", severity="error")


def main():
    """Run the application."""
    app = EpsilonApp()
    app.run()

if __name__ == "__main__":
    main()
