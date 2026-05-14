"""
Visualization utilities for TwoLayerGraph.

draw_full_graph()    — full graph coloured by node type, with layer separation
draw_subgraph()      — neighbourhood around a specific node
draw_disruption()    — supply chain impact + intelligence context for one PO
"""

from __future__ import annotations

from typing import Optional

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx

from .two_layer_graph import NodeType, TwoLayerGraph

# ── Colour palette ────────────────────────────────────────────────────────────

NODE_COLORS: dict[str, str] = {
    # Layer 1 — blues / greens
    NodeType.VENDOR:              "#1565C0",   # deep blue
    NodeType.ITEM:                "#0288D1",   # sky blue
    NodeType.TRADE_AGREEMENT:     "#81D4FA",   # light sky
    NodeType.PURCHASE_ORDER_LINE: "#004D40",   # deep teal
    NodeType.SALES_ORDER:         "#2E7D32",   # forest green
    NodeType.INVENTORY:           "#66BB6A",   # medium green
    NodeType.CUSTOMER:            "#F57F17",   # amber
    # Layer 2 — reds / purples / warm
    NodeType.EPISODE:             "#E65100",   # burnt orange
    NodeType.MITIGATION_DECISION: "#BF360C",   # dark orange-red
    NodeType.FACT:                "#FDD835",   # yellow
    NodeType.REFLECTION:          "#AB47BC",   # purple
    NodeType.CONCEPT:             "#7B1FA2",   # deep purple
    NodeType.POLICY:              "#546E7A",   # blue-grey
    NodeType.GOAL:                "#795548",   # brown
    NodeType.RECOMMENDATION:      "#E91E63",   # pink
}

NODE_SIZES: dict[str, int] = {
    NodeType.VENDOR:              600,
    NodeType.ITEM:                500,
    NodeType.TRADE_AGREEMENT:     200,
    NodeType.PURCHASE_ORDER_LINE: 450,
    NodeType.SALES_ORDER:         400,
    NodeType.INVENTORY:           300,
    NodeType.CUSTOMER:            500,
    NodeType.EPISODE:             500,
    NodeType.MITIGATION_DECISION: 400,
    NodeType.FACT:                400,
    NodeType.REFLECTION:          500,
    NodeType.CONCEPT:             600,
    NodeType.POLICY:              350,
    NodeType.GOAL:                400,
    NodeType.RECOMMENDATION:      500,
}

EDGE_COLORS: dict[str, str] = {
    # Layer 1
    "supplies":              "#1565C0",
    "delivers":              "#0288D1",
    "alternate_for":         "#F44336",
    "substitutes_for":       "#FF9800",
    "stocked_at":            "#66BB6A",
    "allocated_to":          "#2E7D32",
    "pegged_to":             "#004D40",
    "has_trade_agreement":   "#81D4FA",
    # Layer 2
    "NEXT":                  "#E65100",
    "DERIVED_FROM":          "#FDD835",
    "DERIVED_FROM_FACT":     "#AB47BC",
    "HAS_CONCEPT":           "#7B1FA2",
    "ABOUT_CONCEPT":         "#9C27B0",
    "GOVERNED_BY":           "#546E7A",
    "SCORED_AGAINST":        "#795548",
    "SUPPORTED_BY":          "#E91E63",
    # Cross-layer
    "CONCERNS":              "#FF5722",
    "CHARACTERIZES":         "#FF7043",
    "TARGETS":               "#BF360C",
    "RESOLVED":              "#004D40",
}


def _node_color(node_type: str) -> str:
    return NODE_COLORS.get(node_type, "#9E9E9E")


def _node_size(node_type: str) -> int:
    return NODE_SIZES.get(node_type, 300)


def _edge_color(edge_type: str) -> str:
    return EDGE_COLORS.get(edge_type, "#BDBDBD")


