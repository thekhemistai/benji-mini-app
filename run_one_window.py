import importlib.util, sys, pathlib

# Load the polymarket BTC script as a module
script_path = pathlib.Path('/Users/thekhemist/.openclaw/workspace/agents/signal-hunter/polymarket_btc_15m.py')
spec = importlib.util.spec_from_file_location('polymarket_btc', script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules['polymarket_btc'] = mod
spec.loader.exec_module(mod)

# Run a single monitoring window (short‑circuit version for testing)

# 1️⃣ Get start price
start_price = mod.fetch_btc_price()
print(f"Start price: {start_price}")

# 2️⃣ Simulate a short wait (we won’t actually sleep 15 min)
#    Just fetch a slightly later price as the “end” price
end_price = mod.fetch_btc_price()
print(f"End price (simulated): {end_price}")

# 3️⃣ Compute BTC % change
if start_price and end_price:
    btc_change_pct = (end_price - start_price) / start_price
    print(f"BTC change %: {btc_change_pct:.5f}")
else:
    btc_change_pct = None

# 4️⃣ Get Polymarket odds
yes_odds, no_odds = mod.get_polymarket_odds()
print(f"Odds – YES: {yes_odds}, NO: {no_odds}")

# 5️⃣ Calculate edge using the script’s helper
if btc_change_pct is not None and yes_odds is not None and no_odds is not None:
    direction, edge, fair_prob = mod.calculate_edge(btc_change_pct, yes_odds, no_odds)
    print(f"Direction: {direction}, Edge: {edge:.5f}, Fair prob: {fair_prob:.5f}")
    # 6️⃣ If edge exceeds threshold, log a paper trade
    if edge >= mod.CONFIG.get('EDGE_THRESHOLD', 0.04):
        # Use the module’s log_trade function (expects many params)
        mod.log_trade(
            direction=direction,
            stake=mod.CONFIG["VIRTUAL_STAKE"],
            odds=yes_odds if direction == "YES" else no_odds,
            edge=edge,
            btc_start=start_price,
            btc_end=end_price,
            btc_change=btc_change_pct,
        )
        print("✅ Trade recorded")
    else:
        print("❌ Edge below threshold – no trade")
else:
    print("⚠️ Missing data – cannot compute edge")
