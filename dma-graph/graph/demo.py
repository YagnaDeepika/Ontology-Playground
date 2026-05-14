"""
demo.py — demonstrate the DMA two-layer graph queries.

Run:
    uv run python -m thinkingbox.graph.demo
    uv run python -m thinkingbox.graph.demo --visualize
"""

from __future__ import annotations

import argparse
import textwrap
from pprint import pformat

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .dma_seed import build_dma_graph
from .two_layer_graph import NodeType

console = Console()

# ─────────────────────────────────────────────────────────────────────────────


def section(title: str) -> None:
    console.print()
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print()


def demo_graph_summary(g) -> None:
    section("1  Graph Summary")
    s = g.summary()

    t = Table(title="Node counts by type", box=box.MINIMAL_DOUBLE_HEAD, show_header=True)
    t.add_column("Node Type", style="cyan")
    t.add_column("Count",     style="bold white", justify="right")
    for nt, count in sorted(s["nodes_by_type"].items()):
        layer_tag = "[blue]L1[/blue]" if nt in {
            NodeType.VENDOR, NodeType.ITEM, NodeType.TRADE_AGREEMENT,
            NodeType.PURCHASE_ORDER_LINE, NodeType.SALES_ORDER,
            NodeType.INVENTORY, NodeType.CUSTOMER,
        } else "[magenta]L2[/magenta]"
        t.add_row(f"{layer_tag} {nt}", str(count))
    console.print(t)

    console.print(f"  Total nodes          : [bold]{s['total_nodes']}[/bold]")
    console.print(f"  Total edges          : [bold]{s['total_edges']}[/bold]")
    console.print(f"  Layer 1 nodes        : [blue]{s['layer1_nodes']}[/blue]")
    console.print(f"  Layer 2 nodes        : [magenta]{s['layer2_nodes']}[/magenta]")
    console.print(f"  Cross-layer edges    : [yellow]{s['cross_layer_edges']}[/yellow]")


def demo_layer1_pegging(g) -> None:
    section("2  Layer 1 — Pegging Traversal (impact analysis for PO-MOTR)")
    console.print(
        "Scenario: [bold]PO-MOTR[/bold] (100 × DMA-MTR-DC @ $50/unit, vendor 1003) "
        "is delayed 14 days. Traverse pegged_to edges to find impacted downstream orders.\n"
    )
    impacted = g.get_pegged_orders("PO-MOTR")
    t = Table(title="Impacted Orders", box=box.SIMPLE)
    t.add_column("SO ID",         style="green")
    t.add_column("Customer",      style="cyan")
    t.add_column("Tier",          justify="center")
    t.add_column("Qty Required",  justify="right")
    t.add_column("Required Date", style="yellow")
    t.add_column("Impact Type",   style="magenta")
    for row in impacted:
        t.add_row(
            row["so_id"],
            row["customer_id"],
            str(row["customer_tier"]),
            str(int(row["ordered_qty"])),
            row["required_date"],
            row["impact_type"],
        )
    console.print(t)


def demo_layer1_alternates(g) -> None:
    section("3  Layer 1 — Alternate Vendors for DMA-MTR-DC")
    console.print(
        "Query: [italic]find all vendors with a trade agreement for DMA-MTR-DC, "
        "sorted by lead time[/italic]\n"
    )
    vendors = g.get_alternate_vendors("DMA-MTR-DC")
    t = Table(title="Alternate Vendors (PurchasePriceAgreements)", box=box.SIMPLE)
    t.add_column("Vendor ID",       style="cyan")
    t.add_column("Vendor Name",     style="white")
    t.add_column("Price/Unit",      justify="right")
    t.add_column("Fixed Charges",   justify="right")
    t.add_column("Lead Time (d)",   justify="center")
    t.add_column("Has TA?",         justify="center")
    t.add_column("Is Original?",    justify="center")
    for v in vendors:
        t.add_row(
            v["vendor_id"],
            v["vendor_name"],
            f"${v['price']}" if v["price"] else "—",
            f"${v['fixed_charges']}" if v["fixed_charges"] else "$0",
            str(v["lead_time_days"]),
            "✓" if v["has_ta"] else "✗",
            "[red]YES — exclude[/red]" if v["is_original"] else "No",
        )
    console.print(t)

    section("3b  Layer 1 — Alternate Items for DMA-MTR-DC")
    alts = g.get_alternate_items("DMA-MTR-DC")
    if alts:
        t2 = Table(title="Alternate Items (ReleasedProductsV2.AlternativeItemNumber)", box=box.SIMPLE)
        t2.add_column("Item ID",         style="cyan")
        t2.add_column("Description",     style="white")
        t2.add_column("Price/Unit",      justify="right")
        t2.add_column("Available Qty",   justify="right")
        t2.add_column("Safety Stock",    justify="right")
        t2.add_column("Safe Draw",       justify="right", style="yellow")
        t2.add_column("Proc Lead (d)",   justify="center")
        for a in alts:
            t2.add_row(
                a["item_id"],
                a["description"],
                f"${a['purchase_price']}",
                str(int(a["available_qty"])),
                str(int(a["safety_stock"])),
                str(int(a["safe_draw_qty"])),
                str(a["proc_lead_time_days"]),
            )
        console.print(t2)
    else:
        console.print("[yellow]No alternate items configured.[/yellow]")


