"""Small plotting helpers; plotting is optional and never substitutes validation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt


def save_line_plot(
    x: Sequence[float], y: Sequence[float], path: str | Path, *, title: str = "", xlabel: str = "x", ylabel: str = "y"
) -> Path:
    """Save a simple line plot and return its resolved path."""
    if len(x) != len(y) or not x:
        raise ValueError("x and y must have the same non-zero length")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, marker="o")
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output.resolve()
