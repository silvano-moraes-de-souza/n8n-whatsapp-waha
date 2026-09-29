"""Draw workflows/whatsapp-ai-agent.json as an SVG, using the node positions n8n saved.

    python scripts/render_workflow.py   ->  docs/workflow.svg

Solid arrows are the main data flow; dashed lines attach a model or memory to
the AI Agent. Nodes that are not connected (the spare Groq model) are grayed out.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF = json.loads((ROOT / "workflows" / "whatsapp-ai-agent.json").read_text(encoding="utf-8"))

W, H = 180, 60  # node size
PAD = 40
SCALE = 1.3  # n8n draws sub-nodes smaller; spread positions so boxes do not overlap
KIND = {  # type suffix -> (label, color)
    "webhook": ("Trigger", "#7c3aed"),
    "set": ("Transform", "#2a78d6"),
    "switch": ("Filter", "#2a78d6"),
    "agent": ("AI Agent", "#ea4b71"),
    "memoryRedisChat": ("Memory", "#dc382d"),
    "lmChatOpenRouter": ("Model", "#0f766e"),
    "lmChatGroq": ("Model (unused)", "#9ca3af"),
    "WAHA": ("WhatsApp", "#25a560"),
}

nodes = {n["name"]: n for n in WF["nodes"]}
edges, attached = [], set()
for src, outputs in WF["connections"].items():
    for kind, lists in outputs.items():
        for targets in lists:
            for t in targets or []:
                edges.append((src, t["node"], kind))
                attached |= {src, t["node"]}

xs = [n["position"][0] * SCALE for n in nodes.values()]
ys = [n["position"][1] * SCALE for n in nodes.values()]
ox, oy = PAD - min(xs), PAD - min(ys)
width, height = max(xs) - min(xs) + W + 2 * PAD, max(ys) - min(ys) + H + 2 * PAD + 30


def box(name: str) -> tuple[float, float]:
    x, y = nodes[name]["position"]
    return x * SCALE + ox, y * SCALE + oy


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}" font-family="Segoe UI, Roboto, Helvetica, Arial, sans-serif">',
    f'<rect width="{width}" height="{height}" fill="#f7f7f5"/>',
    '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
    '<path d="M0,0 L8,4 L0,8 z" fill="#6b7280"/></marker></defs>',
]
for src, dst, kind in edges:
    sx, sy = box(src)
    dx, dy = box(dst)
    if kind == "main":
        parts.append(f'<path d="M{sx + W},{sy + H / 2} C{sx + W + 30},{sy + H / 2} '
                     f'{dx - 30},{dy + H / 2} {dx},{dy + H / 2}" stroke="#6b7280" '
                     f'stroke-width="2" fill="none" marker-end="url(#a)"/>')  # fmt: skip
    else:  # model or memory plugged into the agent from below
        parts.append(f'<path d="M{sx + W / 2},{sy} C{sx + W / 2},{sy - 60} {dx + W / 2},'
                     f'{dy + H + 60} {dx + W / 2},{dy + H}" stroke="#9ca3af" stroke-width="2" '
                     f'stroke-dasharray="6 5" fill="none"/>')  # fmt: skip
for name, n in nodes.items():
    x, y = box(name)
    label, color = KIND.get(n["type"].split(".")[-1], ("Node", "#6b7280"))
    unused = name not in attached
    fill = "#f3f4f6" if unused else "#ffffff"
    parts.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="10" fill="{fill}" '
                 f'stroke="{color}" stroke-width="2"/>')  # fmt: skip
    parts.append(f'<rect x="{x}" y="{y}" width="8" height="{H}" rx="4" fill="{color}"/>')
    parts.append(f'<text x="{x + 20}" y="{y + 27}" font-size="14" font-weight="600" '
                 f'fill="{"#6b7280" if unused else "#111827"}">{escape(name)}</text>')  # fmt: skip
    parts.append(f'<text x="{x + 20}" y="{y + 48}" font-size="12" fill="{color}">{label}</text>')
parts.append(f'<text x="{PAD}" y="{height - 14}" font-size="12" fill="#6b7280">'
             "Rendered from workflows/whatsapp-ai-agent.json with the node positions saved "
             "by n8n. Solid: data flow. Dashed: model and memory attached to the agent.</text>")  # fmt: skip
parts.append("</svg>")
out = ROOT / "docs" / "workflow.svg"
out.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
print(out)
