import os
import time
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetStatus
from datetime import datetime, timezone

# ──────────────────────────────────────────────
#  VTeX IRON CONDOR SQUADRON
#  Strategy : SPY 0-DTE Iron Condor
#  Structure : Bear Call [722/727] + Bull Put [722/717]
#  Legs      : Short 722C | Long 727C | Short 722P | Long 717P
#  Width     : 5 pts per side | Max Risk: $500/lot
#  Funds     : 30% Equity Allocation
# ──────────────────────────────────────────────

def execute_iron_condor(
    accounts=['chichi', 'wiiwii', 'huihui'],
    call_short=722, call_long=727,
    put_short=722,  put_long=717,
    funds_pct=0.30
):
    spread_width = max(abs(call_long - call_short), abs(put_short - put_long))
    margin_per_lot = spread_width * 100  # $500/lot (5-wide)

    print(f"🦅 VTeX IRON CONDOR | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🎯 SPY 0-DTE | Bear Call [{call_short}/{call_long}] + Bull Put [{put_short}/{put_long}]")
    print(f"📐 Width: {spread_width}pts | Margin/Lot: ${margin_per_lot} | Allocation: {int(funds_pct*100)}%")
    print("=" * 60)

    for acct_name in accounts:
        print(f"\n📡 [{acct_name.upper()}] Pre-flight check...")

        # ── ENV Resolution ──
        candidates = [acct_name]
        env_path = None
        for name in candidates:
            p = f"/Users/wiiche/alpaca-mcp-server/.env.{name}"
            if os.path.exists(p):
                env_path = p
                break
        if not env_path:
            env_path = "/Users/wiiche/alpaca-mcp-server/.env"
            print(f"  ⚠️  No dedicated .env for {acct_name}, using default.")

        load_dotenv(dotenv_path=env_path, override=True)
        api_key    = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")

        if not api_key:
            print(f"  ❌ No API keys found — skipping.")
            continue

        tc = TradingClient(api_key, secret_key, paper=True)

        try:
            # ── Sizing ──
            acct     = tc.get_account()
            equity   = float(acct.equity)
            capital  = equity * funds_pct
            qty      = int(capital // margin_per_lot)

            if qty <= 0:
                print(f"  ⚠️  Insufficient funds (${equity:,.2f}) for 30% allocation.")
                continue

            print(f"  ✅ Equity: ${equity:,.2f} | Allocated: ${capital:,.2f} | Qty: {qty} lots")

            # ── Contract Discovery ──
            req = GetOptionContractsRequest(
                underlying_symbols=['SPY'],
                status=AssetStatus.ACTIVE,
                limit=10000
            )
            res  = tc.get_option_contracts(req)
            today = str(datetime.now(timezone.utc).date())

            def find(option_type, strike):
                return next((
                    c for c in res.option_contracts
                    if c.underlying_symbol == 'SPY'
                    and c.type == option_type
                    and str(c.expiration_date) == today
                    and float(getattr(c, 'strike_price', getattr(c, 'strike', 0))) == float(strike)
                ), None)

            short_call = find('call', call_short)
            long_call  = find('call', call_long)
            short_put  = find('put',  put_short)
            long_put   = find('put',  put_long)

            missing = []
            if not short_call: missing.append(f"Short Call {call_short}")
            if not long_call:  missing.append(f"Long Call  {call_long}")
            if not short_put:  missing.append(f"Short Put  {put_short}")
            if not long_put:   missing.append(f"Long Put   {put_long}")

            if missing:
                print(f"  ❌ Contracts not found: {', '.join(missing)}")
                continue

            print(f"\n  🚀 FIRING 4-LEG IRON CONDOR | {acct_name.upper()} | {qty} lots")

            # ── LEG 1: Long Call (hedge cap) ──
            o1 = tc.submit_order(MarketOrderRequest(
                symbol=long_call.symbol, qty=qty,
                side=OrderSide.BUY, time_in_force=TimeInForce.DAY
            ))
            print(f"  🔷 [1/4] Long  Call {call_long} BOUGHT | {long_call.symbol} | ID: {o1.id}")
            time.sleep(1.2)

            # ── LEG 2: Short Call (premium) ──
            o2 = tc.submit_order(MarketOrderRequest(
                symbol=short_call.symbol, qty=qty,
                side=OrderSide.SELL, time_in_force=TimeInForce.DAY
            ))
            print(f"  🔶 [2/4] Short Call {call_short} SOLD  | {short_call.symbol} | ID: {o2.id}")
            time.sleep(1.2)

            # ── LEG 3: Long Put (hedge floor) ──
            o3 = tc.submit_order(MarketOrderRequest(
                symbol=long_put.symbol, qty=qty,
                side=OrderSide.BUY, time_in_force=TimeInForce.DAY
            ))
            print(f"  🔷 [3/4] Long  Put  {put_long}  BOUGHT | {long_put.symbol} | ID: {o3.id}")
            time.sleep(1.2)

            # ── LEG 4: Short Put (premium) ──
            o4 = tc.submit_order(MarketOrderRequest(
                symbol=short_put.symbol, qty=qty,
                side=OrderSide.SELL, time_in_force=TimeInForce.DAY
            ))
            print(f"  🔶 [4/4] Short Put  {put_short}  SOLD  | {short_put.symbol} | ID: {o4.id}")

            max_loss   = margin_per_lot * qty
            print(f"\n  ✨ SUCCESS: {acct_name.upper()} Iron Condor engaged!")
            print(f"     Max Risk: ${max_loss:,.2f} | Profit Zone: SPY stays within [{put_short}–{call_short}]")

        except Exception as e:
            print(f"\n  💣 CRITICAL ERROR in {acct_name}: {e}")

    print("\n" + "=" * 60)
    print("🏁 IRON CONDOR DEPLOYMENT COMPLETE")
    print(f"📊 Structure: [{call_short}/{call_long}C] | [{put_short}/{put_long}P]")
    print(f"🎯 Profit if SPY expires between {put_short} and {call_short}")
    print("=" * 60)


if __name__ == "__main__":
    execute_iron_condor(
        accounts   = ['chichi', 'wiiwii', 'huihui'],
        call_short = 722,
        call_long  = 727,
        put_short  = 722,
        put_long   = 717,
        funds_pct  = 0.30
    )
