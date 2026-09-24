#!/usr/bin/env python3
"""Idealized NTP-vs-chemical comparison; standard-library only.

This is a transparent rocket-equation calculation, not a vehicle design or
thermal/chemical energy model.  It writes a Δv sweep to data/ideal_comparison.csv.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

G0_M_S2 = 9.80665
CHEMICAL_ISP_S = 452.0  # NASA-reported SSME vacuum Isp; an illustrative reference
NTP_ISP_S = 900.0       # NASA-studied NTP target/reference, not this model's data


def propellant_per_dry_mass(delta_v_m_s: float, isp_s: float) -> float:
    """Return ideal propellant mass / final dry mass for one impulsive burn."""
    c = isp_s * G0_M_S2
    return math.expm1(delta_v_m_s / c)


def compare(delta_v_km_s: float) -> dict[str, float]:
    dv = delta_v_km_s * 1000.0
    c_chem = CHEMICAL_ISP_S * G0_M_S2
    c_ntp = NTP_ISP_S * G0_M_S2
    p_chem = propellant_per_dry_mass(dv, CHEMICAL_ISP_S)
    p_ntp = propellant_per_dry_mass(dv, NTP_ISP_S)
    prop_ratio = p_ntp / p_chem

    # For an ideal constant-velocity rocket with no external work, the increase
    # in total kinetic energy of vehicle + exhaust is 1/2 * c^2 * expelled mass.
    # This is jet/vehicle kinetic-energy output, not reactor or chemical input.
    energy_ratio = (c_ntp * c_ntp * p_ntp) / (c_chem * c_chem * p_chem)

    # With equal final dry mass, wet mass is dry_mass * exp(Δv/c).
    wet_mass_ratio = math.exp(dv / c_ntp - dv / c_chem)

    # Sensitivity example: NTP final dry mass is 25% heavier than chemical.
    dry_mass_penalty = 1.25
    prop_ratio_heavier_ntp = dry_mass_penalty * prop_ratio
    wet_ratio_heavier_ntp = dry_mass_penalty * wet_mass_ratio
    energy_ratio_heavier_ntp = dry_mass_penalty * energy_ratio

    return {
        "delta_v_km_s": delta_v_km_s,
        "chemical_isp_s": CHEMICAL_ISP_S,
        "ntp_isp_s": NTP_ISP_S,
        "chemical_exhaust_speed_m_s": c_chem,
        "ntp_exhaust_speed_m_s": c_ntp,
        "chemical_propellant_per_dry_mass": p_chem,
        "ntp_propellant_per_dry_mass": p_ntp,
        "ntp_to_chemical_propellant_ratio_equal_dry_mass": prop_ratio,
        "propellant_reduction_pct_equal_dry_mass": 100.0 * (1.0 - prop_ratio),
        "wet_mass_ratio_equal_dry_mass": wet_mass_ratio,
        "wet_mass_reduction_pct_equal_dry_mass": 100.0 * (1.0 - wet_mass_ratio),
        "ideal_kinetic_energy_ratio_equal_dry_mass": energy_ratio,
        "ideal_kinetic_energy_change_pct_equal_dry_mass": 100.0 * (energy_ratio - 1.0),
        "ntp_to_chemical_propellant_ratio_ntp_dry_mass_plus_25pct": prop_ratio_heavier_ntp,
        "ntp_to_chemical_wet_mass_ratio_ntp_dry_mass_plus_25pct": wet_ratio_heavier_ntp,
        "ideal_kinetic_energy_ratio_ntp_dry_mass_plus_25pct": energy_ratio_heavier_ntp,
    }


def write_svg(rows: list[dict[str, float]], output: Path) -> None:
    """Write a small dependency-free chart of the three ideal ratios."""
    width, height = 1000, 620
    left, right, top, bottom = 100, 40, 92, 88
    plot_w, plot_h = width - left - right, height - top - bottom
    x_max, y_max = 20.0, 2.2

    def xy(x: float, y: float) -> tuple[float, float]:
        return left + x / x_max * plot_w, top + (y_max - y) / y_max * plot_h

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#07131f"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#dbe8ee}.small{font-size:14px}.axis{stroke:#77909e;stroke-width:1}.grid{stroke:#233746;stroke-width:1}.legend{font-size:16px}</style>',
        '<text x="100" y="42" font-size="25" font-weight="bold">Higher Isp reduces propellant mass; it does not prove lower energy use</text>',
        '<text x="100" y="68" class="small">Ideal 452 s chemical vs 900 s NTP reference · equal final dry mass · Δv sweep · no trajectory or hardware losses</text>',
    ]
    for y in (0, 0.5, 1.0, 1.5, 2.0):
        px, py = xy(0, y)
        svg.append(f'<line x1="{left}" y1="{py:.1f}" x2="{width-right}" y2="{py:.1f}" class="grid"/>')
        svg.append(f'<text x="{left-14}" y="{py+5:.1f}" text-anchor="end" class="small">{y:.1f}</text>')
    for x in (0, 5, 10, 15, 20):
        px, py = xy(x, 0)
        svg.append(f'<line x1="{px:.1f}" y1="{top}" x2="{px:.1f}" y2="{height-bottom}" class="grid"/>')
        svg.append(f'<text x="{px:.1f}" y="{height-bottom+24}" text-anchor="middle" class="small">{x}</text>')
    _, y1 = xy(0, 1.0)
    _, y05 = xy(0, 0.5)
    svg.append(f'<line x1="{left}" y1="{y1:.1f}" x2="{width-right}" y2="{y1:.1f}" stroke="#8ca4af" stroke-dasharray="7 6"/>')
    svg.append(f'<line x1="{left}" y1="{y05:.1f}" x2="{width-right}" y2="{y05:.1f}" stroke="#8ca4af" stroke-dasharray="3 7"/>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>')
    svg.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>')

    series = [
        ("NTP / chemical propellant mass", "#ff9d3d", "ntp_to_chemical_propellant_ratio_equal_dry_mass"),
        ("NTP / chemical wet mass", "#4ed0e8", "wet_mass_ratio_equal_dry_mass"),
        ("NTP / chemical ideal kinetic energy", "#f36d9b", "ideal_kinetic_energy_ratio_equal_dry_mass"),
    ]
    x0, y0 = xy(0, 0)
    for label, color, key in series:
        initial = {
            "ntp_to_chemical_propellant_ratio_equal_dry_mass": NTP_ISP_S / CHEMICAL_ISP_S,
            "wet_mass_ratio_equal_dry_mass": 1.0,
            "ideal_kinetic_energy_ratio_equal_dry_mass": NTP_ISP_S / CHEMICAL_ISP_S,
        }[key]
        points = [xy(0.0, initial)] + [xy(row["delta_v_km_s"], row[key]) for row in rows]
        point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        svg.append(f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="3"/>')

    legend_y = height - 33
    for index, (label, color, _) in enumerate(series):
        x = left + index * 290
        svg.append(f'<line x1="{x}" y1="{legend_y-5}" x2="{x+28}" y2="{legend_y-5}" stroke="{color}" stroke-width="4"/>')
        svg.append(f'<text x="{x+36}" y="{legend_y}" class="legend">{label}</text>')
    svg.append(f'<text x="{left + plot_w/2:.1f}" y="{height-2}" text-anchor="middle" class="small">Required ideal Δv (km/s)</text>')
    svg.append(f'<text x="26" y="{top + plot_h/2:.1f}" text-anchor="middle" transform="rotate(-90 26 {top + plot_h/2:.1f})" class="small">Ratio (NTP / chemical)</text>')
    svg.append('</svg>')
    output.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "data" / "ideal_comparison.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [compare(step / 2.0) for step in range(1, 41)]  # 0.5–20.0 km/s
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    svg_output = Path(__file__).resolve().parent / "ideal_comparison.svg"
    write_svg(rows, svg_output)

    print(f"Wrote {len(rows)} rows to {output}")
    print(f"Wrote chart to {svg_output}")
    print("Δv   propellant reduction   wet-mass reduction   ideal KE change")
    for dv in (2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 18.0):
        row = compare(dv)
        print(
            f"{dv:>4.1f} km/s  "
            f"{row['propellant_reduction_pct_equal_dry_mass']:>7.2f}%  "
            f"{row['wet_mass_reduction_pct_equal_dry_mass']:>7.2f}%  "
            f"{row['ideal_kinetic_energy_change_pct_equal_dry_mass']:>+8.2f}%"
        )

    # Numerical crossover for 50% lower ideal kinetic-energy output.
    # Find the first Δv where the 0.01 km/s sweep reaches the target.
    crossover_50 = None
    for step in range(1, 10001):
        dv = step / 100.0
        if compare(dv)["ideal_kinetic_energy_ratio_equal_dry_mass"] <= 0.5:
            crossover_50 = dv
            break
    print(f"First 0.01-km/s-grid point at <=50% ideal KE: {crossover_50} km/s")


if __name__ == "__main__":
    main()
