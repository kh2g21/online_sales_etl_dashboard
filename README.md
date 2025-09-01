# online_sales_etl_dashboard

## Overview

This is a small project which I've recently worked on, which involved building a complete ETL (Extract, Transform, Load) pipeline for an online sales dataset - moving the data into a warehouse and performing visualization to discover data insights in Tableau. The goal was to transform raw  data into structured tables for analytics and build an interactive dashboard to explore key business metrics.

## Dataset

The dataset `online_sales.csv` contains transactional sales data for a variety of different products with the following fields:
- Transaction ID
- Date
- Product Category
- Product Name
- Units Sold
- Unit Price
- Total Revenue
- Region
- Payment Method

The dataset itself only contains sales information from the period January-August 2024; data for the remaining four months of the year is not included within the dataset. The dataset used can be found on [Kaggle](https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data).

## ETL Process

**Extract**:
The raw CSV data was read using the `pandas` library. Some cleaning had to be performed on the dataset, which included parsing the date to `datetime` objects and removing duplicates where necessary, to save disk space.

**Transform**:
When storing the data in tables, a star schema was chosen. This was because it would simplify the reporting phase of the project to be done later in Tableau, and would make analytical queries easier. For example, aggregation across different dimensions will be faster (e.g querying revenue by month, product or region) and queries for those metrics can be written efficiently with simple joins.

As part of the transforming process, dimension tables for `DateDim`, `ProductDim`, `RegionDim`, and `PaymentDim` were created. The `FactSales` table references those tables using the surrogate keys.

in the DateDim table, additional fields such as Year, Month, Quarter and WeekOfYear were added; by extracting date components using Python libraries. This will enable time-series analysis later in the project.

**Load**
Data was loaded into PostgreSQL using SQLAlchemy library in Python. PostgreSQL was chosen as the data warehouse for this project because of its local availability and also zero cost. If I was to implement something similar to this in a production context, then cloud-based warehouses such as Snowflake, BigQuery or Redshift would be preferred because of its scalability and ability to optimize storage.

Because the dataset I was working with was only 22KB, PostgreSQL was a reasonable trade-off - as it works well for small to medium datasets with ETL pipelines and doesn't incur any storage costs.

## Dashboard

The dashboard was built using Tableau Public (version `2025.2`). This utilised CSV exports from the PostgreSQL database rather than a live connection, as a direct database connection was not available in the environment which I used.

All CSVs were generated from the PostgreSQL tables (FactSales, DateDim, ProductDim, RegionDim, PaymentDim). 

These visualizations include:

**Revenue over Time (Line Chart)**

This visualization shows how sales revenue changes throughout the year. It highlights trends, seasonality, and months with unusually high or low revenue. By applying filters for product categories or regions, users can analyze revenue trends in a more granular way. This enables us to be able to answer different questions, such as finding out when the business experiened peak sales in the 8-month period available - or how revenue evolves over time; more specially across different regions. 

<img width="788" height="365" alt="image" src="https://github.com/user-attachments/assets/c459beb1-92a5-47b3-8256-9afdb03b8157" />

**Units Sold by Product Category (Bar Chart)**

This chart compares the sales volume across different product categories. It helps identify which categories are driving the most sales and which are underperforming. This visualization supports the ability to make strategic decisions related to inventory management, marketing - specifically which products to prioritize over others. We can also apply filters to perform time-series analysis; which enables users to analyse when peak sales and seasonal demand occur for different product lines.

<img width="800" height="374" alt="image" src="https://github.com/user-attachments/assets/beb69f24-b5fa-4984-b3bb-ec31da05f517" />

**Top Products by Revenue per Region (Top 10)**
This visualization shows the top 10 products generating the highest revenue within each region. It helps identify best-selling products regionally and informs product strategy and regional marketing efforts. Users can see which products are driving revenue in specific markets, and push promotions and deals for those products as necessary.

<img width="800" height="377" alt="image" src="https://github.com/user-attachments/assets/c63c9537-90cb-4311-90ba-0b3a23a4143e" />

**Total Revenue Across Regions (Horizontal Bar Chart)**

This chart shows overall revenue contributions from different regions. It highlights regional performance and identifies markets with the highest and lowest revenue, which would be useful for decisions related to market expansion, sales, and resource allocation.

All visualizations include interactive filters as described above, allowing users to dynamically explore data in different ways: by product, region, or time period. Dual-axis charts are used where multiple metrics need comparison, providing wider context for decision-making. The dashboard view is depicted below:

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5ae2171a-7c3e-4104-8335-e6292518069e" />

Together, these visualizations tell a cohesive story: they reveal revenue trends over time, product performance, regional contributions, and important product-regional insights. They enable data-driven decision-making and provide insights that would be valuable to both operational teams and business strategists.

Some of the key insights which can be drawn from the data is as follows:

- Revenue fluctuates throughout, peaking around February to April, where it reaches approximately 10,000–12,000, before declining towards the end of August. Sales volume follow a similar trend, though at a lower scale, mirroring the fluctuations in revenue.
- North America leads with the highest revenue, approximately 28,000–30,000, followed by Europe with around 20,000, and Asia with roughly 15,000.
- Electronics dominates with 29,908 units sold, followed by Home Appliances with 15,559 units, Sports with 11,269 units, Clothing with 6,264 units, Beauty Products with 1,987 units, and Books with 1,505 units. 
- Products such as Canon E., LG OLED, MacBook, Apple M., iPhone 1, Peloton, HP Spec, Roomba, Garmin, and Samsung generate varying revenue levels. North America consistently shows higher values (e.g., around 3,900 for one product) compared to Asia (approximately 600) and Europe (ranging between 1,000–2,600).


## Considerations for future work 

If I were to follow a similar process in industry, there are different design choices I would make. The first of which, is as mentioned above, the use of a cloud data warehouse. I would use tools such as Snowflake, BigQuery or Redshift for greater storage and scability to enable the use of bigger datasets and better query performance. Concerning the ETL process itself, I would likely utilise workflow orchestration tools like Apache Airflow, as in a professional ETL and analytics workflow, I would prefer for dashboards and reports to stay up-to-date automatically without the need to manually intervene. 

Another final point of consideration would be the choice of dataset; having conducted research into available sales APIs, these either required purchase or were difficult to obtain without seeking official permission. And as I had chosen PostgreSQL as the data warehouse, the possibilites of choosing a large dataset for this task were very slim; as this would have likely involved running out of disk space. Therefore, this sales dataset from Kaggle was a reasonable compromise as the file size wasn't very big and scaled well with my choice of data warehouse. However, as mentioned above, this dataset only contained sales information from January until August; any additional data for the remainder of the year was missing - which has limited my analysis and reporting scope. There are additional findings and insights from the data which I will have likely missed. The regional sales data isn't very granular; as the countries in which the sales took place are not specified in the dataset, but only the continent itself. The opportunity to do further analysis in this area was also missed.

## How to run

1. Clone the repo

```
git clone https://github.com/kh2g21/online_sales_etl_dashboard.git
cd online_sales_etl_dashboard
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Make sure that PostgreSQL is installed and running locally. Create a database and update connection details in etl.py with your username, password, port.
   
4. Run ETL script (if from the command line, `python etl.py`)

5. Open `Online_Sales_Dashboard.twbx` in Tableau. Tableau will automatically load the exported dimension/fact CSVs and the visualizations should appear.

 
