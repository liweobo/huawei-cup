"""Run single-root distribution and cache-exclusion regression."""

from pathlib import Path
import sys

import pytest


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    sys.exit(pytest.main([str(root / "development/tests/test_repository_packaging.py"), "-q", "-p", "no:cacheprovider"]))
