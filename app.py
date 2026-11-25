# import libaries
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    # dealing with dataset
    # load csv dataset
    # dataset get from https://www.kaggle.com/datasets/yoongsin/shopee-sample-data
    df =  pd.read_csv('20240121_shopee_sample_data (1).csv')
    # Convert date columns
    df['w_date'] = pd.to_datetime(df['w_date'])
    # Fill NaN values in the 'delivery' column with Other states because too many Nan in this coloum
    df['delivery'] = df['delivery'].fillna('Other states')
    # Split item_category_detail by | into few new columns
    df['Main_Category'] = df['item_category_detail'].str.split('|').str[1]
    df['Sub_Category1'] = df['item_category_detail'].str.split('|').str[2]
    df['Sub_Category2'] = df['item_category_detail'].str.split('|').str[3]
    # split product_location based on specification after From(the keyword)
    # df['product_location'] = df['specification'].str.split('From', n=1, expand=True)[1]
    # Define a function to handle potential data types and extract state
    def extract_state_from_spec(spec):
      # Check if 'spec' is a string (assuming city and state are in string format)
      if isinstance(spec, str):
        # Split the text by 'Ship From:'
        parts = spec.split('Ships From ')
        # If there are parts after splitting, extract the first word (assuming it's the state)
        if len(parts) > 1:
            x = parts[-1].split(" ")
            return x[-1]
        else:
          return 'No state'  # Handle cases where "Ship From:" is present but no state info follows
      else:
        return 'No info'  # Handle cases where 'spec' is not a string (e.g., numeric)
    # Apply the function to the 'specification' column and create a new column
    df['product_location'] = df['specification'].apply(extract_state_from_spec)
    df['product_location'] = df['product_location'].replace('Lumpur', 'Kuala Lumpur')
    oversea = ["Thailand", "China", "Indonesia", "Vietnam", "Korea", "Taiwan"]
    df['product_location'] = df['product_location'].replace(oversea, 'Overseas')  # Replace oversea
    # Convert few columns to numeric
    # Define the columns you want to process
    cols_to_convert = ['item_rating', 'total_rating', 'total_sold']
    # Process the columns
    for col in cols_to_convert:
        # 1. Convert column to string to safely use string methods
        col_str = df[col].astype(str)
        # 2. Check for 'k' or 'K' (equivalent to grepl("k", ., ignore.case = TRUE))
        has_k = col_str.str.contains('k', case=False, na=False)
        # 3. Remove everything except digits and '.' (equivalent to gsub("[^0-9.]", "", .))
        cleaned_str = col_str.str.replace(r'[^0-9.]', '', regex=True)
        # 4. Convert to numeric (equivalent to as.numeric)
        # errors='coerce' turns empty strings or unparseable values into NaN
        numeric_vals = pd.to_numeric(cleaned_str, errors='coerce')
        # 5. Multiply by 1000 if 'k' is present, else leave as is (equivalent to ifelse)
        df[col] = np.where(has_k, numeric_vals * 1000, numeric_vals)
    # drop others row with Nan
    df = df.dropna()
    # drop duplicate
    df = df.drop_duplicates()
    return df

# ============================================================================
# TASK 6: TIMELINE VISUALIZATION
# ============================================================================
def create_timeline():
    #reate project progress timeline
    timeline_data = pd.DataFrame([
        {"Phase": "Project Initiation", "start": "2026-02-01", "end": "2026-02-15", "Description": "Defined the e-commerce business problem and dashboard objectives."},
        {"Phase": "Data Collection", "start": "2026-02-16", "end": "2026-03-10", "Description": "Collected the Shopee product listing dataset."},
        {"Phase": "Data Cleaning", "start": "2026-03-11", "end": "2026-03-31", "Description": "Handled missing values and prepared variables for analysis."},
        {"Phase": "Dashboard Development", "start": "2026-04-01", "end": "2026-05-15", "Description": "Developed the Streamlit dashboard and visualizations."},
        {"Phase": "Testing & Validation", "start": "2026-05-16", "end": "2026-06-10", "Description": "Checked filters, charts, interactions, and usability."},
        {"Phase": "Deployment", "start": "2026-06-11", "end": "2026-07-20", "Description": "Finalized the dashboard and prepared the project presentation."}
    ])
    timeline_data["start"] = pd.to_datetime(timeline_data["start"])
    timeline_data["End"] = pd.to_datetime(timeline_data["end"])
    return timeline_data

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Shopee E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# load data
df = load_data()
timeline_data = create_timeline()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.title("🛒 Shopee Analytics")
st.sidebar.markdown("---")
# User Mode Selection (Task 2: User-Centered Design)
st.sidebar.subheader("👤 User Mode")
user_mode = st.sidebar.radio(
    "Select user type:",
    ["Child", "Adult", "Elderly"],
    index=1,
    help="Different interfaces optimized for different user groups"
)
st.sidebar.subheader("Visualization")
selection_mode = st.sidebar.radio(
    "Select Dashboard Section:",
    ["Executive Overview", "Advanced Visualizations", "Timeline"]
)

