# UX / Setup Improvements

- [X] Rebuild the setup wizard.
  - After SUPLA authorization, go directly to the dashboard.
  - On the dashboard, pair / add a Garmin Watch first.
  - Then select SUPLA items that should be available on the watch.
  - Remove the mandatory separate gate-selection step from the setup wizard.

- [X] Add GarminSupla server configuration through the Garmin Connect / Connect IQ app on the phone.
  - The GarminSupla server URL is configured exclusively in the Connect IQ application settings on the phone.
  - The watch reads the configured URL from `Application.Properties`.
  - The server URL is not configured from the watch UI or GarminSupla web dashboard.

- [X] Improve the SUPLA re-authorization flow.
  - Re-authorization should not restart the setup wizard from the beginning.
  - After successful OAuth, return to the dashboard when configuration already exists.

- [X] Group the `Add from SUPLA` list by device type.
  - Gates
  - Scenes
  - Other devices

- [X] Rebuild the `Watch items` dashboard layout for different screen widths.
  - Desktop / laptop:
    - display items as cards in a responsive grid,
    - use the available page width,
    - avoid one long vertical column.
  - Mobile:
    - keep items in a single vertical column,
    - keep `Move up`, `Move down`, and `Remove` actions inside the card width.

- [X] Add configuration loading through Wi-Fi Sync.
  - When phone communication is unavailable, load configuration through Wi-Fi.
  - Store the last valid configuration as a local snapshot.
  - Display `Cached` when the app is using the locally stored configuration.

- [X] Add watch action execution through Wi-Fi Sync.
  - Support:
    - `toggle`,
    - `open`,
    - `close`,
    - `stop`,
    - `collapse`,
    - `expand`.
  - Refresh the configuration after a successful action.
  - Delete the pending action before requesting refreshed configuration to prevent accidental action replay.

- [X] Improve the UI state transition after Wi-Fi Sync.
  - Avoid the short `Offline -> Cached` transition during manual Wi-Fi refresh.
  - Keep the current view during a short Wi-Fi refresh grace period.
  - Retry foreground verification / configuration while Wi-Fi Sync is completing.
  - Preserve the existing Wi-Fi snapshot fallback logic.

# Multi-watch

- [X] Refactor the backend from a single `watch` to a collection of paired watches.
  - Each watch has its own:
    - `id`,
    - token,
    - user-defined name,
    - device metadata,
    - `enabled` status,
    - `created_at`,
    - `last_seen_at`,
    - independent list of `Watch items`.

- [X] Move `Watch items` configuration to individual watches.
  - Item order and per-item settings are isolated per watch.
  - Changing one watch configuration does not affect other watches.

- [X] Refactor watch authentication for multi-watch support.
  - Identify the watch by its token.
  - Support multiple simultaneously valid watch tokens.
  - Adding a new watch does not invalidate existing watches.

- [X] Refactor pairing for multiple watches.
  - Support multiple active pairing sessions.
  - Each pairing session has its own:
    - `pairing_id`,
    - pairing code,
    - expiration time,
    - approval state.
  - Adding a new watch does not replace an existing watch.

- [X] Add complete watch lifecycle operations.
  - `Add watch` creates a new logical watch with a new `watch_id`.
  - `Re-pair` preserves the logical watch and configuration but invalidates the current token immediately.
  - `Replace watch` preserves the same `watch_id`, name and items.
  - During replacement, the old physical watch stays valid until the new watch consumes the pairing session.
  - `Delete watch` removes the logical watch and its configuration.

- [X] Extend user-defined watch names to multi-watch.
  - Each paired watch has its own user-defined name.
  - Keep the user-defined name separate from the hardware model.
  - Reuse name validation:
    - trim surrounding whitespace,
    - reject empty values,
    - maximum length: 50 characters.

- [X] Add configuration copying when adding a new watch.
  - Allow starting with an empty configuration.
  - Allow deep-copying `Watch items` from an existing watch.
  - Do not copy global UI or SUPLA settings.

- [X] Optionally allow copying `Watch items` between already paired watches.


# Multi-watch Dashboard

- [X] Add active watch selection in the dashboard.
  - Keep `selectedWatchId`.
  - Show only the selected watch's `Watch items`.
  - Switching watches updates the configuration without reloading the page.

- [X] Add an `Add watch` action.
  - Pair another Garmin watch without affecting existing watches.
  - Allow optional configuration copy from an existing watch.

- [X] Add watch management actions.
  - `Rename`
  - `Replace watch`
  - `Re-pair`
  - `Delete`

