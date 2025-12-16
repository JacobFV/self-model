"""
vfs-grafana - Grafana Virtual Filesystem

Projects Grafana dashboards, panels, datasources, and alerts onto a filesystem structure.

## Filesystem Structure

```
/grafana/
├── .info.json                          # Grafana instance info
├── .health.json                        # Health check
│
├── dashboards/
│   ├── .dashboards.json                # All dashboards summary
│   └── {uid}/
│       ├── .dashboard.json             # Full dashboard JSON (writable)
│       ├── title.txt                   # Dashboard title
│       ├── description.md
│       ├── tags.json                   # Tags list
│       ├── folder.txt                  # Parent folder
│       ├── version.txt                 # Current version
│       ├── versions/                   # Version history
│       │   └── {version}.json
│       ├── permissions.json
│       │
│       ├── panels/
│       │   └── {panel-id}/
│       │       ├── .panel.json         # Panel config (writable)
│       │       ├── title.txt
│       │       ├── type.txt            # graph, stat, table, etc.
│       │       ├── datasource.txt
│       │       └── queries/
│       │           └── {query-id}.json
│       │
│       ├── variables/
│       │   └── {var-name}/
│       │       ├── .variable.json
│       │       ├── current.txt         # Current value
│       │       └── options.json        # Available options
│       │
│       ├── annotations/
│       │   └── {id}.json
│       │
│       └── links/
│           └── {id}.json
│
├── folders/
│   └── {uid}/
│       ├── .folder.json
│       ├── title.txt
│       ├── permissions.json
│       └── dashboards/                 # Dashboards in this folder
│           └── {uid} -> ../../dashboards/{uid}
│
├── datasources/
│   └── {uid}/
│       ├── .datasource.json            # Full datasource config
│       ├── name.txt
│       ├── type.txt                    # prometheus, elasticsearch, etc.
│       ├── url.txt
│       ├── access.txt                  # proxy/direct
│       ├── health.json                 # Health check result
│       └── query/                      # Query datasource
│           └── new.json                # Write query here
│
├── alerts/
│   ├── rules/
│   │   └── {uid}/
│   │       ├── .rule.json              # Alert rule config
│   │       ├── title.txt
│   │       ├── condition.json
│   │       ├── folder.txt
│   │       ├── state.txt               # OK/Alerting/NoData/Error
│   │       └── annotations.json
│   │
│   ├── instances/                      # Active alert instances
│   │   └── {fingerprint}/
│   │       ├── .alert.json
│   │       ├── state.txt
│   │       ├── labels.json
│   │       └── value.txt
│   │
│   ├── notifications/
│   │   └── {uid}/
│   │       ├── .notification.json
│   │       └── type.txt
│   │
│   └── silences/
│       └── {id}/
│           ├── .silence.json
│           ├── matchers.json
│           ├── starts.txt
│           └── ends.txt
│
├── users/
│   └── {id}/
│       ├── .user.json
│       ├── login.txt
│       ├── email.txt
│       └── role.txt
│
├── teams/
│   └── {id}/
│       ├── .team.json
│       ├── name.txt
│       └── members/
│           └── {user-id} -> ../../users/{id}
│
├── orgs/
│   └── {id}/
│       ├── .org.json
│       └── name.txt
│
├── plugins/
│   └── {id}/
│       ├── .plugin.json
│       ├── name.txt
│       ├── type.txt
│       └── enabled.txt
│
├── library/                            # Library panels
│   └── {uid}/
│       ├── .panel.json
│       └── name.txt
│
└── snapshots/
    └── {key}/
        ├── .snapshot.json
        └── dashboard.json
```

## Capabilities

- READ: Browse dashboards, datasources, alerts
- WRITE: Update dashboards, panels
- CREATE: Create dashboards, alerts
- DELETE: Delete dashboards, alerts

## Configuration

```python
GrafanaVFS(
    url="http://localhost:3000",
    api_key="...",              # Service account token
    # Or basic auth
    username=None,
    password=None,
    # Options
    cache_ttl=300,
    org_id=1,                   # Organization ID
)
```
"""

from .provider import GrafanaVFS
from .types import GrafanaDashboard, GrafanaPanel, GrafanaDatasource, GrafanaAlert

__all__ = ["GrafanaVFS", "GrafanaDashboard", "GrafanaPanel", "GrafanaDatasource", "GrafanaAlert"]
__version__ = "0.1.0"

Provider = GrafanaVFS


def get_provider_class():
    return GrafanaVFS


def register(registry):
    registry.register(
        name="grafana",
        provider_class=GrafanaVFS,
        description="Grafana dashboards, panels, datasources, alerts",
        required_config=["url", "api_key"],
        optional_config=["cache_ttl", "org_id"],
    )
