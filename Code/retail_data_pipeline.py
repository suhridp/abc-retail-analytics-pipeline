"""
retail_data_pipeline.py — CORRECTED VERSION

ABC Retail Solutions — End-to-End Data Engineering Pipeline
Project: Retail Sales Data Processing and Business Insights Generation

PIPELINE ARCHITECTURE:
    Ingestion → Validation → Cleaning → Transformation → Aggregation → Export
    
RESPONSIBILITIES:
    1. Data Ingestion from Excel files (retail_data1, retail_data2, product_details)
    2. Data Quality Checks (schema validation, null detection, duplicates)
    3. Data Cleaning (missing values, standardization, PII masking)
    4. Data Transformation (joins, feature engineering, business logic)
    5. Business KPI Aggregation (Revenue, Category, City analysis)
    6. Export to cleaned dataset for Power BI visualization

MODULES:
    - DataLoader: Ingest data from Excel
    - DataValidator: Verify schema and data quality
    - DataCleaner: Handle nulls, duplicates, PII masking
    - DataTransformer: Join with product dimension, create business metrics
    - KPIAggregator: Calculate revenue KPIs by category, city, etc.
    - DataExporter: Save cleaned data for BI consumption

DEPENDENCIES:
    pip install pandas openpyxl numpy python-dateutil

"""

import os
import logging
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import argparse
from datetime import datetime

import pandas as pd
import numpy as np


# LOGGER SETUP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("retail_pipeline")


# CONFIG & CONSTANTS
 

REQUIRED_TRANSACTION_COLUMNS = [
    'transaction_id', 'customer_id', 'customer_name', 'product_id',
    'price', 'quantity', 'transaction_date', 'city', 'category',
    'payment_method', 'discount', 'email', 'phone', 'payment_status'
]

REQUIRED_PRODUCT_COLUMNS = [
    'product_id', 'product_name', 'category', 'price'
]

PII_COLUMNS = ['customer_name', 'email', 'phone']


# STEP 1: DATA LOADER

