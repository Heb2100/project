import subprocess
import sys
from datetime import datetime, timedelta

def install_requirements():
    required_packages = ['fastapi', 'uvicorn', 'jinja2', 'plotly', 'pandas', 'yfinance']
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
import pandas as pd

def get_crypto_data(symbol):
    end_date = datetime.now().strftime('%Y-%m-%d')
    data = yf.download(f'{symbol}-USD', start='2016-01-01', end=end_date, auto_adjust=False)
    close_data = data[('Close', f'{symbol}-USD')].copy()
    return pd.DataFrame({'Close': close_data})

# Initialize data
btc_data = get_crypto_data('BTC')
eth_data = get_crypto_data('ETH')
xrp_data = get_crypto_data('XRP')

# Clean the data
btc_data.dropna(inplace=True)
btc_data = btc_data[btc_data['Close'] > 0]
eth_data.dropna(inplace=True)
eth_data = eth_data[eth_data['Close'] > 0]
xrp_data.dropna(inplace=True)
xrp_data = xrp_data[xrp_data['Close'] > 0]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def create_crypto_chart(data, crypto_name):
    # Create figure using the data
    fig = go.Figure()
    
    # Add trace with both lines and markers
    fig.add_trace(go.Scatter(
        x=list(data.index),
        y=list(data['Close']),
        mode='lines',
        name=f'{crypto_name} Price',
        line=dict(color='black', width=2),
        marker=dict(size=6, color='blue')
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'{crypto_name} Price',
            'x': 0.05,
            'xanchor': 'left',
            'font': dict(size=20)
        },
        yaxis_title='Price (USD)',
        template='plotly_white',
        height=600,
        yaxis=dict(
            tickformat="$,.0f",
            showgrid=True,
            gridcolor='lightgrey',
            tickprefix="$"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',
            tickformat="%Y-%m-%d"
        ),
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
    chart = create_crypto_chart(btc_data, "Bitcoin")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chart": chart}
    )

@app.get("/ethereum", response_class=HTMLResponse)
async def ethereum(request: Request):
    chart = create_crypto_chart(eth_data, "Ethereum")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chart": chart}
    )

@app.get("/ripple", response_class=HTMLResponse)
async def ripple(request: Request):
    chart = create_crypto_chart(xrp_data, "Ripple")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chart": chart}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


