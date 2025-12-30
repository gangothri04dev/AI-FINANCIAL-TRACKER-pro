# AI Financial Dashboard Generator

## Overview

This is a Streamlit-based financial data analysis and visualization application that provides AI-powered predictions and interactive dashboards. The application allows users to upload financial data (CSV or Excel format), validate and process it, generate various visualizations, and predict future trends using machine learning models.

The system is designed to be flexible and adaptive, working with various financial data formats as long as they contain date and numeric value columns. It provides statistical analysis, interactive charts, and linear regression-based forecasting capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Visualization Library**: Plotly for interactive charts (line charts, bar charts, pie charts)
- **State Management**: Streamlit session state for persisting user data across interactions
- **Layout**: Wide layout with expandable sidebar for data import and filtering controls

**Design Rationale**: Streamlit was chosen for its simplicity in creating data applications without requiring extensive frontend development. Plotly provides rich, interactive visualizations that are essential for financial data exploration.

### Data Processing Pipeline
- **Data Validation**: Multi-step validation process that checks for:
  - Data existence and non-empty datasets
  - Minimum column requirements (at least 2 columns)
  - Presence of valid date columns (80% valid dates threshold)
  - Presence of numeric columns for financial metrics
  
- **Data Processing**: Automatic detection and categorization of columns into:
  - Date columns (for time series analysis)
  - Numeric columns (for calculations and metrics)
  - Categorical columns (for grouping and filtering)

**Design Rationale**: The validation layer ensures data quality before processing, preventing errors downstream. Automatic column type detection makes the application adaptable to different financial data structures.

### Analysis Engine
- **Statistical Analysis**: Comprehensive summary statistics including:
  - Standard descriptive statistics (mean, std, min, max, quartiles)
  - Advanced metrics (median, skew, kurtosis)
  
- **Financial Metrics**: Adaptive metric calculation based on available columns
  - Dynamically adjusts to the specific data structure provided

**Design Rationale**: The flexible analysis approach allows the system to work with various financial data formats rather than requiring a rigid schema.

### AI/ML Prediction System
- **Model**: Linear Regression from scikit-learn
- **Features**: Time-based features (days since first date)
- **Preprocessing**: MinMaxScaler for normalization
- **Validation**: Minimum 10 data points required for reliable predictions
- **Forecast Horizon**: Configurable (default 30 days)

**Design Rationale**: Linear regression provides a simple, interpretable baseline for trend prediction. The minimum data requirement ensures statistical reliability. The time-based feature engineering converts dates into numeric features suitable for regression.

### Visualization Architecture
- **Chart Types**:
  - Line charts for time series data (with trend lines)
  - Bar charts for comparative analysis
  - Pie charts for composition analysis
  
- **Interactive Features**:
  - Unified hover mode for cross-referencing
  - Trend line overlays using OLS (Ordinary Least Squares)
  - Customizable titles and labels

**Design Rationale**: Multiple visualization types cater to different analytical needs. Plotly's interactivity enhances data exploration capabilities.

### Module Structure
The application follows a modular architecture with separation of concerns:

1. **app.py**: Main application orchestrator and UI controller
2. **data_processor.py**: Data validation and preprocessing
3. **financial_analysis.py**: Statistical and financial metric calculations
4. **visualization.py**: Chart generation and rendering
5. **ai_predictions.py**: Machine learning predictions and forecasting

**Design Rationale**: Modular design improves maintainability, testability, and allows for independent development of features.

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework for the user interface
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing and array operations

### Visualization
- **plotly**: Interactive charting library (using both express and graph_objects APIs)

### Machine Learning
- **scikit-learn**: Machine learning library providing:
  - LinearRegression model for predictions
  - MinMaxScaler for data normalization

### Data Format Support
- **CSV files**: Native pandas support
- **Excel files** (.xlsx, .xls): Via pandas Excel readers (requires openpyxl or xlrd)

### Python Standard Library
- **datetime**: Date and time manipulation
- **io**: In-memory file operations

**Note on Database**: The application currently operates on uploaded files without persistent storage. If database integration is needed in the future, the architecture supports adding a data persistence layer (e.g., PostgreSQL with an ORM like Drizzle).