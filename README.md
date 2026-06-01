ABC RETAIL SOLUTIONS
RETAIL DATA ENGINEERING PIPELINE
End-to-End Data Processing and Business Intelligence Solution

===============================================================================

PROJECT OVERVIEW

ABC Retail Solutions has implemented an end-to-end retail data engineering 
pipeline designed to transform raw transaction data from multiple source systems 
into a clean, standardized, and analytics-ready dataset for business reporting 
and decision-making.

The solution addresses critical data quality challenges including missing values, 
duplicate transactions, invalid quantities, inconsistent product naming, mixed 
date formats, and unprotected personally identifiable information (PII).

This pipeline demonstrates professional data engineering practices including 
comprehensive validation, systematic cleaning, security-conscious PII protection, 
and audit trail generation suitable for regulatory compliance.

===============================================================================

PROBLEM STATEMENT

ABC Retail Solutions operates across multiple retail locations and receives 
transaction data from different source systems. Current challenges include:

- Missing price information in approximately 5% of records
- Duplicate transactions across systems (600-700 records)
- Invalid quantity entries (quantities less than or equal to zero)
- Inconsistent product and category naming conventions
- Mixed date formats across datasets
- Unprotected customer PII (names, emails, phone numbers)
- No standardized business KPI calculations
- Unreliable revenue reporting by category, city, and payment method

These issues result in inaccurate financial analysis, regulatory compliance risks, 
and unreliable reporting dashboards. The pipeline solution systematically 
addresses each issue through validated transformation logic.

===============================================================================

SOLUTION ARCHITECTURE

DATA FLOW

Excel Source Files
    |
    v
Data Ingestion (Load all sheets)
    |
    v
Schema Validation (Verify required columns)
    |
    v
Data Quality Assessment (Profile nulls, duplicates, types)
    |
    v
Data Cleaning (Impute, deduplicate, standardize)
    |
    v
PII Protection (Hash sensitive customer data)
    |
    v
Data Transformation (Join dimensions, create metrics)
    |
    v
KPI Generation (Calculate business metrics)
    |
    v
Audit Logging (Record pipeline execution)
    |
    v
Export Outputs (CSV, Excel, JSON formats)
    |
    v
Power BI Dashboard (Interactive visualization)


SOURCE DATA SPECIFICATION

Input: Single Excel workbook containing three sheets

product_details (Reference Table)
  - 10 products
  - Columns: product_id, product_name, category, price
  - Purpose: Product dimension for enrichment and validation

retail_data1 (Transaction Data - System 1)
  - 4,243 transaction records
  - Columns: transaction_id, customer_id, customer_name, product_id, price,
             quantity, transaction_date, city, category, payment_method,
             discount, email, phone, payment_status
  - Source: System A

retail_data2 (Transaction Data - System 2)
  - 4,251 transaction records
  - Columns: Same as retail_data1
  - Source: System B
  - Note: Contains overlapping records with retail_data1

Combined Input: 8,494 transaction records


SOFTWARE ARCHITECTURE

The pipeline is implemented using object-oriented design with six specialized 
classes, each handling a specific responsibility in the data processing workflow.

DataLoader
  Responsibility: Data source ingestion
  Methods:
    - load_all_sheets(): Load all worksheets from Excel file
    - validate_sheet_exists(): Verify required sheets are present
  Dependencies: pandas, openpyxl

DataValidator
  Responsibility: Data quality assessment
  Methods:
    - validate_schema(): Check for required columns
    - profile_data_quality(): Generate quality report with null counts,
                             duplicates, and data types
  Dependencies: pandas

DataCleaner
  Responsibility: Data preparation and standardization
  Methods:
    - handle_missing_prices(): Impute null prices using product dimension
                               lookup and category median fallback
    - remove_duplicates(): Remove exact and transaction-level duplicates
    - handle_invalid_quantities(): Remove records with quantity <= 0
    - standardize_values(): Normalize text casing and date formats
    - standardize_product_names(): Clean product name variations
    - mask_pii(): Hash customer PII using SHA-256
    - clean_full_pipeline(): Orchestrate all cleaning operations
  Dependencies: pandas, hashlib

DataTransformer
  Responsibility: Feature engineering and metric creation
  Methods:
    - enrich_with_product_dimension(): Join with product reference table
    - calculate_business_metrics(): Create revenue, profit, and temporal
                                    features
  Dependencies: pandas, numpy