def _short_label(nid: str, data: dict, max_len: int = 18) -> str:
    """Extract a readable label from a node id / attributes."""
    nt = data.get("node_type", "")
    if nt == NodeType.VENDOR:
        return f"V{data.get('vendor_id')}\n{data.get('name','')[:12]}"
    if nt == NodeType.ITEM:
        return data.get("item_id", nid)[-14:]
    if nt == NodeType.TRADE_AGREEMENT:
        return f"TA\n{data.get('vendor_id')}→{data.get('item_id','')[-8:]}"
    if nt == NodeType.PURCHASE_ORDER_LINE:
        return data.get("po_id", nid)
    if nt == NodeType.SALES_ORDER:
        return data.get("so_id", nid)
    if nt == NodeType.INVENTORY:
        return f"INV\n{data.get('item_id','')[-10:]}"
    if nt == NodeType.CUSTOMER:
        return data.get("customer_id", nid)
    if nt == NodeType.EPISODE:
        return data.get("ep_id", nid)
    if nt == NodeType.MITIGATION_DECISION:
        return data.get("dec_id", nid)
    if nt == NodeType.FACT:
        body = data.get("body", "")
        return "F: " + body[:20] + "…"
    if nt == NodeType.REFLECTION:
        return "REF\n" + data.get("ref_id", nid)
    if nt == NodeType.CONCEPT:
        return data.get("label", nid)
    if nt == NodeType.POLICY:
        return "POL\n" + data.get("name", nid)[:14]
    if nt == NodeType.GOAL:
        return "GOAL\n" + data.get("name", nid)[:14]
    if nt == NodeType.RECOMMENDATION:
        return "REC\n" + data.get("rec_id", nid)
    return nid[-max_len:]


def draw_full_graph(
    g: TwoLayerGraph,
    figsize: tuple[int, int] = (28, 20),
    title: str = "DMA Two-Layer Supply Chain Intelligence Network",
    show_trade_agreements: bool = False,
    save_path: Optional[str] = None,
) -> None:
    """
    Render the full two-layer graph.

    Layer 1 nodes are positioned in the lower half; Layer 2 in the upper half.
    Cross-layer edges are drawn as dashed red lines.

    Args:
        show_trade_agreements: include TradeAgreement nodes (adds visual clutter).
        save_path: if provided, save PNG instead of showing interactively.
    """
    base_G = g.G
    if not show_trade_agreements:
        keep = {n for n, d in base_G.nodes(data=True) if d.get("node_type") != NodeType.TRADE_AGREEMENT}
        G = base_G.subgraph(keep)
    else:
        G = base_G

    # Position: layer 1 at y ∈ [0, 1], layer 2 at y ∈ [2, 3]
    pos: dict = {}
    l1_nodes = [n for n, d in G.nodes(data=True) if d.get("layer") == 1]
    l2_nodes = [n for n, d in G.nodes(data=True) if d.get("layer") == 2]

    # Spread within each layer using spring layout on the subgraph
    if l1_nodes:
        sub1 = G.subgraph(l1_nodes)
        p1 = nx.spring_layout(sub1, seed=42, k=2.5)
        for n, (x, y) in p1.items():
            pos[n] = (x * 4, y)          # scale x; y stays in [-1, 1]

    if l2_nodes:
        sub2 = G.subgraph(l2_nodes)
        p2 = nx.spring_layout(sub2, seed=99, k=2.5)
        for n, (x, y) in p2.items():
            pos[n] = (x * 4, y + 3.5)    # lift layer 2 above layer 1

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("#1A1A2E")
    fig.patch.set_facecolor("#1A1A2E")

    # Draw layer boundary band
    ax.axhspan(1.8, 2.2, color="#FFFFFF", alpha=0.04, zorder=0)
    ax.text(
        0, 2.0,
        "── LAYER BOUNDARY ── Cross-layer edges below",
        color="#AAAAAA", fontsize=7, ha="center", va="center",
    )

    # Draw edges, grouped by cross-layer vs intra-layer
    for src, dst, data in G.edges(data=True):
        if src not in pos or dst not in pos:
            continue
        etype = data.get("type", "")
        s_layer = G.nodes[src].get("layer")
        d_layer = G.nodes[dst].get("layer")
        cross = s_layer != d_layer
        color = _edge_color(etype)
        style = "dashed" if cross else "solid"
        width = 1.4 if cross else 0.9
        alpha = 0.7 if cross else 0.55
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(src, dst)],
            ax=ax,
            edge_color=color,
            style=style,
            width=width,
            alpha=alpha,
            arrows=True,
            arrowsize=10,
            connectionstyle="arc3,rad=0.08",
        )

    # Draw nodes
    for n, data in G.nodes(data=True):
        if n not in pos:
            continue
        nt = data.get("node_type", "")
        color = _node_color(nt)
        size = _node_size(nt)
        nx.draw_networkx_nodes(
            G, pos, nodelist=[n], ax=ax,
            node_color=color, node_size=size, alpha=0.92,
        )

    # Labels
    labels = {n: _short_label(n, d) for n, d in G.nodes(data=True) if n in pos}
    nx.draw_networkx_labels(
        G, pos, labels=labels, ax=ax,
        font_size=5.5, font_color="white", font_weight="normal",
    )

    # Layer annotations
    ax.text(-6, 0.5, "LAYER 1\nSupply Chain Network",
            color="#4FC3F7", fontsize=10, fontweight="bold", va="center")
    ax.text(-6, 4.0, "LAYER 2\nIntelligence Layer",
            color="#CE93D8", fontsize=10, fontweight="bold", va="center")

    # Legend
    legend_items = [
        mpatches.Patch(color=_node_color(nt), label=nt)
        for nt in [
            NodeType.VENDOR, NodeType.ITEM, NodeType.PURCHASE_ORDER_LINE,
            NodeType.SALES_ORDER, NodeType.INVENTORY, NodeType.CUSTOMER,
            NodeType.EPISODE, NodeType.MITIGATION_DECISION, NodeType.FACT,
            NodeType.REFLECTION, NodeType.CONCEPT, NodeType.POLICY,
            NodeType.GOAL, NodeType.RECOMMENDATION,
        ]
    ]
    ax.legend(
        handles=legend_items,
        loc="lower right",
        fontsize=7,
        framealpha=0.3,
        facecolor="#222222",
        labelcolor="white",
        ncol=2,
    )

    ax.set_title(title, color="white", fontsize=13, pad=14)
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Saved to {save_path}")
    else:
        plt.show()


