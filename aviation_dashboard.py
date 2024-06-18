import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Load the dataset
df = pd.read_csv('data/AviationData.csv', encoding='ISO-8859-1', low_memory=False)

# Clean the dataset
df['Event.Date'] = pd.to_datetime(df['Event.Date'], errors='coerce')
df['Year'] = df['Event.Date'].dt.year

# Calculate number of accidents per year
accidents_per_year = df.groupby('Year').size().reset_index(name='Accident_Count')

# Calculate risk assessment by aircraft category
severity_counts = df.groupby(['Aircraft.Category', 'Injury.Severity']).size().unstack(fill_value=0)
severity_counts['Risk_Score'] = severity_counts.get('Fatal', 0) / (severity_counts.sum(axis=1) + 1)
severity_counts = severity_counts.sort_values(by='Risk_Score', ascending=False).head(10)

# Calculate top 20 risky regions by accident frequency
top_risky_regions = df.groupby('Country').size().reset_index(name='Accident_Count')
top_risky_regions['Risk_Score'] = top_risky_regions['Accident_Count'] / top_risky_regions['Accident_Count'].sum()
top_risky_regions = top_risky_regions.sort_values(by='Accident_Count', ascending=False).head(10)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1('Aviation Accidents Dashboard'),

    html.Div([
        html.H2('Number of Accidents per Year'),
        dcc.Graph(
            id='accidents-per-year',
            figure=px.line(accidents_per_year, x='Year', y='Accident_Count', title='Number of Accidents per Year')
            .update_traces(mode='lines+markers', hoverinfo='x+y')
        )
    ]),

    html.Div([
        html.H2('Risk Assessment by Aircraft Category'),
        dcc.Graph(
            id='risk-by-aircraft-category',
            figure=px.bar(severity_counts, x=severity_counts.index, y='Risk_Score',
                          title='Top 10 Risky Aircraft Categories')
            .update_traces(hoverinfo='x+y')
        )
    ]),

    html.Div([
        html.H2('Top 10 Risky Regions by Accident Frequency'),
        dcc.Graph(
            id='top-risky-regions',
            figure=px.bar(top_risky_regions, x='Country', y='Accident_Count',
                          title='Top 10 Risky Regions by Accident Frequency')
            .update_traces(hoverinfo='x+y')
        )
    ]),
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
