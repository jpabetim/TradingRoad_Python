import dash
from dash import html, dcc, Input, Output, State, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import datetime

# Función para generar datos de ejemplo (simulados)
def generate_sample_data(symbol='BTC/USDT', timeframe='1h', periods=200):
    end_date = datetime.datetime.now()
    if timeframe == '1m':
        start_date = end_date - datetime.timedelta(minutes=periods)
        delta = datetime.timedelta(minutes=1)
    elif timeframe == '5m':
        start_date = end_date - datetime.timedelta(minutes=5*periods)
        delta = datetime.timedelta(minutes=5)
    elif timeframe == '15m':
        start_date = end_date - datetime.timedelta(minutes=15*periods)
        delta = datetime.timedelta(minutes=15)
    elif timeframe == '1h':
        start_date = end_date - datetime.timedelta(hours=periods)
        delta = datetime.timedelta(hours=1)
    elif timeframe == '4h':
        start_date = end_date - datetime.timedelta(hours=4*periods)
        delta = datetime.timedelta(hours=4)
    elif timeframe == '1d':
        start_date = end_date - datetime.timedelta(days=periods)
        delta = datetime.timedelta(days=1)
    else: # Default to 1h
        start_date = end_date - datetime.timedelta(hours=periods)
        delta = datetime.timedelta(hours=1)

    dates = pd.date_range(start_date, end_date, freq=delta)
    if len(dates) > periods:
        dates = dates[-periods:]
    elif len(dates) < periods and len(dates) > 0:
        # If not enough dates, adjust periods
        periods = len(dates)
    elif len(dates) == 0:
        return pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])

    price_data = np.random.normal(loc=50000, scale=500, size=periods)
    open_prices = price_data + np.random.normal(scale=100, size=periods)
    close_prices = open_prices + np.random.normal(scale=200, size=periods) # Make it more volatile
    high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(50, 200, size=periods)
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(50, 200, size=periods)
    volume_data = np.random.randint(100, 10000, size=periods)

    df = pd.DataFrame({
        'time': dates.strftime('%Y-%m-%d %H:%M:%S'), # LWC can also take unix timestamps
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume_data
    })
    # Ensure 'time' is string for JSON serialization if not using unix timestamps
    # For LWC, time can be 'YYYY-MM-DD' for daily, or unix timestamp for intraday.
    # Let's convert to unix timestamps (seconds) for better precision with LWC
    df['time'] = (pd.to_datetime(df['time']).astype(np.int64) // 10**9).tolist()
    return df

def layout():
    return dbc.Container([
        dcc.Store(id='lwc-chart-config-store', data={'symbol': 'BTCUSDT', 'interval': '1h', 'exchange': 'binance_futures'}),
        dcc.Store(id='lwc-ohlcv-data-store'),
        dcc.Store(id='lwc-theme-store', data={'theme': 'dark'}), # 'dark' or 'light'

        # Navbar (simplified for now)
        dbc.NavbarSimple(
            brand="TradingRoad - Lightweight Chart Analysis",
            brand_href="/dashboard/",
            color="primary",
            dark=True,
            className="mb-2"
        ),

        dbc.Row([
            # Side Panel (Controls)
            dbc.Col([
                html.Div([
                    html.H5("Market Controls", className="text-light mb-3"),
                    dbc.Label("Exchange", html_for="lwc-exchange-selector", className="text-light"),
                    dbc.Select(
                        id="lwc-exchange-selector",
                        options=[
                            {"label": "Binance Futures", "value": "binance_futures"},
                            {"label": "Binance Spot", "value": "binance_spot"},
                        ],
                        value="binance_futures", className="mb-2"
                    ),
                    dbc.Label("Symbol (e.g., BTCUSDT)", html_for="lwc-symbol-input", className="text-light"),
                    dbc.Input(id="lwc-symbol-input", value="BTCUSDT", type="text", className="mb-2"),
                    dbc.Label("Timeframe", html_for="lwc-timeframe-buttons", className="text-light"),
                    dbc.ButtonGroup([
                        dbc.Button("1m", id="lwc-tf-1m", n_clicks=0, color="secondary", outline=True, size="sm"),
                        dbc.Button("5m", id="lwc-tf-5m", n_clicks=0, color="secondary", outline=True, size="sm"),
                        dbc.Button("15m", id="lwc-tf-15m", n_clicks=0, color="secondary", outline=True, size="sm"),
                        dbc.Button("1H", id="lwc-tf-1h", n_clicks=0, color="primary", outline=False, size="sm"), # Default active
                        dbc.Button("4H", id="lwc-tf-4h", n_clicks=0, color="secondary", outline=True, size="sm"),
                        dbc.Button("1D", id="lwc-tf-1d", n_clicks=0, color="secondary", outline=True, size="sm"),
                    ], id="lwc-timeframe-buttons", className="d-flex flex-wrap mb-3"),
                    
                    dbc.Button("Toggle Theme", id="lwc-toggle-theme-button", color="info", size="sm", className="mt-3 w-100"),
                    html.Div(id='clientside-chart-output-placeholder', style={'display': 'none'}) # Dummy output for clientside cb
                ], className="p-3 bg-dark", style={'height': 'calc(100vh - 70px)', 'overflowY': 'auto'})
            ], width=3, id="lwc-side-panel"),

            # Chart Area
            dbc.Col([
                html.Div(id='lwc-chart-container', style={'width': '100%', 'height': 'calc(100vh - 70px)', 'backgroundColor': '#131722'})
            ], width=9, id="lwc-chart-col"),
        ], className="g-0"),
    ], fluid=True, className="px-0", style={'backgroundColor': '#131722', 'color': 'white', 'minHeight': '100vh'})


def register_callbacks(app):
    # Update chart config store based on user inputs
    @app.callback(
        Output('lwc-chart-config-store', 'data'),
        [
            Input('lwc-exchange-selector', 'value'),
            Input('lwc-symbol-input', 'value'),
            Input('lwc-tf-1m', 'n_clicks'),
            Input('lwc-tf-5m', 'n_clicks'),
            Input('lwc-tf-15m', 'n_clicks'),
            Input('lwc-tf-1h', 'n_clicks'),
            Input('lwc-tf-4h', 'n_clicks'),
            Input('lwc-tf-1d', 'n_clicks'),
        ],
        [State('lwc-chart-config-store', 'data')]
    )
    def update_chart_config(exchange, symbol, n1m, n5m, n15m, n1h, n4h, n1d, current_config):
        ctx = dash.callback_context
        if not ctx.triggered_id:
            return current_config

        prop_id = ctx.triggered_id
        new_interval = current_config.get('interval', '1h')

        if prop_id == 'lwc-tf-1m': new_interval = '1m'
        elif prop_id == 'lwc-tf-5m': new_interval = '5m'
        elif prop_id == 'lwc-tf-15m': new_interval = '15m'
        elif prop_id == 'lwc-tf-1h': new_interval = '1h'
        elif prop_id == 'lwc-tf-4h': new_interval = '4h'
        elif prop_id == 'lwc-tf-1d': new_interval = '1d'
        
        return {'symbol': symbol, 'interval': new_interval, 'exchange': exchange}

    # Fetch/generate OHLCV data when config changes
    @app.callback(
        Output('lwc-ohlcv-data-store', 'data'),
        [Input('lwc-chart-config-store', 'data')]
    )
    def update_ohlcv_data(chart_config):
        if not chart_config or not chart_config.get('symbol') or not chart_config.get('interval'):
            return {'ohlcv': [], 'volume': []}
        
        symbol = chart_config['symbol']
        interval = chart_config['interval']
        # Here you would fetch real data based on symbol, interval, exchange
        # For now, using simulated data
        df = generate_sample_data(symbol, interval, periods=300)
        
        ohlcv_data = df[['time', 'open', 'high', 'low', 'close']].to_dict(orient='records')
        volume_data = df[['time', 'volume']].rename(columns={'volume': 'value'}).to_dict(orient='records')
        
        # Add color to volume data (example: green if close > open, red otherwise)
        # This needs to be done carefully if using a separate volume series in LWC
        # For simplicity, LWC candlestick series can show volume, or a separate histogram can be used.
        # Let's prepare volume for a separate histogram series if needed.
        # For now, the candlestick series in LWC can derive volume color from candle color.
        
        return {'ohlcv': ohlcv_data, 'volume': volume_data}

    # Update theme store
    @app.callback(
        Output('lwc-theme-store', 'data'),
        Input('lwc-toggle-theme-button', 'n_clicks'),
        State('lwc-theme-store', 'data'),
        prevent_initial_call=True
    )
    def toggle_theme(n_clicks, current_theme_data):
        if current_theme_data['theme'] == 'dark':
            return {'theme': 'light'}
        else:
            return {'theme': 'dark'}

    # Clientside callback to render/update the Lightweight Chart
    clientside_callback(
        ClientsideFunction(
            namespace='lwc',
            function_name='updateChart'
        ),
        Output('clientside-chart-output-placeholder', 'children'), # Dummy output
        [Input('lwc-ohlcv-data-store', 'data'),
         Input('lwc-theme-store', 'data')],
        [State('lwc-chart-container', 'id')]
    )

    # Callback to update timeframe button styles
    @app.callback(
        [Output(f'lwc-tf-{tf}', 'outline') for tf in ['1m', '5m', '15m', '1h', '4h', '1d']] +
        [Output(f'lwc-tf-{tf}', 'color') for tf in ['1m', '5m', '15m', '1h', '4h', '1d']],
        Input('lwc-chart-config-store', 'data')
    )
    def update_timeframe_button_styles(chart_config):
        interval = chart_config.get('interval', '1h') if chart_config else '1h'
        outputs_outline = []
        outputs_color = []
        timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        for tf in timeframes:
            is_active = (tf == interval)
            outputs_outline.append(not is_active)
            outputs_color.append('primary' if is_active else 'secondary')
        return outputs_outline + outputs_color

