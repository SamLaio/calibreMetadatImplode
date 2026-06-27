from __future__ import annotations

from pathlib import Path
import shutil
import zipfile


ROOT = Path(__file__).resolve().parent
PROJECTS = [
    {
        "name": "Embed Metadata Safe",
        "source": ROOT / "Embed Metadata Safe" / "src",
        "output": ROOT / "dist" / "embed-metadata-safe.zip",
    },
    {
        "name": "Modify ePub",
        "source": ROOT / "Modify ePub" / "src",
        "output": ROOT / "dist" / "Modify ePub-zh_TW-release.zip",
    },
    {
        "name": "Find Duplicates",
        "source": ROOT / "Find Duplicates" / "src",
        "output": ROOT / "dist" / "Find Duplicates-zh_TW-release.zip",
    },
]


def clean_dist() -> None:
    dist_dir = ROOT / "dist"
    if not dist_dir.exists():
        return
    for path in dist_dir.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def build_zip(source_dir: Path, output_zip: Path) -> None:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    with zipfile.ZipFile(
        output_zip,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(source_dir)
            if any(part.startswith(".") for part in rel.parts):
                continue
            if any(part == "__pycache__" for part in rel.parts):
                continue
            if file_path.suffix.lower() == ".po":
                continue
            arcname = rel.as_posix()
            zf.write(file_path, arcname)


def main() -> None:
    clean_dist()
    for project in PROJECTS:
        build_zip(project["source"], project["output"])
        print(f"Built {project['name']}: {project['output']}")


if __name__ == "__main__":
    main()