KPIAggregator
  Responsibility: Business metric calculation
  Methods:
    - calculate_kpis(): Compute global and dimensional KPIs
    - print_kpi_summary(): Display formatted KPI output
  Dependencies: pandas

DataExporter
  Responsibility: Output generation and serialization
  Methods:
    - export_to_csv(): Save dataset as CSV
    - export_to_excel(): Save dataset as Excel workbook
    - export_kpis_to_json(): Serialize KPIs as JSON
    - export_audit_log(): Create execution audit trail
  Dependencies: pandas, json, pathlib

===============================================================================

DATA PROCESSING WORKFLOW

STEP 1: DATA INGESTION

Input: Excel workbook with three sheets
Process:
  - Load product_details dimension table
  - Load retail_data1 transaction set
  - Load retail_data2 transaction set
  - Combine retail datasets using union (concatenation)
  - Initial row count: 8,494

Output: Combined DataFrame ready for validation


STEP 2: SCHEMA VALIDATION

Process:
  - Verify all required columns are present in each dataset
  - Validate primary key (transaction_id) is not null
  - Check data types are appropriate
  - Generate quality profile with null counts and duplicates

Output: Validation report, warnings for issues identified


STEP 3: DATA CLEANING

Price Imputation (404-405 missing values)
  Tier 1 - Product Dimension Lookup:
    - Create mapping: product_id -> standard_price
    - Fill null prices using product reference table
    - Expected fill rate: 95%
  
  Tier 2 - Category Median Fallback:
    - Calculate median price per product category
    - Fill remaining nulls with category median
    - Ensures 100% price coverage

Duplicate Removal (580-623 duplicate records)
  Level 1 - Exact Duplicates:
    - Drop rows where all columns are identical
  
  Level 2 - Transaction-Level Duplicates:
    - Identify records with same customer_id, product_id, transaction_date,
      quantity, and price
    - Keep first occurrence, remove others

Invalid Quantity Removal (93 records)
  - Remove records where quantity <= 0
  - Ensures positive transaction volumes only

Value Standardization
  - Category: Trim whitespace, apply title case
  - City: Trim whitespace, apply title case
  - Payment Method: Trim whitespace, apply title case
  - Payment Status: Trim whitespace, apply title case
  - Product Names: Trim whitespace, normalize spacing
  - Transaction Dates: Parse to ISO 8601 format (YYYY-MM-DD)

Output: 7,914 cleaned records (6.8% reduction)


STEP 4: PII PROTECTION

Approach: Irreversible SHA-256 salted hashing
  - Not encryption (cannot decrypt, meets regulatory requirements)
  - Deterministic (same input always produces same hash)
  - One-way function (cannot reverse)
  - Allows row-level joining using consistent hashes

Implementation:
  hash_value = SHA256(original_value + salt)[:16 characters]
  salt = "ABC_Default_Salt"

Columns Masked:
  - customer_name -> customer_name_masked
  - email -> email_masked
  - phone -> phone_masked

Original PII columns are deleted after masking.

Output: Dataset with masked PII, no sensitive customer data exposed


STEP 5: DATA TRANSFORMATION

Dimension Enrichment:
  - Left join transaction data with product dimension table
  - Preserve all transactions (no rows lost)
  - Add standardized product names

Business Metric Creation:
  Revenue Calculation:
    formula: (price * quantity) - discount
    validation: clipped at 0 (no negative revenue)
    example: price=100, qty=2, discount=10 => revenue=190
  
  Cost Estimation:
    formula: (price * quantity) * 0.4
    assumption: 40% of transaction value is cost (60% margin)
    example: price=100, qty=2 => cost=80
  
  Profit Calculation:
    formula: revenue - cost
    range: 0 to revenue (by construction)
    example: cost=80, revenue=190 => profit=110
  
  Time Features:
    - transaction_year: Calendar year
    - transaction_month: Month (1-12)
    - transaction_week: ISO week number
    - day_of_week: Day name (Monday, Tuesday, etc.)
  
  Discount Rate:
    formula: discount / (price * quantity)
    range: 0.0 to 1.0
    usage: Identify over-discounting products

Output: Enriched dataset with calculated business metrics


