from sqlalchemy import create_engine, text
import pandas as pd

# --- Database Connection ---
engine = create_engine("postgresql+psycopg2://postgres:bdjlmttla123@localhost:8081/postgres")

# --- Load Source Data ---
df = pd.read_csv("online_sales.csv")

# --- Drop all tables to start fresh ---
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS FactSales CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS DateDim CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS ProductDim CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS RegionDim CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS PaymentDim CASCADE;"))

# --- Build Dimensions ---

# DateDim
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
date_dim = df[["Date"]].drop_duplicates().rename(columns={"Date": "FullDate"})
date_dim["Year"] = date_dim["FullDate"].dt.year
date_dim["Quarter"] = date_dim["FullDate"].dt.quarter
date_dim["Month"] = date_dim["FullDate"].dt.month
date_dim["DayOfWeek"] = date_dim["FullDate"].dt.day_name()
date_dim["WeekOfYear"] = date_dim["FullDate"].dt.isocalendar().week
date_dim.to_sql("DateDim", engine, if_exists="replace", index=True, index_label="DateKey")

# ProductDim
product_dim = df[["Product Category", "Product Name"]].drop_duplicates().rename(
    columns={"Product Category": "ProductCategory", "Product Name": "ProductName"})
product_dim.to_sql("ProductDim", engine, if_exists="replace", index=True, index_label="ProductKey")

# RegionDim
region_dim = df[["Region"]].drop_duplicates()
region_dim.to_sql("RegionDim", engine, if_exists="replace", index=True, index_label="RegionKey")

# PaymentDim
payment_dim = df[["Payment Method"]].drop_duplicates().rename(columns={"Payment Method": "PaymentMethod"})
payment_dim.to_sql("PaymentDim", engine, if_exists="replace", index=True, index_label="PaymentKey")

# --- Reload dimension tables with surrogate keys ---
date_dim_db = pd.read_sql("SELECT * FROM \"DateDim\"", engine)
product_dim_db = pd.read_sql("SELECT * FROM \"ProductDim\"", engine)
region_dim_db = pd.read_sql("SELECT * FROM \"RegionDim\"", engine)
payment_dim_db = pd.read_sql("SELECT * FROM \"PaymentDim\"", engine)

# --- Build Fact Table ---
fact_df = df.copy()
fact_df["Date"] = pd.to_datetime(fact_df["Date"], format="%d/%m/%Y", errors="coerce")

# Map DateKey
fact_df = fact_df.merge(date_dim_db, left_on="Date", right_on="FullDate", how="left")

# Map ProductKey
fact_df = fact_df.merge(product_dim_db, left_on=["Product Category", "Product Name"],
                        right_on=["ProductCategory", "ProductName"], how="left")

# Map RegionKey
fact_df = fact_df.merge(region_dim_db, on="Region", how="left")

# Map PaymentKey
fact_df = fact_df.merge(payment_dim_db, left_on="Payment Method", right_on="PaymentMethod", how="left")

# Keep only fact columns
fact_final = fact_df[[
    "Transaction ID", "DateKey", "ProductKey", "RegionKey", "PaymentKey",
    "Units Sold", "Unit Price", "Total Revenue"
]]

fact_final.to_sql("FactSales", engine, if_exists="replace", index=False)

print("✅ ETL completed successfully. Data loaded into PostgreSQL.")
