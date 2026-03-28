# JSON Schemas

This document defines the JSON schemas used by the evaluation and benchmarking system.

---

## evals.json

Defines the evals for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths
- `evals[].expectations`: List of verifiable statements

---

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {"text": "The output includes X", "passed": true, "evidence": "Found in output..."}
  ],
  "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67},
  "execution_metrics": {
    "tool_calls": {"Read": 5, "Write": 2, "Bash": 8},
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "total_duration_seconds": 191.0
  },
  "claims": [{"claim": "...", "type": "factual", "verified": true, "evidence": "..."}],
  "eval_feedback": {
    "suggestions": [{"assertion": "...", "reason": "..."}],
    "overall": "..."
  }
}
```

---

## timing.json

Wall clock timing for a run. Located at `<run-dir>/timing.json`.

**How to capture:** When a subagent task completes, the task notification includes `total_tokens` and `duration_ms`. Save these immediately.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

---

## benchmark.json

Output from benchmarking. Located at `benchmarks/<timestamp>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "example",
    "skill_path": "/path/to/skill",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "descriptive-name",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800
      },
      "expectations": [{"text": "...", "passed": true, "evidence": "..."}]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05},
      "time_seconds": {"mean": 45.0, "stddev": 12.0},
      "tokens": {"mean": 3800, "stddev": 400}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08},
      "time_seconds": {"mean": 32.0, "stddev": 8.0},
      "tokens": {"mean": 2100, "stddev": 300}
    },
    "delta": {"pass_rate": "+0.50", "time_seconds": "+13.0", "tokens": "+1700"}
  },
  "notes": ["Analyst observations..."]
}
```

**Important:** `configuration` must be exactly `"with_skill"` or `"without_skill"` — the viewer uses these for grouping and color coding.

---

## comparison.json

Output from blind comparator. Located at `<grading-dir>/comparison.json`.

```json
{
  "winner": "A",
  "reasoning": "...",
  "rubric": {
    "A": {"content_score": 4.7, "structure_score": 4.3, "overall_score": 9.0},
    "B": {"content_score": 2.7, "structure_score": 2.7, "overall_score": 5.4}
  },
  "output_quality": {
    "A": {"score": 9, "strengths": [...], "weaknesses": [...]},
    "B": {"score": 5, "strengths": [...], "weaknesses": [...]}
  }
}
```
