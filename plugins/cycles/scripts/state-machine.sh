#!/usr/bin/env bash
# k3m-cycles state machine — shared by hooks, CI workflows, and commands.
#
# States: unspecified → specced → planned → tracked → implementing →
#         reviewing → testing → verified → complete → retro-done
#
# Usage:
#   source "$CLAUDE_PLUGIN_ROOT/scripts/state-machine.sh"
#   k3m_check_transition "planned" "tracked"  # exits 0 if valid, 1 if not
#   k3m_current_state <tracker-yaml>           # prints current state
#   k3m_validate_gate <target-state>           # checks preconditions

set -euo pipefail

# Valid transitions: from → to
declare -A K3M_TRANSITIONS=(
  ["unspecified:specced"]=1
  ["specced:planned"]=1
  ["planned:tracked"]=1
  ["tracked:implementing"]=1
  ["implementing:reviewing"]=1
  ["reviewing:testing"]=1
  ["reviewing:implementing"]=1  # review rejected → back to implementing
  ["testing:verified"]=1
  ["testing:implementing"]=1    # test failed → back to implementing
  ["verified:complete"]=1
  ["complete:retro-done"]=1
)

k3m_check_transition() {
  local from="$1" to="$2"
  local key="${from}:${to}"
  if [[ -n "${K3M_TRANSITIONS[$key]:-}" ]]; then
    return 0
  else
    echo "BLOCKED: Invalid transition from '$from' to '$to'" >&2
    return 1
  fi
}

# Determine state from tracker YAML task statuses
k3m_current_state_from_tracker() {
  local tracker_file="$1"

  if [[ ! -f "$tracker_file" ]]; then
    echo "unspecified"
    return
  fi

  local pending implemented verified blocked total complete
  pending=$(grep -c 'status: pending' "$tracker_file" 2>/dev/null || echo 0)
  implemented=$(grep -c 'status: implemented' "$tracker_file" 2>/dev/null || echo 0)
  verified=$(grep -c 'status: verified' "$tracker_file" 2>/dev/null || echo 0)
  blocked=$(grep -c 'status: blocked' "$tracker_file" 2>/dev/null || echo 0)
  in_progress=$(grep -c 'status: in_progress' "$tracker_file" 2>/dev/null || echo 0)
  complete=$(grep 'complete:' "$tracker_file" | tail -1 | grep -c 'true' || echo 0)

  total=$((pending + implemented + verified + blocked + in_progress))

  if [[ "$complete" -eq 1 ]]; then
    echo "verified"
  elif [[ "$verified" -eq "$total" && "$total" -gt 0 ]]; then
    echo "verified"
  elif [[ "$implemented" -gt 0 && "$pending" -eq 0 && "$in_progress" -eq 0 ]]; then
    echo "testing"
  elif [[ "$in_progress" -gt 0 || ("$implemented" -gt 0 && "$pending" -gt 0) ]]; then
    echo "implementing"
  elif [[ "$pending" -eq "$total" && "$total" -gt 0 ]]; then
    echo "tracked"
  else
    echo "tracked"
  fi
}

# Determine state from filesystem artifacts
k3m_current_state_fs() {
  local version="$1"
  local kebab="${2:-}"

  # Check for tracker
  local tracker_file
  tracker_file=$(find docs/tracking/ -name "${version}*" -name "*.yaml" 2>/dev/null | head -1)

  if [[ -n "$tracker_file" ]]; then
    local tracker_state
    tracker_state=$(k3m_current_state_from_tracker "$tracker_file")
    echo "$tracker_state"
    return
  fi

  # Check for plan
  if ls docs/plans/${version}* 2>/dev/null | head -1 >/dev/null; then
    echo "planned"
    return
  fi

  # Check for spec
  if ls docs/specs/${version}* 2>/dev/null | head -1 >/dev/null; then
    echo "specced"
    return
  fi

  echo "unspecified"
}

# Determine state from GitHub issue
k3m_current_state_gh() {
  local issue_number="$1"

  local labels
  labels=$(gh issue view "$issue_number" --json labels --jq '.labels[].name' 2>/dev/null || echo "")

  if echo "$labels" | grep -q "retro-done"; then echo "retro-done"; return; fi
  if echo "$labels" | grep -q "complete"; then echo "complete"; return; fi
  if echo "$labels" | grep -q "verified"; then echo "verified"; return; fi
  if echo "$labels" | grep -q "testing"; then echo "testing"; return; fi
  if echo "$labels" | grep -q "reviewing"; then echo "reviewing"; return; fi
  if echo "$labels" | grep -q "implementing"; then echo "implementing"; return; fi
  if echo "$labels" | grep -q "tracked"; then echo "tracked"; return; fi
  if echo "$labels" | grep -q "planned"; then echo "planned"; return; fi
  if echo "$labels" | grep -q "specced"; then echo "specced"; return; fi

  echo "unspecified"
}

# Validate gate conditions for a target state
k3m_validate_gate() {
  local target="$1"
  local version="${2:-}"
  local backend="${K3M_BACKEND:-fs}"

  case "$target" in
    specced)
      # Gate: roadmap entry exists
      if [[ "$backend" == "fs" ]]; then
        if ! grep -q "$version" docs/ROADMAP.md 2>/dev/null; then
          echo "GATE FAILED: No roadmap entry for $version" >&2
          return 1
        fi
      fi
      ;;
    planned)
      # Gate: spec exists
      if [[ "$backend" == "fs" ]]; then
        if ! ls docs/specs/${version}* 2>/dev/null | head -1 >/dev/null; then
          echo "GATE FAILED: No spec found for $version" >&2
          return 1
        fi
      fi
      ;;
    tracked)
      # Gate: plan exists
      if [[ "$backend" == "fs" ]]; then
        if ! ls docs/plans/${version}* 2>/dev/null | head -1 >/dev/null; then
          echo "GATE FAILED: No plan found for $version" >&2
          return 1
        fi
      fi
      ;;
    implementing)
      # Gate: tracker initialized
      if [[ "$backend" == "fs" ]]; then
        if ! ls docs/tracking/${version}* 2>/dev/null | head -1 >/dev/null; then
          echo "GATE FAILED: No tracker found for $version" >&2
          return 1
        fi
      fi
      ;;
    *)
      # Other gates are checked by the cycle itself
      ;;
  esac
  return 0
}