- [X] Add multi-watch dashboard API endpoints.
  - `GET /api/v1/setup/watches`
  - `GET /api/v1/setup/watches/{watch_id}`
  - `PATCH /api/v1/setup/watches/{watch_id}`
  - `DELETE /api/v1/setup/watches/{watch_id}`
  - `GET /api/v1/setup/watches/{watch_id}/items`
  - `PUT /api/v1/setup/watches/{watch_id}/items`

- [X] Protect watch management while `Watch items` contain unsaved changes.
  - Disable watch selection.
  - Disable Add, Replace, Re-pair and Delete until changes are saved.

- [X] Detect successful targeted pairing using credential revision.
  - Do not treat an old physical watch updating `last_seen_at` as completed replacement.
  - Return automatically to the selected watch after replacement completes.

- [X] Optionally rebuild the watch selector as responsive watch cards.
  - Display watch cards side by side on wide screens.
  - Clearly highlight the selected watch.
  - Keep responsive behavior on smaller screens.

- [X] Optionally add a dedicated `Details` view for extended watch metadata.

# Localization

- [X] Add Polish and English support to the Connect IQ application.
  - Use English as the default fallback language.
  - Add complete Polish translations.
  - Remove hardcoded user-facing strings from the watch code.
  - Introduce a shared localization layer for application UI strings.

- [X] Add per-watch application language modes.
  - `Auto`
  - `Polski`
  - `English`
  - `Auto` uses the watch system language.
  - `Polski` / `English` overrides come from backend configuration.
  - Language selection must be independent for each watch.

- [X] Add dashboard localization.
  - `Auto`
  - `Polski`
  - `English`
  - `Auto` should use the browser language by default.
  - Persist the selected dashboard language as a UI setting.
  - Dashboard language must be independent from watch languages.

# Dashboard Theme

- [X] Add dashboard theme modes.
  - `Auto`
  - `Light`
  - `Dark`
  - `Auto` should use the browser / operating system color preference.
  - Persist the selected dashboard theme as a UI setting.
  - Add a theme selector to the dashboard.
  - Use the dark-outline GarminSupla logo on light backgrounds.
  - Use the white-outline GarminSupla logo on dark backgrounds.
  - Keep dashboard theme independent from watch display settings.

# Watch Metadata

- [X] Send device metadata from the Connect IQ application to the backend.
  - Device ID.
  - Part number.
  - Firmware version.
  - Connect IQ version.
  - Detected system language.
  - GarminSupla app version.
  - Resolve the device model on the backend from the Garmin part number.

- [X] Do not label `uniqueIdentifier` as a serial number.
  - Use `Device ID` in the dashboard.
  - The Garmin hardware serial number is not exposed to Connect IQ applications.

- [X] Update watch metadata automatically at relevant lifecycle points.
  - During first pairing.
  - During application startup after successful watch authentication.
  - Firmware and GarminSupla version changes are captured on the next application start.
  - Update `last_seen_at` when metadata is successfully received by the backend.

- [X] Display watch metadata in the dashboard.
  - User-defined name.
  - Device model.
  - Device ID.
  - Part number.
  - Firmware version.
  - Connect IQ version.
  - GarminSupla version.
  - Detected system language.
  - Last seen.

# Watch UI

- [X] Add the production application menu.
  - `Wi-Fi refresh`
  - `About`

- [X] Add an `About` screen.
  - GarminSupla
  - Version `0.5.0`
  - Author: `Krzysztof Zawadzki`
  - E-mail: `garminsupla@home-dev.eu`
  - Prepare the screen for future Polish / English localization.

- [X] Automatically refresh an expired pairing code.
  - Detect an expired pairing session.
  - Request and display a new pairing code without restarting the application.
  - Reject the expired code.
  - Handle expiration both during status polling and immediately before consume.

- [X] Rebuild the main Connect IQ UI toward a more native Garmin / Menu2 style.

- [X] Prepare a consistent icon set for supported item types.
  - Add dedicated icons for supported types, including:
    - gate,
    - light,
    - switch,
    - roller shutter,
    - awning,
    - scene.
  - Use corresponding icons in the Connect IQ app and the dashboard.
  - When selecting an icon in the dashboard, show the exact equivalent used on the watch.
  - Consider readability on small screens and Connect IQ device limitations.
  - Keep a `default` icon as a fallback for unsupported or future item types.

- [X] Use AMOLED / OLED display capabilities.
  - Prepare colored item graphics.
  - Prefer black backgrounds and high contrast.
  - Use color to represent device type and state.
  - Prepare different graphics for device states, for example:
    - ON / OFF,
    - OPENED / CLOSED,
    - ONLINE / OFFLINE.
  - Preserve readability while keeping reasonable power consumption on AMOLED displays.

# Branding

