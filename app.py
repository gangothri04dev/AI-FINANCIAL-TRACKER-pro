import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import io

# Import custom modules
from data_processor import process_data, validate_financial_data
from financial_analysis import calculate_financial_metrics, get_summary_statistics, analyze_trends
from visualization import create_line_chart, create_bar_chart, create_pie_chart
from ai_predictions import predict_future_values
from auth import register_user, login_user, get_user_data

# Set page configuration
st.set_page_config(
    page_title="AI Financial Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'columns' not in st.session_state:
    st.session_state.columns = []
if 'date_column' not in st.session_state:
    st.session_state.date_column = None
if 'numeric_columns' not in st.session_state:
    st.session_state.numeric_columns = []
if 'categorical_columns' not in st.session_state:
    st.session_state.categorical_columns = []

# Authentication Section
if not st.session_state.logged_in:
    st.title("Financial Dashboard - Authentication")
    
    auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
    
    with auth_tab1:
        st.subheader("Login to Your Account")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if login_username and login_password:
                success, message, user_data = login_user(login_username, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_info = user_data
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password.")
    
    with auth_tab2:
        st.subheader("Create a New Account")
        signup_username = st.text_input("Choose a username", key="signup_username")
        signup_email = st.text_input("Email address", key="signup_email")
        signup_password = st.text_input("Create a password (min 6 characters)", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
        
        if st.button("Sign Up", key="signup_button"):
            if not signup_username or not signup_email or not signup_password:
                st.warning("Please fill in all fields.")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(signup_username, signup_email, signup_password)
                if success:
                    st.success(message)
                    st.info("Please go to the Login tab and sign in with your credentials.")
                else:
                    st.error(message)
else:
    # Title and introduction
    st.title("AI Financial Tracker")
    st.markdown("""
    This dashboard helps you visualize and analyze your financial data with interactive charts and AI-powered insights.
    Upload your financial data (CSV or Excel) to get started.
    """)

    # Sidebar for data upload and filtering
    with st.sidebar:
        st.header("User Profile")
        if st.session_state.user_info:
            st.write(f"**Logged in as:** {st.session_state.user_info['username']}")
            st.write(f"**Email:** {st.session_state.user_info['email']}")
        else:
            st.write("User profile not available")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.session_state.data = None
            st.session_state.filtered_data = None
            st.rerun()
        
        st.divider()
        st.header("Data Import")
        uploaded_file = st.file_uploader("Upload your financial data", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                # Determine file type and read accordingly
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                
                # Validate if the data looks like financial data
                is_valid, message = validate_financial_data(data)
                
                if is_valid:
                    # Process data
                    processed_data, date_column, numeric_columns, categorical_columns = process_data(data)
                    
                    # Store in session state
                    st.session_state.data = processed_data
                    st.session_state.filtered_data = processed_data
                    st.session_state.columns = processed_data.columns.tolist()
                    st.session_state.date_column = date_column
                    st.session_state.numeric_columns = numeric_columns
                    st.session_state.categorical_columns = categorical_columns
                    
                    st.success("Data successfully loaded!")
                else:
                    st.error(f"Invalid data format: {message}")
                    st.info("Please upload a financial dataset with at least one date column and numeric values.")
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
        
        # Data filtering (only show if data is loaded)
        if st.session_state.data is not None:
            st.header("Data Filtering")
            
            # Date range filter (if date column exists)
            if st.session_state.date_column:
                st.subheader("Date Range")
                min_date = st.session_state.data[st.session_state.date_column].min()
                max_date = st.session_state.data[st.session_state.date_column].max()
                
                date_range = st.date_input(
                    "Select date range",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_data = st.session_state.data[
                        (st.session_state.data[st.session_state.date_column].dt.date >= start_date) & 
                        (st.session_state.data[st.session_state.date_column].dt.date <= end_date)
                    ]
                    st.session_state.filtered_data = filtered_data
            
            # Category filter (if categorical columns exist)
            if st.session_state.categorical_columns:
                st.subheader("Category Filters")
                selected_category_column = st.selectbox(
                    "Select category column",
                    st.session_state.categorical_columns
                )
                
                if selected_category_column and st.session_state.filtered_data is not None:
                    unique_categories = st.session_state.filtered_data[selected_category_column].unique()
                    selected_categories = st.multiselect(
                        "Select categories",
                        unique_categories,
                        default=unique_categories
                    )
                    
                    if selected_categories:
                        st.session_state.filtered_data = st.session_state.filtered_data[
                            st.session_state.filtered_data[selected_category_column].isin(selected_categories)
                        ]

    # Main content area
    if st.session_state.filtered_data is not None:
        # Display basic data info
        st.header("Data Overview")
        with st.expander("Data Preview"):
            st.dataframe(st.session_state.filtered_data.head(10))
        
        # Summary Statistics
        st.header("Financial Summary Statistics")
        summary_stats = get_summary_statistics(st.session_state.filtered_data, st.session_state.numeric_columns)
        st.dataframe(summary_stats)
        
        # Financial Metrics
        st.header("Key Financial Metrics")
        metrics = calculate_financial_metrics(st.session_state.filtered_data, st.session_state.numeric_columns)
        
        # Display metrics in columns
        if metrics:
            col1, col2, col3, col4 = st.columns(4)
            for i, (metric, value) in enumerate(metrics.items()):
                if i % 4 == 0:
                    col1.metric(metric, f"{value:,.2f}")
                elif i % 4 == 1:
                    col2.metric(metric, f"{value:,.2f}")
                elif i % 4 == 2:
                    col3.metric(metric, f"{value:,.2f}")
                else:
                    col4.metric(metric, f"{value:,.2f}")
        else:
            st.info("No financial metrics could be calculated. This may happen if no numeric columns were detected or data is insufficient.")
        
        # Visualization Section
        st.header("Data Visualization")
        
        # Tabs for different chart types
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Time Series", "Bar Charts", "Pie Charts"])
        
        with viz_tab1:
            st.subheader("Time Series Analysis")
            if st.session_state.date_column and st.session_state.numeric_columns:
                time_series_column = st.selectbox(
                    "Select value to plot over time",
                    st.session_state.numeric_columns,
                    key="time_series"
                )
                
                if not st.session_state.filtered_data.empty:
                    try:
                        line_chart = create_line_chart(
                            st.session_state.filtered_data,
                            st.session_state.date_column,
                            time_series_column
                        )
                        st.plotly_chart(line_chart, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not create time series chart: {str(e)}")
                        st.info("Try selecting different columns or check your data format.")
                else:
                    st.info("No data available for time series visualization. Please upload data or adjust filters.")
        
        with viz_tab2:
            st.subheader("Bar Chart Analysis")
            if st.session_state.numeric_columns:
                bar_value_column = st.selectbox(
                    "Select value for bar chart",
                    st.session_state.numeric_columns,
                    key="bar_value"
                )
                
                if st.session_state.categorical_columns:
                    bar_category_column = st.selectbox(
                        "Group by category",
                        st.session_state.categorical_columns,
                        key="bar_category"
                    )
                    
                    if not st.session_state.filtered_data.empty:
                        try:
                            bar_chart = create_bar_chart(
                                st.session_state.filtered_data,
                                bar_category_column,
                                bar_value_column
                            )
                            st.plotly_chart(bar_chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not create bar chart: {str(e)}")
                            st.info("Try selecting different columns or check your data format.")
                    else:
                        st.info("No data available for bar chart visualization. Please upload data or adjust filters.")
                else:
                    st.info("No categorical columns available for bar chart grouping.")
            else:
                st.info("No numeric columns available for bar chart values.")
        
        with viz_tab3:
            st.subheader("Pie Chart Analysis")
            if st.session_state.categorical_columns and st.session_state.numeric_columns:
                pie_value_column = st.selectbox(
                    "Select value for pie chart",
                    st.session_state.numeric_columns,
                    key="pie_value"
                )
                
                pie_category_column = st.selectbox(
                    "Group by category",
                    st.session_state.categorical_columns,
                    key="pie_category"
                )
                
                if not st.session_state.filtered_data.empty:
                    try:
                        pie_chart = create_pie_chart(
                            st.session_state.filtered_data,
                            pie_category_column,
                            pie_value_column
                        )
                        st.plotly_chart(pie_chart, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not create pie chart: {str(e)}")
                        st.info("Try selecting different columns or check your data format.")
                else:
                    st.info("No data available for pie chart visualization. Please upload data or adjust filters.")
            else:
                st.info("Pie charts require both categorical and numeric columns.")
        
        # AI Predictions
        st.header("AI-Powered Predictions")
        
        if st.session_state.date_column and st.session_state.numeric_columns:
            prediction_column = st.selectbox(
                "Select financial metric to predict",
                st.session_state.numeric_columns,
                key="prediction_column"
            )
            
            prediction_days = st.slider(
                "Number of days to predict",
                min_value=7,
                max_value=90,
                value=30,
                step=7
            )
            
            if st.button("Generate Prediction"):
                with st.spinner("Generating AI predictions..."):
                    try:
                        # Get prediction and figure
                        prediction_result, prediction_fig = predict_future_values(
                            st.session_state.filtered_data,
                            st.session_state.date_column,
                            prediction_column,
                            prediction_days
                        )
                        
                        st.success(f"Prediction generated for the next {prediction_days} days")
                        st.plotly_chart(prediction_fig, use_container_width=True)
                        
                        # Show prediction summary
                        st.subheader("Prediction Summary")
                        st.write(f"Predicted average {prediction_column}: {prediction_result['average_prediction']:.2f}")
                        st.write(f"Predicted trend: {prediction_result['trend_description']}")
                        
                    except Exception as e:
                        st.error(f"Error generating prediction: {str(e)}")
                        st.info("Prediction requires sufficient historical data. Try a different metric or adjust date range.")
        
        # Download section
        st.header("Export Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Data"):
                csv = st.session_state.filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="financial_data_export.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export Summary Report"):
                # Create a simple summary report
                buffer = io.StringIO()
                buffer.write("# Financial Dashboard Summary Report\n\n")
                buffer.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                buffer.write("## Data Summary\n")
                buffer.write(f"Records: {len(st.session_state.filtered_data)}\n")
                
                if st.session_state.date_column and not st.session_state.filtered_data.empty:
                    min_date = st.session_state.filtered_data[st.session_state.date_column].min()
                    max_date = st.session_state.filtered_data[st.session_state.date_column].max()
                    buffer.write(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n\n")
                else:
                    buffer.write("Date range: Not available\n\n")
                
                buffer.write("## Key Metrics\n")
                if metrics:
                    for metric, value in metrics.items():
                        buffer.write(f"{metric}: {value:,.2f}\n")
                else:
                    buffer.write("No metrics available\n")
                
                # Add Graph Analysis section
                buffer.write("\n## Graph Analysis\n")
                
                # Time series analysis
                if st.session_state.date_column and not st.session_state.filtered_data.empty:
                    time_series_metrics = []
                    
                    for value_column in st.session_state.numeric_columns[:3]:
                        try:
                            trend_results = analyze_trends(
                                st.session_state.filtered_data,
                                st.session_state.date_column,
                                value_column
                            )
                            
                            if trend_results:
                                time_series_metrics.append(f"### {value_column} Time Series\n")
                                time_series_metrics.append(f"Trend: {trend_results.get('trend', 'Not available')}\n")
                                time_series_metrics.append(f"Average: {trend_results.get('average', 0):.2f}\n")
                                time_series_metrics.append(f"Volatility: {trend_results.get('volatility', 0):.2f}\n")
                                time_series_metrics.append(f"Change rate: {trend_results.get('change_rate', 0):.2f}%\n\n")
                        except:
                            continue
                    
                    if time_series_metrics:
                        buffer.write("".join(time_series_metrics))
                    else:
                        buffer.write("No time series analysis available.\n\n")
                
                # Categorical analysis if available
                if st.session_state.categorical_columns and not st.session_state.filtered_data.empty:
                    buffer.write("### Categorical Analysis\n")
                    
                    try:
                        cat_column = st.session_state.categorical_columns[0]
                        num_column = st.session_state.numeric_columns[0]
                        
                        category_counts = st.session_state.filtered_data[cat_column].value_counts()
                        total = category_counts.sum()
                        
                        buffer.write(f"Distribution for {cat_column}:\n")
                        for category, count in category_counts.items():
                            percentage = (count / total) * 100
                            buffer.write(f"- {category}: {count} ({percentage:.1f}%)\n")
                        
                        buffer.write("\n")
                    except:
                        buffer.write("Error generating categorical analysis.\n\n")
                
                # Add AI predictions if generated
                if 'prediction_result' in st.session_state and st.session_state.prediction_result:
                    prediction_result = st.session_state.prediction_result
                    buffer.write("## AI Predictions\n")
                    if 'prediction_column' in st.session_state:
                        buffer.write(f"Predicted average {st.session_state.get('prediction_column', 'Value')}: {prediction_result['average_prediction']:.2f}\n")
                    buffer.write(f"Predicted trend: {prediction_result['trend_description']}\n\n")
                
                report_text = buffer.getvalue()
                
                st.download_button(
                    label="Download Report",
                    data=report_text,
                    file_name="financial_summary_report.txt",
                    mime="text/plain"
                )
    
    else:
        # Display instructions when no data is loaded
        st.info("👈 Please upload your financial data file using the sidebar to get started.")
        
        # Sample dashboard preview
        st.header("Dashboard Preview")
        st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4c8.svg", width=100)
        st.markdown("""
        ## What you can do with this dashboard:
        
        - **Visualize financial trends** with interactive time series charts
        - **Compare financial metrics** using bar and pie charts
        - **Filter data** by date ranges and categories
        - **Get AI-powered predictions** for future financial performance
        - **Export data and reports** for further analysis
        
        Supported file formats: CSV and Excel (.xlsx, .xls)
        """)
