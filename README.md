# Open BLDC Motor Test-Bench Dataset for Vibration and Current Analysis

## Introduction

This repository contains time-series measurements collected from a BLDC motor
test bench for vibration and current analysis. The motor under test is a
STEPPEROLINE BLDC Motor 57BYA54-24-01 driven by a BD10LR BLDC motor driver.
Mechanical load is applied using an AHB-05M hysteresis brake. Vibration is
measured with two ADXL355 accelerometers mounted on the front and rear bearing
mount rings, and electrical measurements are recorded with an INA226 current
sensor placed before the BLDC motor driver.

![Test bench](images/test-bench.jpg)

The dataset includes a baseline recording, `analize_0rpm_0mA_bat.csv`, captured
with the test bench switched off. This file represents the background sensor
noise of the measurement chain without motor rotation or load current.

The final suffix in each file name identifies the motor power source. Files
ending in `bat` were recorded with the motor powered from a lead-acid battery.
Files ending in `mait` were recorded with the motor powered from a UNIT-T
UTP3305 laboratory power supply.

The current value in each file name corresponds to the approximate motor load:

| Motor load | Current |
| --- | --- |
| ~15% | 19 mA |
| ~30% | 38 mA |
| ~50% | 64 mA |
| ~75% | 96 mA |
| ~100% | 128 mA |

The main hardware components are:

| Component | Model / description |
| --- | --- |
| Motor driver | BD10LR BLDC |
| Motor under test | STEPPEROLINE BLDC Motor 57BYA54-24-01 |
| Load | Hysteresis Brake AHB-05M |
| Vibration sensors | ADXL355, mounted on the front and rear bearing mount rings |
| Current sensors | INA226 |

## CSV Columns

Each CSV file uses the following columns:

| Column | Description |
| --- | --- |
| `t_us` | Sample timestamp in microseconds. |
| `ax`, `ay`, `az` | ADXL355 vibration sensor axes measured on the front bearing ring, bearing type 608ZZ 8x22x7. |
| `ax1`, `ay1`, `az1` | ADXL355 vibration sensor axes measured on the rear bearing ring, bearing type 606ZZ 6x17x6. |
| `shunt_raw` | Raw INA226 shunt-voltage reading from the current sensor placed before the BLDC motor driver. |
| `bus_raw` | Raw INA226 bus-voltage reading from the current sensor placed before the BLDC motor driver. |
| `curr_raw` | Raw INA226 current reading from the current sensor placed before the BLDC motor driver. |
| `pg_rpm` | Pulse signal from the motor driver. Six pulses correspond to one full mechanical revolution. |
| `seq` | Sample sequence counter. |
| `dt` | Time difference between samples. |

## License

The data and documentation in this repository are licensed under the Creative
Commons Attribution 4.0 International License (CC BY 4.0).
Full license text: https://creativecommons.org/licenses/by/4.0/legalcode.

You may use, copy, distribute, and adapt the data only if you give appropriate
credit to the author.

Recommended citation:

> Robertas Uselis. Open BLDC Motor Test-Bench Dataset for Vibration and Current Analysis. 2026. https://github.com/Atikas/OpenData.
> License: CC BY 4.0.

If you modify the data, indicate that changes were made.
