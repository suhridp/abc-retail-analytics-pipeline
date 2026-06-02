# ABC Retail Solutions - Retail Data Engineering Pipeline

Author: Suhrid Behari Paul

## Overview

This project implements an end-to-end retail data engineering pipeline for ABC Retail Solutions.

The objective is to transform raw retail transaction data from multiple source systems into a clean, standardized, and analytics-ready dataset that supports business intelligence reporting and decision-making.

The pipeline performs:

- Data ingestion from multiple Excel sources
- Schema validation and data quality checks
- Missing value handling
- Duplicate transaction removal
- Product and category standardization
- PII masking using SHA-256 hashing
- Business KPI generation
- Audit logging
- Power BI dashboard reporting

---

## Problem Statement

The source datasets contain several common data quality challenges:

- Missing prices
- Duplicate transactions
- Invalid quantities
- Inconsistent product naming conventions
- Mixed date formats
- Unprotected customer PII

These issues impact reporting accuracy and business decision-making.

The goal of this project is to create a reliable and reusable pipeline that produces trusted data for analytics.

---

## Architecture

```text
Excel Source Files
        │
        ▼
Data Ingestion
        │
        ▼
Schema Validation
        │
        ▼
Data Quality Checks
        │
        ▼
Data Cleaning
        │
        ▼
PII Masking
        │
        ▼
Data Transformation
        │
        ▼
KPI Generation
        │
        ▼
Audit Logging
        │
        ▼
Power BI Dashboard
```

---

## Source Data

The solution uses three datasets:

### product_details

Reference table containing:

- Product ID
- Product Name
- Category
- Standard Product Price

### retail_data1

Retail transaction records from source system 1.

### retail_data2

Retail transaction records from source system 2.

Combined transaction volume:

```text
8,494 records
```

---

## Data Cleaning Strategy

### Missing Price Handling

Missing prices are filled using:

1. Product reference price from the product dimension table
2. Category-level median price (fallback)

### Invalid Quantities

Records where:

```text
quantity <= 0
```

are removed.

### Duplicate Handling

Duplicate transactions are removed using transaction-level business keys.

### Standardization

Implemented for:

- Product names
- Categories
- Cities
- Payment fields
- Dates

Example:

```text
Elec        → Electronics
Furn        → Furniture
PHONE       → Phone
phone       → Phone
```

### PII Protection

The following fields are masked using SHA-256 hashing:

- customer_name
- email
- phone

---

## Transformation Logic

### Revenue

```text
Revenue = (Price × Quantity) − Discount
```

### Cost Assumption

The dataset does not contain product cost information.

For analytical purposes:

```text
Profitability Analysis

Since product cost information was not provided in the source data, category-specific cost assumptions were applied:

Electronics      → 80% cost
Furniture        → 60% cost
Clothing         → 50% cost
Home Appliances  → 70% cost

This allows profitability analysis while maintaining realistic retail margin differences across categories.
```

### Profit

```text
Profit = Revenue − Cost
```

### Additional Features

Generated fields include:

- transaction_year
- transaction_month
- transaction_week
- day_of_week
- discount_rate

---

## KPIs Generated

### Revenue Metrics

- Total Revenue
- Revenue by Category
- Revenue by City
- Revenue by Payment Method
- Revenue by Payment Status

### Product Metrics

- Top Products by Revenue
- Best Selling Products
- Most Profitable Products

### Operational Metrics

- Total Transactions
- Total Quantity Sold
- Average Order Value
- Total Discount Given
- Total Profit

---

## Latest Pipeline Run

| Metric | Value |
|----------|----------|
| Raw Records Loaded | 8,494 |
| Missing Prices Filled | 809 |
| Invalid Quantities Removed | 93 |
| Duplicate Records Removed | 487 |
| Final Records Exported | 7,914 |

---

## Output Files

```text
output/
├── retail_sales_cleaned.csv
├── retail_sales_cleaned.xlsx
├── kpis_summary.json
└── audit_log.json
```

### retail_sales_cleaned.csv

Curated dataset used as the Power BI source.

### kpis_summary.json

Generated KPI summary.

### audit_log.json

Pipeline execution metadata and processing statistics.

---

## Power BI Dashboard

The cleaned dataset is visualized using Power BI.

### Page 1 – Executive Dashboard

- Total Revenue
- Total Profit
- Total Transactions
- Average Order Value
- Revenue by Category
- Revenue by City

### Page 2 – Product Performance

- Top Products by Revenue
- Best Selling Products
- Most Profitable Products

### Page 3 – Category Trends

- Revenue by Category
- Profit by Category
- Quantity Sold by Category

### Page 4 – Regional Insights

- Revenue by City
- Profit by City
- Transactions by City

### Page 5 – Revenue Trends

- Monthly Revenue Trends
- Monthly Profit Trends
- Transaction Trends

### Page 6 – Data Quality Dashboard

- Rows Loaded
- Missing Prices Filled
- Invalid Quantities Removed
- Duplicate Records Removed
- Final Records Exported

---

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate:

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

```bash
python retail_data_pipeline.py \
  --input "NeoStats 2026 - USECASE - Data Engineering.xlsx" \
  --output output
```

---

## Technology Stack

- Python
- Pandas
- NumPy
- OpenPyXL
- XlsxWriter
- Power BI

---

## Repository Structure

```text
.
├── retail_data_pipeline.py
├── README.md
├── QUICK_START_GUIDE.md
├── PROJECT_DOCUMENTATION.docx
├── requirements.txt
│
├── output/
│   ├── retail_sales_cleaned.csv
│   ├── retail_sales_cleaned.xlsx
│   ├── kpis_summary.json
│   └── audit_log.json
│
├── powerbi/
│   ├── ABC_Retail_Dashboard.pbix
│   └── ABC_Retail_Dashboard.pdf
│
└── screenshots/
```

---

## Documentation

Additional project documentation is available in:

- PROJECT_DOCUMENTATION.docx
- QUICK_START_GUIDE.md

---

## Future Improvements

Potential enhancements include:

- Azure Data Factory orchestration
- Azure SQL Database integration
- Incremental loading
- Automated scheduling
- Data quality monitoring
- Cloud-native deployment

---

## License

Developed as part of the NeoStats Data Engineering Assessment.