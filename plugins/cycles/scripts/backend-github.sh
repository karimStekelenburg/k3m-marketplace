#!/usr/bin/env bash
# GitHub backend for k3m-cycles.
# Uses GitHub Issues, Projects, and comments for all state.
#
# Conventions:
#   - Milestones = issues with "milestone" label
#   - Specs = issue comment with <!-- k3m:spec --> marker
#   - Plans = issue comment with <!-- k3m:plan --> marker
#   - Tracker = issue comment with <!-- k3m:tracker --> marker (YAML in code fence)
#   - State = labels on the issue (specced, planned, tracked, implementing, etc.)
#
# Requires: gh CLI authenticated, GITHUB_REPOSITORY set
#
# Usage: source this file, then call k3m_* functions

set -euo pipefail

_gh_repo() {
  echo "${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q '.nameWithOwner')}"
}

_gh_owner() {
  _gh_repo | cut -d/ -f1
}

_gh_name() {
  _gh_repo | cut -d/ -f2
}

# Find the issue number for a milestone version
_gh_issue_for_version() {
  local version="$1"
  gh issue list --repo "$(_gh_repo)" --label milestone --json number,title --jq ".[] | select(.title | test(\"$version\")) | .number" | head -1
}

# Read a marked comment from an issue
_gh_read_marked_comment() {
  local issue="$1" marker="$2"
  gh api "repos/$(_gh_repo)/issues/${issue}/comments" --jq ".[] | select(.body | contains(\"<!-- k3m:${marker} -->\")) | .body" | head -1
}

# Write or update a marked comment on an issue
_gh_write_marked_comment() {
  local issue="$1" marker="$2" content="$3"
  local body="<!-- k3m:${marker} -->\n${content}"

  # Check if comment already exists
  local existing_id
  existing_id=$(gh api "repos/$(_gh_repo)/issues/${issue}/comments" --jq ".[] | select(.body | contains(\"<!-- k3m:${marker} -->\")) | .id" | head -1)

  if [[ -n "$existing_id" ]]; then
    gh api "repos/$(_gh_repo)/issues/comments/${existing_id}" -X PATCH -f body="$body" >/dev/null
  else
    gh issue comment "$issue" --repo "$(_gh_repo)" --body "$body" >/dev/null
  fi
}

# Set state label on an issue (removes old state labels first)
_gh_set_state_label() {
  local issue="$1" new_state="$2"
  local state_labels="specced planned tracked implementing reviewing testing verified complete retro-done"

  for label in $state_labels; do
    gh issue edit "$issue" --repo "$(_gh_repo)" --remove-label "$label" 2>/dev/null || true
  done

  gh issue edit "$issue" --repo "$(_gh_repo)" --add-label "$new_state" 2>/dev/null || true
}

k3m_read_roadmap() {
  # In GitHub mode, roadmap is still a file in the repo
  if [[ -f docs/ROADMAP.md ]]; then
    cat docs/ROADMAP.md
  else
    gh api "repos/$(_gh_repo)/contents/docs/ROADMAP.md" --jq '.content' | base64 -d 2>/dev/null || echo ""
  fi
}

k3m_read_spec() {
  local ref="$1"
  local issue
  issue=$(_gh_issue_for_version "$ref")
  if [[ -n "$issue" ]]; then
    _gh_read_marked_comment "$issue" "spec"
  fi
}

k3m_write_spec() {
  local ref="$1" content_file="$2"
  local issue
  issue=$(_gh_issue_for_version "$ref")
  if [[ -n "$issue" ]]; then
    _gh_write_marked_comment "$issue" "spec" "$(cat "$content_file")"
    _gh_set_state_label "$issue" "specced"
    echo "issue#${issue}:spec"
  fi
}

k3m_read_plan() {
  local ref="$1"
  local issue
  issue=$(_gh_issue_for_version "$ref")
  if [[ -n "$issue" ]]; then
    _gh_read_marked_comment "$issue" "plan"
  fi
}

k3m_write_plan() {
  local ref="$1" content_file="$2"
  local issue
  issue=$(_gh_issue_for_version "$ref")
  if [[ -n "$issue" ]]; then
    _gh_write_marked_comment "$issue" "plan" "$(cat "$content_file")"
    _gh_set_state_label "$issue" "planned"
    echo "issue#${issue}:plan"
  fi
}

k3m_read_tracker() {
  local ref="$1"
  local issue
  issue=$(_gh_issue_for_version "$ref")
  if [[ -n "$issue" ]]; then
    local comment
    comment=$(_gh_read_marked_comment "$issue" "tracker")
    # Extract YAML from code fence
    echo "$comment" | sed -n '/^```yaml/,/^```/p' | sed '1d;$d'
  fi
}

k3m_write_tracker() {
  local ref="$1" content_file="$2"
  local issue
  issue=$(_gh_issue_for_version "$ref")
  if [[ -n "$issue" ]]; then
    local body
    body=$(printf '```yaml\n%s\n```' "$(cat "$content_file")")
    _gh_write_marked_comment "$issue" "tracker" "$body"
    echo "issue#${issue}:tracker"
  fi
}

k3m_tracker_path() {
  local ref="$1"
  # In GitHub mode, also check filesystem (CI checks out the repo)
  find docs/tracking/ -name "${ref}*" -name "*.yaml" 2>/dev/null | head -1
}

k3m_latest_tracker() {
  # Check filesystem first (CI has the repo checked out)
  ls -t docs/tracking/*.yaml 2>/dev/null | head -1
}

k3m_list_milestones() {
  gh issue list --repo "$(_gh_repo)" --label milestone --json number,title,labels --jq '.[] | .title' | while read -r title; do
    local version name
    version=$(echo "$title" | grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?')
    name=$(echo "$title" | sed 's/^v[0-9.]* — //')
    local issue_num
    issue_num=$(_gh_issue_for_version "$version")

    local state
    state=$(k3m_current_state_gh "$issue_num" 2>/dev/null || echo "unspecified")
    echo "${version}|${name}|${state}"
  done
}

k3m_claim_milestone() {
  local version="$1"
  local issue
  issue=$(_gh_issue_for_version "$version")
  if [[ -n "$issue" ]]; then
    _gh_set_state_label "$issue" "implementing"
    # Also commit filesystem artifacts if they exist
    git add docs/specs/ docs/plans/ docs/tracking/ 2>/dev/null || true
    git commit -m "chore: claim ${version} — spec, plan, tracker (in progress)" 2>/dev/null || true
    git push 2>/dev/null || true
  fi
}