STEP 6: KPI AGGREGATION

Global Metrics:
  - Total Revenue: Sum of all transaction revenues
  - Total Transactions: Count of unique transaction_ids
  - Average Order Value: Total revenue / transaction count
  - Total Profit: Sum of all profits
  - Total Discount Given: Sum of discount amounts

Category Analysis:
  - Revenue by Category
  - Transactions by Category
  - Average Price by Category

Geographic Analysis:
  - Revenue by City (5 cities: Mumbai, Delhi, Bangalore, Hyderabad, Chennai)
  - Transactions by City

Payment Analysis:
  - Revenue by Payment Method (Card, Cash, UPI, Netbanking)
  - Revenue by Payment Status (Successful, Failed, Pending)

Product Performance:
  - Top 10 Products by Revenue
  - Best Selling Products by Quantity
  - Most Profitable Products

Output: Structured KPI dictionary in JSON format


STEP 7: AUDIT LOGGING

Execution metadata recorded:
  - rows_loaded: 8,494 (initial combined count)
  - rows_cleaned: 7,914 (after all cleaning steps)
  - rows_exported: 7,914 (final output count)
  - run_timestamp: ISO 8601 datetime of execution
  - pipeline_status: SUCCESS or FAILED

Purpose: Process monitoring, compliance verification, audit trail

Output: audit_log.json file


===============================================================================

SYSTEM REQUIREMENTS

Hardware:
  - RAM: 4 GB minimum (pipeline uses 300-500 MB)
  - Storage: 1 GB free space (for input and output files)
  - CPU: Standard processor (no special requirements)

Software Requirements:
  - Python 3.8 or higher
  - Git (for version control)
  - Power BI Desktop (for dashboard visualization)

Python Libraries:
  - pandas >= 1.3.0 (data manipulation)
  - numpy >= 1.20.0 (numerical computing)
  - openpyxl >= 3.0.0 (Excel reading)
  - Standard library: os, logging, hashlib, json, pathlib, argparse, datetime


INSTALLATION INSTRUCTIONS

Step 1: Install Python
  Download from https://www.python.org/downloads/
  Verify installation: python --version

Step 2: Set Up Project Directory
  mkdir retail-data-pipeline
  cd retail-data-pipeline

Step 3: Create Virtual Environment
  
  On macOS/Linux:
  python3 -m venv venv
  source venv/bin/activate
  
  On Windows:
  python -m venv venv
  venv\Scripts\activate

Step 4: Install Dependencies
  pip install pandas numpy openpyxl python-dateutil

Step 5: Place Input Data
  Copy the Excel file to the project root directory:
  NeoStats_2026_-_USECASE_-_Data_Engineering.xlsx


EXECUTION INSTRUCTIONS

Basic Execution:
  python retail_data_pipeline.py \
    --input "NeoStats_2026_-_USECASE_-_Data_Engineering.xlsx" \
    --output "output"

Expected Execution Output:
  2026-06-01 23:34:25 | INFO | ABC RETAIL SOLUTIONS PIPELINE STARTING
  2026-06-01 23:34:26 | INFO | Loading Excel file...
  2026-06-01 23:34:27 | INFO | Found sheets: ['product_details', 'retail_data1', 'retail_data2']
  2026-06-01 23:34:28 | INFO | Combining retail datasets... (8,494 rows)
  2026-06-01 23:34:30 | INFO | DATA CLEANING PIPELINE STARTING
  2026-06-01 23:34:31 | INFO | Missing prices handled: 809 rows filled
  2026-06-01 23:34:32 | INFO | Invalid quantities removed: 93
  2026-06-01 23:34:33 | INFO | Duplicates removed: 487
  2026-06-01 23:34:35 | INFO | Values standardized
  2026-06-01 23:34:36 | INFO | PII masked: customer_name, email, phone
  2026-06-01 23:34:38 | INFO | Enrichment complete: 7,914 rows
  2026-06-01 23:34:40 | INFO | Business metrics calculated
  2026-06-01 23:34:42 | INFO | KEY PERFORMANCE INDICATORS
  2026-06-01 23:34:42 | INFO | Total Revenue: 1,501,410,824.60
  2026-06-01 23:34:42 | INFO | Total Transactions: 7,914
  2026-06-01 23:34:45 | INFO | Exporting data...
  2026-06-01 23:34:46 | INFO | PIPELINE EXECUTION COMPLETED SUCCESSFULLY

