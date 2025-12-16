"""
vfs-prometheus - Prometheus Virtual Filesystem

Projects Prometheus targets, metrics, rules, and alerts onto a filesystem structure.

## Filesystem Structure

```
/prometheus/
├── .status.json                        # Prometheus status
├── .config.yaml                        # Current configuration
├── .flags.json                         # Command-line flags
├── .runtime.json                       # Runtime info
├── .build.json                         # Build info
│
├── targets/
│   ├── .targets.json                   # All targets summary
│   └── {job}/
│       ├── .job.json                   # Job config
│       └── {instance}/
│           ├── .target.json            # Target metadata
│           ├── health.txt              # up/down
│           ├── labels.json             # Target labels
│           ├── last_scrape.txt         # Timestamp
│           ├── scrape_duration.txt     # Duration
│           └── last_error.txt          # Last scrape error
│
├── metrics/
│   ├── .metrics.txt                    # All metric names
│   └── {metric-name}/
│       ├── .metric.json                # Metric metadata
│       │   # type, help text, unit
│       ├── type.txt                    # counter/gauge/histogram/summary
│       ├── help.txt                    # Help text
│       │
│       ├── series/                     # Time series
│       │   ├── .series.json            # All series for this metric
│       │   └── {label-hash}/
│       │       ├── .series.json        # Series metadata
│       │       ├── labels.json         # Label set
│       │       ├── current.txt         # Current value
│       │       └── range/
│       │           └── {start}-{end}.json  # Time range data
│       │
│       └── query/                      # PromQL interface
│           └── {query-hash}.json       # Cached query results
│
├── rules/
│   ├── .rules.json                     # All rule groups
│   └── {group}/
│       ├── .group.json                 # Group config
│       ├── interval.txt
│       └── {rule-name}/
│           ├── .rule.yaml              # Rule definition
│           ├── type.txt                # recording/alerting
│           ├── expr.txt                # PromQL expression
│           ├── health.txt              # ok/err/unknown
│           └── last_evaluation.txt
│
├── alerts/
│   ├── .alerts.json                    # All alerts summary
│   ├── firing/
│   │   └── {alert-name}/
│   │       └── {fingerprint}/
│   │           ├── .alert.json
│   │           ├── state.txt           # firing
│   │           ├── labels.json
│   │           ├── annotations.json
│   │           ├── active_at.txt
│   │           └── value.txt
│   ├── pending/
│   │   └── {alert-name}/
│   │       └── {fingerprint}/
│   │           └── ...
│   └── inactive/
│       └── ...
│
├── tsdb/                               # TSDB status
│   ├── .status.json
│   ├── head_stats.json
│   ├── label_names.txt
│   └── label_values/
│       └── {label}.txt                 # Values for label
│
├── query/                              # PromQL query interface
│   ├── instant/
│   │   └── {query-hash}.json           # Instant query results
│   └── range/
│       └── {query-hash}.json           # Range query results
│
├── federation/                         # Federation endpoint data
│   └── {match-hash}.txt                # Metrics matching query
│
└── api/                                # Raw API access
    └── v1/
        └── {endpoint}.json
```

## Query Interface

Instant query (write to `query/instant/new.json`):
```json
{
  "query": "up{job='prometheus'}",
  "time": "2024-01-15T10:00:00Z"
}
```

Range query (write to `query/range/new.json`):
```json
{
  "query": "rate(http_requests_total[5m])",
  "start": "2024-01-15T00:00:00Z",
  "end": "2024-01-15T10:00:00Z",
  "step": "1m"
}
```

## Capabilities

- READ: Browse targets, metrics, alerts, query data
- WRITE: (Limited) Update rules via API
- CREATE: (Limited) Create rules
- DELETE: (Limited) Delete rules

## Configuration

```python
PrometheusVFS(
    url="http://localhost:9090",
    # Authentication (if enabled)
    username=None,
    password=None,
    bearer_token=None,
    # Options
    cache_ttl=60,               # Shorter for dynamic data
    query_timeout=30,           # Query timeout seconds
)
```
"""

from .provider import PrometheusVFS
from .types import PromTarget, PromMetric, PromRule, PromAlert

__all__ = ["PrometheusVFS", "PromTarget", "PromMetric", "PromRule", "PromAlert"]
__version__ = "0.1.0"

Provider = PrometheusVFS


def get_provider_class():
    return PrometheusVFS


def register(registry):
    registry.register(
        name="prometheus",
        provider_class=PrometheusVFS,
        description="Prometheus targets, metrics, rules, alerts",
        required_config=["url"],
        optional_config=["username", "password", "bearer_token", "cache_ttl"],
    )