# Set base configs depending on user mode for the advanced tabs
if user_mode == "Child":
    width = 400
    height = 600
    num_of_columns = 2
    alt_color_scheme = 'pastel1'
    plotly_template = 'plotly_white'
    font_size_title = 20
    font_size_label = 14
elif user_mode == "Adult":
    width = 300
    height = 450
    num_of_columns = 3
    alt_color_scheme = 'set1'
    plotly_template = 'plotly'
    font_size_title = 16
    font_size_label = 12
elif user_mode == "Elderly":
    width = 400
    height = 500
    num_of_columns = 2
    alt_color_scheme = 'dark2' 
    plotly_template = 'presentation'
    font_size_title = 24
    font_size_label = 18

# ============================================================
# EXECUTIVE OVERVIEW (USER-CENTERED DESIGN IMPLEMENTATION)
# ============================================================
if selection_mode == "Executive Overview":
    
    if user_mode == "Child":
        # 🎈 CHILD MODE: Large icons, minimal text, bright colors, simple navigation
        st.markdown("<h1 style='text-align: center; color: #FF5722; font-size: 48px;'>🎈 Welcome to the Fun Shop! 🎈</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #4CAF50;'>Let's see what people are buying!</h3>", unsafe_allow_html=True)
        
        # Simple Interactive Filter
        st.write("### 🔍 Pick a Toy Box:")
        top_3_cats = df['Main_Category'].value_counts().head(3).index.tolist()
        child_cat = st.selectbox("Choose one to open!", top_3_cats)
        
        child_df = df[df['Main_Category'] == child_cat]
        
        # Bright Summary Cards / KPIs
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style='background-color: #FFEB3B; padding: 20px; border-radius: 20px; text-align: center; border: 5px dashed #FF9800;'>
                <h2 style='color:#E65100; font-size: 32px;'>🎁 Total Presents Sold</h2>
                <h1 style='color:#E65100; font-size: 50px;'>{int(child_df['total_sold'].sum())}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style='background-color: #81D4FA; padding: 20px; border-radius: 20px; text-align: center; border: 5px dashed #0288D1;'>
                <h2 style='color:#01579B; font-size: 32px;'>⭐ Happy Stars (Rating)</h2>
                <h1 style='color:#01579B; font-size: 50px;'>{child_df['item_rating'].mean():.1f} / 5</h1>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        
        # Colorful Dynamic Chart
        st.write("### 🏆 Top Places Sending Presents!")
        child_loc = child_df.groupby('product_location')['total_sold'].sum().nlargest(5).reset_index()
        fig_child = px.pie(child_loc, values='total_sold', names='product_location', hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_child.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
        fig_child.update_layout(font=dict(size=18, family="Comic Sans MS, Arial"))
        st.plotly_chart(fig_child, use_container_width=True)

    elif user_mode == "Adult":
        # 💼 ADULT MODE: Info-rich, filtering, comparative analysis, drill-downs
        st.title("💼 Executive Analytics Dashboard")
        st.markdown("Detailed breakdown of sales performance, ratings, and product distribution.")
        
        # Interactive Filters
        with st.expander("🔍 Advanced Drill-down Filters", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                sel_cats = st.multiselect("Filter by Main Category", options=df['Main_Category'].unique(), default=df['Main_Category'].value_counts().head(3).index)
            with col_f2:
                sel_locs = st.multiselect("Filter by Product Location", options=df['product_location'].unique(), default=df['product_location'].value_counts().head(5).index)
        
        # Apply filters
        adult_df = df.copy()
        if sel_cats:
            adult_df = adult_df[adult_df['Main_Category'].isin(sel_cats)]
        if sel_locs:
            adult_df = adult_df[adult_df['product_location'].isin(sel_locs)]
            
        # Information-Rich KPIs
        st.subheader("Key Performance Indicators")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Sales Volume", f"{adult_df['total_sold'].sum():,.0f}")
        kpi2.metric("Avg Product Rating", f"{adult_df['item_rating'].mean():.2f} ⭐")
        kpi3.metric("Total Reviews Count", f"{adult_df['total_rating'].sum():,.0f}")
        kpi4.metric("Unique Listings", f"{adult_df['id'].nunique():,}")
        
        st.markdown("---")
        
        # Comparative & Drill-down Charts
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Sub-Category Drill-down (Sales)")
            # Sunburst Chart for deep drill-down analysis
            fig_sun = px.sunburst(adult_df, path=['Main_Category', 'Sub_Category1'], values='total_sold', 
                                  color='item_rating', color_continuous_scale='Blues')
            fig_sun.update_layout(margin=dict(t=20, l=0, r=0, b=0), height=450)
            st.plotly_chart(fig_sun, use_container_width=True)
            
        with col_c2:
            st.subheader("Performance Comparison by State")
            # Bar chart for comparative analysis
            loc_perf = adult_df.groupby('product_location').agg({'total_sold':'sum', 'item_rating':'mean'}).reset_index().nlargest(10, 'total_sold')
            fig_bar = px.bar(loc_perf, x='product_location', y='total_sold', color='item_rating',
                             labels={'total_sold': 'Total Units Sold', 'product_location': 'State', 'item_rating':'Avg Rating'})
            fig_bar.update_layout(margin=dict(t=20, l=0, r=0, b=0), height=450)
            st.plotly_chart(fig_bar, use_container_width=True)

    elif user_mode == "Elderly":
        # 👓 ELDERLY MODE: High contrast, larger fonts, simplified interactions, accessibility
        st.markdown("<h1 style='font-size: 44px; color: #000000; border-bottom: 5px solid #000000;'>📊 Clear Sales Overview</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='font-size: 32px; color: #222222; margin-top: 20px;'>1. Choose a Category to View:</h2>", unsafe_allow_html=True)
        
        # Simplified interaction (Radio buttons instead of dropdowns)
        top_cats_eld = df['Main_Category'].value_counts().head(4).index.tolist()
        top_cats_eld.insert(0, "Show All Categories")
        
        # Using Streamlit's native radio but styling it through the overall interface design
        eld_cat = st.radio("Select one option:", top_cats_eld, index=0, label_visibility="collapsed")
        
        eld_df = df if eld_cat == "Show All Categories" else df[df['Main_Category'] == eld_cat]
        
        st.markdown("<h2 style='font-size: 32px; color: #222222; margin-top: 30px;'>2. Important Metrics:</h2>", unsafe_allow_html=True)
        
        # High contrast, large font summary cards
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown(f"""
            <div style='background-color: #000000; padding: 40px; border: 8px solid #CCCCCC; border-radius: 10px; text-align: center;'>
                <h3 style='color: #FFFFFF; font-size: 32px; margin: 0;'>TOTAL ITEMS SOLD</h3>
                <p style='color: #FFFF00; font-size: 60px; font-weight: bold; margin: 0;'>{eld_df['total_sold'].sum():,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_e2:
            st.markdown(f"""
            <div style='background-color: #000000; padding: 40px; border: 8px solid #CCCCCC; border-radius: 10px; text-align: center;'>
                <h3 style='color: #FFFFFF; font-size: 32px; margin: 0;'>AVERAGE RATING</h3>
                <p style='color: #FFFF00; font-size: 60px; font-weight: bold; margin: 0;'>{eld_df['item_rating'].mean():.1f} / 5</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        st.markdown("<h2 style='font-size: 32px; color: #222222;'>3. Sales by Location:</h2>", unsafe_allow_html=True)
        
        # High contrast dynamic chart
        eld_loc = eld_df.groupby('product_location')['total_sold'].sum().nlargest(5).reset_index()
        fig_eld = px.bar(eld_loc, x='product_location', y='total_sold', text='total_sold')
        
        # Adjusting layout for accessibility (bold lines, large text, high contrast colors)
        fig_eld.update_traces(texttemplate='%{text:,.0f}', textposition='outside', 
                              marker_color='#00008B', marker_line_color='black', marker_line_width=4,
                              textfont_size=24, textfont_color="black")
        fig_eld.update_layout(
            font=dict(size=24, color="#000000"),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            xaxis_title="<b>Location</b>",
            yaxis_title="<b>Total Sold</b>",
            height=600,
            margin=dict(t=40)
        )
        # Bold axes lines
        fig_eld.update_xaxes(showline=True, linewidth=3, linecolor='black', gridcolor='lightgray')
        fig_eld.update_yaxes(showline=True, linewidth=3, linecolor='black', gridcolor='lightgray')
        
        st.plotly_chart(fig_eld, use_container_width=True)

# ============================================================
# ADVANCED VISUALIZATIONS SECTION
# ============================================================
elif selection_mode == "Advanced Visualizations":
    st.title("📊 Advanced Visualization Analysis")
    st.info("This section contains two advanced visualization techniques required by the project.")
    
    # ========================================================
    # ADVANCED TECHNIQUE 1: Trellis Plot
    # ========================================================
    st.header("Trellis Display")
    st.write("Bar chart of number of sale from top 5 product location by top 5 category.") 
    
    top_categories = df['Main_Category'].value_counts().head(5).index.tolist()
    most_location = df['product_location'].value_counts().head(5).index.tolist()
    
    trellis_data = df[df['Main_Category'].isin(top_categories) & df['product_location'].isin(most_location)]
    trellis_data = trellis_data.groupby(['Main_Category', trellis_data['w_date'].dt.month, 'product_location'])['id'].count().reset_index(name='Number_of_Sale')
    
    translation = {4: "April", 5: "May"}
    trellis_data['w_date'] = trellis_data['w_date'].map(translation)
    
    trellis_chart = alt.Chart(trellis_data, width=width, height=height).mark_bar().encode(
        x=alt.X('product_location:N', title=None),
        y=alt.Y('Number_of_Sale:Q', title='Number of Sale'),
        color=alt.Color('w_date:N', scale=alt.Scale(scheme=alt_color_scheme),
        legend=alt.Legend(title='Month')), 
        tooltip=['Number_of_Sale', 'product_location', 'w_date'] 
    ).facet(
        facet=alt.Facet('Main_Category:N', title='Category'),
        columns=num_of_columns 
    ).properties(
        title='Trellis: Number of Sale vs Product Location'
    ).resolve_axis(
        x='independent' # THIS FORCES THE STATE LABELS TO APPEAR ON THE TOP ROW AS WELL
    )
    # Add one shared x-axis title below the whole trellis chart
    shared_x_title = alt.Chart(
        pd.DataFrame({
            'text': ['Product Location']
        })
    ).mark_text(
        fontSize=14,
        dy=20
    ).encode(
        text='text:N'
    )
    # Combine the chart and shared title
    final_chart = alt.vconcat(
        trellis_chart,
        shared_x_title
    ).resolve_scale(
        x='shared'
    )
    st.altair_chart(final_chart, width='stretch') 
    st.caption("**Insight:** The trellis display allows comparison of subcategory performance across different main categories. Each panel shows the same chart type for a different category, enabling easy pattern comparison.")
    
    st.markdown("---")
    
    # ========================================================
    # ADVANCED TECHNIQUE 2: Scatter Plot Matrix
    # ========================================================
    st.header("Scatter Plot Matrix")
    st.write("Pairwise relationships between numerical metrics (Item Rating, Total Rating, and Total Sold) across the Top 5 Categories.")
    
    scatter_data = df[df['Main_Category'].isin(top_categories)].copy()
    if len(scatter_data) > 1000:
        scatter_data = scatter_data.sample(1000, random_state=42)
        st.warning("Note: Data has been sampled down to 1000 points to optimize rendering performance.")
        
    fig_scatter = px.scatter_matrix(
        scatter_data,
        dimensions=['item_rating', 'total_rating', 'total_sold'],
        color='Main_Category',
        title="Scatter Plot Matrix: Ratings and Sales Metrics",
        opacity=0.7,
        labels={
            'item_rating': 'Item Rating',
            'total_rating': 'Total Rating',
            'total_sold': 'Total Sold'
        }
    )
    
    fig_scatter.update_layout(
        height=700,
        hovermode='closest',
        dragmode='select'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("**Insight:** The scatter plot matrix reveals correlations and distributions among multiple numerical variables at once. Plotting them side-by-side with categorical color encodings highlights where different product categories group together.")

# ============================================================
# TIMELINE SECTION
# ============================================================
elif selection_mode == "Timeline":
    st.title("📅 Project Progress Timeline")
    st.markdown("Interactive timeline covering the five-month project development period.")
    
    fig = px.timeline(timeline_data, 
                      x_start="start",
                      x_end="end",
                      y="Phase",
                      color="Phase",
                      hover_data=["Description"],
                      title="Project Development Progress",
                      template=plotly_template, # Dynamic template
                      color_discrete_sequence=px.colors.qualitative.Pastel if user_mode == "Child" else px.colors.qualitative.Dark24) # Dynamic colors
    # Dynamic font sizing in Plotly
    fig.update_layout(
        font=dict(size=font_size_label),
        title=dict(font=dict(size=font_size_title))
    )
    st.plotly_chart(fig, width='stretch')
    # Adjust UI helper text
    if user_mode == "Child":
        st.write("👉 **Pick a step to see what we did:**")
    elif user_mode == "Elderly":
        st.write("**PLEASE SELECT A PROJECT PHASE BELOW:**")
    else:
        st.write("Select a project phase:")
    selected_stage = st.selectbox("", timeline_data["Phase"], label_visibility="collapsed")
    selected_info = timeline_data[timeline_data["Phase"] == selected_stage]
    st.info(selected_info["Description"].iloc[0])
