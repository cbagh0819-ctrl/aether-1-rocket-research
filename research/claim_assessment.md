# Claim assessment: “50% less energy”

## Verdict

**Not proven.** The Blender scene has no physical simulation or measured performance. A higher specific impulse can reduce propellant mass for a fixed ideal Δv, but specific impulse is not a measurement of total source energy consumed. The idealized calculation here predicts *more* total kinetic-energy output for the 4 km/s example even while using less propellant.

## Define the quantities

- **Propellant mass** is the reaction/working mass expelled by the rocket. In the NTP reference case this is hydrogen; the reactor's nuclear fuel is a separate mass and energy source.
- **Specific impulse** is equivalent exhaust velocity divided by standard gravity: `Isp = c / g0`. It measures impulse per unit propellant weight. It does not by itself state how many joules of reactor heat or chemical energy are consumed.
- **Energy** here has two meanings that must not be conflated: (1) ideal kinetic-energy increase of the vehicle plus expelled exhaust, and (2) source energy drawn from chemical reactants or nuclear fuel. This report calculates only the first.
- **Baseline** means the explicit 452 s SSME vacuum-Isp reference and 900 s NTP reference. “Normal rocket” is otherwise undefined.

NASA gives the ideal rocket equation and identifies Isp as a propellant-performance quantity. NASA's NTP material describes 880–900 s as potential/reference performance. These are not test results for AETHER-1.

## Assumptions in the numerical example

1. One ideal burn with constant effective exhaust velocity.
2. Same required Δv and same final dry mass (payload plus all non-propellant mass) for both vehicles.
3. No gravity loss, aerodynamic drag, steering loss, finite-burn transient, boil-off, residual propellant, or staging difference.
4. No engine, reactor, shielding, tank, radiator, or support-mass difference in the equal-dry-mass case.
5. Ideal kinetic-energy output is calculated with 100% conversion and no heat or exhaust losses.

These assumptions isolate the equations. They are not a realistic full-mission comparison. Real NTP sizing must include thrust and transient behavior, engine mass, hydrogen storage volume, vehicle architecture, and mission constraints.

## What the model does establish

For final dry mass `D`, effective exhaust velocity `c = g0 Isp`, and required ideal Δv:

```text
Δv = c ln(m_initial / D)
m_prop = D (exp(Δv / c) - 1)
```

If the exhaust velocity is exactly doubled and `D` is held equal, the propellant ratio is:

```text
m_prop,2c / m_prop,c
  = (exp(Δv / (2c)) - 1) / (exp(Δv / c) - 1)
  = 1 / (exp(Δv / (2c)) + 1)
```

For any positive Δv this ideal mass ratio is below 0.5. That is a mathematical proof about **propellant mass under the listed assumptions**, not a proof about energy or a real vehicle. With 452 s versus 900 s the velocities are not exactly in a 2:1 ratio; the supplied program computes the exact values.

At 4 km/s using the repository's reference values:

| Quantity | 452 s chemical reference | 900 s NTP reference |
| --- | ---: | ---: |
| Effective exhaust velocity `c` | 4,432.61 m/s | 8,825.99 m/s |
| Ideal propellant per unit final dry mass | 1.466 | 0.574 |
| Ideal wet mass per unit final dry mass | 2.466 | 1.574 |

The NTP ideal propellant mass is 0.3912 of the reference (60.88% less). Its ideal wet mass is 0.6381 of the reference (36.19% less). If NTP dry mass is 25% higher, the propellant ratio rises to 0.4890 (51.10% less), while wet mass is 0.7976 of the reference (20.24% less). Such sensitivity is why equal dry mass cannot be silently assumed in a vehicle claim.

## Why “50% less energy” does not follow

For an ideal rocket beginning at rest, conservation of momentum gives `dV = c dμ / M`, where `dμ` is the expelled mass. The change in total kinetic energy of the remaining rocket plus the newly expelled mass is:

```text
dK = 1/2 c² dμ
```

Integrating over the burn gives ideal kinetic-energy output:

```text
K_out = 1/2 c² m_prop
      = 1/2 c² D (exp(Δv / c) - 1)
```

Consequently the ideal NTP-to-chemical kinetic-energy ratio is:

```text
K_NTP / K_chem
  = (c_NTP / c_chem)²
    × (exp(Δv / c_NTP) - 1) / (exp(Δv / c_chem) - 1)
```

At 4 km/s this ratio is 1.5511: about **55.11% more ideal kinetic-energy output**, not 50% less. With the chosen Isp pair, the ideal ratio falls below 1.0 near 9.72 km/s and below 0.5 near 17.27 km/s. Those are outputs of this exact simplified model, not source-energy forecasts.

Actual source energy requires efficiencies and losses. For NTP it would require a defensible reactor-to-propellant thermal balance, burn transients, heat rejection, residual/decay-heat treatment, and system masses. For chemical propulsion it requires a defined propellant pair, reaction enthalpy, nozzle efficiency, and operating point. The mission must also specify trajectory, burn durations, staging, tankage, and mass boundary. Isp alone cannot supply these data.

## Dry-mass sensitivity

Let `q = D_NTP / D_chem`. Then:

```text
propellant-mass ratio = q × (equal-dry-mass propellant ratio)
wet-mass ratio        = q × exp(Δv/c_NTP - Δv/c_chem)
ideal-energy ratio    = q × (equal-dry-mass ideal-energy ratio)
```

At 4 km/s, the NTP dry mass can be up to about 1.279 times the chemical dry mass and still use at least 50% less propellant in this idealized comparison. That threshold says nothing about source energy. The NTP energy-output ratio would increase in direct proportion to `q`.

## Bottom line

The defensible theory is: **a roughly 2×-Isp NTP stage can use about half or less propellant mass for some fixed-Δv comparisons, before vehicle-mass and mission effects are applied.** The stronger statement **“AETHER-1 uses 50% less energy than a normal rocket” is not established and is false for the 4 km/s ideal kinetic-energy example.**
