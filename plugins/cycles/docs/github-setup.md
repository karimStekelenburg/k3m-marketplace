# k3m-cycles — GitHub Setup Guide

Complete setup for the GitHub backend: repository, workflows, project board, issues, and secrets.

---

## 1. Repository Settings

### Permissions
1. Go to **Settings → Actions → General**
2. Set **Workflow permissions** → **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**

### Secrets
Add these repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Description |
|--------|-------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code OAuth token for the Action |
| `PROJECT_PAT` | Classic PAT with `repo` + `project` scopes (needed for project board API) |

**Creating the Classic PAT:**
1. Go to **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Select scopes: `repo` (full), `project` (full)
3. Generate and add as `PROJECT_PAT` secret

---

## 2. Labels

Create these labels on the repository:

### Trigger label
| Label | Color | Purpose |
|-------|-------|---------|
| `/cycle` | `#0E8A16` | Adding this label triggers the Claude Cycle workflow |

### State machine labels (auto-managed)
| Label | Color | Purpose |
|-------|-------|---------|
| `milestone` | `#0E8A16` | Marks issues as roadmap milestones |
| `specced` | `#C2E0C6` | Spec has been written |
| `planned` | `#C2E0C6` | Plan has been written |
| `tracked` | `#C2E0C6` | Tracker initialized |
| `implementing` | `#FBCA04` | Implementation in progress |
| `reviewing` | `#FBCA04` | Code review in progress |
| `testing` | `#FBCA04` | Tests/verification running |
| `verified` | `#0075CA` | All tasks verified |
| `complete` | `#0075CA` | PR created |
| `retro-done` | `#0075CA` | Retrospective completed |

Create them:
```bash
gh label create "/cycle" --color "0E8A16" --description "Trigger Claude Cycle"
gh label create "specced" --color "C2E0C6"
gh label create "planned" --color "C2E0C6"
gh label create "tracked" --color "C2E0C6"
gh label create "implementing" --color "FBCA04"
gh label create "reviewing" --color "FBCA04"
gh label create "testing" --color "FBCA04"
gh label create "verified" --color "0075CA"
gh label create "complete" --color "0075CA"
gh label create "retro-done" --color "0075CA"
```

---

## 3. GitHub Project Board

### Create or configure
The project board should have these columns (Status field options):

| Column | Purpose |
|--------|---------|
| **Todo** | Not started |
| **In Progress** | Being worked on by Claude |
| **Review** | PR opened, awaiting review |
| **Done** | PR merged, issue closed |

### Automation
The project board updates are handled by the `project-sync.yml` workflow:
- PR opened → issue moves to "Review"
- PR merged → issue moves to "Done" + closed

**Note:** `projects_v2_item` events (drag-to-trigger) are NOT supported for user-owned projects — only organization projects. Use the `/cycle` label on the issue instead.

### Project IDs
Update these values in `project-sync.yml` if using a different project:
- `PROJECT_ID` — from `gh project list --owner <owner> --format json`
- `STATUS_FIELD_ID` — from `gh project field-list <number> --owner <owner> --format json`
- Status option IDs (Review, Done) — from the same field-list output

---

## 4. Workflow Files

### `claude-cycle.yml` — Main automation
- **Trigger:** `/cycle` label added to an issue
- **Behavior:** Removes the label, runs `/cycle <version>`, creates PR
- Copy from `k3m-cycles/workflows/claude-cycle.yml`

### `project-sync.yml` — Board sync
- **Trigger:** PR opened or merged
- **Behavior:** Moves linked issues on the project board, closes on merge
- Uses `PROJECT_PAT` for GraphQL project mutations
- Copy from `k3m-cycles/workflows/project-sync.yml`

### `claude.yml` — Ad-hoc @claude mentions
- **Trigger:** Issue/PR comments containing `@claude`
- Separate from the cycle workflow

---

## 5. Milestone Issues

Each roadmap milestone should be a GitHub issue with:
- Title: `v{X.Y.0} — {Milestone Name}`
- Label: `milestone`
- Body: Deliverables, acceptance criteria, dependencies
- Sub-issues: Use GitHub sub-issues to express the dependency graph

### Dependency Graph via Sub-Issues
```
#16 v0.1.0 (root — start here)
├── #17 v0.2.0
│   └── #18 v0.3.0
└── #5 v0.4.0
    └── #6 v0.5.0
        └── #7 v0.6.0
            └── #8 v1.0.0
                └── #9-#14 v2.x (parallel)
```

---

## 6. Usage

### Starting a cycle
Add the `/cycle` label to a milestone issue. The workflow:
1. Removes the `/cycle` label immediately
2. Detects `K3M_BACKEND=github` (CI environment)
3. Runs all 9 phases automatically
4. Creates a PR referencing `Closes #N`
5. The `project-sync.yml` workflow moves the issue to "Review"

### Manual trigger
```bash
gh workflow run claude-cycle.yml -f issue_number=16
```

### Checking status
Look at:
- Issue labels for current state (`implementing`, `testing`, etc.)
- Issue comments for spec/plan/tracker content
- The Actions tab for workflow run logs

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow doesn't trigger | Check the label is exactly `/cycle`, not `in-progress` |
| Permission denied on project board | Verify `PROJECT_PAT` has `repo` + `project` scopes |
| "Workflow file issue" error | `projects_v2_item` trigger is org-only — remove it |
| Claude gets permission denials | Add tools to `.claude/settings.json` permissions.allow |
| State label not updating | Check `PROJECT_PAT` secret exists and is not expired |
