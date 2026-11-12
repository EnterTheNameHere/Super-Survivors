"""Build a Workshop-layout ZIP without development helpers or live save output."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = Path('Contents/mods/SuperbSurvivors')


def release_files(root):
    for folder in ('42', 'common/media'):
        for path in sorted((root / folder).rglob('*')):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            # All console helpers and scenario runners are development-only.
            if relative.parts[:5] == ('42', 'media', 'lua', 'client', 'Debug'):
                continue
            # Reserve this prefix for future development map stations.
            if relative.parts[:3] == ('42', 'media', 'maps') and relative.parts[3].startswith('SSDebug_'):
                continue
            if '__pycache__' in relative.parts or path.suffix in ('.pyc', '.pyo'):
                continue
            yield path, MOD_PATH / relative


def build_archive(root, output):
    files = list(release_files(root))
    if not (root / '42/mod.info').is_file():
        raise ValueError('Expected 42/mod.info in the mod source')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Refuse to silently overwrite an existing artifact.
    with ZipFile(output, 'x', compression=ZIP_DEFLATED) as archive:
        for source, destination in files:
            archive.write(source, destination.as_posix())
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/SuperbSurvivors-release.zip')
    args = parser.parse_args()
    count = build_archive(ROOT, args.output.resolve())
    print(f'Packaged {count} files: {args.output.resolve()}')


if __name__ == '__main__':
    main()
