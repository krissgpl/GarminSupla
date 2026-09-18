# GarminSupla Garmin Compatibility Matrix

This document tracks compatibility of GarminSupla with Garmin Connect IQ
devices declared in `connectiq/GarminSupla/manifest.xml`.

Successful compilation alone does not mean that a device is fully compatible.
Simulator and physical-device testing are tracked separately.

## Status values

- `Not tested` - no GarminSupla runtime test has been performed.
- `Passed` - the relevant GarminSupla test has completed successfully.
- `Failed` - a known compatibility problem exists.
- `N/A` - the test does not apply to the device.

## fēnix 5 family

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenix5s` | fēnix 5S | `006-B2544-00`, `006-B2797-00` | 3.1 | MIP, 218×218, 64 colors | No | Not tested | Not tested | Not tested |
| `fenix5splus` | fēnix 5S Plus | `006-B2900-00`, `006-B3134-00` | 3.3 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fenix5x` | fēnix 5X | `006-B2604-00`, `006-B2798-00` | 3.1 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fenix5xplus` | fēnix 5X Plus | `006-B3111-00`, `006-B3135-00` | 3.3 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |

## Notes

- Product IDs must match the GarminSupla Connect IQ manifest.
- Part numbers must come from verified Garmin device data or observed device metadata.
- Unknown part numbers must not be assigned to a model by inference.
- Wi-Fi Sync status refers to GarminSupla runtime behavior, not only to hardware capability.
- Simulator testing does not replace testing on a physical Garmin device.
