# Undocumented but Verified Claude Code Features

Features confirmed to exist (via settings schema, source code, or reliable demonstration)
but not present in the official docs at https://code.claude.com/docs/en/.

Last verified: 2026-03-29

## Settings (settings.json)

### `skipDangerousModePermissionPrompt`

- **Type:** `boolean`
- **Purpose:** Suppresses the one-time warning dialog when activating `--dangerously-skip-permissions` (bypass permissions mode)
- **Source:** Settings JSON schema (`"Whether the user has accepted the bypass permissions mode dialog"`)
- **Notes:** Normally set automatically after the user accepts the dialog once. Can be pre-set to `true` to skip the dialog entirely.

### `skipAutoPermissionPrompt`

- **Type:** `boolean`
- **Purpose:** Suppresses the one-time opt-in dialog when activating auto mode
- **Source:** Settings JSON schema (`"Whether the user has accepted the auto mode opt-in dialog"`)
- **Notes:** Same pattern as above — normally set by the UI after first acceptance.

## Telemetry Opt-Out (env vars)

The official docs document these as environment variables, but a popular YouTube video
("12 Hidden Settings", AI LABS, 2026-03-25) incorrectly presents them as `settings.json`
keys (`disableTelemetry`, `disableErrorReporting`, `disableFeedbackDisplay`).

The **correct** mechanism is env vars (which CAN be set via `settings.json` under `"env"`):

```json
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "DISABLE_FEEDBACK_COMMAND": "1"
  }
}
```

These ARE documented in the env-vars page, so this is a correction, not an undocumented feature.
