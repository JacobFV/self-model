"""
vfs-elasticsearch - Elasticsearch Virtual Filesystem

Projects Elasticsearch clusters, indices, and documents onto a filesystem structure.

## Filesystem Structure

```
/elasticsearch/
├── _cluster/
│   ├── health.json                     # Cluster health
│   ├── stats.json                      # Cluster stats
│   ├── settings.json                   # Cluster settings
│   ├── pending_tasks.json
│   └── nodes/
│       ├── .nodes.json                 # All nodes summary
│       └── {node-id}/
│           ├── .node.json              # Node info
│           ├── stats.json              # Node stats
│           └── hot_threads.txt
│
├── _cat/                               # CAT API equivalents
│   ├── indices.txt
│   ├── shards.txt
│   ├── nodes.txt
│   ├── allocation.txt
│   └── health.txt
│
├── _templates/
│   └── {template-name}/
│       ├── .template.json
│       └── mappings.json
│
├── _component_templates/
│   └── {name}.json
│
├── _index_templates/
│   └── {name}.json
│
├── _ilm/                               # Index Lifecycle Management
│   └── policies/
│       └── {policy}.json
│
├── _snapshots/
│   └── {repository}/
│       ├── .repository.json
│       └── {snapshot}/
│           ├── .snapshot.json
│           └── indices/
│
├── _ingest/
│   └── pipelines/
│       └── {pipeline}.json
│
├── {index}/                            # Index
│   ├── .index.json                     # Index metadata
│   ├── _settings.json                  # Index settings (writable)
│   ├── _mappings.json                  # Index mappings (writable)
│   ├── _aliases.json                   # Index aliases
│   ├── _stats.json                     # Index stats
│   ├── _segments.json                  # Segment info
│   ├── _recovery.json                  # Recovery status
│   │
│   ├── _doc/                           # Documents
│   │   ├── .count.txt                  # Document count
│   │   ├── {doc-id}.json               # Document by ID
│   │   │   # Reading returns document
│   │   │   # Writing updates/creates document
│   │   └── {doc-id}/                   # Or as directory
│   │       ├── .document.json          # Full document
│   │       ├── _source.json            # Source only
│   │       └── {field}.json            # Individual fields
│   │
│   ├── _search/                        # Search interface
│   │   ├── all.jsonl                   # Match all (paginated)
│   │   ├── query/
│   │   │   └── {query-hash}.jsonl      # Cached search results
│   │   └── new.json                    # Write search query here
│   │
│   ├── _bulk/                          # Bulk operations
│   │   └── new.ndjson                  # Write bulk request here
│   │
│   └── _analyze/                       # Analysis
│       └── {text}.json                 # Analyze text
│
├── _aliases/                           # All aliases
│   └── {alias}/
│       ├── .alias.json
│       └── indices/                    # Indices for this alias
│           └── {index} -> ../../{index}
│
└── _tasks/                             # Task management
    └── {task-id}.json
```

## Search Interface

Write query to `{index}/_search/new.json`:
```json
{
  "query": {
    "bool": {
      "must": [{"match": {"title": "elasticsearch"}}],
      "filter": [{"term": {"status": "published"}}]
    }
  },
  "sort": [{"date": "desc"}],
  "size": 100,
  "from": 0,
  "_source": ["title", "date", "author"]
}
```

Results cached at `{index}/_search/query/{hash}.jsonl`

## Capabilities

- READ: Browse indices, search documents
- WRITE: Update documents, mappings, settings
- CREATE: Create indices, index documents
- DELETE: Delete documents, indices

## Configuration

```python
ElasticsearchVFS(
    hosts=["http://localhost:9200"],
    # Authentication
    api_key=None,               # API key
    basic_auth=("user", "pass"), # Or basic auth
    # TLS
    ca_certs=None,
    verify_certs=True,
    # Options
    cache_ttl=300,
    search_size=100,            # Default search size
)
```
"""

from .provider import ElasticsearchVFS
from .types import ESIndex, ESDocument, ESMapping

__all__ = ["ElasticsearchVFS", "ESIndex", "ESDocument", "ESMapping"]
__version__ = "0.1.0"

Provider = ElasticsearchVFS


def get_provider_class():
    return ElasticsearchVFS


def register(registry):
    registry.register(
        name="elasticsearch",
        provider_class=ElasticsearchVFS,
        description="Elasticsearch indices, documents, mappings",
        required_config=["hosts"],
        optional_config=["api_key", "basic_auth", "cache_ttl"],
    )
