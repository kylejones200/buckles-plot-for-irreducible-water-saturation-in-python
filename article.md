# Buckles Plot for Irreducible Water Saturation in Python

*Identifying producible hydrocarbons from a porosity-saturation crossplot*

---

A formation can have significant porosity and still produce only water. The reason is irreducible water saturation, the water that clings to grain surfaces and cannot be displaced by hydrocarbons regardless of pressure. Whether a formation is at irreducible saturation is the difference between a producing well and a completion mistake.

The Buckles plot identifies irreducible saturation and separates producible hydrocarbon zones from water-productive ones.

## Bulk Volume Water

Buckles (1965) observed that in many sandstone formations, the product of porosity and water saturation is approximately constant for samples at irreducible water saturation:

```
BVW = φ × Sw ≈ constant (at irreducible)
```

BVW is Bulk Volume Water, the fraction of total rock volume occupied by water. At irreducible saturation, BVW stays constant regardless of porosity. Tighter rocks have higher Sw but lower porosity; the product stays the same.

On a crossplot of porosity vs water saturation, constant BVW traces a hyperbola: `Sw = BVW / φ`. Points clustered along one hyperbola are at irreducible saturation and will produce water-free. Points scattered across multiple hyperbolas are in a transition zone and will produce water.

## Implementation

```python
import numpy as np
import matplotlib.pyplot as plt

def buckles_isoline(sw_range, bvw):
    phi = bvw / np.maximum(sw_range, 0.001)
    return np.clip(phi, 0.0, 0.40)

sw_range = np.linspace(0.05, 1.0, 300)
bvw_values = [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20]

fig, ax = plt.subplots(figsize=(8, 8))
for bvw in bvw_values:
    phi_line = buckles_isoline(sw_range, bvw)
    mask = phi_line < 0.38
    ax.plot(phi_line[mask], sw_range[mask], 'k-', linewidth=0.8, alpha=0.5)
    idx = len(phi_line[mask]) // 2
    ax.text(phi_line[mask][idx] + 0.002, sw_range[mask][idx],
            f"BVW={bvw:.2f}", fontsize=7)

ax.set_xlabel("Porosity (fraction)")
ax.set_ylabel("Water Saturation (fraction)")
ax.set_xlim(0, 0.35)
ax.set_ylim(0, 1.0)
```

## Populating the Plot

In a real analysis, data points come from petrophysical log analysis: porosity from the density or neutron log, Sw from the Archie equation applied to the resistivity log.

```python
np.random.seed(42)

# Pay sand at irreducible Sw — points cluster on BVW = 0.04
n_pay = 120
phi_pay = np.random.uniform(0.10, 0.22, n_pay)
sw_pay = np.clip(0.04 / phi_pay + np.random.normal(0, 0.03, n_pay), 0.05, 0.60)

# Transition zone — scattered across multiple BVW lines
phi_trans = np.random.uniform(0.06, 0.16, 80)
sw_trans = np.random.uniform(0.45, 0.80, 80)

# Water zone — high BVW, Sw near 1.0
phi_water = np.random.uniform(0.06, 0.22, 80)
sw_water = np.random.uniform(0.80, 1.00, 80)

ax.scatter(phi_pay, sw_pay, s=15, label='Pay zone', zorder=5)
ax.scatter(phi_trans, sw_trans, s=15, marker='s', label='Transition', zorder=5)
ax.scatter(phi_water, sw_water, s=15, marker='^', label='Water zone', zorder=5)
ax.legend(loc='upper right')
```

## Reading the Plot

**Pay zone:** points cluster tightly along one BVW hyperbola. All samples have approximately the same porosity × saturation product. The formation will produce water-free because the water is immobile at irreducible saturation.

**Transition zone:** points scatter across multiple hyperbolas. BVW varies from sample to sample. Saturation is above irreducible and rises as you approach the free-water level. Expect both hydrocarbons and water production, with increasing water cut at depth.

**Water zone:** points cluster at high saturation with high BVW. The rock is essentially fully water-saturated.

## Irreducible BVW by Rock Type

| Rock type | BVW at irreducible |
|---|---|
| Clean, high-permeability sand | 0.02-0.04 |
| Moderate-quality sand | 0.04-0.07 |
| Shaly or tight sand | 0.07-0.15 |

Tighter formations hold more irreducible water per unit of pore volume. A formation at 10% porosity and Sw = 0.40 has the same BVW as one at 20% porosity and Sw = 0.20. Both would produce water-free.

## Relationship to Capillary Pressure

BVW is not truly constant across the reservoir. It varies with height above the free-water level, controlled by capillary pressure. Near the free-water level, BVW is higher. High in the structure, BVW falls toward the irreducible minimum. If you sort data points by depth, BVW should decrease systematically with height above the contact.

---

The Buckles plot answers a different question than the Pickett plot. Pickett gives you the water saturation. Buckles tells you whether that saturation is mobile or trapped. A formation at Sw = 0.35 that tracks a single BVW hyperbola will produce water-free. The same Sw scattered across multiple hyperbolas will produce water, even though the number looks the same.

Use them together. Pickett gives you Sw; Buckles tells you what that Sw means at the wellbore. If the data clusters on one hyperbola, complete the interval with confidence. If it scatters, you are either looking at a genuine transition zone or a heterogeneous interval worth targeting selectively.
