"""Release boundaries: debug helpers and live saves must never enter the ZIP."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('build_mod', Path(__file__).resolve().parents[1] / 'tools/build_mod.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ReleaseChecks(unittest.TestCase):
    def test_release_excludes_development_and_save_data_but_keeps_normal_scenarios(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            keep = ['42/mod.info', '42/media/lua/client/3_Other/main.lua',
                    '42/media/maps/Hilltop Survivor Camp/spawnpoints.lua',
                    'common/media/textures/PVPOn.png']
            omit = ['42/media/lua/client/Debug/SuperbSurvivorsTests.lua',
                    '42/media/maps/SSDebug_Medical/spawnpoints.lua',
                    'common/world/SurvivorGroup0.lua', 'reference/old.lua', 'docs/readme.md']
            for name in keep + omit:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture')
            output = root / 'package.zip'
            self.assertEqual(builder.build_archive(root, output), len(keep))
            with ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {f'Contents/mods/SuperbSurvivors/{p}' for p in keep})
            with self.assertRaises(FileExistsError):
                builder.build_archive(root, output)