Success Indicators:
  - No error messages in output
  - Exit code is 0
  - All four output files created in output/ directory


===============================================================================

OUTPUT SPECIFICATIONS

The pipeline generates four output files in the output directory:

1. retail_sales_cleaned.csv
   Format: CSV (comma-separated values)
   Size: Approximately 1.9 MB
   Rows: 7,914 transaction records
   Columns: 30+ (transaction fields plus calculated metrics)
   Encoding: UTF-8
   Purpose: Primary dataset for Power BI import
   
   Key Columns:
     - transaction_id (unique identifier)
     - customer_id
     - customer_name_masked (hashed)
     - product_name_standardized
     - category
     - city
     - transaction_date (ISO format)
     - quantity
     - price
     - revenue (calculated)
     - profit (calculated)
     - payment_method
     - payment_status
     - discount_rate
     - transaction_year, transaction_month, transaction_week, day_of_week

2. retail_sales_cleaned.xlsx
   Format: Microsoft Excel 2007+ (.xlsx)
   Size: Approximately 1.3 MB
   Sheet: "Retail Data" containing same content as CSV
   Purpose: Backup format, local analysis
   Usage: Can be opened directly in Excel or Power BI

3. kpis_summary.json
   Format: JSON (JavaScript Object Notation)
   Size: Approximately 2.1 KB
   Content: All calculated business KPIs
   
   Structure:
     Global Metrics:
       - Total Revenue
       - Total Transactions
       - Total Quantity Sold
       - Average Order Value
       - Total Discount Given
       - Total Profit
     
     Dimensional Aggregations:
       - Revenue by Category
       - Transactions by Category
       - Avg Price by Category
       - Revenue by City
       - Transactions by City
       - Revenue by Payment Method
       - Revenue by Payment Status
       - Top Products by Revenue
       - Best Selling Products
       - Most Profitable Products
   
   Purpose: API consumption, dashboard data, metric reference
   Format: Human-readable with indentation

4. audit_log.json
   Format: JSON
   Size: Approximately 155 bytes
   Content:
     - rows_loaded: 8,494
     - rows_cleaned: 7,914
     - rows_exported: 7,914
     - run_timestamp: 2026-06-01T23:34:46.683521
     - pipeline_status: SUCCESS
   
   Purpose: Execution tracking, compliance verification, audit trail


VERIFICATION CHECKLIST

After pipeline execution, verify:

Data Output:
  - All four output files are created in output/ directory
  - retail_sales_cleaned.csv contains 7,914 rows of data
  - retail_sales_cleaned.xlsx opens correctly in Excel
  - kpis_summary.json is valid JSON (can be parsed)
  - audit_log.json is valid JSON

Data Quality:
  - Customer names are masked (16-character hashes, not original names)
  - Email addresses are masked (16-character hashes)
  - Phone numbers are masked (16-character hashes)
  - Revenue column contains numeric values (no nulls)
  - Profit column contains numeric values (no negative values)
  - All transaction_ids are unique (no duplicates)
  - All product_names are standardized (title case, consistent)
  - All cities are title-cased (no lowercase or uppercase variations)

Business Logic:
  - Revenue equals (price * quantity) - discount
  - Profit equals revenue - cost
  - Profit is always less than or equal to revenue
  - Average Order Value equals total revenue / transaction count
  - Category, city, and payment method totals sum to overall totals

KPI Accuracy:
  - Total Revenue: 1,501,410,824.60
  - Total Transactions: 7,914
  - Average Order Value: 189,715.79
  - All cities are represented (5 cities total)
  - All categories are represented (4 categories total)
  - Top products list contains realistic product names


POWER BI DASHBOARD

The cleaned dataset is designed to be imported into Power BI for interactive 
visualization. The recommended dashboard structure includes:

Page 1: Executive Summary
  - KPI cards displaying total revenue, transactions, AOV, profit
  - Revenue trend line chart by month
  - Top 5 categories bar chart

Page 2: Revenue Analysis
  - Revenue by city (map or table)
  - Revenue by payment method (donut chart)
  - Payment status breakdown
  - Daily/weekly revenue trend

