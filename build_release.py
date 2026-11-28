from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent
PROJECTS = [
    {
        "name": "Virtual Library Builder",
        "source": ROOT / "Virtual Library Builder" / "src",
        "output": ROOT / "dist" / "VirtualLibraryBuilder.zip",
    },
    {
        "name": "Tag Cloud",
        "source": ROOT / "Tag Cloud" / "src",
        "output": ROOT / "dist" / "TagCloud.zip",
    },
    {
        "name": "GitHub Plugin Updater",
        "source": ROOT / "GitHub Plugin Updater" / "src",
        "output": ROOT / "dist" / "GitHub Plugin Updater-zh_TW-release.zip",
    },
    {
        "name": "CrossPoint Reader",
        "source": ROOT / "CrossPoint Reader" / "src",
        "output": ROOT / "dist" / "CrossPoint Reader-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Shortcuts Helper",
        "source": ROOT / "Shortcuts Helper" / "src",
        "output": ROOT / "dist" / "Shortcuts Helper-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "CBZ Output",
        "source": ROOT / "CBZ Output" / "src",
        "output": ROOT / "dist" / "CBZ Output-zh_TW-release.zip",
    },
    {
        "name": "Plugin Backup",
        "source": ROOT / "Plugin Backup" / "src",
        "output": ROOT / "dist" / "Plugin Backup-zh_TW-release.zip",
    },
    {
        "name": "Diaps Editing Toolbag",
        "source": ROOT / "Diaps Editing Toolbag" / "src",
        "output": ROOT / "dist" / "Diaps Editing Toolbag-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Columns Helper",
        "source": ROOT / "Columns Helper" / "src",
        "output": ROOT / "dist" / "Columns Helper-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Manage Series",
        "source": ROOT / "Manage Series" / "src",
        "output": ROOT / "dist" / "Manage Series-zh_TW-release.zip",
        "compile_translations": True,
    },
    {
        "name": "Export Folder",
        "source": ROOT / "exportFolder" / "src",
        "output": ROOT / "dist" / "Export Folder-zh_TW-release.zip",
    },
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


def write_member(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def payload_digest(archive: zipfile.ZipFile) -> str:
    result = hashlib.sha256(b"calibre-plugin-content-v1\0")
    for member in sorted(archive.infolist(), key=lambda m: m.filename):
        if member.is_dir() or member.filename == "github-plugin-identity.json":
            continue
        name = member.filename.encode("utf-8")
        result.update(len(name).to_bytes(8, "big"))
        result.update(name)
        result.update(member.file_size.to_bytes(8, "big"))
        with archive.open(member) as stream:
            while chunk := stream.read(1024 * 1024):
                result.update(chunk)
    return result.hexdigest()


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
            if arcname == "github-plugin-identity.json":
                continue
            write_member(zf, arcname, file_path.read_bytes())
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
                    write_member(zf, "translations/" + translation.name, translation.read_bytes())
        project = next((p for p in PROJECTS if p["source"] == source_dir), None)
        if project is not None:
            identity = {
                "id": "samlaio." + re.sub(r"[^a-z0-9]+", "-", project["name"].lower()).strip("-"),
                "source": "github:samlaio/calibremetadatimplode",
                "sha256": payload_digest(zf),
            }
            write_member(zf, "github-plugin-identity.json",
                         (json.dumps(identity, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def build_manifest() -> None:
    """Read our packaged declarations using calibre; hash only completed ZIPs."""
    with tempfile.TemporaryDirectory(dir=ROOT / "dist") as temporary:
        metadata_path = Path(temporary) / "metadata.json"
        script = (
            "import json,sys; from pathlib import Path; "
            "from calibre.customize.zipplugin import loader; "
            "files=json.loads(sys.argv[1]); result=[]; "
            "\nfor filename in files:\n"
            " cls=loader.load(filename)\n"
            " result.append(dict(name=cls.name,version=list(cls.version),"
            "minimum_calibre_version=list(cls.minimum_calibre_version),"
            "supported_platforms=list(cls.supported_platforms)))\n"
            "Path(sys.argv[2]).write_text(json.dumps(result),encoding='utf-8')"
        )
        subprocess.run(
            ["calibre-debug", "-c", script, json.dumps([str(p["output"]) for p in PROJECTS]), str(metadata_path)],
            env=dict(os.environ, CALIBRE_CONFIG_DIRECTORY=str(Path(temporary) / "profile")), check=True,
        )
        entries = json.loads(metadata_path.read_text(encoding="utf-8"))
    for project, entry in zip(PROJECTS, entries):
        package = project["output"]
        with zipfile.ZipFile(package) as archive:
            identity = json.loads(archive.read("github-plugin-identity.json"))
        entry.update(id=identity["id"], asset=package.name, size=package.stat().st_size,
                     sha256=identity["sha256"], package_sha256=hashlib.sha256(package.read_bytes()).hexdigest())
    manifest = {"format": "calibre-github-plugins", "schema": 1,
                "source": "github:samlaio/calibremetadatimplode", "plugins": entries}
    (ROOT / "dist" / "plugins.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    clean_dist()
    for project in PROJECTS:
        build_zip(project["source"], project["output"], project.get("compile_translations", False))
        print(f"Built {project['name']}: {project['output']}")
    build_manifest()


if __name__ == "__main__":
    main()
