from flask import Flask
import pandas as pd

app = Flask(__name__)

# ---------------- LOAD DATA ---------------- #
def load_data():
    try:
        df = pd.read_csv("trades.csv")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return pd.DataFrame(columns=["timestamp","symbol","side","entry","stop","target","result"])


# ---------------- DASHBOARD ---------------- #
@app.route("/")
def dashboard():
    df = load_data()

    if df.empty:
        return "<h1 style='color:white;background:black;padding:20px;'>No trades yet</h1>"

    # Convert numbers
    df["entry"] = pd.to_numeric(df["entry"], errors="coerce")
    df["target"] = pd.to_numeric(df["target"], errors="coerce")
    df["stop"] = pd.to_numeric(df["stop"], errors="coerce")

    # PnL + equity
    pnl = []
    equity = []
    balance = 0

    for _, row in df.iterrows():
        if row["result"] == "win":
            gain = abs(row["target"] - row["entry"])
        elif row["result"] == "loss":
            gain = -abs(row["entry"] - row["stop"])
        else:
            gain = 0

        balance += gain
        pnl.append(gain)
        equity.append(balance)

    df["pnl"] = pnl
    df["equity"] = equity

    total = len(df)
    wins = len(df[df["result"] == "win"])
    losses = len(df[df["result"] == "loss"])
    win_rate = round((wins / total) * 100, 2) if total > 0 else 0

    # Create simple chart (HTML line)
    chart_points = ",".join([str(x) for x in equity])

    html = f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="10">
        <style>
            body {{
                background:#0e0e0e;
                color:#eee;
                font-family:Arial;
                padding:20px;
            }}
            h1 {{ color:#00ffcc; }}
            .card {{
                background:#1a1a1a;
                padding:15px;
                margin-bottom:20px;
                border-radius:10px;
            }}
            table {{
                width:100%;
                border-collapse:collapse;
            }}
            th, td {{
                padding:8px;
                border:1px solid #333;
                text-align:center;
            }}
            th {{
                background:#222;
            }}
        </style>
    </head>
    <body>

    <h1>📊 Trading Dashboard</h1>

    <div class="card">
        <h2>Stats</h2>
        <p>Total Trades: {total}</p>
        <p>Wins: {wins}</p>
        <p>Losses: {losses}</p>
        <p>Win Rate: {win_rate}%</p>
        <p>Total PnL: {round(balance,2)}</p>
    </div>

    <div class="card">
        <h2>Equity Curve</h2>
        <svg width="100%" height="200">
            <polyline
                fill="none"
                stroke="#00ffcc"
                stroke-width="2"
                points="
                {" ".join([f"{i*20},{200 - val*5}" for i,val in enumerate(equity)])}
                "
            />
        </svg>
    </div>

    <div class="card">
        <h2>Recent Trades</h2>
        {df.tail(20).to_html(index=False)}
    </div>

    </body>
    </html>
    """

    return html


# ---------------- RUN ---------------- #
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)