"""Integration tests using isolated Git repositories and no network access."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "bin" / "gitview"


class GitviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="gitview-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repository with spaces"
        self.repo.mkdir()
        self.git("init", "-b", "dev")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.com")
        self.write("original.txt", "original\n")
        self.write("deleted.txt", "delete me\n")
        self.git("add", ".")
        self.git("commit", "-m", "Initial files")
        self.git("checkout", "-b", "feature")

    def git(self, *args):
        return subprocess.check_output(
            ["git", *args], cwd=self.repo, stderr=subprocess.DEVNULL
        )

    def write(self, name, contents):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)

    def run_tool(self, *args, cwd=None, env=None):
        return subprocess.run(
            [sys.executable, str(TOOL), *args], cwd=cwd or self.repo,
            env=env, capture_output=True,
        )

    def add_changes(self):
        self.write("committed.txt", "committed\n")
        self.git("add", ".")
        self.git("commit", "-m", "Add committed change")
        self.write("original.txt", "modified\n")
        self.write("staged.txt", "staged\n")
        self.git("add", "staged.txt")
        self.write("untracked.txt", "not included\n")
        (self.repo / "deleted.txt").unlink()

    def test_lists_committed_staged_and_unstaged_changes(self):
        self.add_changes()
        result = self.run_tool("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            set(result.stdout.decode().splitlines()),
            {"committed.txt", "original.txt", "staged.txt"},
        )

    def test_merge_base_does_not_include_target_only_changes(self):
        self.git("checkout", "dev")
        self.write("dev-only.txt", "not a feature change\n")
        self.git("add", ".")
        self.git("commit", "-m", "Advance dev")
        self.git("checkout", "feature")
        self.assertEqual(self.run_tool("--list").stdout, b"")

    def test_exclude_regex(self):
        self.add_changes()
        result = self.run_tool("dev", "--list", "--exclude", "committed|staged")
        self.assertEqual(result.stdout, b"original.txt\n")

    def test_runs_from_subdirectory(self):
        self.add_changes()
        nested = self.repo / "nested"
        nested.mkdir()
        result = self.run_tool("--list", cwd=nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"committed.txt", result.stdout)

    def test_null_output_handles_unusual_paths(self):
        names = ["space name.txt", "line\nbreak.txt", "quote'file.txt", "unicode-\u00e9.txt"]
        for name in names:
            self.write(name, "contents\n")
        self.git("add", ".")
        result = self.run_tool("--list", "--null")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.split(b"\0")[:-1]), {os.fsencode(n) for n in names})

    def test_missing_branch_and_non_repository(self):
        self.assertNotEqual(self.run_tool("missing-branch", "--list").returncode, 0)
        self.assertNotEqual(self.run_tool("--list", cwd=self.root).returncode, 0)

    def test_invalid_arguments(self):
        for arguments in [("--width", "0"), ("--width", "81"), ("--width", "abc"),
                          ("--exclude", "["), ("--null",)]:
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_tool(*arguments).returncode, 2)

    def test_no_changes_does_not_require_vim(self):
        result = self.run_tool("--vim", "nonexistent-editor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"No matching tracked changes", result.stdout)

    def test_missing_editor(self):
        self.add_changes()
        result = self.run_tool("--vim", "nonexistent-editor")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"Vim executable not found", result.stderr)

    @unittest.skipUnless(shutil.which("vim"), "Vim is not installed")
    def test_real_vim_sidebar_and_safe_filenames(self):
        names = ["space name.txt", "line\nbreak.txt", "quote'file.txt", "unicode-\u00e9.txt"]
        for name in names:
            self.write(name, "contents\n")
        self.git("add", ".")
        wrapper = self.root / "headless-vim"
        capture = self.root / "capture.json"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os, subprocess, sys\n"
            f"command = [{shutil.which('vim')!r}, '-Nu', 'NONE', '-i', 'NONE', '-n', '-es']\n"
            "command += sys.argv[1:]\n"
            "command += ['-c', 'call writefile([json_encode({"
            '\"items\": getqflist(), \"width\": winwidth(0), '
            '\"columns\": &columns, \"fixed\": &l:winfixwidth, '
            '\"equal\": &equalalways, \"base\": g:gitgutter_diff_base'
            "})], $GITVIEW_CAPTURE)', '-c', 'qa!']\n"
            "sys.exit(subprocess.call(command))\n"
        )
        wrapper.chmod(0o755)
        result = self.run_tool(
            "--vim", str(wrapper), "--width", "25",
            env=dict(os.environ, GITVIEW_CAPTURE=str(capture)),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(capture.read_text())
        self.assertEqual(data["width"], data["columns"] // 4)
        self.assertTrue(data["fixed"])
        self.assertFalse(data["equal"])
        self.assertEqual(data["base"], self.git("merge-base", "HEAD", "dev").decode().strip())
        self.assertEqual(len(data["items"]), len(names))
        self.assertTrue(all(item["valid"] for item in data["items"]))


if __name__ == "__main__":
    unittest.main()
