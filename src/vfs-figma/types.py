"""Type definitions for Figma VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class FigmaFile:
    """Represents a Figma file."""

    key: str
    name: str
    thumbnail_url: str = ""
    version: str = ""
    last_modified: datetime = field(default_factory=datetime.now)
    editor_type: str = "figma"  # figma or figjam
    link_access: str = "view"  # inherit, view, edit
    role: str = "viewer"  # owner, editor, viewer
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "name": self.name,
            "thumbnail_url": self.thumbnail_url,
            "version": self.version,
            "last_modified": self.last_modified.isoformat(),
            "editor_type": self.editor_type,
            "link_access": self.link_access,
            "role": self.role,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }, indent=2)


@dataclass
class FigmaPage:
    """Represents a page in a Figma file."""

    id: str
    name: str
    type: str = "CANVAS"
    children: list[str] = field(default_factory=list)
    background_color: dict[str, float] = field(default_factory=dict)
    flow_starting_points: list[dict[str, Any]] = field(default_factory=list)
    guides: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "children": self.children,
            "background_color": self.background_color,
            "flow_starting_points": self.flow_starting_points,
            "guides": self.guides,
        }, indent=2)


@dataclass
class FigmaNode:
    """Represents a node in a Figma document."""

    id: str
    name: str
    type: str  # FRAME, GROUP, COMPONENT, INSTANCE, TEXT, RECTANGLE, etc.
    visible: bool = True
    locked: bool = False
    children: list[str] = field(default_factory=list)
    absolute_bounding_box: dict[str, float] = field(default_factory=dict)
    constraints: dict[str, str] = field(default_factory=dict)
    layout_mode: str | None = None
    layout_align: str | None = None
    layout_grow: float | None = None
    primary_axis_sizing_mode: str | None = None
    counter_axis_sizing_mode: str | None = None
    padding_left: float = 0.0
    padding_right: float = 0.0
    padding_top: float = 0.0
    padding_bottom: float = 0.0
    item_spacing: float = 0.0
    fills: list[dict[str, Any]] = field(default_factory=list)
    strokes: list[dict[str, Any]] = field(default_factory=list)
    stroke_weight: float = 0.0
    stroke_align: str = "INSIDE"
    corner_radius: float = 0.0
    effects: list[dict[str, Any]] = field(default_factory=list)
    opacity: float = 1.0
    blend_mode: str = "PASS_THROUGH"
    styles: dict[str, str] = field(default_factory=dict)
    export_settings: list[dict[str, Any]] = field(default_factory=list)
    component_id: str | None = None
    component_properties: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "visible": self.visible,
            "locked": self.locked,
            "children": self.children,
            "absolute_bounding_box": self.absolute_bounding_box,
            "constraints": self.constraints,
            "layout_mode": self.layout_mode,
            "layout_align": self.layout_align,
            "layout_grow": self.layout_grow,
            "primary_axis_sizing_mode": self.primary_axis_sizing_mode,
            "counter_axis_sizing_mode": self.counter_axis_sizing_mode,
            "padding_left": self.padding_left,
            "padding_right": self.padding_right,
            "padding_top": self.padding_top,
            "padding_bottom": self.padding_bottom,
            "item_spacing": self.item_spacing,
            "fills": self.fills,
            "strokes": self.strokes,
            "stroke_weight": self.stroke_weight,
            "stroke_align": self.stroke_align,
            "corner_radius": self.corner_radius,
            "effects": self.effects,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode,
            "styles": self.styles,
            "export_settings": self.export_settings,
            "component_id": self.component_id,
            "component_properties": self.component_properties,
        }, indent=2)


@dataclass
class FigmaComponent:
    """Represents a Figma component."""

    id: str
    key: str
    name: str
    description: str = ""
    containing_frame: dict[str, Any] = field(default_factory=dict)
    component_set_id: str | None = None
    component_properties: dict[str, Any] = field(default_factory=dict)
    thumbnail_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "containing_frame": self.containing_frame,
            "component_set_id": self.component_set_id,
            "component_properties": self.component_properties,
            "thumbnail_url": self.thumbnail_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }, indent=2)


@dataclass
class FigmaStyle:
    """Represents a Figma style."""

    id: str
    key: str
    name: str
    style_type: str  # FILL, TEXT, EFFECT, GRID
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "style_type": self.style_type,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }, indent=2)
