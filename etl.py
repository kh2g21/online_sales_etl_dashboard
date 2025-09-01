from sqlalchemy import create_engine, text
import pandas as pd

# --- Database Connection ---
engine = create_engine("postgresql+psycopg2://postgres:************@localhost:8081/postgres")

# --- Load data from CSV ---
df = pd.read_csv("online_sales.csv")

# --- Create tables ---
with engine.connect() as conn:

    conn.execute(text("""
    CREATE TABLE DateDim (
        DateKey SERIAL PRIMARY KEY,
        FullDate DATE NOT NULL,
        Year INT,
        Quarter INT,
        Month VARCHAR(20),
        DayOfWeek VARCHAR(20),
        WeekOfYear INT
    );
    """))

    conn.execute(text("""
    CREATE TABLE ProductDim (
        ProductKey SERIAL PRIMARY KEY,
        ProductCategory VARCHAR(50),
        ProductName VARCHAR(100)
    );
    """))

    conn.execute(text("""
    CREATE TABLE RegionDim (
        RegionKey SERIAL PRIMARY KEY,
        Region VARCHAR(50)
    );
    """))

    conn.execute(text("""
    CREATE TABLE PaymentDim (
        PaymentKey SERIAL PRIMARY KEY,
        PaymentMethod VARCHAR(50)
    );
    """))

    conn.execute(text("""
    CREATE TABLE FactSales (
        TransactionID INT PRIMARY KEY,
        DateKey INT REFERENCES DateDim(DateKey),
        ProductKey INT REFERENCES ProductDim(ProductKey),
        RegionKey INT REFERENCES RegionDim(RegionKey),
        PaymentKey INT REFERENCES PaymentDim(PaymentKey),
        UnitsSold INT,
        UnitPrice NUMERIC(12,2),
        TotalRevenue NUMERIC(12,2)
    );
    """))

# --- Build Dimensions ---

# DateDim
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
date_dim = df[["Date"]].drop_duplicates().rename(columns={"Date": "FullDate"})
date_dim["Year"] = date_dim["FullDate"].dt.year
date_dim["Quarter"] = date_dim["FullDate"].dt.quarter
date_dim["Month"] = date_dim["FullDate"].dt.month
date_dim["DayOfWeek"] = date_dim["FullDate"].dt.day_name()
date_dim["WeekOfYear"] = date_dim["FullDate"].dt.isocalendar().week
date_dim.to_sql("DateDim", engine, if_exists="append", index=False)

# ProductDim
product_dim = df[["Product Category", "Product Name"]].drop_duplicates().rename(
    columns={"Product Category": "ProductCategory", "Product Name": "ProductName"})
product_dim.to_sql("ProductDim", engine, if_exists="append", index=False)

# RegionDim
region_dim = df[["Region"]].drop_duplicates()
region_dim.to_sql("RegionDim", engine, if_exists="append", index=False)

# PaymentDim
payment_dim = df[["Payment Method"]].drop_duplicates().rename(columns={"Payment Method": "PaymentMethod"})
payment_dim.to_sql("PaymentDim", engine, if_exists="append", index=False)

# --- Reload tables with keys for mapping ---
date_dim_db = pd.read_sql("SELECT * FROM DateDim", engine)
product_dim_db = pd.read_sql("SELECT * FROM ProductDim", engine)
region_dim_db = pd.read_sql("SELECT * FROM RegionDim", engine)
payment_dim_db = pd.read_sql("SELECT * FROM PaymentDim", engine)

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

fact_final = fact_df[[
    "Transaction ID", "DateKey", "ProductKey", "RegionKey", "PaymentKey",
    "Units Sold", "Unit Price", "Total Revenue"
]]

fact_final.to_sql("FactSales", engine, if_exists="append", index=False)

print("Data loaded into tables.")

