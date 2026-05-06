import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from datetime import datetime, timezone

def generate_xpulse_report(account_names=['cheche', 'huiui', 'wiiwii']):
    print(f"🧬 [VTeX X-PULSE] STATUS AUDIT | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*65)
    
    total_equity = 0
    total_pnl = 0
    
    for acct in account_names:
        possible_names = [acct]
        if acct == 'huiui': possible_names.append('huihui')
        
        env_path = None
        for name in possible_names:
            p = f"/Users/wiiche/alpaca-mcp-server/.env.{name}"
            if os.path.exists(p):
                env_path = p
                break
        
        if not env_path:
            # Fallback to default .env (cheche's usually)
            env_path = "/Users/wiiche/alpaca-mcp-server/.env"
            
        load_dotenv(dotenv_path=env_path, override=True)
        tc = TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True)
        
        try:
            acc = tc.get_account()
            positions = tc.get_all_positions()
            
            equity = float(acc.equity)
            pnl = sum(float(p.unrealized_pl) for p in positions if "SPY" in p.symbol)
            
            total_equity += equity
            total_pnl += pnl
            
            print(f"👤 Account: {acct.upper():<8} | Equity: ${equity:11,.2f} | 0-DTE PnL: ${pnl:+10,.2f}")
            for p in positions:
                if "SPY" in p.symbol:
                    print(f"   ∟ {p.symbol:<20} | Qty: {p.qty:>4} | PnL: ${float(p.unrealized_pl):+7,.2f}")
                    
        except Exception as e:
            print(f"👤 Account: {acct.upper():<8} | ❌ ERROR: {e}")
            
    print("-" * 65)
    print(f"🔥 SQUAD TOTALS       | Equity: ${total_equity:11,.2f} | Net PnL: ${total_pnl:+10,.2f}")
    print("=" * 65)
    print("🎯 STRATEGY STATUS: 0-DTE BULL PUT [708/692] - THETA DECAY IN PROGRESS.")

if __name__ == "__main__":
    generate_xpulse_report()