Page 3: Product Performance
  - Top 10 products by revenue (horizontal bar)
  - Best selling products by quantity
  - Most profitable products

Page 4: Category Analysis
  - Revenue distribution by category (pie chart)
  - Category performance table
  - Category revenue trend area chart

Page 5: Regional Insights
  - Top cities ranking (table with metrics)
  - City-category performance heatmap
  - Geographic revenue distribution

Page 6: Data Quality Dashboard
  - Rows ingested
  - Missing prices filled
  - Invalid quantities removed
  - Duplicates removed
  - Final records exported

Interactive Features:
  - Date range slicer for temporal filtering
  - Category multi-select for product analysis
  - City filter for regional focus
  - Payment method filter for payment analysis
  - Cross-page filtering and drill-down capabilities
  - Conditional formatting for metric highlighting
  - Mobile-responsive design


DATA QUALITY METRICS

Latest Execution Results:

Raw data loaded: 8,494 rows
  - retail_data1: 4,243 rows
  - retail_data2: 4,251 rows

Cleaning Operations:
  - Missing prices imputed: 809 rows
  - Invalid quantities removed: 93 rows
  - Duplicate transactions removed: 487 rows
  
Total rows after cleaning: 7,914 rows
Data reduction: 6.8% (acceptable threshold)

KPI Results:
  - Total Revenue: 1,501,410,824.60 (reasonable magnitude)
  - Total Profit: 900,845,784.60 (60% of revenue, matches cost assumptions)
  - Average Order Value: 189,715.79 (consistent with product mix)
  - Total Discount Given: 1,775.40 (0.12% of revenue, minimal discounting)

Category Distribution:
  - Electronics: 870,949,458 (58%)
  - Furniture: 314,159,645 (21%)
  - Home Appliances: 294,239,474 (20%)
  - Clothing: 22,062,248 (1%)

Geographic Distribution:
  - Chennai: 317,288,445 (21%)
  - Delhi: 309,960,635 (21%)
  - Hyderabad: 299,164,337 (20%)
  - Mumbai: 290,212,243 (19%)
  - Bangalore: 284,785,165 (19%)
  All cities within 5% variance, balanced distribution

Payment Method Distribution:
  - Card: 389,192,554 (26%)
  - Cash: 384,530,849 (26%)
  - UPI: 375,293,345 (25%)
  - Netbanking: 352,394,076 (23%)
  Good diversification across payment methods


TROUBLESHOOTING GUIDE

Issue: File Not Found Error
Solution: Verify the Excel file is in the project directory and filename 
          matches exactly: NeoStats_2026_-_USECASE_-_Data_Engineering.xlsx

Issue: Missing Dependencies Error
Solution: Reinstall dependencies using:
          pip install -r requirements.txt
          Or manually: pip install pandas numpy openpyxl python-dateutil

Issue: Power BI Import Fails
Solution: Ensure Power BI is importing retail_sales_cleaned.csv from the output/
          directory, not the original Excel workbook. Set text encoding to UTF-8.

Issue: Revenue/Profit Values Seem Incorrect
Solution: Verify calculation formulas:
          Revenue = (price * quantity) - discount
          Profit = revenue - (price * quantity * 0.4)
          Profit should always be less than revenue.

Issue: Product Names Still Inconsistent in Output
Solution: Check that standardize_product_names() is being called in the cleaning
          pipeline. Verify input data doesn't have unusual variations.

Issue: PII Not Masked in Output
Solution: Verify that customer_name_masked, email_masked, and phone_masked columns
          exist in output. Check that original PII columns have been dropped.


REPOSITORY STRUCTURE

retail-data-engineering-pipeline/
  
  retail_data_pipeline.py          Main pipeline code
  README.md                         Project overview and documentation
  QUICK_START_GUIDE.txt             Quick setup and execution guide
  
  output/                           Output directory (created after execution)
    retail_sales_cleaned.csv        Cleaned dataset for Power BI
    retail_sales_cleaned.xlsx       Backup Excel format
    kpis_summary.json               Business KPI metrics
    audit_log.json                  Execution audit trail
  
  data/                             Input data directory (optional)
    NeoStats_2026_-_USECASE_-_Data_Engineering.xlsx
  
  powerbi/                          Power BI resources (optional)
    ABC_Retail_Dashboard.pbix       Power BI workbook
    ABC_Retail_Dashboard.pdf        Dashboard screenshots


