import plotly.express as px
import pandas as pd
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc

df_climate = pd.read_csv('climate.csv')
df_iso= pd.read_csv('iso_codes.csv')

merged_df = df_climate.merge(df_iso, on='country', how='left')

merged_df['date'] = pd.to_datetime(merged_df['date'])

merged_df['day'] = merged_df['date'].dt.day
merged_df['month'] = merged_df['date'].dt.month
merged_df['year'] = merged_df['date'].dt.year


merged_df_country = merged_df.sort_values(by='month', ascending=True)
merged_df_country['monthly_avg']=merged_df_country.groupby(['country', 'month'])['avg_temp'].transform('mean')

df_morocco = merged_df_country[merged_df_country['country']=='Morocco']


df_morocco = df_morocco[['month', 'avg_temp', 'avg_max_temp', 'avg_min_temp']]

df_countries =merged_df_country[merged_df_country['country'].isin(['Egypt', 'South Africa', 'Mozambique','Tanzania','Sudan'])]
df_countries = df_countries[['country','alpha-3','month', 'monthly_avg', 'avg_max_temp', 'avg_min_temp']]
df_countries['alpha-3'] = df_countries['alpha-3'].fillna('TZ')

monthly_country_aggregates = df_countries.groupby(['country', 'month']).agg({
    'monthly_avg': 'mean', 'avg_max_temp': 'max', 'avg_min_temp':'min',
}).reset_index()
d_table = dash_table.DataTable(monthly_country_aggregates.to_dict('records'),
                                  [{"name": i, "id": i} for i in monthly_country_aggregates.columns],
                               style_data={'color': 'black','backgroundColor': '#FFFFE0'},
                              style_header={
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'
    })

fig =px.bar(df_countries, 
             x='month', 
             y='monthly_avg',  
             color='country',
             barmode='group',
            color_discrete_sequence=px.colors.qualitative.Plotly,
             height=300, title = "Monthly Averages of : Egypt, South Africa, Mozambique, Tanzania",)
graph = dcc.Graph()

fig2 = px.line(df_countries, x='month', y='monthly_avg', color='country', height=300, title="Average Temperature in Egypt, South Africa, Mozambique, Tanzania", markers=True)
graph2 = dcc.Graph(figure=fig2)

fig3 = px.choropleth(df_countries, locations='country', 
                    projection='natural earth', animation_frame="month",
                    scope='africa',
                    color='monthly_avg', locationmode='country names', 
                    color_continuous_scale=px.colors.sequential.Electric)
graph3 = dcc.Graph(figure=fig3)


app =dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
countries =df_countries['country'].unique().tolist() 

dropdown = dcc.Dropdown(['Egypt', 'South Africa', 'Mozambique','Tanzania','Sudan'], value=['Egypt', 'South Africa', 'Mozambique','Tanzania','Sudan'], 
                        clearable=False, multi=True, style ={'padding': '15px', 'backgroundColor': '#FFFFE0', 'color': 'purple'})


app.layout = html.Div([html.H1('Weather Analysis for Africas Top-5 Best Diving Destinations', style={'textAlign': 'center', 'color': '#008080', 'fontSize': '40px'}),
                      html.Div(html.P("Monthly Averages of:", style={'fontSize': '20px', 'textAlign': 'center'}), 
                         style={'backgroundColor': '#50C878','color': 'white','marginLeft': 50, 'marginRight': 25, 'textAlign': 'center', 'borderRadius': '10px','borderstyle':'double'}),
                       html.Div([html.Div('Egypt, South Africa, Mozambique, Tanzania , Sudan', 
                                          style={'backgroundColor': '#007FFF', 'color': 'white', 'padding': '10px', 
                        'width': '80%', 'margin': '20px auto', 'textAlign': 'center', 'borderRadius': '10px'}),
                                d_table,dropdown, graph,  graph2, graph3])
                      ])
@callback(
    Output(graph, "figure"),
    Output(graph2, "figure"),
    Output(graph3, "figure"),
    Input(dropdown, "value"))

def update_bar_chart(countries): 
    mask = df_countries["country"].isin(countries) 
    fig =px.bar(df_countries[mask], 
             x='month', 
             y='monthly_avg',  
             color='country',
            barmode='group',
             height=300, title = 'Monthly Averages of: Egypt, South Africa, Mozambique, Tanzania & Sudan',)
    fig = fig.update_layout(
        plot_bgcolor="#FFFFE0", paper_bgcolor="#FFFFE0", font_color="black"
    )
    fig2 = px.line(df_countries[mask], x='month', y='monthly_avg', color='country', height=300, title="Monthly Averages of : Egypt, South Africa, Mozambique, Tanzania & Sudan", markers=True)
    fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='black')
    fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='black')
    fig2.update_layout(
    plot_bgcolor="#FFFFE0", 
    paper_bgcolor="#FFFFE0", 
    font_color="black"
    )
    fig3 = px.choropleth(df_countries[mask], locations='country', 
                    projection='natural earth', animation_frame="month",
                    scope='africa',
                    color='monthly_avg', locationmode='country names', 
                    color_continuous_scale=px.colors.sequential.Electric)
    fig3 = fig3.update_layout(height=600,
    coloraxis_colorbar=dict(title='Average Temperature (°C)'),
    coloraxis=dict(cmin=df_countries[mask]['monthly_avg'].min(), cmax=df_countries[mask]['monthly_avg'].max(),
    ))

    fig3 = fig3.update_layout(
        plot_bgcolor="#FFFFE0", paper_bgcolor="#FFFFE0", font_color="black", geo_bgcolor="#FFFFE0")
    fig3.update_layout(updatemenus=[
    dict(type='buttons', showactive=False, buttons=[
        dict(label='Play', method='animate', args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)]),
        dict(label='Pause', method='animate', args=[[None], dict(frame=dict(duration=0, redraw=True), mode='immediate')]),
    ])
])
    
    return fig, fig2, fig3

if __name__ == "__main__":
    app.run_server(port=8092)