# Changelog

All notable changes to the GarminSupla project are documented in this file.

This project follows conventions based on Keep a Changelog.

---

## [Unreleased]

---

## [0.5.1] - 2026-10-03

### Improved
- Improved the first-install administrator login flow. When no administrator account exists, the login page now displays the local account-creation command instead of the login form.
- Documented creation of the first dashboard administrator account with `scripts.create_admin`.

### Versioning
- Backend/dashboard version: `0.5.1`.
- Connect IQ application version remains `0.11.0`.

---

## [0.5.0] - 2026-10-03

### Added
- Added optional TOTP two-factor authentication for dashboard administrators.
- Added QR-code enrollment compatible with standard authenticator applications.
- Added password confirmation before enabling or disabling administrator 2FA.
- Added one-time recovery codes displayed after successful 2FA enrollment.
- Added secure recovery-code storage using hashes instead of plaintext codes.
- Added encrypted storage of the administrator TOTP secret.
- Added one-time recovery-code authentication when the authenticator is unavailable.
- Added local emergency administrator 2FA reset:
  ```bash
  docker compose exec garminsupla-api \
      python -m scripts.reset_admin_2fa
  ```
- Added local emergency administrator password reset:
  ```bash
  docker compose exec garminsupla-api \
      python -m scripts.reset_admin_password
  ```
- Added atomic password reset support in `AdminStore`.

### Improved
- Security-sensitive administrator authentication changes now rotate `session_version` and invalidate existing sessions.
- Recovery-code authentication consumes each recovery code exactly once.
- TOTP counters are persisted and protected against code reuse.
- Emergency password reset preserves the existing 2FA configuration.
- Emergency 2FA reset removes the TOTP secret, recovery codes, and used-counter state without changing the administrator password.
- Added a `Copy all codes` action for newly generated recovery codes.
- Authentication pages now follow the configured dashboard `Auto`, `Light`, or `Dark` theme.
- The login page receives the saved theme from the backend and does not require access to the protected setup API.

### Fixed
- Fixed loading of the shared dashboard JavaScript behind an HTTPS reverse proxy by using a root-relative static resource path.
- Fixed the login page remaining permanently in light mode when the dashboard was configured for dark mode.
- Updated authentication test fixtures to include the dashboard theme setting.

### Verification
- Manually verified administrator 2FA enrollment, TOTP login, recovery-code login, and 2FA disable flow.
- Manually verified emergency 2FA reset from the container console.
- Manually verified emergency administrator password reset with both 2FA disabled and enabled.
- Verified that password reset invalidates existing sessions while preserving 2FA configuration.
- Backend regression suite: 135 tests passed.

### Versioning
- Backend/dashboard version: `0.5.0`.
- Connect IQ application version remains `0.11.0`.

---

## [Connect IQ 0.11.0] - 2026-09-27

### Improved
- Completed simulator testing for six supported vívoactive targets: vívoactive 3 Music, 3 Music LTE, 4, 4S, 5, and 6.
- Added device-specific launcher icons for all six supported vívoactive models.
- Added scaled item graphics for vívoactive 3 Music, 3 Music LTE, 4, and 4S.
- Verified online, offline, and cached operation across the supported vívoactive family.
- Verified About and Wi-Fi refresh on supported devices. vívoactive 3 Music LTE does not support Wi-Fi.
- Updated the default build verification targets to replace vívoactive 3 with vívoactive 3 Music.

### Removed
- Removed vívoactive 3 after simulator testing revealed an Out Of Memory error.

### Verification
- Full manifest build verification completed with Connect IQ SDK 9.2.0.
- 68 manifest targets, 68 successful builds, 0 failures, 0 skipped targets.
- Default smoke-build verification: 5 successful builds, 0 failures.
- Verified Connect IQ 0.11.0 on a physical fēnix 8 Pro.

### Versioning
- Connect IQ application version: `0.11.0`.
- Backend/dashboard version remains `0.4.0`.

---

## [Connect IQ 0.10.0] - 2026-09-27

