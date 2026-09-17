# Changelog

Wszystkie istotne zmiany w projekcie GarminSupla.

Projekt stosuje zasady zbliżone do Keep a Changelog.

---

## [Unreleased]

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
