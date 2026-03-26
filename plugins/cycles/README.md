# k3m-cycles

Full spec implementation cycles with filesystem and GitHub backends. Orchestrates spec → plan → track → implement → review → test → verify → retro.

## Commands

| Command | Description |
|---------|-------------|
| `/cycle [ref]` | Run full implementation cycle |
| `/spec [ref]` | Generate technical specification |
| `/plan [ref]` | Generate implementation plan |
| `/spec-tracker` | Initialize/update task tracker |
| `/spec-status` | Display tracker status |
| `/roadmap` | Manage project roadmap |
| `/retro` | Post-cycle retrospective |

## Backends

- **Filesystem** (`K3M_BACKEND=fs`): Reads/writes `docs/specs/`, `docs/plans/`, `docs/tracking/`
- **GitHub** (`K3M_BACKEND=github`): Issues as milestones, comments for specs/plans/trackers, labels for state

Backend is auto-detected: GitHub Actions → `github`, otherwise → `fs`.

## State Machine

```
unspecified → specced → planned → tracked → implementing → reviewing → testing → verified → complete → retro-done
```

Every transition is validated. Invalid transitions are blocked.

## Setup

- **Local:** Install the plugin. Works out of the box with filesystem backend.
- **GitHub CI:** See [docs/github-setup.md](docs/github-setup.md) for full setup instructions.

## Agents

| Agent | Phase | Purpose |
|-------|-------|---------|
| `code-reviewer` | 4 | Review implementation against spec |
| `test-writer` | 5 | Write and run bun:test tests |
| `verification-gate` | 5 | Independent verification with proof |
| `ui-verifier` | 5 | Visual/interactive verification |
