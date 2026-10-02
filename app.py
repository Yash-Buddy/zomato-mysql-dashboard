import os
from urllib.parse import quote_plus

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import bindparam, create_engine, text

st.set_page_config(page_title="Zomato Dashboard", layout="wide")
st.title("Zomato Restaurants Dashboard")

# ---------- connection ----------
pwd = os.getenv("MYSQL_PASSWORD") or st.sidebar.text_input("MySQL password", type="password")
if not pwd:
    st.info("Enter your MySQL password in the sidebar.")
    st.stop()


@st.cache_resource
def get_engine(p):
    return create_engine(f"mysql+pymysql://root:{quote_plus(p)}@localhost:3306/zomato_db?charset=utf8mb4")


engine = get_engine(pwd)


def run(sql, params):
    stmt = text(sql)
    expanding = [bindparam(k, expanding=True) for k in ("cities", "prices") if k in params]
    if expanding:
        stmt = stmt.bindparams(*expanding)
    with engine.connect() as c:
        return pd.read_sql(stmt, c, params=params)


# ---------- sidebar filters ----------
st.sidebar.header("Filters")
all_cities = run("SELECT city FROM restaurants GROUP BY city ORDER BY COUNT(*) DESC", {})["city"].tolist()
cities = st.sidebar.multiselect("City (empty = all)", all_cities)
prices = st.sidebar.multiselect("Price range", [1, 2, 3, 4])
rmin, rmax = st.sidebar.slider("Rating", 0.0, 5.0, (0.0, 5.0), 0.1)
min_votes = st.sidebar.number_input("Minimum votes", 0, 10000, 0, 50)
delivery = st.sidebar.radio("Online delivery", ["All", "Yes", "No"], horizontal=True)

where = ["aggregate_rating BETWEEN :rmin AND :rmax", "votes >= :votes"]
params = {"rmin": rmin, "rmax": rmax, "votes": min_votes}
if cities:
    where.append("city IN :cities")
    params["cities"] = cities
if prices:
    where.append("price_range IN :prices")
    params["prices"] = prices
if delivery != "All":
    where.append("has_online_delivery = :deliv")
    params["deliv"] = delivery
W = "WHERE " + " AND ".join(where)

# ---------- KPIs ----------
k = run(f"""SELECT COUNT(*) AS n, ROUND(AVG(aggregate_rating),2) AS avg_rating,
                   COALESCE(SUM(votes),0) AS votes,
                   ROUND(100*AVG(has_online_delivery='Yes'),1) AS pct_delivery
            FROM restaurants {W}""", params).iloc[0]
if k["n"] == 0:
    st.warning("No restaurants match these filters.")
    st.stop()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Restaurants", f"{int(k['n']):,}")
c2.metric("Avg rating", k["avg_rating"])
c3.metric("Total votes", f"{int(k['votes']):,}")
c4.metric("Online delivery %", f"{k['pct_delivery']}%")

# ---------- row 1 ----------
a, b = st.columns(2)
df = run(f"SELECT city, COUNT(*) AS total FROM restaurants {W} GROUP BY city ORDER BY total DESC LIMIT 10", params)
a.plotly_chart(px.bar(df, x="city", y="total", title="Top 10 cities by restaurant count"), use_container_width=True)

df = run(f"""SELECT city, COUNT(*) AS total, ROUND(AVG(aggregate_rating),2) AS avg_rating
             FROM restaurants {W} GROUP BY city HAVING total >= 20
             ORDER BY avg_rating DESC LIMIT 10""", params)
b.plotly_chart(px.bar(df, x="city", y="avg_rating", title="Best-rated cities (min 20 restaurants)"), use_container_width=True)

# ---------- row 2 ----------
a, b = st.columns(2)
df = run(f"""SELECT has_table_booking, has_online_delivery, COUNT(*) AS total,
                    ROUND(AVG(aggregate_rating),2) AS avg_rating
             FROM restaurants {W} GROUP BY has_table_booking, has_online_delivery""", params)
a.plotly_chart(px.bar(df, x="has_table_booking", y="avg_rating", color="has_online_delivery",
                      barmode="group", title="Rating: table booking vs online delivery"), use_container_width=True)

df = run(f"""SELECT price_range, COUNT(*) AS total, ROUND(AVG(aggregate_rating),2) AS avg_rating,
                    ROUND(AVG(votes)) AS avg_votes
             FROM restaurants {W} GROUP BY price_range ORDER BY price_range""", params)
b.plotly_chart(px.bar(df, x="price_range", y="avg_rating", color="avg_votes",
                      title="Price range vs average rating"), use_container_width=True)

# ---------- row 3 ----------
a, b = st.columns(2)
df = run(f"SELECT rating_text, COUNT(*) AS total FROM restaurants {W} GROUP BY rating_text ORDER BY total DESC", params)
a.plotly_chart(px.pie(df, names="rating_text", values="total", title="Rating distribution"), use_container_width=True)

df = run(f"""SELECT cuisines, COUNT(*) AS total FROM restaurants {W} AND cuisines IS NOT NULL
             GROUP BY cuisines ORDER BY total DESC LIMIT 10""", params)
b.plotly_chart(px.bar(df, x="total", y="cuisines", orientation="h", title="Most common cuisine combos")
               .update_yaxes(autorange="reversed"), use_container_width=True)

# ---------- map ----------
df = run(f"""SELECT restaurant_name, city, aggregate_rating, votes, latitude, longitude
             FROM restaurants {W} AND latitude <> 0 AND longitude <> 0 LIMIT 3000""", params)
if not df.empty:
    df[["latitude", "longitude"]] = df[["latitude", "longitude"]].astype(float)
    fig = px.scatter_map(df, lat="latitude", lon="longitude", color="aggregate_rating",
                         hover_name="restaurant_name", hover_data=["city", "votes"],
                         zoom=3, height=500, title="Restaurant map (max 3000 points)",
                         color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)

# ---------- table ----------
st.subheader("Top-rated restaurants (by rating, then votes)")
df = run(f"""SELECT restaurant_name, city, cuisines, aggregate_rating, votes
             FROM restaurants {W} ORDER BY aggregate_rating DESC, votes DESC LIMIT 20""", params)
st.dataframe(df, use_container_width=True, hide_index=True)
