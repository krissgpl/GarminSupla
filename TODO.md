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

- [ ] Optionally allow copying `Watch items` between already paired watches.


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

- [ ] Optionally rebuild the watch selector as responsive watch cards.
  - Display watch cards side by side on wide screens.
  - Clearly highlight the selected watch.
  - Keep responsive behavior on smaller screens.

- [ ] Optionally add a dedicated `Details` view for extended watch metadata.

# Localization

- [X] Add Polish and English support to the Connect IQ application.
  - Use English as the default fallback language.
  - Add complete Polish translations.
  - Remove hardcoded user-facing strings from the watch code.
  - Introduce a shared localization layer for application UI strings.

- [ ] Add per-watch application language modes.
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

- [ ] Rebuild the main Connect IQ UI toward a more native Garmin / Menu2 style.

- [ ] Prepare a consistent icon set for supported item types.
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

- [ ] Use AMOLED / OLED display capabilities.
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
