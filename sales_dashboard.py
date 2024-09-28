# sales_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Load the sales data
@st.cache_data
def load_data():
    # Replace 'Cleaned_Superstore_Sales_Dataset.csv' with your cleaned sales dataset
    df = pd.read_csv('Cleaned_Superstore_Sales_Dataset.csv', parse_dates=['Order Date'])
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df.set_index('Order Date', inplace=True)
    return df

df = load_data()

# Dashboard title
st.title("Sales Performance Analysis and Forecasting Dashboard")

# Sidebar filters
st.sidebar.header("Filter Options")

# Date range filter
st.sidebar.subheader("Select Order Date Range")
min_date = df.index.min().date()
max_date = df.index.max().date()
start_date, end_date = st.sidebar.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply date filter
filtered_df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]

# Region filter
region_filter = st.sidebar.multiselect("Select Regions", options=filtered_df['Region'].unique(), default=filtered_df['Region'].unique())
# Category filter
category_filter = st.sidebar.multiselect("Select Product Categories", filtered_df['Category'].unique(), default=filtered_df['Category'].unique())

# Apply category and region filters
filtered_df = filtered_df[(filtered_df['Region'].isin(region_filter)) & (filtered_df['Category'].isin(category_filter))]

# Display raw data
st.subheader("Filtered Sales Data Preview")
st.write("This section provides an overview of the sales data based on your selected filters.")
st.dataframe(filtered_df.head())

# Animated Monthly Sales Trend
st.subheader("Animated Monthly Sales Trend (Filtered by Selected Regions and Categories)")
monthly_sales = filtered_df['Sales'].resample('M').sum().reset_index()
monthly_sales['Year-Month'] = monthly_sales['Order Date'].dt.to_period('M').astype(str)  # Create a year-month column for animation
fig = px.line(monthly_sales, 
              x='Order Date', 
              y='Sales', 
              title='Animated Monthly Sales Trend (Filtered)',
              animation_frame='Year-Month',
              labels={'Order Date': 'Date', 'Sales': 'Total Sales (USD)'},
              range_y=[0, monthly_sales['Sales'].max()],
              template="plotly", 
              markers=True)
fig.update_traces(hovertemplate='<b>Date:</b> %{x|%Y-%m}<br><b>Total Sales:</b> %{y:,.2f} USD')
st.plotly_chart(fig)

# Monthly Sales Trend by Region
st.subheader("Monthly Sales Trend by Region")
monthly_sales_region = filtered_df.groupby([filtered_df.index.to_period("M"), 'Region'])['Sales'].sum().reset_index()
monthly_sales_region['Order Date'] = monthly_sales_region['Order Date'].astype(str)
fig = px.bar(monthly_sales_region, 
             x='Order Date', 
             y='Sales', 
             color='Region', 
             title='Monthly Sales by Region',
             labels={'Order Date': 'Month', 'Sales': 'Total Sales (USD)', 'Region': 'Region'},
             template="plotly")
fig.update_traces(hovertemplate='<b>Month:</b> %{x}<br><b>Region:</b> %{legendgroup}<br><b>Sales:</b> %{y:,.2f} USD')
st.plotly_chart(fig)

# Interactive Bar Chart: Sales by Sub-Category over Time
st.subheader("Interactive Sales by Sub-Category Over Time")
monthly_subcategory_sales = filtered_df.groupby([filtered_df.index.to_period('M'), 'Sub-Category'])['Sales'].sum().reset_index()
monthly_subcategory_sales['Order Date'] = monthly_subcategory_sales['Order Date'].astype(str)
fig = px.bar(monthly_subcategory_sales, 
             x='Order Date', 
             y='Sales', 
             color='Sub-Category', 
             title='Interactive Sales by Sub-Category Over Time',
             labels={'Order Date': 'Month', 'Sales': 'Total Sales (USD)', 'Sub-Category': 'Sub-Category'},
             template="plotly",
             animation_frame='Order Date',
             animation_group='Sub-Category',
             range_y=[0, monthly_subcategory_sales['Sales'].max()])
fig.update_traces(hovertemplate='<b>Month:</b> %{x}<br><b>Sub-Category:</b> %{legendgroup}<br><b>Sales:</b> %{y:,.2f} USD')
st.plotly_chart(fig)

# Sales Contribution by Sub-Category Pie Chart
st.subheader("Sales Contribution by Sub-Category")
sales_by_subcategory = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()
fig = px.pie(sales_by_subcategory, values='Sales', names='Sub-Category',
             title='Sales Contribution by Sub-Category',
             template="plotly", hole=0.4)
fig.update_traces(textinfo='percent+label', hovertemplate='<b>Sub-Category:</b> %{label}<br><b>Sales:</b> %{value:,.2f} USD (%{percent})')
st.plotly_chart(fig)

# Heatmap by Region and Month
st.subheader("Heatmap of Sales by Region and Month")
st.write("The heatmap below shows the total sales by region across different months, providing insights into regional sales trends.")

# Create a pivot table for the heatmap
region_monthly_sales = filtered_df.groupby([filtered_df.index.to_period("M"), 'Region'])['Sales'].sum().reset_index()
region_monthly_sales_pivot = region_monthly_sales.pivot(index="Region", columns="Order Date", values="Sales").fillna(0)

# Display the heatmap using seaborn
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(region_monthly_sales_pivot, cmap="YlGnBu", linewidths=0.5, annot=True, fmt=".0f", ax=ax)
plt.title('Heatmap of Sales by Region and Month')
plt.xlabel('Month')
plt.ylabel('Region')
st.pyplot(fig)

# Top 10 Products by Sales
st.subheader("Top 10 Products by Sales (Filtered by Selected Regions and Categories)")
top_products = filtered_df.groupby('Product Name')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(10)
fig = px.bar(top_products, x='Product Name', y='Sales', title="Top 10 Products by Sales", 
             labels={'Sales': 'Total Sales (USD)', 'Product Name': 'Product'}, 
             template="plotly", color='Sales')
fig.update_traces(hovertemplate='<b>Product:</b> %{x}<br><b>Total Sales:</b> %{y:,.2f} USD')
st.plotly_chart(fig)
