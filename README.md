# Africa Temperature Dashboard

An interactive Dash app that compares monthly average temperatures across five African countries: Egypt, South Africa, Mozambique, Tanzania, and Sudan.

**Live app:** https://weather-dashapp-qpu9.onrender.com

## What it shows

- A summary table of monthly averages, maximum temperatures, and minimum temperatures for each country.
- A grouped bar chart and a line chart of monthly averages.
- An animated choropleth map showing how average temperatures change month by month.
- A country dropdown that filters all three charts.

## Data

- `climate.csv`: city-level daily temperature records (maximum, minimum, and average) for 211 countries, covering September 2022 to September 2023.
- `iso_codes.csv`: country names, ISO alpha-3 codes, and regions. The current app doesn't use this file, but it's kept for future joins.

## Limitations

- The data covers one year, so each "monthly average" reflects a single year of observations, not a long-term climate baseline.
- Sudan has two cities in the source data. The averages combine both cities.
- The five countries were chosen for the analysis, not ranked against other destinations.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:8092.

## Deployment

The app exposes a WSGI server object named `server`, so it can run under gunicorn:

```bash
gunicorn app:server
```

## Files

- `app.py`: data preparation, figure construction, and the Dash layout and callback
- `Friday.ipynb`: the exploratory notebook the app was built from
- `climate.csv`, `iso_codes.csv`: source data
