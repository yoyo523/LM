"""Package Assignment 2b deliverables, excluding course learning material."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
CONTENTS = {
    "klean": {".py"},
    "tests": {".py"},
    "examples": {".kln", ".md", ".json"},
    "docs": {".md"},
    "scripts": {".py", ".sh"},
}


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("archive", type=Path, help="new .zip file; existing files are preserved")
    args = cli.parse_args()
    if args.archive.suffix.lower() != ".zip":
        cli.error("archive must have a .zip extension")

    files = [ROOT / "README.md"]
    for folder, extensions in CONTENTS.items():
        source = ROOT / folder
        if not source.is_dir() or source.is_symlink():
            cli.error(f"missing or linked source directory: {folder}")
        for path in sorted(source.rglob("*")):
            parts = path.relative_to(ROOT).parts
            if any(part.startswith(".") or part == "__pycache__" for part in parts):
                continue
            if any((ROOT.joinpath(*parts[:i])).is_symlink() for i in range(1, len(parts) + 1)):
                continue
            if path.is_file() and path.suffix in extensions:
                files.append(path)

    if not files[0].is_file() or files[0].is_symlink():
        cli.error("README.md must be a regular file")
    try:
        # Exclusive creation avoids replacing an existing submission archive.
        with zipfile.ZipFile(args.archive, "x", zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, Path("klean-assignment-2b") / path.relative_to(ROOT))
    except OSError as error:
        cli.exit(1, f"Cannot create archive: {error}\n")
    print(f"Created {args.archive} with {len(files)} files (course/ excluded).")


if __name__ == "__main__":
    main()
