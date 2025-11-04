"""Simple runner for the project that imports the package correctly.

Run this from the repository root with:

    python run.py

This avoids pitfalls when running `python src/main.py` directly.
"""
import sys
import os

# Ensure project root is on sys.path so we can import `src` as a package
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.main import main

if __name__ == "__main__":
    main()
