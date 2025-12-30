import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_line_chart(data, date_column, value_column, title=None):
    """
    Create a line chart for time series financial data.
    
    Args:
        data (pd.DataFrame): The data frame to visualize
        date_column (str): Name of the date column
        value_column (str): Name of the value column
        title (str, optional): Chart title. Defaults to None.
    
    Returns:
        plotly.graph_objects._figure.Figure: Plotly figure object
    """
    if title is None:
        title = f"{value_column} Over Time"
    
    # Create the line chart
    fig = px.line(
        data, 
        x=date_column, 
        y=value_column,
        title=title,
        labels={
            date_column: "Date",
            value_column: value_column
        }
    )
    
    # Add trend line
    fig.add_traces(
        px.scatter(
            data,
            x=date_column,
            y=value_column,
            trendline="ols"
        ).data[1]
    )
    
    # Enhance the layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=value_column,
        hovermode="x unified",
        legend_title="",
        height=500
    )
    
    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def create_bar_chart(data, category_column, value_column, title=None):
    """
    Create a bar chart for categorical financial data.
    
    Args:
        data (pd.DataFrame): The data frame to visualize
        category_column (str): Name of the category column
        value_column (str): Name of the value column
        title (str, optional): Chart title. Defaults to None.
    
    Returns:
        plotly.graph_objects._figure.Figure: Plotly figure object
    """
    if title is None:
        title = f"{value_column} by {category_column}"
    
    # Group by category and sum values
    grouped_data = data.groupby(category_column)[value_column].sum().reset_index()
    
    # Sort by value for better visualization
    grouped_data = grouped_data.sort_values(by=value_column, ascending=False)
    
    # Create the bar chart
    fig = px.bar(
        grouped_data,
        x=category_column,
        y=value_column,
        title=title,
        color=category_column,
        labels={
            category_column: category_column,
            value_column: value_column
        }
    )
    
    # Enhance the layout
    fig.update_layout(
        xaxis_title=category_column,
        yaxis_title=value_column,
        legend_title="",
        height=500
    )
    
    return fig

def create_pie_chart(data, category_column, value_column, title=None):
    """
    Create a pie chart for categorical financial data.
    
    Args:
        data (pd.DataFrame): The data frame to visualize
        category_column (str): Name of the category column
        value_column (str): Name of the value column
        title (str, optional): Chart title. Defaults to None.
    
    Returns:
        plotly.graph_objects._figure.Figure: Plotly figure object
    """
    if title is None:
        title = f"{value_column} Distribution by {category_column}"
    
    # Group by category and sum values
    grouped_data = data.groupby(category_column)[value_column].sum().reset_index()
    
    # Sort by value for better visualization (largest first)
    grouped_data = grouped_data.sort_values(by=value_column, ascending=False)
    
    # Limit to top 10 categories if there are too many
    if len(grouped_data) > 10:
        # Keep top 9 and sum others
        top_data = grouped_data.iloc[:9]
        other_sum = grouped_data.iloc[9:][value_column].sum()
        
        # Create 'Other' category
        other_row = pd.DataFrame({
            category_column: ['Other'],
            value_column: [other_sum]
        })
        
        grouped_data = pd.concat([top_data, other_row])
    
    # Create the pie chart
    fig = px.pie(
        grouped_data,
        names=category_column,
        values=value_column,
        title=title,
        hole=0.4,  # Create a donut chart
        labels={
            category_column: category_column,
            value_column: value_column
        }
    )
    
    # Enhance the layout
    fig.update_layout(
        legend_title="",
        height=500
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_heatmap(data, date_column, category_column, value_column, title=None):
    """
    Create a heatmap for time series and categorical financial data.
    
    Args:
        data (pd.DataFrame): The data frame to visualize
        date_column (str): Name of the date column
        category_column (str): Name of the category column
        value_column (str): Name of the value column
        title (str, optional): Chart title. Defaults to None.
    
    Returns:
        plotly.graph_objects._figure.Figure: Plotly figure object
    """
    if title is None:
        title = f"{value_column} Heatmap by {category_column} Over Time"
    
    # Convert date to period (month/year)
    data = data.copy()
    data['period'] = data[date_column].dt.strftime('%Y-%m')
    
    # Group by period and category, sum values
    pivot_data = data.pivot_table(
        index='period',
        columns=category_column,
        values=value_column,
        aggfunc='sum'
    ).fillna(0)
    
    # Create the heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(
            x=category_column,
            y="Time Period",
            color=value_column
        ),
        x=pivot_data.columns,
        y=pivot_data.index,
        title=title,
        color_continuous_scale='RdBu_r'
    )
    
    # Enhance the layout
    fig.update_layout(
        xaxis_title=category_column,
        yaxis_title="Time Period",
        height=500
    )
    
    return fig

def create_waterfall_chart(data, date_column, value_column, title=None):
    """
    Create a waterfall chart for time series financial data.
    Useful for visualizing changes in values over time.
    
    Args:
        data (pd.DataFrame): The data frame to visualize
        date_column (str): Name of the date column
        value_column (str): Name of the value column
        title (str, optional): Chart title. Defaults to None.
    
    Returns:
        plotly.graph_objects._figure.Figure: Plotly figure object
    """
    if title is None:
        title = f"{value_column} Change Over Time"
    
    # Ensure data is sorted by date
    data = data.sort_values(by=date_column)
    
    # Group by month and sum
    data['period'] = data[date_column].dt.strftime('%Y-%m')
    grouped_data = data.groupby('period')[value_column].sum().reset_index()
    
    # Calculate changes between periods
    grouped_data['change'] = grouped_data[value_column].diff()
    
    # Prepare data for waterfall chart
    periods = grouped_data['period'].tolist()
    values = grouped_data['change'].tolist()[1:]  # Skip first (NaN)
    
    # Insert first period's absolute value
    periods = [periods[0]] + periods[1:]
    values = [grouped_data[value_column].iloc[0]] + values
    
    # Create measure and text arrays
    measure = ['absolute'] + ['relative'] * (len(values) - 1)
    text = [f"{values[0]:.2f}"] + [f"{v:.2f}" for v in values[1:]]
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        name=value_column,
        orientation="v",
        measure=measure,
        x=periods,
        textposition="outside",
        text=text,
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    # Add total
    fig.add_trace(go.Scatter(
        x=[periods[-1]],
        y=[grouped_data[value_column].iloc[-1]],
        mode="markers",
        marker=dict(color="red", size=10),
        name="Final Value"
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Time Period",
        yaxis_title=value_column,
        showlegend=True,
        height=500
    )
    
    return fig
