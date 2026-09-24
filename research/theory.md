# Theory note: propellant mass is not energy

## Research question and result

Can a rocket with about twice the effective exhaust velocity use at least 50% less propellant for the same ideal velocity change? **Yes, conditionally.** Does that prove the rocket consumes 50% less energy? **No.** Those are different quantities, and the ideal kinetic-energy calculation below is greater than the chemical reference for the 4 km/s example.

This is a mathematical comparison, not a measured AETHER-1 result. The Blender scene is a visual concept; it does not contain a working engine or a physical simulation.

## Definitions and boundary

- `c` is effective exhaust velocity in m/s.
- `Isp` is specific impulse in seconds, with `c = g0 Isp` and `g0 = 9.80665 m/s²`.
- `D` is final dry mass, excluding expelled propellant.
- `Δv` is the ideal rocket velocity change.
- `m_p` is expelled propellant mass.
- “Energy output” below means the change in kinetic energy of the vehicle plus all expelled exhaust, in an ideal inertial frame. It does **not** mean reactor heat, chemical reaction energy, electrical input, or total source energy.

For the worked illustration, the explicit references are 452 s vacuum Isp for the Space Shuttle Main Engine (chemical) and 900 s for a NASA-described nuclear thermal propulsion (NTP) reference/potential case. “Normal rocket” is not a defined baseline, so results should not be generalized beyond this pair.

## Propellant-mass derivation

The ideal rocket equation for constant effective exhaust velocity is:

```text
Δv = c ln(m0 / D)
```

where `m0 = D + m_p` is initial wet mass. Rearranging:

```text
m0 / D = exp(Δv / c)
m_p / D = exp(Δv / c) - 1
m_p = D [exp(Δv / c) - 1]
```

For two engines with the same `D` and maneuver but exactly doubled effective exhaust velocity, `c2 = 2c`:

```text
m_p,2 / m_p,1
  = [exp(Δv / (2c)) - 1] / [exp(Δv / c) - 1]
  = 1 / [exp(Δv / (2c)) + 1]
```

For any positive `Δv`, the denominator is greater than 2, so the ratio is strictly less than 0.5. This proves a conditional **propellant-mass** result. It assumes equal final dry mass and the ideal rocket equation; it does not account for vehicle design or prove lower source-energy use. When `Δv` is small relative to `c`, the ratio approaches 0.5 from below.

## Worked 4 km/s comparison

Using the selected reference Isp values:

```text
c_chem = 452 s × 9.80665 m/s² = 4,432.6058 m/s
c_NTP  = 900 s × 9.80665 m/s² = 8,825.9850 m/s
```

The NTP reference has 1.9893 times the effective exhaust velocity, close to but not exactly twice. For `Δv = 4,000 m/s` and equal `D`:

| Quantity per unit final dry mass | 452 s chemical reference | 900 s NTP reference |
| --- | ---: | ---: |
| Propellant `m_p / D` | 1.466 | 0.574 |
| Wet mass `m0 / D` | 2.466 | 1.574 |

Therefore, in this ideal comparison, NTP propellant is 0.3912 of the chemical reference, or **60.88% less propellant mass**. Wet mass is 0.6381 of the reference, or **36.19% less wet mass**. These percentages are not interchangeable: wet mass includes the shared dry mass.

If the NTP dry mass is 25% higher, its propellant ratio becomes `1.25 × 0.3912 = 0.4890`, which is 51.10% less propellant. Its wet-mass ratio is 0.7976, only 20.24% less. Engine, reactor, shielding, tank, radiator, and support-system mass therefore matter to a vehicle-level result.

## Ideal kinetic-energy derivation

Let `dμ > 0` be a small expelled propellant mass and `M` the rocket mass just before expulsion. Conservation of momentum for an ideal exhaust speed `c` gives:

```text
M dV = c dμ
```

The exhaust parcel leaves with inertial velocity `V - c` in the same direction convention. Expanding the before/after kinetic energies to first order in `dμ` and `dV`, and substituting `M dV = c dμ`, gives:

```text
dK_vehicle+exhaust = 1/2 c² dμ
```

Integrating from zero expelled mass to `m_p`:

```text
K_out = 1/2 c² m_p
      = 1/2 c² D [exp(Δv / c) - 1]
```

For equal dry mass, the ratio for an NTP case `N` and chemical case `C` is:

```text
K_N / K_C
  = (c_N / c_C)²
    × [exp(Δv / c_N) - 1] / [exp(Δv / c_C) - 1]
```

At 4 km/s this ideal kinetic-energy-output ratio is 1.5511: **55.11% more**, not 50% less. It falls below 1.0 near 9.72 km/s and below 0.5 near 17.27 km/s for this exhaust-velocity pair and equal dry mass. These are equation outputs, not real energy-use predictions. A higher exhaust velocity can reduce propellant mass yet increase the ideal kinetic energy carried by the vehicle and exhaust over some maneuver ranges.

## Why the source-energy claim remains unproven

Specific impulse relates thrust to propellant weight flow; it does not state how many joules of chemical or nuclear source energy are consumed. A source-energy comparison needs consistent system boundaries and measured or validated conversion efficiencies. For NTP it must include reactor-to-propellant heat transfer, operating and transient behavior, decay heat, rejected heat, residuals, and reactor/engine/support masses. The chemical reference needs a named propellant pair, reaction-energy accounting, engine operating point, and nozzle efficiency. Both vehicles also need comparable thrust, burn duration, storage, staging, trajectory, gravity and steering losses, boil-off, and payload requirements.

NASA's ideal rocket-equation and specific-impulse pages support the mass-ratio calculation. NASA NTP material describes roughly 880–900 s as potential/reference performance, while mission studies show architecture and transient assumptions affect outcomes. These sources do not establish a measured 50% source-energy saving for this Blender concept. See the source register and claim assessment for citations and limitations.

## Defensible statement

The defensible hypothesis is: **a high-Isp NTP stage may use at least 50% less propellant mass than a specified lower-Isp chemical stage for some fixed-Δv comparisons, before real vehicle mass and mission effects are closed.** The statement **“AETHER-1 uses 50% less energy than a normal rocket” is not demonstrated** by the available evidence. At the worked 4 km/s ideal comparison, the output-energy metric is higher, and actual source-energy consumption remains undetermined.
