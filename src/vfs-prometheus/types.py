"""Type definitions for Prometheus VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class PromTarget:
    """Represents a Prometheus scrape target."""

    job: str
    instance: str
    health: str  # up, down
    labels: dict[str, str] = field(default_factory=dict)
    last_scrape: datetime | None = None
    scrape_duration: float = 0.0  # seconds
    last_error: str = ""
    discovered_labels: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "job": self.job,
            "instance": self.instance,
            "health": self.health,
            "labels": self.labels,
            "lastScrape": self.last_scrape.isoformat() if self.last_scrape else None,
            "scrapeDuration": self.scrape_duration,
            "lastError": self.last_error,
            "discoveredLabels": self.discovered_labels,
        }, indent=2)


@dataclass
class PromMetric:
    """Represents a Prometheus metric."""

    name: str
    metric_type: str  # counter, gauge, histogram, summary
    help_text: str = ""
    unit: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "type": self.metric_type,
            "help": self.help_text,
            "unit": self.unit,
        }, indent=2)


@dataclass
class PromSeries:
    """Represents a Prometheus time series."""

    metric: str
    labels: dict[str, str] = field(default_factory=dict)
    values: list[tuple[float, str]] = field(default_factory=list)  # [(timestamp, value), ...]

    def to_json(self) -> str:
        return json.dumps({
            "metric": self.metric,
            "labels": self.labels,
            "values": [[ts, val] for ts, val in self.values],
        }, indent=2)


@dataclass
class PromRule:
    """Represents a Prometheus recording or alerting rule."""

    name: str
    rule_type: str  # recording, alerting
    group: str
    expr: str
    interval: str = ""
    for_duration: str = ""  # for alerting rules
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    health: str = "ok"  # ok, err, unknown
    last_evaluation: datetime | None = None
    evaluation_time: float = 0.0  # seconds

    def to_json(self) -> str:
        rule_obj = {
            "name": self.name,
            "type": self.rule_type,
            "group": self.group,
            "query": self.expr,
            "labels": self.labels,
            "health": self.health,
            "lastEvaluation": self.last_evaluation.isoformat() if self.last_evaluation else None,
            "evaluationTime": self.evaluation_time,
        }
        if self.rule_type == "alerting":
            rule_obj["for"] = self.for_duration
            rule_obj["annotations"] = self.annotations
        return json.dumps(rule_obj, indent=2)


@dataclass
class PromAlert:
    """Represents a Prometheus alert instance."""

    name: str
    state: str  # firing, pending, inactive
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    value: str = ""
    active_at: datetime | None = None
    fired_at: datetime | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "state": self.state,
            "labels": self.labels,
            "annotations": self.annotations,
            "value": self.value,
            "activeAt": self.active_at.isoformat() if self.active_at else None,
            "firedAt": self.fired_at.isoformat() if self.fired_at else None,
        }, indent=2)


@dataclass
class PromQuery:
    """Represents a PromQL query."""

    query: str
    time: datetime | None = None  # for instant query
    start: datetime | None = None  # for range query
    end: datetime | None = None
    step: str = "1m"  # for range query

    def to_json(self) -> str:
        if self.time:
            # Instant query
            return json.dumps({
                "query": self.query,
                "time": self.time.isoformat(),
            }, indent=2)
        else:
            # Range query
            return json.dumps({
                "query": self.query,
                "start": self.start.isoformat() if self.start else None,
                "end": self.end.isoformat() if self.end else None,
                "step": self.step,
            }, indent=2)
