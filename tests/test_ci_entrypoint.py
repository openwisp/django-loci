"""Check the CI entry point without executing application tests."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class CiEntrypointTests(unittest.TestCase):
    def test_rejects_unreviewed_options(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "coverage"
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
            env = {**os.environ, "PATH": f"{directory}:{os.environ['PATH']}"}
            for argument in (
                "--settings=other",
                "--testrunner=other.Runner",
                "os.system",
            ):
                with self.subTest(argument=argument):
                    result = subprocess.run(
                        [str(ROOT / "runtests"), argument],
                        cwd=ROOT,
                        env=env,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("unsupported", result.stderr.lower())

    def test_full_run_preserves_both_coverage_configurations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            log = path / "calls"
            coverage = path / "coverage"
            coverage.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n')
            coverage.chmod(0o755)
            result = subprocess.run(
                [str(ROOT / "runtests")],
                cwd=ROOT,
                env={
                    **os.environ,
                    "PATH": f"{path}:{os.environ['PATH']}",
                    "CALLS": str(log),
                },
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                log.read_text().splitlines(),
                [
                    "erase",
                    "run runtests.py --parallel --exclude-tag=selenium_tests",
                    "run runtests.py --tag=selenium_tests --exclude-pytest",
                    "combine",
                    "xml",
                ],
            )

    def test_focused_channels_does_not_add_the_whole_test_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            (root / "tests").mkdir()
            (root / "django.py").write_text("def setup(): pass\n")
            (root / "pytest.py").write_text(
                'def main(args):\n    print("|".join(args))\n    return 17\n'
            )
            result = subprocess.run(
                [str(root / "runtests"), "django_loci/tests/pytest_channels.py", "-q"],
                cwd=root,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 17)
        self.assertEqual(
            result.stdout.strip(),
            "-o|addopts=--create-db --reuse-db --nomigrations|django_loci/tests/pytest_channels.py|-q",
        )

    def test_rejects_a_non_test_class(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            (root / "tests").mkdir()
            (root / "django.py").write_text("def setup(): pass\n")
            (root / "django_loci" / "tests").mkdir(parents=True)
            (root / "django_loci" / "__init__.py").touch()
            (root / "django_loci" / "tests" / "__init__.py").touch()
            (root / "django_loci" / "tests" / "test_probe.py").write_text(
                'class Helper:\n    @staticmethod\n    def test_action(): print("unexpected")\n'
            )
            result = subprocess.run(
                [
                    str(root / "runtests"),
                    "django_loci.tests.test_probe.Helper.test_action",
                ],
                cwd=root,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported", result.stderr.lower())
        self.assertNotIn("unexpected", result.stdout)
