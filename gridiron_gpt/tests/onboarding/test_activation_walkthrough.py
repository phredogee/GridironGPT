import os
import sys
from pathlib import Path

import pytest


def test_virtualenv_active():
    """Check if the virtual environment is active."""
    venv = os.environ.get("VIRTUAL_ENV")
    assert venv is not None, "❌ Virtual environment not active"
    print(f"✅ Virtual environment detected: {venv}")


def test_python_path_consistency():
    """Ensure pytest is running inside the active virtual environment."""
    python_path = Path(sys.executable)

    assert python_path.name.startswith("python"), (
        f"Unexpected interpreter name: {python_path.name}"
    )

    virtual_env = os.environ.get("VIRTUAL_ENV")
    assert virtual_env is not None, "Virtual environment is not active"

    assert Path(virtual_env) in python_path.parents, (
        f"Interpreter is not inside the active virtual environment: "
        f"{python_path}"
    )


@pytest.mark.skipif(
    os.environ.get("SHELL", "").endswith("xonsh"),
    reason="Xonsh shell detected",
)
def test_shell_specific_behavior():
    """Skip this test if running in Xonsh."""
    print("✅ Non-Xonsh shell detected, running shell-specific test")


def test_xonsh_activation_hint():
    """Provide guidance if Xonsh shell is detected."""
    shell = os.environ.get("SHELL", "")

    if shell.endswith("xonsh"):
        print(
            "⚠️ Xonsh shell detected — ensure you run "
            "`source activate.xsh` or use `xontrib` if needed"
        )
    else:
        print("✅ Shell is not Xonsh — standard activation applies")
