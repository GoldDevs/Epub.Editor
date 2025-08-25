from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Container, Vertical, Horizontal, Grid


class LayoutManager:
    """Manages responsive layouts for different screen sizes."""

    def __init__(self, screen_size):
        self.width = screen_size[0]
        self.height = screen_size[1]

    def is_mobile(self) -> bool:
        """Check if the screen size is considered mobile."""
        return self.width < 80

    def get_main_container(self, *children) -> Container:
        """Returns the main container for a screen."""
        if self.is_mobile():
            return Vertical(*children, id="main-container")
        else:
            return Horizontal(*children, id="main-container")

    def create_responsive_grid(self, *children) -> Grid:
        """Creates a grid that adapts to screen size."""
        if self.is_mobile():
            return Grid(*children, id="responsive-grid-mobile")
        else:
            return Grid(*children, id="responsive-grid-desktop")


class ResponsiveGrid(Grid):
    """A grid that rearranges its children based on screen width."""

    def __init__(self, *children: Widget, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.is_grid = True

    def on_resize(self, event) -> None:
        """Handle screen resize events."""
        if self.is_grid and event.size.width < 80:
            self.styles.grid_size_columns = 1
        elif self.is_grid:
            self.styles.grid_size_columns = 2