def demo_layer1_safety_stock(g) -> None:
    section("4  Layer 1 — Safety-Stock Breach Check")
    console.print(
        "If we draw [bold]30 units[/bold] of DMA-MTR-DC from on-hand to cover the shortfall:\n"
    )
    result = g.check_inventory_breach("DMA-MTR-DC", units_to_draw=30.0)
    t = Table(box=box.SIMPLE)
    t.add_column("Field",   style="cyan")
    t.add_column("Value",   style="white")
    for k, v in result.items():
        color = "red bold" if k == "breached" and v else "green" if k == "breached" else "white"
        t.add_row(k, f"[{color}]{v}[/{color}]")
    console.print(t)

    console.print(
        "\n[bold yellow]⚠  Drawing all 30 units breaches the 20-unit safety stock floor.[/bold yellow]\n"
        "   UseOnHandInventory and AlternateItem are Partial mitigations for this disruption.\n"
        "   Safe standalone draw without breach: [bold]10 units[/bold].\n"
    )


def demo_layer1_cost_calculation(g) -> None:
    section("5  Layer 1 — Incremental Cost Calculation for AlternateVendor")
    console.print(
        "PO-MOTR: 100 units @ $50/unit (vendor 1003). "
        "Evaluate incremental cost for each alternate vendor.\n"
    )
    t = Table(title="Monetary Cost per Vendor", box=box.SIMPLE)
    t.add_column("Vendor",        style="cyan")
    t.add_column("Price/Unit",    justify="right")
    t.add_column("Fixed Charges", justify="right")
    t.add_column("Alt Total",     justify="right")
    t.add_column("Orig Total",    justify="right")
    t.add_column("Incremental ↑", justify="right", style="yellow")
    t.add_column("Lead (d)",      justify="center")

    for vendor_id in ["1001", "1002"]:
        r = g.compute_mitigation_cost(vendor_id, "DMA-MTR-DC", qty=100.0, original_price=50.0)
        t.add_row(
            r["vendor_name"],
            f"${r['price_per_unit']}",
            f"${r['fixed_charges']}",
            f"${r['alt_total']:.2f}",
            f"${r['orig_total']:.2f}",
            f"[bold]${r['incremental_cost']:.2f}[/bold]",
            str(r["lead_time_days"]),
        )
    console.print(t)


def demo_layer2_supplier_context(g) -> None:
    section("6  Layer 2 — Supplier Context for Vendor 1003")
    console.print(
        "Before evaluating mitigations the DMA retrieves institutional memory about "
        "vendor 1003 from Layer 2 via CONCERNS← and CHARACTERIZES← traversal.\n"
    )
    ctx = g.get_supplier_context("1003")
    console.print(f"  [cyan]Episodes involving vendor 1003:[/cyan] {len(ctx['episodes'])}")
    for ep in ctx["episodes"]:
        console.print(f"    • {ep['ep_id']}  {ep['scenario'][:60]}…")

    console.print(f"\n  [yellow]Facts characterising vendor 1003:[/yellow]")
    for f in ctx["facts"]:
        console.print(Panel(
            textwrap.fill(f["body"], width=90),
            title=f"[yellow]{f['fact_id']}[/yellow]",
            border_style="yellow",
            padding=(0, 2),
        ))

    console.print(f"\n  [magenta]Reflections targeting vendor 1003:[/magenta]")
    for r in ctx["reflections"]:
        console.print(Panel(
            textwrap.fill(r["body"], width=90),
            title=f"[magenta]{r['ref_id']}[/magenta]",
            border_style="magenta",
            padding=(0, 2),
        ))

    console.print(f"\n  [pink1]Recommendations:[/pink1]")
    for rec in ctx["recommendations"]:
        console.print(Panel(
            textwrap.fill(rec["body"], width=90),
            title=f"[pink1]{rec['rec_id']}[/pink1]",
            border_style="pink1",
            padding=(0, 2),
        ))


def demo_layer2_concept_expansion(g) -> None:
    section("7  Layer 2 — Concept-Mediated Retrieval")
    console.print(
        "Expand concept [bold]'safety_stock_erosion'[/bold] to find all related "
        "episodes, facts, and reflections.\n"
    )
    result = g.expand_by_concept("safety_stock_erosion")
    console.print(f"  Episodes : {len(result['episodes'])}")
    for ep in result["episodes"]:
        console.print(f"    • {ep['ep_id']}  {ep['scenario'][:70]}")
    console.print(f"  Facts    : {len(result['facts'])}")
    for f in result["facts"]:
        console.print(f"    • {f['fact_id']}  {f['body'][:80]}…")
    console.print(f"  Reflections : {len(result['reflections'])}")
    for r in result["reflections"]:
        console.print(f"    • {r['ref_id']}")


