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

## fēnix Chronos

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenixchronos` | fēnix Chronos | `006-B2432-00`, `006-B2675-00` | 3.1 | MIP, 218×218, 64 colors | No | Not tested | Not tested | Not tested |

## fēnix 5 family

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenix5splus` | fēnix 5S Plus | `006-B2900-00`, `006-B3134-00` | 3.3 | MIP, 240×240, 64 colors | No | Passed | Passed | Not tested |
| `fenix5x` | fēnix 5X | `006-B2604-00`, `006-B2798-00` | 3.1 | MIP, 240×240, 64 colors | No | N/A (no Wi-Fi) | Passed | Not tested |
| `fenix5xplus` | fēnix 5X Plus | `006-B3111-00`, `006-B3135-00` | 3.3 | MIP, 240×240, 64 colors | No | Passed | Passed | Not tested |

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

## fēnix 9 family

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenix943mm` | fēnix 9 43mm | `006-B5133-00` | 6.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |
| `fenix947mm` | fēnix 9 47mm / 51mm | `006-B5134-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fenix9pro43mm` | fēnix 9 Pro 43mm | `006-B4952-00` | 6.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |
| `fenix9pro47mm` | fēnix 9 Pro 47mm | `006-B4953-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fenix9pro51mm` | fēnix 9 Pro 51mm | `006-B4954-00` | 6.0 | AMOLED, 466×466 | Yes | Not tested | Not tested | Not tested |
| `fenix9prosolar47mm` | fēnix 9 Pro Solar 47mm | `006-B4955-00` | 6.0 | MIP, 260×260, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fenix9prosolar51mm` | fēnix 9 Pro Solar 51mm | `006-B4956-00` | 6.0 | MIP, 280×280, 64 colors | Yes | Not tested | Not tested | Not tested |

## fēnix E

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fenixe` | fēnix E | `006-B4666-00` | 6.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |

## Forerunner

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fr55` | Forerunner 55 | `006-B3869-00`, `006-B4033-00`, `006-B4838-00` | 3.4 | MIP, 208×208, 8 colors | No | Not tested | Not tested | Not tested |
| `fr70` | Forerunner 70 | `006-B4916-00`, `006-B5214-00` | 6.0 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `fr165` | Forerunner 165 | `006-B4432-00` | 5.2 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `fr165m` | Forerunner 165 Music | `006-B4433-00` | 5.2 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `fr170` | Forerunner 170 | `006-B4815-00` | 6.0 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `fr170m` | Forerunner 170 Music | `006-B4814-00` | 6.0 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `fr245` | Forerunner 245 | `006-B3076-00`, `006-B3145-00`, `006-B3914-00` | 3.3 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr245m` | Forerunner 245 Music | `006-B3077-00`, `006-B3321-00`, `006-B3913-00` | 3.3 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr255` | Forerunner 255 | `006-B3992-00` | 5.2 | MIP, 260×260, 64 colors | No | Not tested | Not tested | Not tested |
| `fr255m` | Forerunner 255 Music | `006-B3990-00` | 5.2 | MIP, 260×260, 64 colors | No | Not tested | Not tested | Not tested |
| `fr255s` | Forerunner 255S | `006-B3993-00` | 5.2 | MIP, 218×218, 64 colors | No | Not tested | Not tested | Not tested |
| `fr255sm` | Forerunner 255S Music | `006-B3991-00` | 5.2 | MIP, 218×218, 64 colors | No | Not tested | Not tested | Not tested |
| `fr265` | Forerunner 265 | `006-B4257-00` | 5.2 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |
| `fr265s` | Forerunner 265S | `006-B4258-00` | 5.2 | AMOLED, 360×360 | Yes | Not tested | Not tested | Not tested |
| `fr57042mm` | Forerunner 570 42mm | `006-B4574-00` | 6.0 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `fr57047mm` | Forerunner 570 47mm | `006-B4570-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fr645` | Forerunner 645 | `006-B2886-00`, `006-B3003-00` | 3.1 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr645m` | Forerunner 645 Music | `006-B2888-00`, `006-B3004-00` | 3.2 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr745` | Forerunner 745 | `006-B3589-00`, `006-B3794-00` | 3.3 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr935` | Forerunner 935 | `006-B2691-00`, `006-B2833-00` | 3.1 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr945` | Forerunner 945 | `006-B3113-00`, `006-B3441-00` | 3.3 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr945lte` | Forerunner 945 LTE | `006-B3652-00`, `006-B3978-00` | 3.4 | MIP, 240×240, 64 colors | No | Not tested | Not tested | Not tested |
| `fr955` | Forerunner 955 / Solar | `006-B4024-00` | 5.2 | MIP, 260×260, 64 colors | Yes | Not tested | Not tested | Not tested |
| `fr965` | Forerunner 965 | `006-B4315-00` | 5.2 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `fr970` | Forerunner 970 | `006-B4565-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |

