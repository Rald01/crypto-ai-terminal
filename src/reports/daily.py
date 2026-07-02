def generate_report(ranked, symbol, tech_score, backtest_metrics=None):
    top = ranked.head(5)[["symbol", "name", "score"]].to_dict("records") if hasattr(ranked, "head") and len(ranked) else []

    lines = [
        "# Daily AI Crypto Research Report",
        "",
        "## Market Leaders by Score"
    ]

    for item in top:
        lines.append(f"- {item['name']} ({item['symbol'].upper()}): {item['score']}/100")

    lines += [
        "",
        f"## Technical View: {symbol.upper()}",
        f"Technical score: {tech_score.get('technical_score', 'N/A')}/100"
    ]

    for note in tech_score.get("notes", []):
        lines.append(f"- {note}")

    if backtest_metrics:
        lines += ["", "## Backtest Snapshot"]
        for k, v in backtest_metrics.items():
            lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## Decision Discipline",
        "- Define entry, invalidation, target, and position size before any trade.",
        "- Avoid leverage unless you have tested the strategy over several market regimes.",
        "- This report is research support, not financial advice."
    ]

    return "\n".join(lines)
