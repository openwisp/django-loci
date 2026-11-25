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

    def test_focused_django_labels_are_forwarded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            (root / "tests").mkdir()
            (root / "django" / "core").mkdir(parents=True)
            (root / "django_loci" / "tests").mkdir(parents=True)
            for package in (
                root / "django",
                root / "django" / "core",
                root / "django_loci",
                root / "django_loci" / "tests",
            ):
                (package / "__init__.py").touch()
            (root / "django" / "__init__.py").write_text("def setup(): pass\n")
            (root / "django" / "core" / "management.py").write_text(
                'def execute_from_command_line(args): print("|".join(args[1:]))\n'
            )
            (root / "django_loci" / "tests" / "test_probe.py").write_text(
                "import unittest\nclass TestProbe(unittest.TestCase):\n    def test_ok(self): pass\n"
            )
            for label in (
                "django_loci.tests.test_probe",
                "django_loci.tests.test_probe.TestProbe",
                "django_loci.tests.test_probe.TestProbe.test_ok",
            ):
                with self.subTest(label=label):
                    result = subprocess.run(
                        [str(root / "runtests"), label, "--noinput"],
                        cwd=root,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), f"test|{label}|--noinput")

    def test_rejects_callable_in_place_of_test_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            (root / "tests").mkdir()
            (root / "django.py").write_text("def setup(): pass\n")
            (root / "django_loci" / "tests").mkdir(parents=True)
            (root / "django_loci" / "__init__.py").touch()
            (root / "django_loci" / "tests" / "__init__.py").write_text(
                'def test_action(): print("unexpected execution")\n'
            )
            result = subprocess.run(
                [str(root / "runtests"), "django_loci.tests.test_action"],
                cwd=root,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("unexpected execution", result.stdout)