def draw_disruption(
    g: TwoLayerGraph,
    po_id: str,
    figsize: tuple[int, int] = (20, 14),
    save_path: Optional[str] = None,
) -> None:
    """
    Draw a focused subgraph for one disrupted PO, including:
      - Layer 1: vendor → PO → item → inventory → sales orders → customers
      - Layer 2: episodes + decisions + facts + reflections connected to the PO's vendor/item
    """
    G = g.G
    po_nid = f"po:{po_id}"
    if po_nid not in G:
        raise ValueError(f"PO not found in graph: {po_id}")

    # Collect relevant nodes (2-hop neighbourhood in both directions)
    relevant: set[str] = {po_nid}
    for _ in range(2):
        frontier = set()
        for n in relevant:
            frontier.update(G.predecessors(n))
            frontier.update(G.successors(n))
        relevant.update(frontier)

    # Also include all Layer 2 nodes that CONCERN or CHARACTERIZE the PO's vendor/item
    po_data = G.nodes[po_nid]
    vendor_nid = f"vendor:{po_data.get('vendor_id', '')}"
    item_nid = f"item:{po_data.get('item_id', '')}"
    for n, d in G.nodes(data=True):
        if d.get("layer") == 2:
            for _, dst, edata in G.out_edges(n, data=True):
                if dst in (vendor_nid, item_nid, po_nid):
                    relevant.add(n)
                    break

    sub = G.subgraph(relevant)

    # Layout: PO at centre, layers separated vertically
    l1 = [n for n in sub if sub.nodes[n].get("layer") == 1]
    l2 = [n for n in sub if sub.nodes[n].get("layer") == 2]
    pos: dict = {}

    if l1:
        p1 = nx.spring_layout(sub.subgraph(l1), seed=7, k=3.0)
        for n, (x, y) in p1.items():
            pos[n] = (x * 3, y)
    if l2:
        p2 = nx.spring_layout(sub.subgraph(l2), seed=13, k=3.0)
        for n, (x, y) in p2.items():
            pos[n] = (x * 3, y + 3.5)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("#1A1A2E")
    fig.patch.set_facecolor("#1A1A2E")

    for src, dst, data in sub.edges(data=True):
        if src not in pos or dst not in pos:
            continue
        etype = data.get("type", "")
        cross = sub.nodes[src].get("layer") != sub.nodes[dst].get("layer")
        nx.draw_networkx_edges(
            sub, pos, edgelist=[(src, dst)], ax=ax,
            edge_color=_edge_color(etype),
            style="dashed" if cross else "solid",
            width=1.6 if cross else 1.0,
            alpha=0.75,
            arrows=True, arrowsize=12,
            connectionstyle="arc3,rad=0.1",
        )

    for n, data in sub.nodes(data=True):
        if n not in pos:
            continue
        border = "#FFEB3B" if n == po_nid else None
        nx.draw_networkx_nodes(
            sub, pos, nodelist=[n], ax=ax,
            node_color=_node_color(data.get("node_type", "")),
            node_size=_node_size(data.get("node_type", "")) * 1.2,
            edgecolors=border or "none",
            linewidths=2.5 if border else 0,
            alpha=0.92,
        )

    labels = {n: _short_label(n, sub.nodes[n]) for n in sub.nodes() if n in pos}
    nx.draw_networkx_labels(sub, pos, labels=labels, ax=ax, font_size=6.5, font_color="white")

    ax.text(-5, 0.5, "LAYER 1", color="#4FC3F7", fontsize=10, fontweight="bold")
    ax.text(-5, 4.0, "LAYER 2", color="#CE93D8", fontsize=10, fontweight="bold")

    ax.set_title(
        f"Disruption Subgraph: PO {po_id}\n"
        f"Item: {po_data.get('item_id')}  |  Vendor: {po_data.get('vendor_id')}  |  "
        f"Qty: {po_data.get('ordered_qty')} @ ${po_data.get('purchase_price')}/unit",
        color="white", fontsize=11, pad=12,
    )
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Saved to {save_path}")
    else:
        plt.show()


