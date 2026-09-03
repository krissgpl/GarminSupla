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

- [ ] Improve the UI state transition after Wi-Fi Sync.
  - Avoid or reduce the short `Offline -> Cached` transition.
  - Do not change the currently working Wi-Fi fallback logic.

# Multi-watch

- [ ] Refactor the backend from a single `watch` to a collection of paired watches.
  - Each watch should have its own:
    - `id`,
    - token,
    - user-defined name,
    - device model,
    - Device ID,
    - part number,
    - firmware version,
    - Connect IQ version,
    - GarminSupla app version,
    - detected system language,
    - application language,
    - `enabled` status,
    - `created_at`,
    - `last_seen_at`,
    - independent list of `Watch items`.

- [ ] Move `Watch items` configuration to individual watches.
  - Each watch should have its own:
    - item order,
    - visibility,
    - icon,
    - confirmation setting,
    - remaining per-item settings.
  - Changing one watch configuration must not affect other watches.

- [ ] Refactor watch authentication for multi-watch support.
  - Identify the watch by its token.
  - Support multiple simultaneously valid watch tokens.
  - Adding a new watch must not invalidate existing watches.

- [ ] Refactor pairing for multiple watches.
  - Support multiple active pairing sessions.
  - Each pairing session should have its own:
    - `pairing_id`,
    - pairing code,
    - expiration time,
    - status.
  - Adding a new watch must not replace the currently paired watch.

- [ ] Add user-defined watch names.
  - Examples:
    - `Krzysztof Fenix`,
    - `Anna Watch`,
    - `Training Fenix`.
  - The user-defined name must be separate from the hardware model.
  - Add a `Rename` action.
  - Validate empty values and limit the maximum name length.

- [ ] Add the ability to copy `Watch items` configuration.
  - From an existing watch to a newly paired watch.
  - Optionally between already paired watches.

# Multi-watch Dashboard

- [ ] Rebuild the upper part of the dashboard as watch cards.
  - Display watch cards side by side on wide screens.
  - Use a responsive layout on smaller screens.
  - Each watch card should show:
    - user-defined name,
    - device model,
    - connection / activity status,
    - firmware version,
    - GarminSupla version,
    - application language,
    - `last_seen_at`.
  - Additional technical details may be available through `Details`.

- [ ] Add active watch selection in the dashboard.
  - Clicking a watch card sets `selectedWatchId`.
  - Clearly highlight the currently selected watch.
  - Show only the selected watch's `Watch items` below the watch cards.
  - Switching the selected watch should update the lower configuration section without reloading the whole page.

- [ ] Add an `Add watch` card / action.
  - Allow pairing another Garmin watch.
  - Do not disable already paired watches.

- [ ] Add watch management actions to each watch card.
  - `Rename`
  - `Repair / Re-pair`
  - `Remove`
  - `Details`
  - optionally `Refresh`

- [ ] Prepare dashboard API endpoints for multi-watch.
  - Target endpoints:
    - `GET /api/v1/setup/watches`
    - `GET /api/v1/setup/watches/{watch_id}`
    - `PATCH /api/v1/setup/watches/{watch_id}`
    - `DELETE /api/v1/setup/watches/{watch_id}`
    - `GET /api/v1/setup/watches/{watch_id}/items`
    - `PUT /api/v1/setup/watches/{watch_id}/items`

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

- [ ] Send device metadata from the Connect IQ application to the backend.
  - device model,
  - Device ID,
  - part number,
  - firmware version,
  - Connect IQ version,
  - detected system language,
  - GarminSupla app version.

- [ ] Do not label `uniqueIdentifier` as a serial number.
  - Use `Device ID` in the dashboard.
  - The Garmin hardware serial number is not exposed to Connect IQ applications.

- [ ] Update watch metadata periodically.
  - During first pairing.
  - During application startup / communication with the backend.
  - After firmware or GarminSupla version changes.

- [ ] Display watch metadata in the dashboard.
  - User-defined name.
  - Device model.
  - Device ID.
  - Part number.
  - Firmware version.
  - Connect IQ version.
  - GarminSupla version.
  - Language.
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
