import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, dcc, html

COUNTRIES = ['Egypt', 'South Africa', 'Mozambique', 'Tanzania', 'Sudan']
PAPER = '#FFFFE0'


def load_country_data(path='climate.csv'):
    """Return monthly average temperatures for the five featured countries.

    One row per city-day in the source file. Temperatures are averaged per
    country and calendar month, then the monthly averages are kept per row.
    """
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month

    df['monthly_avg'] = (
        df.groupby(['country', 'month'])['avg_temp'].transform('mean').round(2)
    )
    return df[df['country'].isin(COUNTRIES)][
        ['country', 'month', 'monthly_avg', 'avg_max_temp', 'avg_min_temp']
    ].copy()


def build_summary_table(df):
    summary = df.groupby(['country', 'month']).agg(
        monthly_avg=('monthly_avg', 'mean'),
        avg_max_temp=('avg_max_temp', 'max'),
        avg_min_temp=('avg_min_temp', 'min'),
    ).reset_index().round(2)

    return dash_table.DataTable(
        summary.to_dict('records'),
        [{'name': c, 'id': c} for c in summary.columns],
        style_data={'color': 'black', 'backgroundColor': PAPER},
        style_header={'backgroundColor': 'rgb(210, 210, 210)',
                      'color': 'black', 'fontWeight': 'bold'},
    )


def style_figure(fig):
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='black')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='black')
    fig.update_layout(plot_bgcolor=PAPER, paper_bgcolor=PAPER, font_color='black')
    return fig


def build_figures(df, selected):
    # With nothing selected, show all five countries rather than an empty chart.
    selected = selected or COUNTRIES
    data = df[df['country'].isin(selected)]
    title_countries = ', '.join(selected)

    bar = style_figure(px.bar(
        data, x='month', y='monthly_avg', color='country', barmode='group',
        height=300, title=f'Monthly Averages of: {title_countries}',
    ))

    line = style_figure(px.line(
        data, x='month', y='monthly_avg', color='country', markers=True,
        height=300, title=f'Monthly Averages of: {title_countries}',
    ))

    choropleth = px.choropleth(
        data, locations='country', locationmode='country names',
        projection='natural earth', scope='africa',
        animation_frame='month', color='monthly_avg',
        color_continuous_scale=px.colors.sequential.Electric,
    )
    choropleth.update_layout(
        height=600,
        coloraxis_colorbar=dict(title='Average Temperature (°C)'),
        coloraxis=dict(cmin=data['monthly_avg'].min(), cmax=data['monthly_avg'].max()),
        plot_bgcolor=PAPER, paper_bgcolor=PAPER, font_color='black', geo_bgcolor=PAPER,
        updatemenus=[dict(type='buttons', showactive=False, buttons=[
            dict(label='Play', method='animate',
                 args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)]),
            dict(label='Pause', method='animate',
                 args=[[None], dict(frame=dict(duration=0, redraw=True), mode='immediate')]),
        ])],
    )
    return bar, line, choropleth


df_countries = load_country_data()

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = html.Div([
    html.H1("Weather Analysis for Africa's Top-5 Best Diving Destinations",
            style={'textAlign': 'center', 'color': '#008080', 'fontSize': '40px'}),
    html.Div(html.P('Monthly Averages of:', style={'fontSize': '20px', 'textAlign': 'center'}),
             style={'backgroundColor': '#50C878', 'color': 'white', 'marginLeft': 50,
                    'marginRight': 25, 'textAlign': 'center', 'borderRadius': '10px',
                    'borderStyle': 'double'}),
    html.Div([
        html.Div(', '.join(COUNTRIES),
                 style={'backgroundColor': '#007FFF', 'color': 'white', 'padding': '10px',
                        'width': '80%', 'margin': '20px auto', 'textAlign': 'center',
                        'borderRadius': '10px'}),
        build_summary_table(df_countries),
        dcc.Dropdown(COUNTRIES, value=COUNTRIES, multi=True, clearable=False,
                     id='country-dropdown',
                     style={'padding': '15px', 'backgroundColor': PAPER, 'color': 'purple'}),
        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='line-chart'),
        dcc.Graph(id='map-chart'),
    ]),
])


@callback(
    Output('bar-chart', 'figure'),
    Output('line-chart', 'figure'),
    Output('map-chart', 'figure'),
    Input('country-dropdown', 'value'),
)
def update_charts(selected):
    return build_figures(df_countries, selected)


if __name__ == '__main__':
    app.run(port=8092)
