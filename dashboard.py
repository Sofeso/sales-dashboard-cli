import os
import glob
import pandas as pd
from datetime import datetime


def load_data(data_folder):
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
    if not csv_files:
        print(f"No data files found in '{data_folder}'")
        return None
    dfs = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(dfs, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["date"].dt.strftime("%B %Y")
    return df


def print_header(title):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def overview(df):
    print_header("SALES DASHBOARD — OVERVIEW")
    total_revenue = df["revenue"].sum()
    total_orders = len(df)
    total_units = df["quantity"].sum()
    avg_order = df["revenue"].mean()
    best_month = df.groupby("month")["revenue"].sum().idxmax()
    best_month_rev = df.groupby("month")["revenue"].sum().max()

    print(f"  {'Total Revenue':<25} ₦{total_revenue:>15,.2f}")
    print(f"  {'Total Orders':<25} {total_orders:>16,}")
    print(f"  {'Total Units Sold':<25} {total_units:>16,}")
    print(f"  {'Avg Order Value':<25} ₦{avg_order:>15,.2f}")
    print(f"  {'Best Month':<25} {best_month} (₦{best_month_rev:,.2f})")


def revenue_by_month(df):
    print_section("MONTHLY REVENUE TREND")
    monthly = df.groupby("month")["revenue"].sum().reset_index()
    monthly["date_sort"] = pd.to_datetime(monthly["month"], format="%B %Y")
    monthly = monthly.sort_values("date_sort")

    max_rev = monthly["revenue"].max()
    for _, row in monthly.iterrows():
        bar_len = int((row["revenue"] / max_rev) * 30)
        bar = "█" * bar_len
        pct_change = ""
        print(f"  {row['month']:<15} {bar:<30} ₦{row['revenue']:>12,.2f} {pct_change}")


def top_products(df):
    print_section("TOP 5 PRODUCTS BY REVENUE")
    products = (
        df.groupby("product")
        .agg(units=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
        .head(5)
        .reset_index()
    )
    print(f"  {'Rank':<6}{'Product':<35}{'Units':>8}{'Revenue':>15}")
    print(f"  {'─'*4:<6}{'─'*33:<35}{'─'*6:>8}{'─'*13:>15}")
    for i, row in products.iterrows():
        print(f"  {i+1:<6}{row['product']:<35}{row['units']:>8,}  ₦{row['revenue']:>12,.2f}")


def revenue_by_category(df):
    print_section("REVENUE BY CATEGORY")
    cats = (
        df.groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    total = cats["revenue"].sum()
    for _, row in cats.iterrows():
        pct = (row["revenue"] / total) * 100
        bar = "█" * int(pct / 2)
        print(f"  {row['category']:<15} {bar:<25} {pct:>5.1f}%  ₦{row['revenue']:>12,.2f}")


def leaderboard(df):
    print_section("SALESPERSON LEADERBOARD")
    reps = (
        df.groupby("salesperson")
        .agg(orders=("revenue", "count"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
    medals = ["🥇", "🥈", "🥉"]
    print(f"  {'':4}{'Salesperson':<28}{'Orders':>8}{'Revenue':>15}")
    print(f"  {'─'*2:<4}{'─'*26:<28}{'─'*6:>8}{'─'*13:>15}")
    for i, row in reps.iterrows():
        medal = medals[i] if i < 3 else f"  {i+1}."
        print(f"  {medal}  {row['salesperson']:<26}{row['orders']:>8,}  ₦{row['revenue']:>12,.2f}")


def regional_performance(df):
    print_section("REGIONAL PERFORMANCE")
    regions = (
        df.groupby("region")
        .agg(orders=("revenue", "count"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
    total = regions["revenue"].sum()
    for _, row in regions.iterrows():
        pct = (row["revenue"] / total) * 100
        print(f"  {row['region']:<20} Orders: {row['orders']:>4} | "
              f"Revenue: ₦{row['revenue']:>12,.2f} | Share: {pct:.1f}%")


def export_report(df, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    summary = (
        df.groupby(["month", "category", "salesperson", "region"])
        .agg(
            total_orders=("quantity", "count"),
            total_units=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            avg_order_value=("revenue", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(output_file, index=False)
    print(f"\n  📁 Full report exported to: {output_file}")


def run_dashboard(data_folder="sample_data", output_file="output/sales_report.csv"):
    df = load_data(data_folder)
    if df is None:
        return

    overview(df)
    revenue_by_month(df)
    top_products(df)
    revenue_by_category(df)
    leaderboard(df)
    regional_performance(df)
    export_report(df, output_file)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_dashboard()
