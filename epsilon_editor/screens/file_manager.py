from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DirectoryTree, Header, Footer
from textual.containers import Container
from textual.message import Message


class EpubDirectoryTree(DirectoryTree):
    """A DirectoryTree that filters for EPUB files."""

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        """Filter paths to only include directories and .epub files."""
        return [path for path in paths if path.is_dir() or path.suffix == ".epub"]


class FileManager(Screen):
    """A screen for selecting an EPUB file."""

    class FileSelected(Message):
        """Posted when a file is selected."""
        def __init__(self, path: Path) -> None:
            self.path = path
            super().__init__()

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        yield Container(EpubDirectoryTree(Path.home()))
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        self.post_message(self.FileSelected(event.path))
