#!/usr/bin/env bash
# Filesystem backend for k3m-cycles.
# Reads/writes docs/specs/, docs/plans/, docs/tracking/, docs/ROADMAP.md
#
# Usage: source this file, then call k3m_* functions
#   source "$CLAUDE_PLUGIN_ROOT/scripts/backend-fs.sh"

set -euo pipefail

k3m_read_roadmap() {
  cat docs/ROADMAP.md 2>/dev/null || echo ""
}

k3m_read_spec() {
  local ref="$1"
  local file
  file=$(find docs/specs/ -name "${ref}*" -name "*.md" 2>/dev/null | head -1)
  if [[ -n "$file" ]]; then
    cat "$file"
  fi
}

k3m_spec_path() {
  local ref="$1"
  find docs/specs/ -name "${ref}*" -name "*.md" 2>/dev/null | head -1
}

k3m_write_spec() {
  local ref="$1" content_file="$2"
  mkdir -p docs/specs
  cp "$content_file" "docs/specs/${ref}.md"
  echo "docs/specs/${ref}.md"
}

k3m_read_plan() {
  local ref="$1"
  local file
  file=$(find docs/plans/ -name "${ref}*" -name "*.md" 2>/dev/null | head -1)
  if [[ -n "$file" ]]; then
    cat "$file"
  fi
}

k3m_plan_path() {
  local ref="$1"
  find docs/plans/ -name "${ref}*" -name "*.md" 2>/dev/null | head -1
}

k3m_write_plan() {
  local ref="$1" content_file="$2"
  mkdir -p docs/plans
  cp "$content_file" "docs/plans/${ref}.md"
  echo "docs/plans/${ref}.md"
}

k3m_read_tracker() {
  local ref="$1"
  local file
  file=$(find docs/tracking/ -name "${ref}*" -name "*.yaml" 2>/dev/null | head -1)
  if [[ -n "$file" ]]; then
    cat "$file"
  fi
}

k3m_tracker_path() {
  local ref="$1"
  find docs/tracking/ -name "${ref}*" -name "*.yaml" 2>/dev/null | head -1
}

k3m_write_tracker() {
  local ref="$1" content_file="$2"
  mkdir -p docs/tracking
  cp "$content_file" "docs/tracking/${ref}.yaml"
  echo "docs/tracking/${ref}.yaml"
}

k3m_latest_tracker() {
  ls -t docs/tracking/*.yaml 2>/dev/null | head -1
}

k3m_list_milestones() {
  # Returns: version|name|status (one per line)
  # Status derived from filesystem artifacts
  local roadmap
  roadmap=$(k3m_read_roadmap)

  echo "$roadmap" | grep -E '^## v[0-9]' | while read -r line; do
    local version name
    version=$(echo "$line" | grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?')
    name=$(echo "$line" | sed 's/^## //' | sed 's/ — /|/' | cut -d'|' -f2)

    if echo "$line" | grep -qi "complete\|done\|✅"; then
      echo "${version}|${name}|complete"
    else
      source "$K3M_SCRIPTS/state-machine.sh"
      local state
      state=$(k3m_current_state_fs "$version")
      echo "${version}|${name}|${state}"
    fi
  done
}

k3m_claim_milestone() {
  local version="$1"
  git add docs/specs/ docs/plans/ docs/tracking/ 2>/dev/null || true
  git commit -m "chore: claim ${version} — spec, plan, tracker (in progress)" 2>/dev/null || true
  git push 2>/dev/null || true
}
