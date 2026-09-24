# What would be needed to validate a 50% energy claim

The current Blender project cannot validate propulsion performance. A defensible energy claim would need the following work in order.

## 1. Freeze the comparison

Specify a mission and a baseline before calculating savings:

- payload and terminal mass/orbit/velocity;
- departure and arrival states, required maneuver sequence, launch assumptions, and staging;
- same trajectory objective, burn-time and thrust constraints for both vehicles;
- exact chemical baseline (propellants, engine, nozzle, feed system, operating point);
- exact NTP reference architecture (propellant, achieved—not aspirational—Isp, thrust/transients, reactor/engine mass).

“Normal rocket” is not a reproducible baseline. A SSME 452 s datum and an NTP 900 s study target are useful for a screening calculation, not a matched vehicle comparison.

## 2. Define the energy boundary

Report separate numbers for:

1. **Jet/vehicle kinetic-energy increase**, `ΔK`, calculated from a finite-burn trajectory.
2. **Chemical energy released** by the baseline propellant.
3. **Nuclear thermal energy supplied** to the NTP propellant and nuclear fuel depletion.
4. **Rejected heat and other losses**, including start-up/shut-down, pressure drops, nozzle inefficiency, pumps, cryogenic management, and power conversion where applicable.

The desired comparison must state whether “50% less energy” means source joules, reactor fuel, propellant mass, or energy per delivered payload/mission. These are different metrics.

## 3. Close the vehicle mass model

Include payload, engine, reactor, shielding, nozzle, supports, tanks, insulation, pressurization, thermal management, power/control equipment, residuals, propellant boil-off, and staging/disposal masses. Iterate mass with trajectory until the vehicle closes. A high-Isp engine can lower propellant mass but a heavier propulsion system or low-density hydrogen tankage can reduce or remove that advantage.

## 4. Use a finite-burn trajectory and validated engine models

Use mission-level trajectory integration with gravity, steering, thrust, changing mass, burn transients, and operating limits. Use a thermal/propulsion model with independently checked thermodynamic properties and losses, plus structural and materials assessments. Calibrate against applicable ground-test data. NASA's NTP transient study (S5) explicitly notes that start/stop behavior changes average burn Isp; the ideal equation alone omits this.

## 5. Acceptance test for the claim

Publish both systems' full mass and energy ledgers, model versions, input sources, uncertainty ranges, and convergence evidence. The energy claim passes only if the same mission and energy boundary show:

```text
E_source,NTP / E_source,chemical <= 0.50
```

across the agreed uncertainty range. A lower propellant mass or higher Isp is not a substitute for this test. No reactor construction specification or hazardous hardware detail is needed to perform a top-level mission trade study.
