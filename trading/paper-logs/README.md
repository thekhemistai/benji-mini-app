# Paper Trading Logs

Daily paper trading performance tracking for BTC Polymarket strategy.

## Structure

- `daily/` - Daily trade logs (YYYY-MM-DD.md)
- `summary.json` - Running win/loss ratio and PnL
- `backtest/` - Strategy backtest results

## Metrics Tracked

- Win/Loss Ratio
- Average Win %
- Average Loss %
- Total PnL
- Sharpe Ratio (risk-adjusted returns)
- Max Drawdown

## Strategy

BTC 1-hour and 4-hour Up/Down markets on Polymarket.
Entry: When technical indicators show >5% edge vs market odds.
Exit: Market resolution or stop loss at -10%.

