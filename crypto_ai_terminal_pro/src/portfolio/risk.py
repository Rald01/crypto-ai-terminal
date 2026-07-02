def position_size(account_size: float, risk_percent: float, entry: float, stop: float) -> dict:
    risk_amount = account_size * risk_percent / 100
    risk_per_unit = abs(entry - stop)
    if risk_per_unit <= 0:
        raise ValueError('Entry and stop must be different.')
    units = risk_amount / risk_per_unit
    notional = units * entry
    return {'risk_amount': round(risk_amount,2), 'units': round(units,6), 'notional': round(notional,2), 'max_loss_if_stopped': round(risk_amount,2)}

def portfolio_summary(positions):
    total = sum(p['quantity'] * p['price'] for p in positions)
    rows = []
    for p in positions:
        value = p['quantity'] * p['price']
        rows.append({**p, 'value': value, 'weight_%': (value/total*100 if total else 0)})
    return rows, total
