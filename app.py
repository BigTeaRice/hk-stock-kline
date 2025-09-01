from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timedelta

app = FastAPI()

# 允许前端域名跨域（GitHub Pages 域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名（如 https://username.github.io）
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_hk_stock_data(symbol: str, days: int = 7):
    """获取港股历史数据（Yahoo Finance）"""
    # Yahoo Finance 港股代码格式：00700.HK → 0700.HK（需去掉前导零）
    yahoo_symbol = symbol.replace('00', '0') if symbol.startswith('00') else symbol
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 下载数据（间隔 1 天）
    df = yf.download(
        yahoo_symbol,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval='1d'
    )
    
    # 格式化数据（时间戳转字符串，保留 OHLC）
    timestamps = df.index.strftime('%Y-%m-%d').tolist()
    ohlc = df[['Open', 'High', 'Low', 'Close']].values.tolist()
    return {"timestamps": timestamps, "ohlc": ohlc}

@app.get("/api/realtime")
async def realtime_data(symbol: str = "00700.HK"):
    return get_hk_stock_data(symbol)

# 生产环境建议添加缓存（如 Redis），避免频繁调用 Yahoo Finance