import os
import time
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from datetime import datetime, timezone

# ══════════════════════════════════════════════════════════
#  VTeX THETA CONDOR — 尾盘 Theta 速减策略
#  ──────────────────────────────────────────────────────
#  入场时间 : 11:30 AM PDT (18:30 UTC) — 距收盘 90 分钟
#  策略结构 : SPY 0-DTE Iron Condor（双侧卖权）
#  盈利逻辑 : 最后 90 分钟 0-DTE Theta 指数衰减
#  目标账户 : cheche / wiiwii / huihui
#  资金配比 : 30% 权益
#  风险控制 : 权价宽度 5pt，最大亏损封顶
# ══════════════════════════════════════════════════════════

ACCOUNTS       = ['cheche', 'wiiwii', 'huihui']
SPREAD_WIDTH   = 5       # 每侧宽度（点数）
OTM_OFFSET     = 3       # 短腿偏离 ATM 的距离（点数）
FUNDS_PCT      = 0.30    # 资金比例
ENTRY_HOUR_UTC = 18      # 11:00 AM PDT = 18:00 UTC
ENTRY_MIN_UTC  = 30      # 11:30 AM PDT = 18:30 UTC

# ──────────────────────────────────────────────
def get_spy_price(api_key, secret_key):
    """获取 SPY 实时价格"""
    dc = StockHistoricalDataClient(api_key, secret_key)
    q  = dc.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols='SPY'))
    mid = (float(q['SPY'].ask_price) + float(q['SPY'].bid_price)) / 2
    return round(mid)

def round_to_strike(price, offset, direction='up'):
    """将价格四舍五入到最近整数 strike"""
    base = round(price)
    return base + offset if direction == 'up' else base - offset

def load_client(acct_name):
    candidates = [acct_name, 'huihui' if acct_name == 'huiui' else acct_name]
    env_path = None
    for name in candidates:
        p = f"/Users/wiiche/alpaca-mcp-server/.env.{name}"
        if os.path.exists(p):
            env_path = p
            break
    if not env_path:
        env_path = "/Users/wiiche/alpaca-mcp-server/.env"
    load_dotenv(dotenv_path=env_path, override=True)
    return TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True), \
           os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY")

def find_contract(contracts, option_type, strike, today):
    return next((
        c for c in contracts
        if c.underlying_symbol == 'SPY'
        and c.type == option_type
        and str(c.expiration_date) == today
        and float(getattr(c, 'strike_price', getattr(c, 'strike', 0))) == float(strike)
    ), None)

