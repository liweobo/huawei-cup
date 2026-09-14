"""Run the tiny-fixture portable runtime regression without any model calls."""

from pathlib import Path
import sys

import pytest


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    sys.exit(pytest.main([str(root / "development/tests/test_portable_runtime.py"), "-q", "-p", "no:cacheprovider"]))
