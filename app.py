import plotly.express as px
import pandas as pd
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc

df_climate = pd.read_csv('/Users/lamiaebenouahi/Desktop/Spiced Bootcamp/weather_dash/climate.csv')
df_iso= pd.read_csv('/Users/lamiaebenouahi/Desktop/Spiced Bootcamp/weather_dash/iso_codes.csv')

merged_df = df_climate.merge(df_iso, on='country', how='left')

merged_df['date'] = pd.to_datetime(merged_df['date'])

merged_df['day'] = merged_df['date'].dt.day
merged_df['month'] = merged_df['date'].dt.month
merged_df['year'] = merged_df['date'].dt.year


merged_df_country = merged_df.sort_values(by='month', ascending=True)

df_morocco = merged_df_country[merged_df_country['country']=='Morocco']


df_morocco = df_morocco[['month', 'avg_temp', 'avg_max_temp', 'avg_min_temp']]

merged_df_country['monthly_avg']=merged_df_country.groupby(['country', 'month'])['avg_temp'].transform('mean')

d_table = dash_table.DataTable(df_morocco.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_morocco.columns],
                               style_data={'color': 'white','backgroundColor': 'black'},
                              style_header={
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'
    })

df_countries =merged_df_country[merged_df_country['country'].isin(['Morocco', 'Rwanda', 'South Africa'])]


fig =px.bar(df_countries, 
             x='month', 
             y='avg_temp',  
             color='country',
             barmode='group',
             height=300, title = "Morocco vs Rwanda & South Africa",)
graph = dcc.Graph()

fig2 = px.line(df_countries, x='month', y='monthly_avg', color='country', height=300, title="Average Temperature in Morocco, Rwanda & South Africa", markers=True)
graph2 = dcc.Graph(figure=fig2)

fig3 = px.choropleth(df_countries, locations='alpha-3', 
                    projection='natural earth', animation_frame="month",
                    scope='africa',
                    color='avg_temp', locationmode='ISO-3', 
                    color_continuous_scale=px.colors.sequential.Plasma)
graph3 = dcc.Graph(figure=fig3)


app =dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
server = app.server
countries =df_countries['country'].unique().tolist() 

dropdown = dcc.Dropdown(['Morocco', 'Rwanda', 'South Africa'], value=['Morocco', 'Rwanda', 'South Africa'], 
                        clearable=False, multi=True, style ={'paddingLeft': '30px', 
                                                             "backgroundColor": "#222222", "color": "#222222"})


app.layout = html.Div([html.H1('Weather Analysis', style={'textAlign': 'center', 'color': '#636EFA'}), 
                       html.Div(html.P("Using our  we take a look at Morocco's profile"), 
                                style={'marginLeft': 50, 'marginRight': 25}),
                       html.Div([html.Div('Morocco', 
                                          style={'backgroundColor': '#636EFA', 'color': 'white', 
                                                 'width': '900px', 'marginLeft': 'auto', 'marginRight': 'auto'}),
                                 d_table, dropdown, graph,  graph2, graph3])
                      ])
@callback(
    Output(graph, "figure"),
    Output(graph2, "figure"),
    Output(graph3, "figure"),
    Input(dropdown, "value"))

def update_bar_chart(countries): 
    mask = df_countries["country"].isin(countries) # coming from the function parameter
    fig =px.bar(df_countries[mask], 
             x='month', 
             y='avg_temp',  
             color='country',
             barmode='group',
             height=300, title = "Morocco vs Rwanda & South Africa",)
    fig = fig.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )
    fig2 = px.line(df_countries[mask], x='month', y='monthly_avg', color='country', height=300, title="Average Temperature in Morocco, Rwanda & South Africa", markers=True)
    fig2.update_layout(
    plot_bgcolor="#222222", 
    paper_bgcolor="#222222", 
    font_color="white"
    )
    fig3 = px.choropleth(df_countries[mask], locations='alpha-3', 
                    projection='natural earth', animation_frame="month",
                    scope='africa',
                    color='avg_temp', locationmode='ISO-3', 
                    color_continuous_scale=px.colors.sequential.Plasma)
    fig3 = fig3.update_layout(width=1000, height=600,
    coloraxis_colorbar=dict(title='Average Temperature (°C)'),
    coloraxis=dict(cmin=df_countries[mask]['avg_temp'].min(), cmax=df_countries[mask]['avg_temp'].max(),
    ))

    fig3 = fig3.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white", geo_bgcolor="#222222")
    
    return fig, fig2, fig3

if __name__ == "__main__":
    app.run_server()