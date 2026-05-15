# Buckles Plot for Irreducible Water Saturation in Python

*Using porosity-water saturation crossplots to identify producible hydrocarbons*

---

A formation can have significant porosity and still produce only water. The reason is irreducible water saturation — the water that clings to grain surfaces and cannot be displaced by hydrocarbons no matter how much pressure you apply. Knowing whether a formation is at irreducible saturation is the difference between a producing well and a completion mistake.

The Buckles plot is a simple but powerful crossplot that identifies irreducible water saturation and distinguishes producible hydrocarbon zones from water-productive zones.

## The Bulk Volume Water Concept

Buckles (1965) observed that in many sandstone formations, the product of porosity and water saturation is approximately constant for samples at irreducible water saturation:

```
BVW = φ × Sw ≈ constant (at irreducible)
```

BVW is the Bulk Volume Water — the fraction of the total rock volume occupied by water. For a formation at irreducible saturation, BVW is constant regardless of porosity: tighter rocks have higher Sw but lower porosity, and the product stays the same.

On a crossplot of porosity (x-axis) vs water saturation (y-axis), constant BVW defines a hyperbola: `Sw = BVW / φ`. A cluster of data points lying along one of these hyperbolas indicates the formation is at irreducible saturation and will produce water-free hydrocarbons. Points scattered above multiple hyperbolas are in a transition zone and will produce water.

## Implementation

```python
import numpy as np
import matplotlib.pyplot as plt

def buckles_isoline(sw_range, bvw):
    """Porosity along a constant BVW hyperbola."""
    phi = bvw / np.maximum(sw_range, 0.001)
    return np.clip(phi, 0.0, 0.40)

# Draw BVW isolines
sw_range = np.linspace(0.05, 1.0, 300)
bvw_values = [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20]

fig, ax = plt.subplots(figsize=(8, 8))
for bvw in bvw_values:
    phi_line = buckles_isoline(sw_range, bvw)
    mask = phi_line < 0.38
    ax.plot(phi_line[mask], sw_range[mask], 'k-', linewidth=0.8, alpha=0.5)
    # Label at top of each line
    idx = np.argmax(phi_line[mask])
    ax.text(phi_line[mask][idx] + 0.002, sw_range[mask][idx],
            f"BVW={bvw:.2f}", fontsize=7)

ax.set_xlabel("Porosity (fraction)")
ax.set_ylabel("Water Saturation (fraction)")
ax.set_xlim(0, 0.35)
ax.set_ylim(0, 1.0)
ax.set_title("Buckles Plot — Bulk Volume Water Isolines")
```

## Generating Synthetic Well Log Data

In a real analysis, the data points come from petrophysical log analysis — porosity from the density or neutron log, Sw from the Archie equation applied to the resistivity log:

```python
np.random.seed(42)

# Zone 1: Pay sand at irreducible Sw — points cluster on BVW=0.04 hyperbola
n_pay = 120
phi_pay = np.random.uniform(0.10, 0.22, n_pay)
sw_pay = 0.04 / phi_pay + np.random.normal(0, 0.03, n_pay)
sw_pay = np.clip(sw_pay, 0.05, 0.60)

# Zone 2: Transition zone — scattered across multiple BVW lines
n_trans = 80
phi_trans = np.random.uniform(0.06, 0.16, n_trans)
sw_trans = np.random.uniform(0.45, 0.80, n_trans)

# Zone 3: Water-bearing sand — high BVW, Sw near 1.0
n_water = 80
phi_water = np.random.uniform(0.06, 0.22, n_water)
sw_water = np.random.uniform(0.80, 1.00, n_water)

# Plot
ax.scatter(phi_pay, sw_pay, s=15, c='black', label='Pay zone', zorder=5)
ax.scatter(phi_trans, sw_trans, s=15, c='gray', marker='s', label='Transition', zorder=5)
ax.scatter(phi_water, sw_water, s=15, c='lightgray', marker='^', label='Water zone', zorder=5)
ax.legend(loc='upper right')
```

## Reading the Buckles Plot

**Pay zone at irreducible Sw:** data points cluster tightly along a single BVW hyperbola (e.g., BVW = 0.04). All points have approximately the same porosity × saturation product. This formation will produce water-free — the water is immobile because it is already at irreducible saturation.

**Transition zone:** data points scatter between hyperbolas. Some have BVW of 0.06, others 0.10. The saturation is above irreducible and varies with position relative to the free-water level. This zone will produce both hydrocarbons and water, with increasing water cut as you approach the free-water level.

**Water zone:** data points cluster at high saturation (0.8–1.0) with high BVW. The rock is essentially fully water-saturated.

## The Irreducible BVW Value

The BVW at irreducible saturation varies by rock type:
- Clean, high-permeability sands: BVW ≈ 0.02–0.04
- Moderate-quality sands: BVW ≈ 0.04–0.07
- Shaly or tight sands: BVW ≈ 0.07–0.15

Tighter formations hold more irreducible water per unit of pore volume. A formation with 10% porosity at irreducible Sw = 0.40 has the same BVW as a formation with 20% porosity at Sw = 0.20 — both would produce water-free.

## Relationship to Capillary Pressure

The BVW constant is not truly constant — it varies with the height above the free-water level (controlled by capillary pressure). Near the free-water level, BVW is higher (transition zone). High in the structure, far from the free-water level, BVW is lower and approaches the irreducible minimum.

The Buckles plot implicitly shows this: if you color-code data points by depth, you should see BVW decreasing systematically with height above the free-water level.

## Key Takeaways

The Buckles plot answers a different question than the Pickett plot. Pickett tells you the water saturation; Buckles tells you whether that saturation is mobile or trapped. A formation with Sw = 0.35 that clusters tightly on BVW = 0.04 will produce water-free at that saturation. A formation with Sw = 0.35 that scatters across multiple BVW lines will produce water — even though the saturation number looks the same.

Use the two plots together, not as alternatives. The Pickett plot gives you Sw; the Buckles plot tells you what that Sw means for completion decisions. If the data clusters on one hyperbola, complete the interval with confidence. If it scatters, investigate whether you are looking at a genuine transition zone or a heterogeneous interval that could be targeted selectively.