ASSUMPTIONS AND DESIGN DECISIONS

Price Imputation Strategy:
  Assumption: Product dimension contains authoritative prices for most products
  Decision: Use product lookup first, category median as fallback
  Rationale: Preserves transaction records while using most reliable source

Duplicate Handling:
  Assumption: Duplicates across systems represent the same transaction
  Decision: Keep first occurrence, remove subsequent duplicates
  Rationale: Same customer, product, date, quantity, and amount indicates
            identical transaction

Cost Estimation:
  Assumption: 40% of transaction value represents cost of goods sold
  Decision: Calculate profit as revenue minus 40% of transaction total
  Rationale: Standard retail margin assumption, can be refined with actual costs

PII Protection:
  Assumption: Customer data must not be recoverable after processing
  Decision: Use irreversible SHA-256 hashing instead of encryption
  Rationale: GDPR compliant, prevents accidental data exposure

Row Clipping:
  Assumption: Some revenue calculations may produce edge cases
  Decision: Clip profit at minimum 0, clip discount_rate at 1.0
  Rationale: Prevents nonsensical negative values or percentages above 100%

Date Parsing:
  Assumption: Transaction dates may have multiple formats in source data
  Decision: Use pandas.to_datetime with errors='coerce'
  Rationale: Flexible parsing handles various date formats, coerces errors to NaT


FUTURE ENHANCEMENTS

Phase 2 Improvements:
  - Customer RFM (Recency, Frequency, Monetary) analysis
  - Product correlation and recommendation engine
  - Seasonality and trend detection
  - Demand forecasting using statistical models

Phase 3 Enhancements:
  - Real-time analytics pipeline using streaming data
  - Automated anomaly detection and alerting
  - Predictive churn modeling for customer retention
  - Personalized product recommendations

Phase 4 Advanced Features:
  - Machine learning pipeline for demand forecasting
  - Automated data quality monitoring with threshold alerts
  - Self-service BI portal for business users
  - Advanced customer segmentation and insights

Infrastructure Modernization:
  - Azure Data Factory for pipeline orchestration
  - Azure SQL Database for transformed data storage
  - Azure Data Lake for data archival
  - Synapse Analytics for advanced analytics
  - Automated scheduling and monitoring
  - Cloud-native deployment architecture


TECHNOLOGY STACK

Programming Language:
  - Python 3.8+

Core Libraries:
  - pandas: Data manipulation and analysis
  - NumPy: Numerical computing and array operations
  - openpyxl: Excel file reading and writing
  - json: JSON serialization and deserialization
  - hashlib: Cryptographic hashing for PII masking

Data Visualization:
  - Power BI Desktop: Interactive dashboard creation

Version Control:
  - Git: Source code management

Deployment:
  - Command-line execution
  - Scheduled task (Windows/Linux)
  - Cloud orchestration (optional future enhancement)


EXECUTION EXAMPLE

Command:
  python retail_data_pipeline.py \
    --input "NeoStats_2026_-_USECASE_-_Data_Engineering.xlsx" \
    --output "output"

Result:
  Pipeline successfully executed
  8,494 rows loaded
  7,914 rows exported after cleaning
  4 output files generated
  Audit log created
  Ready for Power BI import


SUPPORT AND DOCUMENTATION

For detailed technical information, refer to:
  - README.md (this file): Complete project documentation
  - Code comments in retail_data_pipeline.py: Implementation details
  - QUICK_START_GUIDE.txt: Step-by-step setup instructions

For issues or questions:
  1. Review this README for common scenarios
  2. Check the Troubleshooting Guide section above
  3. Verify input data format matches specifications
  4. Ensure all dependencies are installed correctly


CONCLUSION

The ABC Retail Solutions Data Engineering Pipeline provides a robust, 
production-ready solution for transforming raw retail transaction data into 
trusted, analytics-ready datasets. The implementation demonstrates professional 
data engineering practices including comprehensive validation, systematic 
cleaning, security-conscious PII protection, audit trail generation, and 
comprehensive documentation suitable for enterprise deployment.

The solution is designed to be maintainable, scalable, and suitable for 
integration with cloud-based analytics platforms for long-term business 
intelligence applications.

===============================================================================