# Zomato Restaurants Dashboard

Interactive dashboard built with MySQL + Python (Plotly) + Streamlit.
All filtering, sorting and aggregation (WHERE, HAVING, GROUP BY, ORDER BY) runs in MySQL.

## Dataset
Zomato restaurants (9,551 rows) from Kaggle. Download `zomato.csv` and place it in the project folder.

## Setup
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
1. Run `01_schema.sql` in MySQL to create `zomato_db` and the `restaurants` table.
2. Load the data: `python 02_load_data.py`
3. Start the dashboard: `streamlit run app.py`

## Features
KPI cards, sidebar filters, city and cuisine charts, map, top-restaurants table.
