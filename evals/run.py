"""Run the red-team failure-mode suite — the governed-agency receipts + CI.

    python -m evals.run          # from the repo root

Thin wrapper over pytest so the README's `python -m evals.run` works and the suite
has one obvious entry point.
"""
import sys

import pytest


def main() -> int:
    return pytest.main(["-q", "evals"])


if __name__ == "__main__":
    sys.exit(main())