- [X] Prepare a shared GarminSupla icon / logo.
  - Use the same visual theme in:
    - Garmin Connect IQ application,
    - watch launcher icon,
    - web dashboard,
    - website favicon.
  - Prepare variants suitable for different sizes and resolutions.
  - Prepare versions readable on both light and dark backgrounds.
  - For Connect IQ, prepare a launcher icon that meets the requirements of supported devices instead of scaling the current 24x24 source.
  - Keep one consistent GarminSupla visual identity as the source for all variants.

# SUPLA

- [X] Add SUPLA scenes support.
  - Load scenes from `scenes_r`.
  - Execute scenes through `scenes_ea`.
  - Show only active and non-hidden scenes in `Add from SUPLA`.

# Garmin Device Compatibility

- [ ] Expand Garmin watch model resolution by part number.
  - Extend `WATCH_MODELS_BY_PART_NUMBER` beyond the currently known fēnix 8 Pro entry.
  - Cover supported Garmin models from the Connect IQ manifest where reliable part-number information is available.
  - Keep unknown part numbers safe and display them without guessing the device model.
  - Add tests for known, unknown, empty and normalized part numbers.

- [ ] Prepare a Garmin compatibility matrix.
  - Track:
    - Connect IQ product ID,
    - Garmin model,
    - known part numbers,
    - Connect IQ API level,
    - display type and resolution,
    - touch support,
    - Wi-Fi Sync behavior,
    - simulator test status,
    - physical-device test status.
  - Do not treat successful compilation as proof of full device compatibility.


# Dashboard Authentication

- [ ] Add two-factor authentication for dashboard administrators.
  - Use TOTP compatible with standard authenticator applications.
  - Add QR-code enrollment.
  - Require password confirmation before enabling or disabling 2FA.
  - Generate one-time recovery codes.
  - Store recovery codes securely.
  - Protect the TOTP secret from accidental exposure and logging.
  - Define a secure recovery procedure if the authenticator is lost.
  - Invalidate or rotate existing sessions when security-sensitive authentication settings change.


# Security

- [ ] Perform a complete GarminSupla security audit.
  - Review the dashboard authentication and authorization flow.
  - Review administrator sessions and expiration.
  - Review CSRF protection for all state-changing operations.
  - Review XSS and HTML escaping for user-controlled, SUPLA and watch-provided data.
  - Review SUPLA OAuth authorization, callback validation and stored tokens.
  - Review Garmin watch Bearer-token authentication.
  - Review pairing session creation, approval, consumption and expiration.
  - Review API-key authentication.
  - Review token generation, entropy, rotation and invalidation.
  - Verify that secrets and credentials are never written to application logs.
  - Review permissions of persistent configuration and token files.
  - Review static resources and all unauthenticated endpoints.
  - Review dependency and container vulnerabilities.

- [ ] Harden the Internet-exposed port `8008`.
  - Document the actual network path:
    - Internet,
    - router / NAT,
    - firewall,
    - reverse proxy,
    - TLS termination,
    - Docker host,
    - GarminSupla container.
  - Determine whether port `8008` needs to be directly reachable from the Internet.
  - Verify whether direct access to port `8008` can bypass protections provided by the reverse proxy or other network layers.
  - Prefer exposing only the reverse proxy publicly when direct port `8008` access is not required.
  - If direct Internet access to port `8008` is required, secure it explicitly.
  - Enumerate every route reachable through the public port.
  - Review exposure of:
    - `/docs`,
    - `/redoc`,
    - `/openapi.json`.
  - Disable or restrict development / API documentation endpoints in production when they are not required.
  - Enforce HTTPS for all public communication.
  - Review TLS configuration and certificate handling.
  - Add appropriate production security headers.
  - Review Host-header handling and allowed public hostnames.
  - Review HTTP methods accepted by public endpoints.
  - Introduce rate limiting where appropriate, especially for:
    - administrator login,
    - pairing creation,
    - pairing status polling,
    - pairing consumption,
    - invalid watch-token attempts,
    - public API endpoints.
  - Add protection against brute-force authentication attempts.
  - Review request-body size limits.
  - Review connection, request and upstream timeouts.
  - Review concurrent connection limits and resource exhaustion.
  - Review protection against simple denial-of-service and slow-request attacks.
  - Define firewall rules for the public service.
  - Consider automated blocking such as Fail2ban or an equivalent mechanism where useful.
  - Log suspicious authentication and network activity without logging credentials or tokens.
  - Test the deployed service from outside the local network.
  - Perform an external port and HTTP attack-surface scan after hardening.

- [ ] Harden the production Docker deployment.
  - Do not use the development-style full repository bind mount in the final production deployment unless required.
  - Persist only required configuration and data directories.
  - Run the application with the minimum required privileges.
  - Evaluate running the container as a non-root user.
  - Restrict filesystem access where practical.
  - Protect `.env` and persistent secrets with appropriate filesystem permissions.
  - Add container health checks.
  - Define CPU and memory limits where appropriate.
  - Pin and periodically review Python dependencies.
  - Separate development and production Docker configuration where useful.