### Improved
- Added and simulator-tested 13 supported Venu family targets.
- Added device-specific launcher icons for Venu, Venu 2, Venu 3, Venu 4, Venu Sq 2, Venu Sq Music, and Venu X1 models.
- Added scaled item graphics for Venu Sq Music.
- Added action-menu gesture support for Venu 4 41mm, Venu 4 45mm, and Venu X1.
- Verified Wi-Fi refresh and About menu operation on Venu 4 and Venu X1.

### Fixed
- Improved the About screen layout for 320×360 displays used by Venu Sq 2 and Venu Sq 2 Music.
- Corrected launcher icon sizes across the supported Venu family.

### Removed
- Removed Venu Sq after simulator testing revealed an Out Of Memory error.

### Verification
- Full manifest build verification completed with Connect IQ SDK 9.2.0.
- 69 manifest targets, 69 successful builds, 0 failures, 0 skipped targets.

### Versioning
- Connect IQ application version: `0.10.0`.
- Backend/dashboard version remains `0.4.0`.

---

## [Connect IQ 0.9.0] - 2026-09-20

### Improved
- Added and verified fēnix 5S Plus, fēnix 5X, and fēnix 5X Plus compatibility.
- Added compact 240×240 layout adjustments for the fēnix 5 family.
- Added device-specific launcher icons and scaled item graphics for the fēnix 5 family.
- Wi-Fi functionality is now exposed only on devices with Wi-Fi support.
- Added and verified fēnix 6 Pro, fēnix 6S, fēnix 6S Pro, and fēnix 6X Pro compatibility.
- Reduced runtime memory usage by loading only the bitmap required for the current item state.
- Added device-specific resources for memory-constrained fēnix 6 family devices.
- Added and verified fēnix 7, fēnix 7 Pro, fēnix 7 Pro Solar (No Wi-Fi), fēnix 7S, fēnix 7S Pro, fēnix 7X, fēnix 7X Pro, and fēnix 7X Pro (No Wi-Fi) compatibility.
- Added device-specific launcher icons and scaled item graphics for the fēnix 7 family.
- Added and verified fēnix 8 43mm, fēnix 8 47mm/51mm, fēnix 8 Pro, fēnix 8 Solar 47mm, and fēnix 8 Solar 51mm compatibility.
- Added device-specific launcher icons and scaled item graphics where required for the fēnix 8 family.
- Verified fēnix 8 Pro operation on a physical device.
- Added and verified all seven fēnix 9 family targets in the simulator.
- Added device-specific launcher icons for the fēnix 9 family.
- Added scaled item graphics for fēnix 9 Pro Solar 47mm and 51mm.
- Added and verified fēnix E compatibility in the simulator.
- Added a device-specific 60×60 launcher icon for fēnix E.
- Verified 21 Forerunner targets in the simulator, including online, offline, cached data, item controls, and Wi-Fi behavior.
- Added device-specific launcher icons for supported Forerunner models.
- Added scaled item graphics for Forerunner models with smaller MIP displays.

### Fixed
- Devices without Wi-Fi no longer restore items from the Wi-Fi configuration snapshot.
- Offline items no longer allow actions or open confirmation/action menus.
- Improved About screen layout on compact 240×240 devices.
- Cached Wi-Fi capability detection to avoid repeated device-settings allocations on memory-constrained devices.
- Improved compact About screen e-mail layout by adapting between one and two lines based on available width.

### Removed
- Removed the fēnix 6 non-Pro target after runtime testing showed insufficient application memory for reliable operation.
- Removed the fēnix Chronos target after simulator testing revealed an Out Of Memory crash during application startup.
- Removed Forerunner 55, 245, 645, and 935 targets after simulator testing revealed Out Of Memory errors.

### Versioning
- Backend/dashboard version remains `0.4.0`.
- Connect IQ application version: `0.9.0`.

---

## [Connect IQ 0.8.0] - 2026-09-18

### Improved
- Added high-contrast color coding for watch item states.
- Active states such as `ON`, `OPENED`, and `EXPANDED` use green.
- Inactive states such as `OFF`, `CLOSED`, and `COLLAPSED` use light gray.
- Offline and unknown states use red.
- Cached configuration state uses yellow.
- Connection status text and indicator now use the same semantic colors.
- Completed the AMOLED / OLED visual treatment while preserving the existing GarminSupla mountain background.

