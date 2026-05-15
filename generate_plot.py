#!/usr/bin/env python3
"""
Generate visualization for Buckles Plot blog post.
Creates a porosity vs water saturation crossplot with BVW isolines.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


from pathlib import Path


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent / 'config.yaml'
    if not config_path.exists():
        return {}
    with open(config_path) as _f:
        import yaml as _yaml
        return _yaml.safe_load(_f) or {}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Set publication-quality defaults

logger.info("Generating Buckles plot...")
logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def buckles_isoline(sw_range, bvw):
    """Calculate porosity for constant BVW isoline."""
    sw_safe = np.maximum(sw_range, 0.001)
    phi = bvw / sw_safe
    return np.clip(phi, 0, 0.4)

# Generate synthetic well log data with realistic patterns
np.random.seed(42)
n_samples = 300

# Create three zones with different characteristics
# Zone 1: Good pay (low BVW, Sw ~ 0.2-0.4, phi ~ 0.08-0.18)
n1 = 120
phi_pay = np.random.uniform(0.08, 0.18, n1)
sw_pay = np.random.uniform(0.20, 0.40, n1)
# Add some scatter
sw_pay += np.random.normal(0, 0.05, n1)
phi_pay += np.random.normal(0, 0.02, n1)

# Zone 2: Transition zone (moderate BVW, Sw ~ 0.4-0.7, phi ~ 0.06-0.15)
n2 = 100
phi_trans = np.random.uniform(0.06, 0.15, n2)
sw_trans = np.random.uniform(0.40, 0.70, n2)
sw_trans += np.random.normal(0, 0.06, n2)
phi_trans += np.random.normal(0, 0.02, n2)

# Zone 3: Water zone (high BVW, Sw ~ 0.7-1.0, phi ~ 0.05-0.20)
n3 = 80
phi_water = np.random.uniform(0.05, 0.20, n3)
sw_water = np.random.uniform(0.70, 1.0, n3)
sw_water += np.random.normal(0, 0.05, n3)
phi_water += np.random.normal(0, 0.02, n3)

# Combine all zones
phi_all = np.concatenate([phi_pay, phi_trans, phi_water])
sw_all = np.concatenate([sw_pay, sw_trans, sw_water])

# Clip to physical ranges
sw_all = np.clip(sw_all, 0.0, 1.0)
phi_all = np.clip(phi_all, 0.01, 0.35)

# Create figure
fig, ax = plt.subplots(figsize=tuple(config.get('output', {}).get('figsize', [8, 8])))

# Plot isolines
sw_range = np.linspace(0.01, 1.0, 200)
bvw_lines = [0.02, 0.04, 0.06, 0.08, 0.10]
bvw_cutoff = 0.04

for bvw in bvw_lines:
    phi_line = buckles_isoline(sw_range, bvw)
    
    if bvw == bvw_cutoff:
        linestyle = '-'
        linewidth = 1.2
        alpha = 1.0
        label = f'BVW = {bvw:.3f} (cutoff)'
    elif bvw < bvw_cutoff:
        linestyle = ':'
        linewidth = 0.9
        alpha = 0.7
        label = f'BVW = {bvw:.3f}'
    else:
        linestyle = '--'
        linewidth = 0.9
        alpha = 0.7
        label = f'BVW = {bvw:.3f}'
    
    ax.plot(
        sw_range,
        phi_line,
        color='black',
        linestyle=linestyle,
        linewidth=linewidth,
        alpha=alpha,
        label=label
    )

# Plot data points
ax.scatter(
    sw_all,
    phi_all,
    color='gray',
    s=12,
    alpha=0.5,
    edgecolors='none',
    label='Log data'
)

# Set linear scales
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 0.35)

# Labels
ax.set_xlabel('Water Saturation, Sw (fraction)', fontsize=11)
ax.set_ylabel('Porosity, φ (fraction)', fontsize=11)
ax.set_title('Buckles Plot', fontsize=12)

# Legend
ax.legend(loc='upper right', frameon=False, fontsize=9)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Light grid
ax.grid(True, linestyle=':', linewidth=0.3, alpha=0.5)

plt.tight_layout()
plt.savefig('buckles_plot.png', dpi=300, bbox_inches='tight')
plt.close()

logger.info("Generated: buckles_plot.png")
logger.info("Plot uses synthetic data for demonstration.\n")


