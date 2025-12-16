"""Type definitions for Elasticsearch VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class ESIndex:
    """Represents an Elasticsearch index."""

    name: str
    uuid: str
    health: str  # green, yellow, red
    status: str  # open, close
    docs_count: int = 0
    docs_deleted: int = 0
    store_size: int = 0  # bytes
    pri_shards: int = 1
    replicas: int = 1
    creation_date: datetime = field(default_factory=datetime.now)
    aliases: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "uuid": self.uuid,
            "health": self.health,
            "status": self.status,
            "docs": {
                "count": self.docs_count,
                "deleted": self.docs_deleted,
            },
            "store_size": self.store_size,
            "pri_shards": self.pri_shards,
            "replicas": self.replicas,
            "creation_date": self.creation_date.isoformat(),
            "aliases": self.aliases,
        }, indent=2)


@dataclass
class ESDocument:
    """Represents an Elasticsearch document."""

    doc_id: str
    index: str
    source: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    seq_no: int = 0
    primary_term: int = 1
    found: bool = True

    def to_json(self) -> str:
        return json.dumps({
            "_id": self.doc_id,
            "_index": self.index,
            "_version": self.version,
            "_seq_no": self.seq_no,
            "_primary_term": self.primary_term,
            "found": self.found,
            "_source": self.source,
        }, indent=2)


@dataclass
class ESMapping:
    """Represents an Elasticsearch mapping."""

    index: str
    properties: dict[str, Any] = field(default_factory=dict)
    dynamic: str | bool = "true"  # true, false, strict
    meta: dict[str, Any] = field(default_factory=dict)
    runtime: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "dynamic": self.dynamic,
            "properties": self.properties,
            "_meta": self.meta,
            "runtime": self.runtime,
        }, indent=2)


@dataclass
class ESQuery:
    """Represents an Elasticsearch query."""

    query: dict[str, Any]
    index: str
    sort: list[dict[str, Any]] = field(default_factory=list)
    size: int = 10
    from_: int = 0
    source: list[str] | bool = field(default_factory=lambda: True)
    aggs: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        query_obj = {
            "query": self.query,
            "sort": self.sort,
            "size": self.size,
            "from": self.from_,
            "_source": self.source,
        }
        if self.aggs:
            query_obj["aggs"] = self.aggs
        return json.dumps(query_obj, indent=2)


@dataclass
class ESClusterHealth:
    """Represents Elasticsearch cluster health."""

    cluster_name: str
    status: str  # green, yellow, red
    number_of_nodes: int
    number_of_data_nodes: int
    active_primary_shards: int
    active_shards: int
    relocating_shards: int
    initializing_shards: int
    unassigned_shards: int
    timed_out: bool = False

    def to_json(self) -> str:
        return json.dumps({
            "cluster_name": self.cluster_name,
            "status": self.status,
            "number_of_nodes": self.number_of_nodes,
            "number_of_data_nodes": self.number_of_data_nodes,
            "active_primary_shards": self.active_primary_shards,
            "active_shards": self.active_shards,
            "relocating_shards": self.relocating_shards,
            "initializing_shards": self.initializing_shards,
            "unassigned_shards": self.unassigned_shards,
            "timed_out": self.timed_out,
        }, indent=2)
