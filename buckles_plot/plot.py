"""
Buckles plot: porosity vs water saturation with BVW isolines.

Data sources:
  - rottweiler: KGS PfEFFER Rottweiler Sandstone zones A–J (real teaching well)
  - aapg:       capillary-pressure / Buckles crossplot example (12 points)
  - synthetic:  random demo points (article.md)
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# AAPG Figure 10 style: porosity and Sw in percent; BVW = φ(%) × Sw(%)
AAPG_POINTS: list[tuple[int, float, float, float]] = [
    (1, 19, 21, 399),
    (2, 18, 22, 396),
    (3, 16, 26, 416),
    (4, 14, 30, 420),
    (5, 12, 34, 408),
    (6, 10, 39, 390),
    (7, 16, 52, 832),
    (8, 12, 65, 780),
    (9, 15, 75, 1125),
    (10, 16, 85, 1360),
    (11, 13, 92, 1196),
    (12, 14, 97, 1358),
]

AAPG_BVW_ISOLINES = [100, 500, 1000, 1500]
AAPG_CRITICAL_SW_PCT = 45

# KGS PfEFFER: irreducible trend Buckles number ≈ 0.05 (zones A–E)
ROTTWEILER_BVW_ISOLINES = [0.02, 0.04, 0.05, 0.06, 0.08, 0.10, 0.15]
ROTTWEILER_BVW_HIGHLIGHT = 0.05

ZONE_COLORS = {
    "pay": "#2c6e49",
    "transition": "#bc6c25",
    "water": "#386fa4",
}


@dataclass(frozen=True)
class BucklesDataset:
    phi: np.ndarray
    sw: np.ndarray
    labels: np.ndarray | None = None
    units: str = "fraction"
    zone_types: np.ndarray | None = None


def load_config(config_path: Path | None = None) -> dict:
    if config_path is None:
        config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        import yaml

        return yaml.safe_load(f) or {}


def buckles_isoline(sw: np.ndarray, bvw: float, *, percent: bool = False) -> np.ndarray:
    """Porosity along a constant-BVW curve. φ = BVW / Sw (same units as input)."""
    sw_safe = np.maximum(sw, 0.001 if percent else 1e-4)
    phi = bvw / sw_safe
    return np.clip(phi, 0.0, 50.0 if percent else 0.40)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        lines = [row for row in f if not row.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def rottweiler_dataset(csv_path: Path | None = None) -> BucklesDataset:
    """
    KGS PfEFFER Rottweiler Sandstone (zones A–J).

    https://www.kgs.ku.edu/software/PfEFFER-java/HELP/PfEFFER/Pfeffer-theory2.html
    https://www.kgs.ku.edu/software/PfEFFER-java/HELP/PfEFFER/Pfeffer-theory4.html
    """
    csv_path = csv_path or PROJECT_ROOT / "data" / "rottweiler_sandstone.csv"
    rows = _read_csv_rows(csv_path)
    phi = np.array([float(r["porosity_pct"]) / 100.0 for r in rows])
    sw = np.array([float(r["sw"]) for r in rows])
    labels = np.array([r["zone"] for r in rows])
    zone_types = np.array([r["zone_type"] for r in rows])
    return BucklesDataset(phi=phi, sw=sw, labels=labels, zone_types=zone_types, units="fraction")


def aapg_dataset() -> BucklesDataset:
    labels, phi, sw, _bvw = zip(*AAPG_POINTS, strict=True)
    return BucklesDataset(
        phi=np.asarray(phi, dtype=float),
        sw=np.asarray(sw, dtype=float),
        labels=np.asarray(labels, dtype=int),
        units="percent",
    )


def synthetic_dataset(seed: int = 42) -> BucklesDataset:
    rng = np.random.default_rng(seed)
    n_pay = 120
    phi_pay = rng.uniform(0.10, 0.22, n_pay)
    sw_pay = np.clip(0.04 / phi_pay + rng.normal(0, 0.03, n_pay), 0.05, 0.60)
    phi_trans = rng.uniform(0.06, 0.16, 80)
    sw_trans = rng.uniform(0.45, 0.80, 80)
    phi_water = rng.uniform(0.06, 0.22, 80)
    sw_water = rng.uniform(0.80, 1.00, 80)
    return BucklesDataset(
        phi=np.concatenate([phi_pay, phi_trans, phi_water]),
        sw=np.concatenate([sw_pay, sw_trans, sw_water]),
        units="fraction",
    )


def _plot_bvw_isolines_fraction(
    ax: plt.Axes,
    bvw_values: list[float],
    *,
    highlight: float | None = None,
    sw_range: np.ndarray | None = None,
) -> None:
    sw_range = sw_range if sw_range is not None else np.linspace(0.05, 1.0, 300)
    for bvw in bvw_values:
        phi_line = buckles_isoline(sw_range, bvw, percent=False)
        mask = phi_line <= 0.38
        is_highlight = highlight is not None and abs(bvw - highlight) < 1e-9
        ax.plot(
            sw_range[mask],
            phi_line[mask],
            color="black",
            linewidth=1.2 if is_highlight else 0.8,
            linestyle="-" if is_highlight else ":",
            alpha=1.0 if is_highlight else 0.55,
        )
        idx = len(sw_range[mask]) // 2
        label = f"BVW={bvw:.2f}" + (" (Buckles #)" if is_highlight else "")
        ax.text(sw_range[mask][idx], phi_line[mask][idx], label, fontsize=7)


def plot_buckles_fraction(ax: plt.Axes, data: BucklesDataset) -> None:
    """Article layout: Sw on x, porosity on y (fractions)."""
    _plot_bvw_isolines_fraction(ax, [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20])
    ax.scatter(data.sw, data.phi, s=12, c="0.45", alpha=0.5, edgecolors="none", label="Log data", zorder=5)
    ax.set_xlabel("Water Saturation, Sw (fraction)")
    ax.set_ylabel("Porosity, φ (fraction)")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 0.35)
    ax.legend(loc="upper right")


def plot_buckles_rottweiler(ax: plt.Axes, data: BucklesDataset) -> None:
    """KGS PfEFFER Figure 11 style (Sw–porosity, fraction scales)."""
    _plot_bvw_isolines_fraction(ax, ROTTWEILER_BVW_ISOLINES, highlight=ROTTWEILER_BVW_HIGHLIGHT)

    assert data.zone_types is not None and data.labels is not None
    for ztype in ("pay", "transition", "water"):
        mask = data.zone_types == ztype
        ax.scatter(
            data.sw[mask],
            data.phi[mask],
            s=70,
            c=ZONE_COLORS[ztype],
            label=ztype.replace("_", " ").title(),
            zorder=5,
            edgecolors="white",
            linewidths=0.5,
        )

    for label, phi, sw in zip(data.labels, data.phi, data.sw, strict=True):
        ax.annotate(str(label), (sw, phi), xytext=(4, 4), textcoords="offset points", fontsize=10, fontweight="bold")

    ax.set_xlabel("Water Saturation, Sw (fraction)")
    ax.set_ylabel("Porosity, φ (fraction)")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 0.30)
    ax.legend(loc="upper right", fontsize=8)


def plot_buckles_aapg(ax: plt.Axes, data: BucklesDataset) -> None:
    """AAPG layout: Sw on x, porosity on y (percent)."""
    sw_range = np.linspace(1.0, 100.0, 300)
    for bvw in AAPG_BVW_ISOLINES:
        phi_line = buckles_isoline(sw_range, bvw, percent=True)
        mask = (phi_line > 0) & (phi_line <= 50)
        ax.plot(sw_range[mask], phi_line[mask], "k-", linewidth=0.8, alpha=0.5)
        idx = len(sw_range[mask]) // 2
        ax.text(sw_range[mask][idx], phi_line[mask][idx], str(bvw), fontsize=8)

    ax.axvline(AAPG_CRITICAL_SW_PCT, color="0.35", linestyle="--", linewidth=0.9, label="Critical Sw")
    ax.scatter(data.sw, data.phi, s=40, c="0.15", zorder=5)
    for label, phi, sw in zip(data.labels, data.phi, data.sw, strict=True):
        ax.annotate(str(label), (sw, phi), xytext=(3, 3), textcoords="offset points", fontsize=9)

    ax.set_xlabel("Water Saturation, Sw (%)")
    ax.set_ylabel("Porosity (%)")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.legend(loc="upper right", fontsize=8)


SOURCES: dict[str, tuple] = {
    "rottweiler": (
        rottweiler_dataset,
        plot_buckles_rottweiler,
        "KGS PfEFFER Rottweiler Sandstone (zones A–J, Buckles # ≈ 0.05 for pay).",
    ),
    "aapg": (
        aapg_dataset,
        plot_buckles_aapg,
        "AAPG capillary-pressure teaching example (12 points).",
    ),
    "synthetic": (
        synthetic_dataset,
        plot_buckles_fraction,
        "Synthetic log samples for demonstration.",
    ),
}


def main() -> Path:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    config = load_config()

    source = config.get("data", {}).get("source", "rottweiler")
    seed = config.get("data", {}).get("seed", 42)
    output_cfg = config.get("output", {})
    figsize = tuple(output_cfg.get("figsize", [8, 8]))
    dpi = output_cfg.get("figure_dpi", 300)
    figures_dir = Path(output_cfg.get("figures_dir", "."))
    if not figures_dir.is_absolute():
        figures_dir = PROJECT_ROOT / figures_dir
    figures_dir.mkdir(parents=True, exist_ok=True)
    ext = output_cfg.get("figure_format", "png")
    out_path = figures_dir / f"buckles_plot_{source}.{ext}"

    if source not in SOURCES:
        allowed = ", ".join(sorted(SOURCES))
        raise ValueError(f"Unknown data.source: {source!r} (use {allowed})")

    loader, plot_fn, note = SOURCES[source]
    data = loader(seed=seed) if source == "synthetic" else loader()

    logger.info("Generating Buckles plot (%s)...", source)
    logger.info("Timestamp: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    title = {
        "rottweiler": "Buckles Plot — Rottweiler Sandstone (KGS PfEFFER)",
        "aapg": "Buckles Plot — AAPG Example",
        "synthetic": "Buckles Plot",
    }[source]

    fig, ax = plt.subplots(figsize=figsize)
    plot_fn(ax, data)
    ax.set_title(title, fontsize=12)
    ax.grid(True, linestyle=":", linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    logger.info("Generated: %s", out_path)
    logger.info(note)
    return out_path