def demo_scoring(g) -> None:
    section("8  Scoring — Rank Mitigation Options for PO-MOTR (14-day delay)")
    console.print(
        "Evaluate three Full mitigation options for PO-MOTR against the "
        "embedded Goal nodes (25/25/25/25 weighting).\n"
    )
    options = [
        # Full mitigations (will be ranked)
        dict(name="AltVendor 1002 (Lande)",     feasibility="Full",
             monetary_cost=5200.0, delay_days=8, qty_shortfall=0, inventory_depletion=0),
        dict(name="AltVendor 1001 (Acme)",      feasibility="Full",
             monetary_cost=5500.0, delay_days=5, qty_shortfall=0, inventory_depletion=0),
        # Partial mitigations (not ranked)
        dict(name="UseOnHand DMA-MTR-DC (30u)", feasibility="Partial",
             monetary_cost=0.0,    delay_days=0, qty_shortfall=70, inventory_depletion=20),
        dict(name="AltItem DMA-MTR-AC (30u)",   feasibility="Partial",
             monetary_cost=0.0,    delay_days=0, qty_shortfall=70, inventory_depletion=20),
        dict(name="AcceptDisruption",            feasibility="Baseline",
             monetary_cost=0.0,    delay_days=14, qty_shortfall=0, inventory_depletion=0),
    ]
    ranked = g.score_mitigation_options(options)

    t = Table(title="Ranked Mitigations", box=box.SIMPLE)
    t.add_column("Rank",         justify="center")
    t.add_column("Option",       style="white")
    t.add_column("Feasibility",  justify="center")
    t.add_column("Cost ↑",       justify="right")
    t.add_column("Lead (d)",     justify="center")
    t.add_column("Qty Short",    justify="center")
    t.add_column("Inv Depl",     justify="center")
    t.add_column("Score",        justify="right", style="yellow")
    for opt in ranked:
        rank_str = str(opt.get("rank", "—")) if opt.get("rank") else "—"
        feas_color = {
            "Full": "green", "Partial": "yellow", "Baseline": "blue"
        }.get(opt["feasibility"], "white")
        t.add_row(
            rank_str,
            opt["name"],
            f"[{feas_color}]{opt['feasibility']}[/{feas_color}]",
            f"${opt['monetary_cost']:,.0f}",
            str(opt["delay_days"]),
            str(opt.get("qty_shortfall", 0)),
            str(opt.get("inventory_depletion", 0)),
            f"{opt['total_score']:.4f}" if opt.get("total_score") is not None else "—",
        )
    console.print(t)


def demo_prior_mitigations(g) -> None:
    section("9  Layer 2 — Prior Full Mitigations for Vendor 1001")
    console.print(
        "Query: [italic]all Full MitigationDecisions where vendor_id = '1001'[/italic] "
        "(most recent first)\n"
    )
    priors = g.get_prior_mitigations(vendor_id="1001", feasibility="Full")
    t = Table(box=box.SIMPLE)
    t.add_column("Decision",  style="cyan")
    t.add_column("Episode",   style="yellow")
    t.add_column("Item",      style="white")
    t.add_column("Type",      style="magenta")
    t.add_column("Cost ↑",    justify="right")
    t.add_column("Lead (d)",  justify="center")
    t.add_column("Rank",      justify="center")
    for d in priors:
        t.add_row(
            d["dec_id"],
            d["ep_id"],
            d["item_id"],
            d["mitigation_type"],
            f"${d['total_monetary_cost']:,.0f}",
            str(d["delay_days"]),
            str(d["rank"]),
        )
    console.print(t)


# ─── Entry point ──────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="DMA two-layer graph demo")
    parser.add_argument("--visualize", action="store_true",
                        help="Render matplotlib graphs (requires display)")
    parser.add_argument("--save-dir", default="",
                        help="Directory to save PNG visualisations instead of displaying")
    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold white]DMA Two-Layer Supply Chain Intelligence Network[/bold white]\n"
            "[dim]Layer 1: Supply Chain Network  |  Layer 2: Intelligence / Context Graph[/dim]",
            border_style="cyan",
        )
    )

    g = build_dma_graph()

    demo_graph_summary(g)
    demo_layer1_pegging(g)
    demo_layer1_alternates(g)
    demo_layer1_safety_stock(g)
    demo_layer1_cost_calculation(g)
    demo_layer2_supplier_context(g)
    demo_layer2_concept_expansion(g)
    demo_scoring(g)
    demo_prior_mitigations(g)

    if args.visualize:
        from .visualize import draw_full_graph, draw_disruption

        save = (lambda name: f"{args.save_dir}/{name}") if args.save_dir else (lambda _: None)

        console.print("\n[cyan]Rendering full graph…[/cyan]")
        draw_full_graph(g, save_path=save("dma_full_graph.png"))

        console.print("[cyan]Rendering disruption subgraph for PO-MOTR…[/cyan]")
        draw_disruption(g, "PO-MOTR", save_path=save("dma_disruption_PO-MOTR.png"))

        console.print("[cyan]Rendering disruption subgraph for _PO-SEAL…[/cyan]")
        draw_disruption(g, "_PO-SEAL", save_path=save("dma_disruption_PO-SEAL.png"))


if __name__ == "__main__":
    main()
