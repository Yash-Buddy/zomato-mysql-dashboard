import getpass
import pandas as pd
from sqlalchemy import create_engine

CSV = "zomato.csv"
pwd = getpass.getpass("MySQL root password: ")

df = pd.read_csv(CSV, encoding="latin-1")
df = df.drop(columns=["Switch to order menu"])
df.columns = [
    "restaurant_id", "restaurant_name", "country_code", "city", "address",
    "locality", "locality_verbose", "longitude", "latitude", "cuisines",
    "avg_cost_for_two", "currency", "has_table_booking", "has_online_delivery",
    "is_delivering_now", "price_range", "aggregate_rating", "rating_color",
    "rating_text", "votes",
]

engine = create_engine(f"mysql+pymysql://root:{pwd}@localhost:3306/zomato_db?charset=utf8mb4")
df.to_sql("restaurants", engine, if_exists="append", index=False, chunksize=1000)
print("Loaded rows:", len(df))
