import argparse
from pathlib import Path
import sys

from epsilon_editor.core.epub_loader import EpubLoader, InvalidEpubFileError


def view_metadata(filepath: Path):
    """Loads an EPUB and prints its metadata."""
    if not filepath.exists() or not filepath.is_file():
        print(f"Error: File not found at {filepath}")
        sys.exit(1)

    try:
        loader = EpubLoader(filepath)
        book = loader.load()
        print(f"Metadata for: {filepath.name}")
        print("-" * 20)
        for key, value in book.metadata.all_metadata.items():
            # The values are lists, join them for printing
            print(f"{key.capitalize()}: {', '.join(value)}")
        print("-" * 20)

    except InvalidEpubFileError as e:
        print(f"Error loading EPUB: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Epsilon Editor Command-Line Interface.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Metadata command
    meta_parser = subparsers.add_parser("meta", help="View EPUB metadata.")
    meta_parser.add_argument("filepath", type=Path, help="Path to the EPUB file.")

    args = parser.parse_args()

    if args.command == "meta":
        view_metadata(args.filepath)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
