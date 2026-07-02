def generate_report(ranked, symbol, tech_score, backtest_metrics=None, smc=None, wyckoff=None, elliott=None):
    score_col = "opportunity_score" if "opportunity_score" in ranked.columns else "score"
    top = ranked.head(7)[["symbol", "name", score_col, "risk_label"]].to_dict("records") if hasattr(ranked, "head") and len(ranked) else []
    lines = ["# Daily AI Crypto Research Report", "", "## Top Investable Opportunities"]
    for item in top:
        lines.append(f"- {item['name']} ({item['symbol'].upper()}): {item[score_col]}/100 | Risk: {item.get('risk_label','N/A')}")
    lines += ["", f"## Technical View: {symbol.upper()}", f"Technical score: {tech_score.get('technical_score', 'N/A')}/100"]
    for note in tech_score.get("notes", []):
        lines.append(f"- {note}")
    if smc: lines += ["", "## Smart Money Concepts", *[f"- {k}: {v}" for k,v in smc.items()]]
    if wyckoff: lines += ["", "## Wyckoff Read", *[f"- {k}: {v}" for k,v in wyckoff.items()]]
    if elliott: lines += ["", "## Elliott Wave Heuristic", *[f"- {k}: {v}" for k,v in elliott.items()]]
    if backtest_metrics:
        lines += ["", "## Backtest Snapshot"]
        for k, v in backtest_metrics.items(): lines.append(f"- {k}: {v}")
    lines += ["", "## Decision Discipline", "- This is research support, not financial advice.", "- Use predefined entries, stops, and position sizing.", "- Avoid leverage as a beginner."]
    return "\n".join(lines)
