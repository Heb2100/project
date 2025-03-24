import subprocess
import sys
from datetime import datetime, timedelta
import requests

def install_requirements():
    required_packages = ['fastapi', 'uvicorn', 'jinja2', 'plotly', 'pandas', 'yfinance', 'requests']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully!")

# Install required packages first
install_requirements()

# Now import all required packages after installation
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def get_crypto_data(symbol):
    end_date = datetime.now().strftime('%Y-%m-%d')
    data = yf.download(f'{symbol}-USD', start='2016-01-01', end=end_date, auto_adjust=False)
    close_data = data[('Close', f'{symbol}-USD')].copy()
    return pd.DataFrame({'Close': close_data})

def get_mvrv_data():
    # MVRV Z-Score 데이터를 가져오는 함수
    # 실제로는 API나 데이터베이스에서 가져와야 하지만, 예시로 더미 데이터 생성
    dates = pd.date_range(start='2016-01-01', end=datetime.now(), freq='D')
    import numpy as np
    np.random.seed(42)
    z_scores = np.random.normal(0, 2, size=len(dates))
    print('z_scores', z_scores)
    z_scores = pd.Series(np.cumsum(z_scores) / 10, index=dates)
    return pd.DataFrame({'Z-Score': z_scores})

# Initialize data
crypto_data = {
    'bitcoin': get_crypto_data('BTC'),
    'ethereum': get_crypto_data('ETH'),
    'ripple': get_crypto_data('XRP')
}
mvrv_data = get_mvrv_data()

# Clean the data
for data in crypto_data.values():
    data.dropna(inplace=True)
    data = data[data['Close'] > 0]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def create_multi_crypto_chart(selected_cryptos, show_mvrv=False):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Color mapping for each cryptocurrency
    colors = {
        'bitcoin': '#F7931A',  # Bitcoin orange
        'ethereum': '#627EEA',  # Ethereum blue
        'ripple': '#23292F'    # Ripple dark
    }
    
    # Add trace for each selected cryptocurrency
    for crypto_name in selected_cryptos:
        data = crypto_data[crypto_name]
        display_name = crypto_name.capitalize()
        
        fig.add_trace(
            go.Scatter(
                x=list(data.index),
                y=list(data['Close']),
                mode='lines',
                name=f"{display_name} Price",
                line=dict(color=colors.get(crypto_name, 'black'), width=2)
            ),
            secondary_y=False
        )
    
    # Add MVRV Z-Score if enabled
    if show_mvrv:
        fig.add_trace(
            go.Scatter(
                x=list(mvrv_data.index),
                y=list(mvrv_data['Z-Score']),
                mode='lines',
                name='MVRV Z-Score',
                line=dict(color='#FF9900', width=2)
            ),
            secondary_y=True
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Cryptocurrency Prices & MVRV Z-Score',
            'x': 0.05,
            'xanchor': 'left',
            'font': dict(size=20)
        },
        template='plotly_white',
        height=600,
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Update yaxis properties
    fig.update_yaxes(
        title_text="Price (USD)",
        type="log",
        tickformat="$,.0f",
        showgrid=True,
        gridcolor='lightgrey',
        tickprefix="$",
        secondary_y=False
    )

    # Update secondary yaxis properties
    if show_mvrv:
        fig.update_yaxes(
            title_text="MVRV Z-Score",
            showgrid=False,
            secondary_y=True,
            tickformat=".2f"
        )
    
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id="chart",
        config={
            'displayModeBar': True,
            'scrollZoom': True,
            'responsive': True
        }
    )

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    chart = create_multi_crypto_chart(['bitcoin'])
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chart": chart}
    )

@app.get("/multi/{cryptos}", response_class=HTMLResponse)
async def multi_crypto(request: Request, cryptos: str, mvrv: bool = False):
    selected_cryptos = cryptos.split(',')
    if not selected_cryptos:
        selected_cryptos = ['bitcoin']
    
    chart = create_multi_crypto_chart(selected_cryptos, show_mvrv=mvrv)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chart": chart}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