class DataLoader:
    """Ingests retail transaction data from Excel files."""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.log = logging.getLogger("DataLoader")

    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from Excel workbook."""
        self.log.info(f"Loading Excel file: {self.excel_path}")

        try:
            sheets = {}
            xl = pd.ExcelFile(self.excel_path)
            self.log.info(f"Found sheets: {xl.sheet_names}")

            for sheet in xl.sheet_names:
                df = pd.read_excel(self.excel_path, sheet_name=sheet)
                sheets[sheet] = df
                self.log.info(f"  {sheet}: {len(df):,} rows × {len(df.columns)} columns")

            return sheets
        except Exception as e:
            self.log.error(f"Failed to load Excel file: {str(e)}")
            raise

    def validate_sheet_exists(self, sheets: Dict, required_sheets: List[str]) -> bool:
        """Verify all required sheets are present."""
        missing = set(required_sheets) - set(sheets.keys())
        if missing:
            self.log.error(f"Missing required sheets: {missing}")
            return False
        return True


# STEP 2: DATA VALIDATOR

class DataValidator:
    """Validates data schema, nulls, and data quality issues."""

    def __init__(self):
        self.log = logging.getLogger("DataValidator")
        self.validation_report = {}

    def validate_schema(self, df: pd.DataFrame, required_cols: List[str], sheet_name: str) -> bool:
        """Check if all required columns are present."""
        present = set(df.columns)
        required = set(required_cols)
        missing = required - present
        if 'transaction_id' in df.columns:
            if df['transaction_id'].isnull().any():
                raise ValueError("Missing transaction IDs detected")
        if missing:
            self.log.error(f"{sheet_name}: Missing columns: {missing}")
            return False

        self.log.info(f"{sheet_name}: Schema validation passed")
        return True

    def profile_data_quality(self, df: pd.DataFrame, sheet_name: str) -> dict:
        """Generate data quality report."""
        report = {
            'sheet': sheet_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'null_percentage': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.astype(str).to_dict()
        }

        self.log.info(f"{sheet_name} Quality Report:")
        self.log.info(f"  Null cells: {df.isnull().sum().sum():,}")
        self.log.info(f"  Duplicates: {report['duplicate_rows']:,}")

        return report


# STEP 3: DATA CLEANER

class DataCleaner:
    """Handles missing values, duplicates, standardization, and PII masking."""

    def __init__(self):
        self.log = logging.getLogger("DataCleaner")
        self.cleaning_report = {}

    def handle_missing_prices(self, df: pd.DataFrame, product_dim: pd.DataFrame) -> pd.DataFrame:
        """Fill missing prices using product dimension table.
        For unfillable nulls, use category median."""
        df = df.copy()
        rows_before = len(df)

        # Create price lookup from product dimension 
        price_lookup = dict(zip(product_dim['product_id'], product_dim['price']))

        # Fill from product dimension
        mask_null = df['price'].isnull()
        df.loc[mask_null, 'price'] = df.loc[mask_null, 'product_id'].map(price_lookup)

        # For remaining nulls, use category median
        if df['price'].isnull().any():
            category_medians = df.groupby('category', dropna=False)['price'].median().to_dict()
            df['price'] = df.apply(
                lambda row: category_medians.get(row['category'], df['price'].median())
                if pd.isna(row['price']) else row['price'],
                axis=1
            )

        self.log.info(f"Missing prices handled: {mask_null.sum():,} rows filled")
        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate transactions based on key fields."""
        df = df.copy()
        rows_before = len(df)
       
       # Remove exact duplicates first
        df = df.drop_duplicates(keep='first')
       
       # Then remove transaction-level duplicates
        if 'transaction_id' in df.columns:
           df = df.drop_duplicates(
               subset=['transaction_id'],
               keep='first'
           )
       
        rows_after = len(df)
        dups_removed = rows_before - rows_after
        self.log.info(f"Duplicates removed: {dups_removed:,}")
        return df

    def handle_invalid_quantities(self,df: pd.DataFrame) -> pd.DataFrame:

        """Remove records with invalid quantities"""

        df = df.copy()

        rows_before = len(df)
        df = df[df['quantity'] > 0]

        rows_removed = rows_before - len(df)

        self.log.info(f"Invalid quantity records removed: {rows_removed}"    )

        return df
    def standardize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize categorical values (trim, title case, etc)."""
        df = df.copy()
        if 'category' in df.columns:

            df['category'] = (
                df['category']
                .astype(str)
                .str.strip()
                .str.upper()
            )

            category_mapping = {
                'ELEC': 'Electronics',
                'ELECTRONICS': 'Electronics',

                'FURN': 'Furniture',
                'FURNITURE': 'Furniture',

                'CLOTH': 'Clothing',
                'CLOTHING': 'Clothing',

                'HOME': 'Home Appliances',
                'HOME APPLIANCES': 'Home Appliances'
            }

            df['category'] = df['category'].replace(category_mapping)
        category_col = None

        if 'category_trans' in df.columns:
            category_col = 'category_trans'
        elif 'category' in df.columns:
            category_col = 'category'

        if category_col:
            df[category_col] = (
                df[category_col]
                .astype(str)
                .str.strip()
                .replace(category_mapping)
            )
    # Trim whitespace and standardize case for categorical columns        
        categorical_cols = ['category_trans', 'payment_method', 'payment_status', 'city']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].str.strip().str.title()

            # Standardize product names
        if 'product_name' in df.columns:
            df['product_name'] = df['product_name'].str.strip()

            # Convert transaction_date to datetime
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

        self.log.info("Values standardized")
        return df
    def standardize_product_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize inconsistent product names."""

        df = df.copy()

        if 'product_name' in df.columns:

            df['product_name'] = (
                df['product_name']
                .astype(str)
                .str.strip()
                .str.lower()
                .str.replace('-', ' ', regex=False)
                .str.replace('_', ' ', regex=False)
                .str.replace(r'\s+', ' ', regex=True)
            )

            # Convert back to title case
            df['product_name'] = df['product_name'].str.title()

        self.log.info("Product names standardized")

        return df
    def mask_pii(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mask PII fields using SHA-256 hashing with salt.
        Original data is hashed irreversibly for compliance.
        """
        df = df.copy()
        salt = os.getenv("PII_SALT", "ABC_Default_Salt")

        for col in PII_COLUMNS:
            if col in df.columns:
                df[f'{col}_masked'] = df[col].apply(
                lambda x:
                "MASKED_NULL"
                if pd.isna(x)
                else hashlib.sha256(
                    f"{x}_{salt}".encode()
                ).hexdigest()[:16])
                # Drop original PII column
                df = df.drop(columns=[col])

        self.log.info(f"PII masked: {PII_COLUMNS}")
        return df

    def clean_full_pipeline(self,
                           df: pd.DataFrame,
                           product_dim: pd.DataFrame) -> pd.DataFrame:
        """Execute full cleaning pipeline."""
        self.log.info("=" * 60)
        self.log.info("DATA CLEANING PIPELINE STARTING")
        self.log.info("=" * 60)

        df = self.handle_missing_prices(df, product_dim)
        df = self.handle_invalid_quantities(df)

        df = self.remove_duplicates(df)
        df = self.standardize_values(df)
        df = self.standardize_product_names(df)
        df = self.mask_pii(df)

        self.log.info("=" * 60)
        self.log.info(f"CLEANING COMPLETE: {len(df):,} rows")
        self.log.info("=" * 60)
        return df


# STEP 4: DATA TRANSFORMER

class DataTransformer:
    """Joins data with product dimension and creates business metrics."""

    def __init__(self):
        self.log = logging.getLogger("DataTransformer")

    def enrich_with_product_dimension(self,
                                      transactions: pd.DataFrame,
                                      products: pd.DataFrame) -> pd.DataFrame:
        """
        Join transaction data with product dimension.
        Validates product_id integrity.
        """
        if not products["product_id"].is_unique:
            raise ValueError("Duplicate product_id values found in product dimension")

        df = transactions.copy()
        self.log.info("Enriching with product dimension...")

        # Left join to preserve all transactions
        df = df.merge(
            products[['product_id', 'product_name', 'category']],
            on='product_id',
            how='left',
            suffixes=('_trans', '_prod')
        )
        df['product_name_standardized'] = (df['product_name_prod'].fillna(df['product_name_trans']))

        # Report unmatched products
        unmatched = df['product_name_prod'].isnull().sum()
        if unmatched > 0:
            self.log.warning(f"Unmatched products: {unmatched} ")
            
        self.log.info(f"Enrichment complete: {len(df):,} rows")
        return df

    def calculate_business_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate transaction-level business metrics."""
        df = df.copy()

        # Revenue = (price * quantity) - discount
        df['revenue'] = (df['price'] * df['quantity']) - df['discount']
        df['revenue'] = df['revenue'].clip(lower=0)  # Ensure non-negative

        # Profit margin indicator
        # Category-specific cost assumptions

        category_cost_mapping = {
        'Electronics': 0.80,      # 20% margin
        'Furniture': 0.60,        # 40% margin
        'Clothing': 0.50,         # 50% margin
        'Home Appliances': 0.70   # 30% margin
        }

        category_col = 'category_prod' if 'category_prod' in df.columns else 'category'

        df['cost_ratio'] = (
        df[category_col]
        .map(category_cost_mapping)
        .fillna(0.60)
        )

        df['total_cost'] = (
        df['price']
        * df['quantity']
        * df['cost_ratio']
        )

        df['profit'] = df['revenue'] - df['total_cost']

        df['profit_margin_pct'] = np.where(
        df['revenue'] > 0,
        (df['profit'] / df['revenue']) * 100,
        0
        )
        # Transaction date features for time-based analysis
        df['transaction_year'] = df['transaction_date'].dt.year
        df['transaction_month'] = df['transaction_date'].dt.month
        
        # Handle pandas >=2.0 compatibility
        try:
            df['transaction_week'] = df['transaction_date'].dt.isocalendar().week
        except:
            df['transaction_week'] = df['transaction_date'].dt.strftime('%V').astype(int)

        df['day_of_week'] = df['transaction_date'].dt.day_name()

        # Discount rate 
        base = df['price'] * df['quantity']
        df['discount_rate'] = np.where(base > 0, df['discount'] / base, 0)

        self.log.info("Business metrics calculated")
        return df


# STEP 5: KPI AGGREGATOR

class KPIAggregator:
    """Calculates business KPIs for reporting."""

    def __init__(self):
        self.log = logging.getLogger("KPIAggregator")
        self.kpis = {}

    def calculate_kpis(self, df: pd.DataFrame) -> Dict:
        """Calculate all key business KPIs."""
        self.log.info("Calculating KPIs...")

        kpis = {
            'Total Revenue': df['revenue'].sum(),
            'Total Transactions':df['transaction_id'].nunique(),
            'Total Quantity Sold': df['quantity'].sum(),
            'Average Order Value': df.groupby('transaction_id')['revenue'].sum().mean(),
            'Total Discount Given': df['discount'].sum(),
            'Total Profit': df['profit'].sum(),
        }
        kpis['Top Products by Revenue'] = (
        df.groupby('product_name_standardized')['revenue'].sum().sort_values(ascending=False).head(10).round(2).to_dict())
        # Determine category column name 
        if 'category_prod' in df.columns:
            category_col = 'category_prod'
        elif 'category' in df.columns:
            category_col = 'category'
        else:
            raise ValueError("No category column found")
        kpis['Best Selling Products by Quantity'] = (
        df.groupby('product_name_standardized')['quantity']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .to_dict())
        kpis['Most Profitable Products'] = (
        df.groupby('product_name_standardized')['profit']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .to_dict())
        # By Category
        kpis['Revenue by Category'] = df.groupby(category_col)['revenue'].sum().to_dict()
        kpis['Transactions by Category'] = df.groupby(category_col).size().to_dict()
        kpis['Avg Price by Category'] = df.groupby(category_col)['price'].mean().round(2).to_dict()

        # By City
        kpis['Revenue by City'] = df.groupby('city')['revenue'].sum().to_dict()
        kpis['Transactions by City'] = df.groupby('city').size().to_dict()

        # By Payment Method
        kpis['Revenue by Payment Method'] = df.groupby('payment_method')['revenue'].sum().to_dict()

        # By Payment Status
        kpis['Revenue by Payment Status'] = df.groupby('payment_status')['revenue'].sum().to_dict()
        
        return kpis

    def print_kpi_summary(self, kpis: Dict) -> None:
        """Print formatted KPI summary."""
        self.log.info("=" * 60)
        self.log.info("KEY PERFORMANCE INDICATORS")
        self.log.info("=" * 60)
        # Global KPIs
        self.log.info(f"\nGlobal Metrics:")
        self.log.info(f"  Total Revenue: ₹{kpis['Total Revenue']:,.2f}")
        self.log.info(f"  Total Transactions: {kpis['Total Transactions']:,}")
        self.log.info(f"  Average Order Value: ₹{kpis['Average Order Value']:,.2f}")
        self.log.info(f"  Total Profit: ₹{kpis['Total Profit']:,.2f}")

        # Category breakdown
        self.log.info(f"\nTop 3 Categories by Revenue:")
        cat_revenue = sorted(kpis['Revenue by Category'].items(),
                            key=lambda x: x[1], reverse=True)[:3]
        for cat, rev in cat_revenue:
            self.log.info(f"  {cat}: ₹{rev:,.2f}")

        # City breakdown
        self.log.info(f"\nTop 3 Cities by Revenue:")
        city_revenue = sorted(kpis['Revenue by City'].items(),
                             key=lambda x: x[1], reverse=True)[:3]
        for city, rev in city_revenue:
            self.log.info(f"  {city}: ₹{rev:,.2f}")


# STEP 6: DATA EXPORTER

class DataExporter:
    """Exports cleaned and transformed data for BI consumption."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.log = logging.getLogger("DataExporter")

    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Export dataframe to CSV."""
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        self.log.info(f"Exported: {output_path} ({len(df):,} rows)")
        return str(output_path)

    def export_to_excel(self, df: pd.DataFrame, filename: str) -> str:
        """Export dataframe to Excel."""
        output_path = self.output_dir / filename
        df.to_excel(output_path, index=False, sheet_name='Retail Data')
        self.log.info(f"Exported: {output_path}")
        return str(output_path)

    def export_kpis_to_json(self, kpis: Dict, filename: str = "kpis.json") -> str:
        """Export KPIs to JSON."""
        output_path = self.output_dir / filename

        # Convert numpy types to native Python types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            return obj

        serializable_kpis = convert_to_serializable(kpis)

        with open(output_path, 'w') as f:
            json.dump(serializable_kpis, f, indent=2)

        self.log.info(f"KPIs exported: {output_path}")
        return str(output_path)

    def export_audit_log(self, audit_data: Dict) -> str:
        """Export audit log to JSON."""
        output_path = self.output_dir / "audit_log.json"

        with open(output_path, "w") as f:
            json.dump(audit_data, f, indent=2)

        self.log.info(f"Audit log exported: {output_path}")
        return str(output_path)


# MAIN ORCHESTRATOR

def run_retail_pipeline(excel_path: str, output_dir: str = "output") -> Tuple[pd.DataFrame, Dict]:
    """
    Execute the complete retail data engineering pipeline.

    Args:
        excel_path: Path to the Excel file containing all sheets
        output_dir: Directory to save output files

    Returns:
        Tuple of (cleaned_dataframe, kpis_dict)
    """

    log.info("\n" + "=" * 70)
    log.info("ABC RETAIL SOLUTIONS — DATA ENGINEERING PIPELINE")
    log.info("=" * 70 + "\n")

    # ── Initialize modules ────────────────────────────────────────
    loader = DataLoader(excel_path)
    validator = DataValidator()
    cleaner = DataCleaner()
    transformer = DataTransformer()
    aggregator = KPIAggregator()
    exporter = DataExporter(output_dir)

    # ── Step 1: Load data ─────────────────────────────────────────
    sheets = loader.load_all_sheets()
    if not loader.validate_sheet_exists(sheets, ['product_details', 'retail_data1', 'retail_data2']):
        raise ValueError("Required sheets not found in Excel file")

    # ── Step 2: Validate schema ───────────────────────────────────
    if not validator.validate_schema(sheets['product_details'], REQUIRED_PRODUCT_COLUMNS, 'product_details'):
        raise ValueError("Schema validation failed")
    if not validator.validate_schema(sheets['retail_data1'], REQUIRED_TRANSACTION_COLUMNS, 'retail_data1'):
        raise ValueError("Schema validation failed")
    if not validator.validate_schema(sheets['retail_data2'], REQUIRED_TRANSACTION_COLUMNS, 'retail_data2'):
        raise ValueError("Schema validation failed")

    # ── Step 3: Combine retail datasets 
    log.info("\nCombining retail datasets...")
    retail_combined = pd.concat(
        [sheets['retail_data1'], sheets['retail_data2']],
        ignore_index=True
    )
    log.info(f"Combined dataset: {len(retail_combined):,} rows")

    # ── Step 4: Profile combined data quality ──────────────────────
    for sheet in ['retail_data1', 'retail_data2', 'product_details']:
        validator.profile_data_quality(sheets[sheet], sheet)

    null_pct = (retail_combined.isnull().sum().sum() /
                (len(retail_combined) * len(retail_combined.columns))) * 100

    if null_pct > 25:
        log.warning(f"Data quality warning: {null_pct:.2f}% nulls detected (threshold: 25%)")

    # ── Step 5: Clean data ────────────────────────────────────────
    retail_cleaned = cleaner.clean_full_pipeline(retail_combined, sheets['product_details'])

    # ── Step 6: Transform data ────────────────────────────────────
    log.info("\nTransforming data...")
    retail_transformed = transformer.enrich_with_product_dimension(
        retail_cleaned,
        sheets['product_details']
    )
    retail_transformed = transformer.calculate_business_metrics(retail_transformed)

    # ── Step 7: Calculate KPIs ────────────────────────────────────
    log.info("\nCalculating KPIs...")
    kpis = aggregator.calculate_kpis(retail_transformed)
    aggregator.print_kpi_summary(kpis)

    # ── Step 8: Export data ───────────────────────────────────────
    log.info("\nExporting data...")
    exporter.export_to_csv(retail_transformed, "retail_sales_cleaned.csv")
    exporter.export_to_excel(retail_transformed, "retail_sales_cleaned.xlsx")
    exporter.export_kpis_to_json(kpis, "kpis_summary.json")

    log.info("\n" + "=" * 70)
    log.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    log.info("=" * 70 + "\n")

    audit = {
        "rows_loaded": len(retail_combined),
        "rows_cleaned": len(retail_cleaned),
        "rows_exported": len(retail_transformed),
        "run_timestamp": datetime.now().isoformat(),
        "pipeline_status": "SUCCESS"
    }

    exporter.export_audit_log(audit)
    return retail_transformed, kpis


# ENTRY POINT

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Retail Data Engineering Pipeline"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to Excel file"
    )

    parser.add_argument(
        "--output",
        default="output",
        help="Output directory"
    )

    args = parser.parse_args()

    try:

        cleaned_df, kpis = run_retail_pipeline(
            args.input,
            args.output
        )

    except Exception as e:

        logger = logging.getLogger("RetailPipeline")

        logger.exception(
            f"Pipeline failed: {str(e)}"
        )

        audit = {
            "pipeline_status": "FAILED",
            "error": str(e),
            "run_timestamp": datetime.now().isoformat()
        }

        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)

        with open(
            output_dir / "audit_log.json",
            "w"
        ) as f:
            json.dump(audit, f, indent=2)

        sys.exit(1)