from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
import json
import geopandas as gpd
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px

app = Flask(__name__)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

FILE_MAP = {
    "hospitals": "hospitals.geojson",
    "fire_stations": "fire_stations.geojson",
    "schools": "pubschools.geojson"
}

chat_history = ""

@app.route('/')
@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route("/aichat.html")
def aichat():
    return render_template("aichat.html")

@app.route("/map.html")
def map():
    return render_template("map.html")

@app.route('/handbook.html')
def handbook():
    return render_template('handbook.html')

@app.route("/aichatapi", methods=["POST"])
def aichat_api():
    global chat_history
    data = request.json
    user_message = data.get("message", "")
    client = genai.Client(api_key="AIzaSyDDvtylxc-SAy0s9gM-A5gIuvYyWt2QgvI")
    response = client.models.generate_content(
        model='gemini-2.0-flash-thinking-exp',
        contents=user_message + '\nChat history: \n' + chat_history,
        config=types.GenerateContentConfig(
        system_instruction='You are AI assistant named Irena Astra, You are situated in the Philippines, You are suited for giving advice related to natural disasters and preventing hazards, You must act profesionally, You are to priotize the safety of the user.',
        max_output_tokens= 400,
        top_k= 2,
        top_p= 0.5,
        temperature= 0.5,
        seed=42,
        ),
    )
    chat_history += f"\nUser:\t{user_message}\nBot:\t{response.text}"

    return jsonify({"response": response.text})

@app.route('/geojson/<dataset>')
def get_geojson(dataset):
    file_path = FILE_MAP.get(dataset)
    if not file_path:
        return jsonify({"error": "Dataset not found"}), 404

    gdf = gpd.read_file(file_path)
    for col in gdf.select_dtypes(include=["datetime"]).columns:
        gdf[col] = gdf[col].astype(str)
    return jsonify(json.loads(gdf.to_json()))

@app.route("/forecast.html")
def forecast():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 14.7011,
        "longitude": 120.9830,
        "current": ["temperature_2m", "wind_speed_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max"],
        "past_days": 7,
        "forecast_days": 0
    }
    responses = openmeteo.weather_api(url, params=params)
    
    response = responses[0]
    
    current = response.Current()
    current_time = pd.to_datetime(current.Time(), unit="s", utc=True)
    current_temperature = current.Variables(0).Value()
    current_wind_speed = current.Variables(1).Value()
    current_temperature_formatted = f"{current_temperature:.1f}"
    current_wind_speed_formatted = f"{current_wind_speed:.1f}"
    
    daily = response.Daily()
    daily_temperature_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_min = daily.Variables(1).ValuesAsNumpy()
    daily_wind_speed_max = daily.Variables(2).ValuesAsNumpy()
    
    daily_temperature_max = [f"{temp:.1f}" for temp in daily_temperature_max]
    daily_temperature_min = [f"{temp:.1f}" for temp in daily_temperature_min]
    daily_wind_speed_max = [f"{wind:.1f}" for wind in daily_wind_speed_max]
    
    daily_dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )

    daily_dates_formatted = [date.strftime("%B %d") for date in daily_dates]
    
    daily_forecasts = []
    for date_str, max_temp, min_temp, wind_max in zip(daily_dates_formatted, daily_temperature_max, daily_temperature_min, daily_wind_speed_max):
        daily_forecasts.append({
            "date": date_str,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "wind_max": wind_max
        })
    
    return render_template(
        "forecast.html",
        current_time=current_time.strftime("%B %d, %Y %H:%M:%S"),
        current_temperature=current_temperature_formatted,
        current_wind_speed=current_wind_speed_formatted,
        daily_forecasts=daily_forecasts
    )

dash = Dash(__name__, app, routes_pathname_prefix='/dash/')

dash.layout = html.Div([
    html.Div([
        html.H2(children="Flood"),
        dcc.Dropdown(df.country.unique(), 'Flood', id='dropdown-selection-1', className="dash-dropdown"),
        dcc.Graph(id='graph-content-1', className="dash-graph")
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        html.H2(children="Fire"),
        dcc.Dropdown(df.country.unique(), 'Fire', id='dropdown-selection-2', className="dash-dropdown"),
        dcc.Graph(id='graph-content-2', className="dash-graph")
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.H2(children="Heavy Rainfall"),
        dcc.Dropdown(df.country.unique(), 'Heavy Rainfall', id='dropdown-selection-3', className="dash-dropdown"),
        dcc.Graph(id='graph-content-3', className="dash-graph")
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.H2(children="Hailstorm"),
        dcc.Dropdown(df.country.unique(), 'Hailstorm', id='dropdown-selection-4', className="dash-dropdown"),
        dcc.Graph(id='graph-content-4', className="dash-graph")
    ], style={'width': '48%', 'display': 'inline-block'}),
])

@callback(
    [Output('graph-content-1', 'figure'),
     Output('graph-content-2', 'figure'),
     Output('graph-content-3', 'figure'),
     Output('graph-content-4', 'figure')],
    [Input('dropdown-selection-1', 'value'),
     Input('dropdown-selection-2', 'value'),
     Input('dropdown-selection-3', 'value'),
     Input('dropdown-selection-4', 'value')]
)
def update_graph(value1, value2, value3, value4):
    dff1 = df[df.country == value1]
    dff2 = df[df.country == value2]
    dff3 = df[df.country == value3]
    dff4 = df[df.country == value4]  
    
    fig1 = px.line(dff1, x='year', y='pop', title=f'Population of {value1}')
    fig2 = px.line(dff2, x='year', y='pop', title=f'Population of {value2}')
    fig3 = px.line(dff3, x='year', y='pop', title=f'Population of {value3}')
    fig4 = px.line(dff4, x='year', y='pop', title=f'Population of {value4}')

    return fig1, fig2, fig3, fig4

@app.route("/reporthazard.html")
def report():
    return render_template("reporthazard.html")

if __name__ == '__main__':
    app.run(debug=True)
