from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent
PROJECTS = [
    {
        "name": "Goodreads Sync",
        "source": ROOT / "Goodreads Sync" / "src",
        "output": ROOT / "dist" / "Goodreads Sync-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Hardcover Sync",
        "source": ROOT / "HardCover Sync" / "src",
        "output": ROOT / "dist" / "Hardcover Sync-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Markdown Output",
        "source": ROOT / "Markdown Output" / "src",
        "output": ROOT / "dist" / "Markdown Output-zh_TW-release.zip",
    },
    {
        "name": "Traditional Chinese Supplement",
        "source": ROOT / "Traditional Chinese Supplement" / "src",
        "output": ROOT / "dist" / "Traditional Chinese Supplement-zh_TW-release.zip",
    },
    {
        "name": "Enhanced Search and Replace",
        "source": ROOT / "Enhanced Search and Replace" / "src",
        "output": ROOT / "dist" / "enhanced-search-and-replace.zip",
    },
    {
        "name": "Toolbar Manager",
        "source": ROOT / "Toolbar Manager" / "src",
        "output": ROOT / "dist" / "Toolbar Manager-zh_TW-release.zip",
    },
    {
        "name": "Generate Cover",
        "source": ROOT / "Generate Cover" / "src",
        "output": ROOT / "dist" / "Generate Cover-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Skip ASCII Text Plugin",
        "source": ROOT / "Skip ASCII Text Plugin" / "src",
        "output": ROOT / "dist" / "Skip ASCII Text Plugin-zh_TW-release.zip",
    },
    {
        "name": "Extract ISBN",
        "source": ROOT / "Extract ISBN" / "src",
        "output": ROOT / "dist" / "Extract ISBN-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Goodreads",
        "source": ROOT / "Goodreads" / "src",
        "output": ROOT / "dist" / "Goodreads.zip",
    },
    {
        "name": "AZW6 Image Merge",
        "source": ROOT / "AZW6 Image Merge" / "src",
        "output": ROOT / "dist" / "AZW6 Image Merge-zh_TW-release.zip",
    },
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
    {
        "name": "EpubSplit",
        "source": ROOT / "EpubSplit" / "src",
        "output": ROOT / "dist" / "EpubSplit-zh_TW-release.zip",
    },
    {
        "name": "Count Pages",
        "source": ROOT / "Count Pages" / "src",
        "output": ROOT / "dist" / "Count Pages-zh_TW-release.zip",
    },
    {
        "name": "Send to Kindle",
        "source": ROOT / "Send to Kindle" / "src",
        "output": ROOT / "dist" / "Send to Kindle-zh_TW-release.zip",
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


def build_zip(source_dir: Path, output_zip: Path, compile_translations: bool = False) -> None:
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
            if source_dir == ROOT / "Embed Metadata Safe" / "src" and rel.parts[0] == "embed_metadata_safe":
                rel = Path(*rel.parts[1:])
            if any(part.startswith(".") for part in rel.parts):
                continue
            if any(part == "__pycache__" for part in rel.parts):
                continue
            if file_path.suffix.lower() == ".po":
                continue
            arcname = rel.as_posix()
            zf.write(file_path, arcname)
        if compile_translations:
            with tempfile.TemporaryDirectory(dir=output_zip.parent) as temp_dir:
                script = (
                    "from pathlib import Path; import sys; "
                    "from calibre.translations.msgfmt import make_with_stats as make; "
                    "[make(str(p), str(Path(sys.argv[2]) / (p.stem + '.mo'))) "
                    "for p in Path(sys.argv[1]).glob('*.po')]"
                )
                subprocess.run(
                    ["calibre-debug", "-c", script, str(source_dir / "translations"), temp_dir],
                    check=True,
                )
                for translation in sorted(Path(temp_dir).glob("*.mo")):
                    zf.write(translation, "translations/" + translation.name)


def main() -> None:
    clean_dist()
    for project in PROJECTS:
        build_zip(project["source"], project["output"], project.get("compile_translations", False))
        print(f"Built {project['name']}: {project['output']}")


if __name__ == "__main__":
    main()