## Venu

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `venu` | Venu | `006-B3226-00`, `006-B3389-00` | 3.3 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `venu2` | Venu 2 | `006-B3703-00`, `006-B3950-00` | 5.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |
| `venu2plus` | Venu 2 Plus | `006-B3851-00`, `006-B4017-00` | 5.0 | AMOLED, 416×416 | Yes | Not tested | Not tested | Not tested |
| `venu2s` | Venu 2S | `006-B3704-00`, `006-B3949-00` | 5.0 | AMOLED, 360×360 | Yes | Not tested | Not tested | Not tested |
| `venu3` | Venu 3 | `006-B4260-00` | 5.2 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `venu3s` | Venu 3S | `006-B4261-00` | 5.2 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `venu441mm` | Venu 4 41mm | `006-B4644-00` | 6.0 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `venu445mm` | Venu 4 45mm | `006-B4643-00` | 6.0 | AMOLED, 454×454 | Yes | Not tested | Not tested | Not tested |
| `venud` | Venu Mercedes-Benz Collection | `006-B3737-00`, `006-B3740-00` | 3.3 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `venusq` | Venu Sq | `006-B3600-00`, `006-B3603-00`, `006-B3837-00`, `006-B4118-00` | 3.3 | Transflective LCD, 240×240, 65K colors | Yes | N/A (no Wi-Fi) | Not tested | Not tested |
| `venusq2` | Venu Sq 2 | `006-B4115-00` | 5.0 | AMOLED, 320×360 | Yes | N/A (no Wi-Fi) | Not tested | Not tested |
| `venusq2m` | Venu Sq 2 Music | `006-B4116-00` | 5.0 | AMOLED, 320×360 | Yes | Not tested | Not tested | Not tested |
| `venusqm` | Venu Sq Music Edition | `006-B3596-00`, `006-B3599-00`, `006-B3838-00`, `006-B4119-00` | 3.3 | Transflective LCD, 240×240, 65K colors | Yes | Not tested | Not tested | Not tested |
| `venux1` | Venu X1 | `006-B4603-00` | 6.0 | AMOLED, 448×486 | Yes | Not tested | Not tested | Not tested |

Mercedes-Benz Venu 2 and Venu 2S part numbers are recognized by the
backend resolver, but their Connect IQ product-ID mapping has not yet been
verified, so they are not assigned to a matrix row here.

## vívoactive

| Connect IQ product ID | Garmin model | Known part numbers | Connect IQ API | Display | Touch | Wi-Fi Sync | Simulator | Physical device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `vivoactive3` | vívoactive 3 | `006-B2700-00`, `006-B2976-00`, `006-B3446-00` | 3.1 | MIP, 240×240, 64 colors | Yes | Not tested | Not tested | Not tested |
| `vivoactive3m` | vívoactive 3 Music | `006-B2988-00`, `006-B3163-00` | 3.2 | MIP, 240×240, 64 colors | Yes | Not tested | Not tested | Not tested |
| `vivoactive3mlte` | vívoactive 3 Music LTE | `006-B3066-00` | 3.1 | MIP, 240×240, 64 colors | Yes | Not tested | Not tested | Not tested |
| `vivoactive4` | vívoactive 4 | `006-B3225-00`, `006-B3388-00` | 3.3 | MIP, 260×260, 64 colors | Yes | Not tested | Not tested | Not tested |
| `vivoactive4s` | vívoactive 4S | `006-B3224-00`, `006-B3387-00` | 3.3 | MIP, 218×218, 64 colors | Yes | Not tested | Not tested | Not tested |
| `vivoactive5` | vívoactive 5 | `006-B4426-00` | 5.2 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |
| `vivoactive6` | vívoactive 6 | `006-B4625-00` | 6.0 | AMOLED, 390×390 | Yes | Not tested | Not tested | Not tested |

## Connect IQ build verification

Build verification confirms that GarminSupla compiles successfully for a
Connect IQ target. It does not count as simulator or physical-device runtime
testing.

Full manifest build verification was completed with Connect IQ SDK 9.2.0 on
2026-09-19:

- Manifest targets: 77
- Installed manifest targets: 77
- Successful builds: 77
- Failed builds: 0
- Skipped / not installed targets: 0

The full manifest verification can be repeated with:

```powershell
.\scripts\verify_connectiq_builds.ps1 `
    -DeveloperKey $Key `
    -InstalledManifestTargets

```

The script also keeps a smaller default smoke-build set for faster development
verification:

| Connect IQ product ID | Representative case |
| --- | --- |
| `fr55` | API 3.4, MIP 208×208, 8 colors |
| `vivoactive3` | API 3.1, MIP 240×240, touch |
| `venusq2` | API 5.0, AMOLED 320×360, rectangular touch display, no Wi-Fi |
| `fenix7pronowifi` | API 5.2, MIP 260×260, touch, no Wi-Fi |
| `fenix8pro47mm` | API 6.0, AMOLED 454×454, touch, target-specific resources |

## Notes

- Product IDs must match the GarminSupla Connect IQ manifest.
- Part numbers must come from verified Garmin device data or observed device metadata.
- Unknown part numbers must not be assigned to a model by inference.
- Wi-Fi Sync status refers to GarminSupla runtime behavior, not only to hardware capability.
- Simulator testing does not replace testing on a physical Garmin device.