- [ ] Add administrator security audit logging.
  - Record security-relevant administrative actions such as:
    - login success and failure,
    - logout,
    - 2FA changes,
    - SUPLA re-authorization,
    - watch pairing,
    - re-pair,
    - replacement,
    - deletion,
    - configuration changes.
  - Do not log passwords, session tokens, Bearer tokens, OAuth tokens or TOTP secrets.


# Reliability / Operations

- [ ] Define backup and recovery procedures.
  - Identify all persistent GarminSupla data that must be backed up.
  - Document backup of configuration, administrator data and SUPLA-related state.
  - Define a restore procedure on a clean server.
  - Verify restore with a real recovery test.
  - Document what data must not be committed to Git.

- [ ] Define application upgrade and rollback procedures.
  - Document how to upgrade the backend/dashboard.
  - Document how to update the Connect IQ application.
  - Preserve persistent configuration during upgrades.
  - Define a rollback procedure for failed backend releases.
  - Document version compatibility expectations between backend and Connect IQ releases.

- [ ] Improve production observability.
  - Define useful application and security logs.
  - Add log rotation / retention guidance.
  - Keep sensitive values out of logs.
  - Verify the health endpoint is useful for production monitoring.
  - Document basic service-health checks.


# Automated Testing / CI

- [ ] Add automated backend regression tests.
  - Cover administrator authentication.
  - Cover session and CSRF validation.
  - Cover pairing lifecycle.
  - Cover multi-watch lifecycle.
  - Cover watch-token authentication.
  - Cover configuration isolation between watches.
  - Cover configuration copying.
  - Cover SUPLA-related error handling.
  - Cover watch model resolution.

- [ ] Add continuous integration.
  - Run backend tests automatically.
  - Validate Python syntax.
  - Validate repository formatting / whitespace checks.
  - Add dependency vulnerability scanning.
  - Add security-focused static analysis where useful.
  - Build representative Connect IQ targets automatically if Garmin SDK automation is practical.
  - Keep CI secrets separate from production secrets.

- [ ] Prepare a release checklist.
  - Backend tests pass.
  - Connect IQ build passes.
  - Representative simulator tests pass.
  - Required physical-device tests pass.
  - Security checks pass.
  - Version numbers are consistent.
  - `CHANGELOG.md` is updated.
  - Documentation is updated.
  - Backup / rollback considerations are reviewed.


# Documentation

- [ ] Create a complete GarminSupla installation and deployment guide.
  - Start from a clean Linux server.
  - Install Docker and Docker Compose.
  - Clone and configure GarminSupla.
  - Document every required environment variable.
  - Expand `.env.example` so it reflects the real required configuration.
  - Create the dashboard administrator account.
  - Configure persistent storage.
  - Configure SUPLA OAuth.
  - Describe SUPLA application registration.
  - Describe required OAuth redirect URLs and scopes.
  - Configure DNS.
  - Configure HTTPS certificates.
  - Configure the reverse proxy.
  - Configure router / NAT rules where required.
  - Explain the recommended secure exposure of GarminSupla to the Internet.
  - Explain the security implications of exposing port `8008` directly.
  - Configure firewall rules.
  - Configure the Garmin Connect IQ `serverUrl`.
  - Pair the first Garmin watch.
  - Add SUPLA items.
  - Verify watch actions and status updates.
  - Verify Wi-Fi Sync fallback.
  - Document backup and restore.
  - Document upgrades and rollback.
  - Add troubleshooting for common deployment, OAuth, pairing and networking problems.

- [ ] Rebuild the project README for end users and administrators.
  - Add a short project overview.
  - Describe supported functionality.
  - Add architecture overview.
  - Link the installation guide.
  - Link supported Garmin devices / compatibility matrix.
  - Document backend and Connect IQ versioning.
  - Add security considerations.
  - Add support / contact information.


# Connect IQ Store

- [ ] Prepare GarminSupla for Connect IQ Store publication.
  - Verify the final supported-device list.
  - Verify builds for all declared product targets.
  - Perform representative simulator testing.
  - Perform physical-device testing on available devices.
  - Prepare English and Polish application descriptions.
  - Prepare store screenshots and promotional graphics.
  - Verify launcher icon and application branding.
  - Prepare setup instructions for the public `serverUrl`.
  - Prepare support/contact information.
  - Prepare privacy and data-handling information where required.
  - Review the current Garmin Connect IQ Store submission requirements before submission.
  - Protect the Connect IQ developer/signing key.
  - Produce a final signed release build.
  - Submit the application for Garmin review.
  - Document the procedure for publishing later updates.
