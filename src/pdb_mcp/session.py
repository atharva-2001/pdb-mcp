import os
import shutil
import sys

import pexpect


PDB_PROMPT = r"\(Pdb\)\s*$"
TIMEOUT = 10


class PdbSession:
    def __init__(self):
        self.child = None
        self.project_root = None
        self.file_path = None

    @property
    def alive(self):
        return self.child is not None and self.child.isalive()

    def start(self, file_path, args=None, python_path=None, use_pytest=False):
        if self.alive:
            raise RuntimeError("Session already running. Call end() first.")

        abs_file = os.path.abspath(file_path)
        if not os.path.exists(abs_file):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.file_path = abs_file
        self.project_root = self._find_project_root(os.path.dirname(abs_file))

        python = python_path or self._find_python()

        if use_pytest:
            cmd_parts = [python, "-m", "pytest", "--pdb", "-s", "--pdbcls=pdb:Pdb", abs_file]
        else:
            cmd_parts = [python, "-m", "pdb", abs_file]

        if args:
            cmd_parts.extend(args)

        cmd = " ".join(cmd_parts)

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        # Ensure the project root is on PYTHONPATH so imports work
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = self.project_root + (os.pathsep + existing if existing else "")

        self.child = pexpect.spawn(
            cmd,
            cwd=self.project_root,
            env=env,
            encoding="utf-8",
            timeout=TIMEOUT,
        )

        # Wait for initial pdb prompt
        try:
            self.child.expect(PDB_PROMPT, timeout=15)
        except pexpect.TIMEOUT:
            output = self.child.before or ""
            self.end()
            raise RuntimeError(f"pdb did not produce a prompt within 15s. Output:\n{output}")
        except pexpect.EOF:
            output = self.child.before or ""
            self.child = None
            raise RuntimeError(f"Process exited immediately. Output:\n{output}")

        return self.child.before or ""

    def send(self, command):
        if not self.alive:
            raise RuntimeError("No active session.")

        self.child.sendline(command)

        try:
            self.child.expect(PDB_PROMPT, timeout=TIMEOUT)
        except pexpect.TIMEOUT:
            return (self.child.before or "") + "\n[timeout waiting for (Pdb) prompt]"
        except pexpect.EOF:
            output = self.child.before or ""
            self.child = None
            return output + "\n[session ended]"

        return self.child.before or ""

    def end(self):
        if self.child is not None:
            if self.child.isalive():
                try:
                    self.child.sendline("q")
                    self.child.expect(pexpect.EOF, timeout=3)
                except Exception:
                    self.child.terminate(force=True)
            self.child = None
            self.project_root = None
            self.file_path = None

    def _find_python(self):
        """Find the user's Python — check project venv first, then PATH."""
        if self.project_root:
            for venv_name in [".venv", "venv", "env"]:
                candidate = os.path.join(self.project_root, venv_name, "bin", "python")
                if os.path.exists(candidate):
                    return candidate

        # Fall back to whatever python3 is on PATH
        p = shutil.which("python3") or shutil.which("python")
        if p:
            return p

        raise RuntimeError("Could not find a Python interpreter")

    def _find_project_root(self, start):
        current = start
        indicators = ["pyproject.toml", ".git", "setup.py", "requirements.txt"]
        while current != os.path.dirname(current):
            for ind in indicators:
                if os.path.exists(os.path.join(current, ind)):
                    return current
            current = os.path.dirname(current)
        return start
