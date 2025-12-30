import pandas as pd
import numpy as np
from datetime import datetime

def validate_financial_data(data):
    """
    Validate if the uploaded data looks like financial data.
    
    Args:
        data (pd.DataFrame): The uploaded data frame
    
    Returns:
        tuple: (is_valid, message) - Boolean indicating if valid and explanation message
    """
    # Check if data exists
    if data is None:
        return False, "No data was provided."
    
    # Check if dataframe is empty
    if data.empty:
        return False, "The uploaded file contains no data."
    
    # Check column count
    if len(data.columns) < 2:
        return False, "The data must have at least two columns (typically date and values)."
    
    # Look for invalid or problematic values
    if data.isnull().all().all():
        return False, "All values in the dataset are missing (null)."
    
    # Check if there's at least one column that might be a date
    has_date_column = False
    date_column_name = None
    for col in data.columns:
        try:
            # Try to convert to datetime
            test_conversion = pd.to_datetime(data[col], errors='raise')
            # Check if this really looks like a date column (at least 80% valid dates)
            valid_dates = test_conversion.notna().mean() >= 0.8
            if valid_dates:
                has_date_column = True
                date_column_name = col
                break
        except:
            continue
    
    if not has_date_column:
        return False, "No valid date column found. Financial data should include dates (like transaction dates, statement dates, etc.)."
    
    # Check if there are numeric columns (potential financial values)
    numeric_columns = data.select_dtypes(include=['number']).columns
    if len(numeric_columns) == 0:
        return False, "No numeric columns found. Financial data should include numeric values (like amounts, prices, etc.)."
    
    # Check for potential financial column names as an additional validation
    financial_keywords = ['amount', 'price', 'value', 'cost', 'revenue', 'income', 'expense', 
                         'balance', 'profit', 'sale', 'asset', 'liability', 'cash', 'fund', 
                         'tax', 'interest', 'dividend', 'payment']
    
    found_financial_cols = []
    for col in data.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in financial_keywords):
            found_financial_cols.append(col)
    
    if found_financial_cols:
        return True, f"Data appears to be valid financial data with date column '{date_column_name}' and financial columns: {', '.join(found_financial_cols)}"
    else:
        # Even without matching column names, if we have dates and numbers, it's probably financial data
        return True, f"Data contains dates and numeric values which might represent financial data."

def process_data(data):
    """
    Process the uploaded financial data:
    - Identify date columns
    - Identify numeric and categorical columns
    - Handle missing values
    - Convert date columns to datetime
    
    Args:
        data (pd.DataFrame): The uploaded data frame
    
    Returns:
        tuple: (processed_data, date_column, numeric_columns, categorical_columns)
    """
    # Basic validation
    if data is None or data.empty:
        return data, None, [], []
    
    # Create a copy to avoid modifying the original
    try:
        df = data.copy()
    except Exception as e:
        print(f"Error creating data copy: {str(e)}")
        return data, None, [], []
    
    # Identify date columns (choose the first one as primary date)
    date_column = None
    date_cols_attempted = []
    
    # First try column names that might suggest dates
    date_indicators = ['date', 'time', 'day', 'month', 'year', 'period']
    for indicator in date_indicators:
        for col in df.columns:
            if indicator.lower() in col.lower() and col not in date_cols_attempted:
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_column = col
                    break
                except:
                    date_cols_attempted.append(col)
        if date_column:
            break
    
    # If no column with date-like name found, try all columns
    if date_column is None:
        for col in df.columns:
            if col not in date_cols_attempted:
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_column = col
                    break
                except:
                    continue
    
    # Identify numeric columns (excluding the date column)
    try:
        numeric_columns = [col for col in df.select_dtypes(include=['number']).columns if col != date_column]
    except Exception as e:
        print(f"Error identifying numeric columns: {str(e)}")
        numeric_columns = []
    
    # Identify categorical columns
    try:
        categorical_columns = [col for col in df.columns 
                              if col != date_column and col not in numeric_columns]
    except Exception as e:
        print(f"Error identifying categorical columns: {str(e)}")
        categorical_columns = []
    
    # Handle missing values
    # For numeric columns, fill with mean or 0
    for col in numeric_columns:
        try:
            if df[col].isnull().any():
                # If more than 50% are missing, use 0 instead of mean to avoid skew
                if df[col].isnull().mean() > 0.5:
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df[col].mean())
        except Exception as e:
            print(f"Error handling missing values in column {col}: {str(e)}")
            # Use a safe fallback
            df[col] = df[col].fillna(0)
    
    # For categorical columns, fill with 'Unknown'
    for col in categorical_columns:
        try:
            if df[col].isnull().any():
                df[col] = df[col].fillna('Unknown')
        except Exception as e:
            print(f"Error handling missing values in categorical column {col}: {str(e)}")
            df[col] = df[col].fillna('Unknown')
    
    # Sort by date column if available
    if date_column:
        try:
            df = df.sort_values(by=date_column)
        except Exception as e:
            print(f"Error sorting by date: {str(e)}")
    
    return df, date_column, numeric_columns, categorical_columns

def filter_data_by_date(data, date_column, start_date, end_date):
    """
    Filter the dataframe by date range.
    
    Args:
        data (pd.DataFrame): The data frame to filter
        date_column (str): Name of the date column
        start_date (datetime): Start date for filtering
        end_date (datetime): End date for filtering
    
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # Safety checks
    if data is None or data.empty:
        return data
    
    if date_column is None or date_column not in data.columns:
        return data
    
    try:
        filtered_data = data[(data[date_column] >= start_date) & (data[date_column] <= end_date)]
        # If filtering removed all data, return the original instead
        if filtered_data.empty and not data.empty:
            print(f"Date filtering resulted in empty dataframe. Using original data instead.")
            return data
        return filtered_data
    except Exception as e:
        print(f"Error filtering by date: {str(e)}")
        return data  # Return original data if error occurs

def filter_data_by_category(data, category_column, selected_categories):
    """
    Filter the dataframe by selected categories.
    
    Args:
        data (pd.DataFrame): The data frame to filter
        category_column (str): Name of the category column
        selected_categories (list): List of categories to include
    
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # Safety checks
    if data is None or data.empty:
        return data
    
    if category_column is None or category_column not in data.columns:
        return data
        
    if not selected_categories:
        return data
    
    try:
        filtered_data = data[data[category_column].isin(selected_categories)]
        # If filtering removed all data, return the original instead
        if filtered_data.empty and not data.empty:
            print(f"Category filtering resulted in empty dataframe. Using original data instead.")
            return data
        return filtered_data
    except Exception as e:
        print(f"Error filtering by category: {str(e)}")
        return data  # Return original data if error occurs
