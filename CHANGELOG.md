# Changelog

Wszystkie istotne zmiany w projekcie GarminSupla.

Projekt stosuje zasady zbliżone do Keep a Changelog.

---

## [Unreleased]

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
