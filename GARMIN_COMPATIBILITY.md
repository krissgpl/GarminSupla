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

## fēnix 6 family

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenix6` | fēnix 6 / 6 Solar / 6 Dual Power | `006-B3289-00`, `006-B3514-00`, `006-B3766-00`, `006-B3770-00` | 3.4 | MIP, 260×260, 64 colors | No | N/A (no Wi-Fi) | Not tested | Not tested |
| `fenix6pro` | fēnix 6 Pro / 6 Sapphire / 6 Pro Solar / 6 Pro Dual Power | `006-B3290-00`, `006-B3515-00`, `006-B3767-00`, `006-B3771-00` | 3.4 | MIP, 260×260, 64 colors | No | Not tested | Not tested | Not tested |
| `fenix6s` | fēnix 6S / 6S Solar / 6S Dual Power | `006-B3287-00`, `006-B3512-00`, `006-B3764-00`, `006-B3768-00` | 3.4 | MIP, 240×240, 64 colors | No | N/A (no Wi-Fi) | Not tested | Not tested |
| `fenix6spro` | fēnix 6S Pro / 6S Sapphire / 6S Pro Solar / 6S Pro Dual Power | `006-B3288-00`, `006-B3513-00`, `006-B3765-00`, `006-B3769-00` | 3.4 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fenix6xpro` | fēnix 6X Pro / 6X Sapphire / 6X Pro Solar | `006-B3291-00`, `006-B3516-00` | 3.4 | MIP, 280×280, 64 colors | No | Not tested | Not tested | Not tested |

## fēnix 7 family

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenix7` | fēnix 7 | `006-B3906-00`, `006-B3909-00` | 5.2 | MIP, 260×260, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix7pro` | fēnix 7 Pro | `006-B4375-00` | 5.2 | MIP, 260×260, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix7pronowifi` | fēnix 7 Pro Solar (No Wi-Fi) | `006-B4595-00` | 5.2 | MIP, 260×260, 64 colors | Yes | N/A (no Wi-Fi) | Not tested | Not tested |
| `fenix7s` | fēnix 7S | `006-B3905-00`, `006-B3908-00` | 5.2 | MIP, 240×240, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix7spro` | fēnix 7S Pro | `006-B4374-00` | 5.2 | MIP, 240×240, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix7x` | fēnix 7X | `006-B3907-00`, `006-B3910-00` | 5.2 | MIP, 280×280, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix7xpro` | fēnix 7X Pro | `006-B4376-00` | 5.2 | MIP, 280×280, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix7xpronowifi` | fēnix 7X Pro (No Wi-Fi) | `006-B4596-00` | 5.2 | MIP, 280×280, 64 colors | Yes | N/A (no Wi-Fi) | Not tested | Not tested |

## fēnix 8 family

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenix843mm` | fēnix 8 43mm | `006-B4534-00` | 6.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |
| `fenix847mm` | fēnix 8 47mm / 51mm | `006-B4536-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fenix8pro47mm` | fēnix 8 Pro | `006-B4631-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fenix8solar47mm` | fēnix 8 Solar 47mm | `006-B4532-00` | 6.0 | MIP, 260×260, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix8solar51mm` | fēnix 8 Solar 51mm | `006-B4533-00` | 6.0 | MIP, 280×280, 64 colors | Yes | Not tested | Not tested | Not tested |

## fēnix E

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenixe` | fēnix E | `006-B4666-00` | 6.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |

## Forerunner

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fr965` | Forerunner 965 | `006-B4315-00` | 5.2 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fr970` | Forerunner 970 | `006-B4565-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |

## Venu

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `venusq2` | Venu Sq 2 | `006-B4115-00` | 5.0 | AMOLED, 320×360 | Yes | N/A (no Wi-Fi) | Not tested | Not tested |

## Notes

- Product IDs must match the GarminSupla Connect IQ manifest.
- Part numbers must come from verified Garmin device data or observed device metadata.
- Unknown part numbers must not be assigned to a model by inference.
- Wi-Fi Sync status refers to GarminSupla runtime behavior, not only to hardware capability.
- Simulator testing does not replace testing on a physical Garmin device.