### Fixed
- Keep the local Wi-Fi configuration snapshot synchronized with the latest live watch configuration.
- Prevent stale cached item lists from reappearing when the watch falls back to offline configuration.
- Avoid rewriting the cached snapshot on every polling cycle when only dynamic device state changes.

### Versioning
- Backend/dashboard version remains `0.4.0`.
- Connect IQ application version: `0.8.0`.

---

## [0.4.0] - 2026-09-17

### Improved
- Replaced the multi-watch selector dropdown with responsive watch cards.
- The selected watch is clearly highlighted, with responsive layouts for mobile, tablet, and desktop.
- Watch switching remains disabled while `Watch items` contain unsaved changes.
- Added a dedicated `Details` view for extended watch metadata.
- Extended watch metadata is hidden by default and can be expanded on demand.
- Per-watch application language remains available directly in the main watch view.
- Migrated the Connect IQ application menu to native `Menu2`.
- Refined the main watch item layout while preserving the existing background and device graphics.
- Navigation chevrons and the item position indicator are now shown only when multiple watch items are configured.
- Dashboard watch item previews now use the same icon bitmap resources as the Connect IQ application.
- Supported watch item types now share a consistent icon set between the dashboard and the watch.

### Versioning
- Backend/dashboard version: `0.4.0`.
- Connect IQ application version: `0.7.0`.

---

## [0.3.0] - 2026-09-15

### Added
- Per-watch application language modes: `Auto`, `Polski`, and `English`.
- Copy `Watch items` between already paired watches from the dashboard.

### Improved
- Connect IQ runtime UI now follows the per-watch application language in the main view, menus, confirmation dialogs, roller shutter and awning menus, About view, and Wi-Fi Sync errors.
- `Auto` application language follows the watch system language.
- Copying `Watch items` preserves the target watch identity, token, metadata, and application language.
- Copying `Watch items` does not modify the source watch or global UI / SUPLA settings.
- Watch item copying is disabled while the target watch has unsaved configuration changes.

### Fixed
- Expired dashboard administrator sessions now redirect directly to the login screen instead of showing a generic operation error.

### Versioning
- Backend/dashboard version: `0.3.0`.
- Connect IQ application version: `0.6.0`.

---

## [0.2.0] - 2026-09-12

### Added
- Multi-watch backend support.
- Independent authentication tokens and `Watch items` configuration for each watch.
- Multi-watch dashboard selection and management.
- Add new watch without affecting existing watches.
- Optional `Watch items` configuration copy when adding a new watch.
- Per-watch rename, replace, re-pair and delete operations.
- Multi-watch setup API endpoints.
- Credential revision tracking for reliable pairing completion detection.

### Improved
- Watch replacement preserves the same logical `watch_id`, name and configuration.
- Re-pair preserves the logical watch while invalidating the current token immediately.
- Replace keeps the old physical watch active until the new watch completes pairing.
- Dashboard returns automatically after successful targeted pairing.
- Watch management actions are disabled while unsaved `Watch items` changes exist.
- Empty watch configuration supports adding items from SUPLA.

### Fixed
- Prevented an old physical watch from falsely completing a replacement flow by updating `last_seen_at`.
- Connect IQ application now automatically requests a new pairing code when the current pairing session expires.
- Expired pairing codes no longer require restarting the watch application.

### Versioning
- Backend/dashboard version: `0.2.0`.
- Connect IQ application version: `0.5.1`.
- Backend/dashboard version is defined in `app/config.py` instead of being overridden through `APP_VERSION`.
- Connect IQ application version is defined once in the base string resources.

---

## [0.1.0] - 2026-07-19

### Added
- Initial FastAPI backend.
- Docker support.
- Health endpoint.
- API Key authentication.
- Persistent JSON configuration store.
- Setup service for application configuration.
- Responsive setup wizard.
- Wizard progress component.
- Server URL validation using Pydantic.
- Persistent SUPLA server configuration.

### Improved
- Responsive setup page layout.
- Mobile spacing and desktop alignment.
- Consistent Bootstrap styling.
- Green focus state for form controls.

### Fixed
- Setup button alignment.
- Responsive card width.
- Layout spacing on desktop and mobile.