# ──────────────────────────────────────────────
def execute_theta_condor(
    accounts=ACCOUNTS,
    spread_width=SPREAD_WIDTH,
    otm_offset=OTM_OFFSET,
    funds_pct=FUNDS_PCT,
    dry_run=False
):
    now_utc = datetime.now(timezone.utc)
    today   = str(now_utc.date())

    print(f"\n{'═'*62}")
    print(f"  🧬 VTeX THETA CONDOR — 尾盘 Theta 速减策略")
    print(f"  ⏰ 入场时间: {now_utc.strftime('%Y-%m-%d %H:%M UTC')} | 距收盘: ~{int((21*60 - now_utc.hour*60 - now_utc.minute))}分钟")
    print(f"  📋 模式: {'DRY RUN 🔍' if dry_run else '实盘执行 🚀'}")
    print(f"{'═'*62}")

    # ── 获取 SPY 当前价格 ──
    tc0, ak, sk = load_client(accounts[0])
    try:
        spy_price = get_spy_price(ak, sk)
    except Exception as e:
        print(f"⚠️  无法获取 SPY 实时价格，尝试从持仓估算: {e}")
        spy_price = 722  # fallback，实盘请确认

    # ── 自动计算 Strike ──
    call_short = round_to_strike(spy_price, +otm_offset, 'up')
    call_long  = call_short + spread_width
    put_short  = round_to_strike(spy_price, -otm_offset, 'down')
    put_long   = put_short - spread_width

    margin_per_lot = spread_width * 100  # 每手最大风险

    print(f"\n  📍 SPY 当前价格: ~${spy_price}")
    print(f"  📐 策略结构:")
    print(f"     Bear Call Spread : Short {call_short}C / Long {call_long}C")
    print(f"     Bull Put  Spread : Short {put_short}P  / Long {put_long}P")
    print(f"     宽度: {spread_width}pts | 每手最大风险: ${margin_per_lot}")
    print(f"     盈利区间: SPY 收盘在 [{put_short} ~ {call_short}] 之间")
    print(f"{'─'*62}")

    if dry_run:
        print(f"\n  ✅ DRY RUN 完成 — 实盘执行请设置 dry_run=False")
        return

    # ── 各账户执行 ──
    for acct_name in accounts:
        print(f"\n  📡 [{acct_name.upper()}] 准备执行...")
        try:
            tc, ak, sk = load_client(acct_name)
            acct    = tc.get_account()
            equity  = float(acct.equity)
            capital = equity * funds_pct
            qty     = int(capital // margin_per_lot)

            if qty <= 0:
                print(f"  ⚠️  资金不足，跳过 ({acct_name})")
                continue

            print(f"  ✅ 权益: ${equity:,.2f} | 分配: ${capital:,.2f} | 手数: {qty} lots")

            # 获取合约链
            res   = tc.get_option_contracts(GetOptionContractsRequest(
                underlying_symbols=['SPY'], status=AssetStatus.ACTIVE, limit=10000
            ))
            chain = res.option_contracts

            sc = find_contract(chain, 'call', call_short, today)
            lc = find_contract(chain, 'call', call_long,  today)
            sp = find_contract(chain, 'put',  put_short,  today)
            lp = find_contract(chain, 'put',  put_long,   today)

            missing = [n for n, c in [
                (f'Short Call {call_short}', sc),
                (f'Long  Call {call_long}',  lc),
                (f'Short Put  {put_short}',  sp),
                (f'Long  Put  {put_long}',   lp)
            ] if not c]

            if missing:
                print(f"  ❌ 合约未找到: {', '.join(missing)}")
                continue

            print(f"  🚀 发射 4腿 Iron Condor | {acct_name.upper()} | {qty} lots")

            # Leg 1: Long Call (hedge)
            o1 = tc.submit_order(MarketOrderRequest(
                symbol=lc.symbol, qty=qty, side=OrderSide.BUY, time_in_force=TimeInForce.DAY))
            print(f"  🔷 [1/4] Long  Call {call_long} BOUGHT | {lc.symbol}")
            time.sleep(1.2)

            # Leg 2: Short Call (premium)
            o2 = tc.submit_order(MarketOrderRequest(
                symbol=sc.symbol, qty=qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY))
            print(f"  🔶 [2/4] Short Call {call_short} SOLD   | {sc.symbol}")
            time.sleep(1.2)

            # Leg 3: Long Put (hedge)
            o3 = tc.submit_order(MarketOrderRequest(
                symbol=lp.symbol, qty=qty, side=OrderSide.BUY, time_in_force=TimeInForce.DAY))
            print(f"  🔷 [3/4] Long  Put  {put_long}  BOUGHT | {lp.symbol}")
            time.sleep(1.2)

            # Leg 4: Short Put (premium)
            o4 = tc.submit_order(MarketOrderRequest(
                symbol=sp.symbol, qty=qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY))
            print(f"  🔶 [4/4] Short Put  {put_short}  SOLD   | {sp.symbol}")

            max_risk   = margin_per_lot * qty
            max_reward = "收取所有权利金"
            print(f"\n  ✨ {acct_name.upper()} 部署完成！")
            print(f"     最大风险: ${max_risk:,.2f} | 盈利条件: SPY 收盘 [{put_short}~{call_short}]")

        except Exception as e:
            print(f"\n  💣 [{acct_name.upper()}] 错误: {e}")

    print(f"\n{'═'*62}")
    print(f"  🏁 THETA CONDOR 部署完成")
    print(f"  ⏰ 下次检查: 12:00 PM PDT (60分钟后) — vpulse 监控")
    print(f"  🛑 止损建议: 如 SPY 偏离 >{spread_width*2} 点，考虑平仓一侧")
    print(f"{'═'*62}\n")


# ══════════════════════════════════════════════
#  运行方式:
#    dry_run=True  → 仅计算结构，不下单（推荐先测试）
#    dry_run=False → 实盘执行
# ══════════════════════════════════════════════
if __name__ == "__main__":
    execute_theta_condor(
        accounts     = ['cheche', 'wiiwii', 'huihui'],
        spread_width = 5,      # 5点宽度
        otm_offset   = 3,      # 短腿偏 ATM 3点
        funds_pct    = 0.30,   # 30% 资金
        dry_run      = True    # ← 改为 False 执行实盘
    )
