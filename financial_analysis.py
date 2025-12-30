import pandas as pd
import numpy as np

def get_summary_statistics(data, numeric_columns):
    """
    Calculate summary statistics for numeric columns.
    
    Args:
        data (pd.DataFrame): The financial data
        numeric_columns (list): List of numeric column names
    
    Returns:
        pd.DataFrame: Summary statistics
    """
    # Check if we have data and numeric columns
    if data is None or len(data) == 0 or not numeric_columns:
        # Return empty DataFrame with appropriate columns if no data
        return pd.DataFrame(columns=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'median', 'skew', 'kurtosis'])
    
    # Select only numeric columns for summary
    numeric_data = data[numeric_columns]
    
    # Calculate basic statistics
    summary = numeric_data.describe().T
    
    # Add additional statistics
    summary['median'] = numeric_data.median()
    summary['skew'] = numeric_data.skew()
    summary['kurtosis'] = numeric_data.kurtosis()
    
    # Format the summary
    summary = summary.round(2)
    
    return summary

def calculate_financial_metrics(data, numeric_columns):
    """
    Calculate key financial metrics based on available data.
    Adapts to the columns present in the dataset.
    
    Args:
        data (pd.DataFrame): The financial data
        numeric_columns (list): List of numeric column names
    
    Returns:
        dict: Dictionary of financial metrics
    """
    # Check if we have data and numeric columns
    if data is None or len(data) == 0 or not numeric_columns:
        return {}
        
    metrics = {}
    
    # Default metrics for any numeric data
    for col in numeric_columns:
        col_data = data[col].dropna()
        if len(col_data) > 0:
            # Basic metrics
            metrics[f"Avg {col}"] = col_data.mean()
            
            # Growth metrics (if we have enough data points)
            if len(col_data) > 1:
                first_value = col_data.iloc[0]
                last_value = col_data.iloc[-1]
                if first_value != 0:  # Avoid division by zero
                    change_pct = ((last_value - first_value) / first_value) * 100
                    metrics[f"{col} Change %"] = change_pct
            
            # Volatility metric
            if len(col_data) > 2:
                metrics[f"{col} Volatility"] = col_data.std()
    
    # Special handling for columns with specific names
    # Revenue metrics
    revenue_cols = [col for col in numeric_columns if 'revenue' in col.lower() or 'income' in col.lower() or 'sales' in col.lower()]
    if revenue_cols:
        revenue_col = revenue_cols[0]  # Use the first one found
        revenue_data = data[revenue_col].dropna()
        if len(revenue_data) > 0:
            metrics["Total Revenue"] = revenue_data.sum()
    
    # Expense metrics
    expense_cols = [col for col in numeric_columns if 'expense' in col.lower() or 'cost' in col.lower() or 'spend' in col.lower()]
    if expense_cols:
        expense_col = expense_cols[0]  # Use the first one found
        expense_data = data[expense_col].dropna()
        if len(expense_data) > 0:
            metrics["Total Expenses"] = expense_data.sum()
    
    # Profit metrics
    if 'Total Revenue' in metrics and 'Total Expenses' in metrics:
        metrics["Net Profit"] = metrics["Total Revenue"] - metrics["Total Expenses"]
        if metrics["Total Revenue"] != 0:
            metrics["Profit Margin %"] = (metrics["Net Profit"] / metrics["Total Revenue"]) * 100
    
    # Asset metrics
    asset_cols = [col for col in numeric_columns if 'asset' in col.lower()]
    if asset_cols:
        asset_col = asset_cols[0]
        asset_data = data[asset_col].dropna()
        if len(asset_data) > 0:
            metrics["Total Assets"] = asset_data.mean()
    
    # Liability metrics
    liability_cols = [col for col in numeric_columns if 'liab' in col.lower() or 'debt' in col.lower()]
    if liability_cols:
        liability_col = liability_cols[0]
        liability_data = data[liability_col].dropna()
        if len(liability_data) > 0:
            metrics["Total Liabilities"] = liability_data.mean()
    
    # Calculate ROI if we have investment and return data
    investment_cols = [col for col in numeric_columns if 'invest' in col.lower()]
    return_cols = [col for col in numeric_columns if 'return' in col.lower() or 'roi' in col.lower()]
    
    if investment_cols and return_cols:
        investment_data = data[investment_cols[0]].dropna()
        return_data = data[return_cols[0]].dropna()
        
        if len(investment_data) > 0 and len(return_data) > 0 and investment_data.mean() != 0:
            metrics["ROI %"] = (return_data.mean() / investment_data.mean()) * 100
    
    return metrics

def analyze_trends(data, date_column, value_column):
    """
    Analyze trends in a time series financial data.
    
    Args:
        data (pd.DataFrame): The financial data
        date_column (str): Name of the date column
        value_column (str): Name of the value column to analyze
    
    Returns:
        dict: Dictionary of trend analysis results
    """
    # Ensure data is sorted by date
    data = data.sort_values(by=date_column)
    
    # Extract the value series
    series = data[value_column].dropna()
    
    if len(series) < 2:
        return {
            "trend": "Unknown",
            "description": "Not enough data points for trend analysis",
            "change_pct": 0
        }
    
    # Calculate basic trend metrics
    first_value = series.iloc[0]
    last_value = series.iloc[-1]
    change = last_value - first_value
    
    if first_value != 0:
        change_pct = (change / first_value) * 100
    else:
        change_pct = 0
    
    # Determine trend direction
    if change_pct > 5:
        trend = "Increasing"
        description = f"Strong upward trend with {change_pct:.2f}% growth"
    elif change_pct > 0:
        trend = "Slightly Increasing"
        description = f"Slight upward trend with {change_pct:.2f}% growth"
    elif change_pct < -5:
        trend = "Decreasing"
        description = f"Strong downward trend with {abs(change_pct):.2f}% decline"
    elif change_pct < 0:
        trend = "Slightly Decreasing"
        description = f"Slight downward trend with {abs(change_pct):.2f}% decline"
    else:
        trend = "Stable"
        description = "Stable with minimal change over time"
    
    # Calculate volatility
    if len(series) > 2:
        volatility = series.std() / series.mean() if series.mean() != 0 else 0
        
        if volatility > 0.2:
            volatility_desc = "High volatility"
        elif volatility > 0.1:
            volatility_desc = "Moderate volatility"
        else:
            volatility_desc = "Low volatility"
            
        description += f" with {volatility_desc}"
    
    return {
        "trend": trend,
        "description": description,
        "change_pct": change_pct
    }
