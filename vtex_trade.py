import os
import time
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetStatus
from datetime import datetime, timezone

def execute_squadron_706_696(accounts=['cheche', 'huihui', 'wiiwii'], short_strike=706, long_strike=696, funds_pct=0.70):
    print(f"🦅 VTeX COMMAND | 706/696 SQUADRON DEPLOYMENT | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: SPY 0-DTE | Strikes: Short ${short_strike} / Long ${long_strike}")
    print(f"💰 Parameters: {funds_pct*100}% Equity Allocation | Vertical Spread (Width 10)")
    print("-" * 50)

    for acct_name in accounts:
        print(f"📡 [PRE-FLIGHT] Checking Account: {acct_name.upper()}")
        
        # Determine .env path based on previous patterns
        env_path = f"/Users/wiiche/alpaca-mcp-server/.env.{acct_name}"
        if not os.path.exists(env_path):
            env_path = "/Users/wiiche/alpaca-mcp-server/.env" # Final fallback
        
        load_dotenv(dotenv_path=env_path, override=True)
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not api_key:
            print(f"❌ Skipping {acct_name}: No API keys.")
            continue
            
        tc = TradingClient(api_key, secret_key, paper=True)
        
        try:
            # Sizing
            acct = tc.get_account()
            equity = float(acct.equity)
            target_risk = equity * funds_pct
            margin_per_lot = abs(short_strike - long_strike) * 100
            qty = int(target_risk // margin_per_lot)
            
            if qty <= 0:
                print(f"⚠️ Insufficient funds in {acct_name} (${equity:,.2f}) for 70% allocation.")
                continue

            print(f"✅ Ready: Equity ${equity:,.2f} | Allocated ${target_risk:,.2f} | Qty: {qty} lots")

            # Contract Discovery
            req = GetOptionContractsRequest(underlying_symbols=['SPY'], status=AssetStatus.ACTIVE, limit=10000)
            res = tc.get_option_contracts(req)
            today = datetime.now(timezone.utc).date()
            
            puts = [c for c in res.option_contracts if c.underlying_symbol == 'SPY' and c.type == 'put' and str(c.expiration_date) == str(today)]
            
            def get_strike(c): return float(c.strike_price if hasattr(c, 'strike_price') else c.strike)
            
            short_contract = next((c for c in puts if get_strike(c) == float(short_strike)), None)
            long_contract = next((c for c in puts if get_strike(c) == float(long_strike)), None)
            
            if not short_contract or not long_contract:
                print(f"❌ Strikes {short_strike} or {long_strike} not found in 0-DTE chain.")
                continue

            # Execution
            print(f"🚀 [FIRE] Executing Squadron for {acct_name.upper()}...")
            
            # 1. Long Leg (Cover Margin)
            l_order = tc.submit_order(MarketOrderRequest(
                symbol=long_contract.symbol, qty=qty, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
            ))
            print(f"  🔹 Long Put {long_strike} Bought | ID: {l_order.id}")
            
            time.sleep(1.5) # Throttle for risk engine
            
            # 2. Short Leg (Generate Premium)
            s_order = tc.submit_order(MarketOrderRequest(
                symbol=short_contract.symbol, qty=qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY
            ))
            print(f"  🔸 Short Put {short_strike} Sold | ID: {s_order.id}")
            
            print(f"✨ SUCCESS: {acct_name.upper()} squadron engaged at {qty} lots.")

        except Exception as e:
            print(f"💣 CRITICAL ERROR in {acct_name}: {e}")

if __name__ == "__main__":
    execute_squadron_706_696()