def draw_subgraph(
    g: TwoLayerGraph,
    node_id: str,
    hops: int = 2,
    figsize: tuple[int, int] = (16, 10),
    save_path: Optional[str] = None,
) -> None:
    """
    Draw a neighbourhood subgraph centred on node_id with radius `hops`.
    """
    G = g.G
    if node_id not in G:
        raise ValueError(f"Node not found: {node_id}")

    relevant: set[str] = {node_id}
    for _ in range(hops):
        frontier: set[str] = set()
        for n in relevant:
            frontier.update(G.predecessors(n))
            frontier.update(G.successors(n))
        relevant.update(frontier)

    sub = G.subgraph(relevant)
    pos = nx.spring_layout(sub, seed=42, k=2.5)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("#1A1A2E")
    fig.patch.set_facecolor("#1A1A2E")

    for src, dst, data in sub.edges(data=True):
        cross = sub.nodes[src].get("layer") != sub.nodes[dst].get("layer")
        nx.draw_networkx_edges(
            sub, pos, edgelist=[(src, dst)], ax=ax,
            edge_color=_edge_color(data.get("type", "")),
            style="dashed" if cross else "solid",
            width=1.4, alpha=0.65,
            arrows=True, arrowsize=12,
            connectionstyle="arc3,rad=0.1",
        )

    for n, data in sub.nodes(data=True):
        nx.draw_networkx_nodes(
            sub, pos, nodelist=[n], ax=ax,
            node_color=_node_color(data.get("node_type", "")),
            node_size=_node_size(data.get("node_type", "")) * (1.6 if n == node_id else 1.0),
            edgecolors="#FFEB3B" if n == node_id else "none",
            linewidths=3 if n == node_id else 0,
            alpha=0.92,
        )

    labels = {n: _short_label(n, sub.nodes[n]) for n in sub.nodes()}
    nx.draw_networkx_labels(sub, pos, labels=labels, ax=ax, font_size=7, font_color="white")

    ax.set_title(f"{hops}-hop neighbourhood of  {node_id}", color="white", fontsize=12, pad=12)
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Saved to {save_path}")
    else:
        plt.show()
