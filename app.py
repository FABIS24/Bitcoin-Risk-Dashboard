import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================================================
# 1. CARGA DE DATOS PARA LA APLICACIÓN WEB (app.py)
# =====================================================================
# Cargar el archivo CSV exportado previamente desde Jupyter
df_dash = pd.read_csv('bitcoin_datos_dashboard.csv')

# Convertir explícitamente la columna de fechas a formato DateTime para que Plotly la entienda
df_dash['Timestamp'] = pd.to_datetime(df_dash['Timestamp'])

# Recalculamos las variables por si se borraron
df_dash['Return'] = (df_dash['Close'] - df_dash['Open']) / df_dash['Open']
df_dash['Spread_Lag1'] = df_dash['Spread'].shift(1)
df_dash = df_dash.dropna() # Borramos cualquier valor nulo que rompa la gráfica

# Aseguramos la variable binaria de volatilidad
mediana_spread = df_dash['Spread'].median()
df_dash['Alta_Volatilidad'] = (df_dash['Spread'] > mediana_spread).astype(int)
# =====================================================================

# 2. Inicializar la aplicación Dash
app = dash.Dash(__name__)
app.title = "Dashboard Bitcoin Riesgo"

# 3. Diseñar la Interfaz (Layout)
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f6f9'}, children=[
    
    html.Div(style={'textAlign': 'center', 'marginBottom': '30px'}, children=[
        html.H1("Análisis de Volatilidad y Riesgo de Bitcoin (2020-2021)", style={'color': '#2c3e50'}),
        html.P("Dashboard interactivo para explorar el impacto del volumen en las fluctuaciones de precio.", 
               style={'fontSize': '18px', 'color': '#7f8c8d'})
    ]),

    # Filtros interactivos
    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'}, children=[
        html.Label("Selecciona la variable para comparar contra el Precio de Cierre:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='selector-variable',
            options=[
                {'label': 'Spread (Volatilidad Diaria en USD)', 'value': 'Spread'},
                {'label': 'Volumen Diario de Comercio', 'value': 'Volume'},
                {'label': 'Retorno Diario', 'value': 'Return'}
            ],
            value='Spread',
            clearable=False,
            style={'width': '50%', 'marginTop': '10px'}
        )
    ]),

    # Gráficos Interactivos
    html.Div(style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'}, children=[
        # Gráfico Temporal (Izquierda)
        html.Div(style={'flex': '2', 'minWidth': '600px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}, children=[
            dcc.Graph(id='grafico-temporal')
        ]),
        
        # Gráfico de Dispersión (Derecha)
        html.Div(style={'flex': '1', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}, children=[
            html.H3("Modelo Predictivo: Volumen vs Spread", style={'textAlign': 'center', 'color': '#34495e', 'fontSize': '16px'}),
            dcc.Graph(
                id='grafico-dispersion',
                figure=px.scatter(df_dash, x='Volume', y='Spread', trendline="ols", 
                                  color='Alta_Volatilidad',
                                  color_continuous_scale=['#3498db', '#e74c3c']).update_layout(margin=dict(l=20, r=20, t=30, b=20))
            )
        ])
    ]),
    
    # Narrativa
    html.Div(style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginTop': '20px'}, children=[
        html.H3("Conclusiones del Modelo Optimizado"),
        html.Ul([
            html.Li("La inclusión del retorno diario y la volatilidad anterior mejoró la predicción drásticamente."),
            html.Li("Aplicando regularización L1 (C=10), el modelo alcanzó un Recall del 89.7%, logrando detectar casi todos los días de alto riesgo."),
            html.Li("El volumen de transacciones se confirma como el principal motor de la volatilidad extrema.")
        ])
    ])
])

# 4. Interactividad usando los datos limpios
@app.callback(
    Output('grafico-temporal', 'figure'),
    [Input('selector-variable', 'value')]
)
def actualizar_grafico(variable_seleccionada):
    if not variable_seleccionada:
        return go.Figure()

    # Usamos make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Eje Principal: Precio de Cierre
    fig.add_trace(
        go.Scatter(x=df_dash['Timestamp'], y=df_dash['Close'], name='Precio (USD)', mode='lines', line=dict(color='#2980b9', width=2)),
        secondary_y=False,
    )
    
    # Eje Secundario: Variable del filtro (Spread, Volume, Return)
    fig.add_trace(
        go.Scatter(x=df_dash['Timestamp'], y=df_dash[variable_seleccionada], name=variable_seleccionada, mode='lines', line=dict(color='#e74c3c', width=1, dash='dot')),
        secondary_y=True,
    )
    
    fig.update_layout(
        title=f"Evolución del Precio de Bitcoin vs {variable_seleccionada}",
        hovermode="x unified",
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

# 5. Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=False)
# Hay que esperar más o menos 1 minuto para que se lance la app