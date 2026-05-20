import streamlit as st
import polars as pl
import numpy as np
import plotly.express as px
import time

# --- STAGE 0: Page Layout Configuration ---
st.set_page_config(
    page_title="Enterprise Risk Engine: Macro Stress Testing",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 High-Performance Risk Engine")
st.caption("Polars-accelerated portfolio stress testing over 100,000 contract positions")

# --- STAGE 1: Data Initialization (Cached for speed) ---
@st.cache_data(max_entries=1)
def generate_portfolio(num_records=100000):
    """Generates synthetic baseline commodities portfolio."""
    np.random.seed(42)
    commodities = ["Crude Oil", "Natural Gas", "Gold", "Copper", "Corn", "Wheat"]
    
    data = {
        "contract_id": [f"CNT-{i:06d}" for i in range(num_records)],
        "commodity": np.random.choice(commodities, num_records),
        "position_size": np.random.uniform(1000, 50000, num_records),
        "current_price": np.random.uniform(5.0, 200.0, num_records),
    }
    
    df = pl.DataFrame(data)
    return df.with_columns(
        (pl.col("position_size") * pl.col("current_price")).alias("base_value")
    )

# Pre-load the core asset dataframe
base_portfolio = generate_portfolio(100000)

# --- STAGE 2: Sidebar Control Panel (Shock Inputs) ---
st.sidebar.header("Macro Shock Controls")
st.sidebar.markdown("Adjust the price multiplier for each commodity class below:")

# Interactive sliders for custom shock scenarios
shocks = {
    "Crude Oil": st.sidebar.slider("Oil (Crude) Multiplier", 0.20, 1.80, 0.60, 0.05),
    "Natural Gas": st.sidebar.slider("Natural Gas Multiplier", 0.20, 1.80, 0.50, 0.05),
    "Gold": st.sidebar.slider("Gold Multiplier", 0.20, 1.80, 1.25, 0.05),
    "Copper": st.sidebar.slider("Copper Multiplier", 0.20, 1.80, 0.75, 0.05),
    "Corn": st.sidebar.slider("Corn Multiplier", 0.20, 1.80, 0.90, 0.05),
    "Wheat": st.sidebar.slider("Wheat Multiplier", 0.20, 1.80, 0.85, 0.05)
}

# --- STAGE 3: Core Analytical Engine Processing ---
def compute_stressed_portfolio(df: pl.DataFrame, shock_map: dict):
    """Leverages deeply nested when/then structures to match old Polars versions."""
    
    # Start with the baseline default value
    shock_expr = pl.col("current_price")
    
    # Wrap each commodity scenario inside a nested conditional layer
    for commodity, multiplier in shock_map.items():
        shock_expr = pl.when(pl.col("commodity") == commodity).then(pl.col("current_price") * multiplier).otherwise(shock_expr)
    
    # Run optimization pipeline via engine
    return (
        df.lazy()
        .with_columns(shock_expr.alias("stressed_price"))
        .with_columns(
            (pl.col("position_size") * pl.col("stressed_price")).alias("stressed_value")
        )
        .with_columns(
            (pl.col("stressed_value") - pl.col("base_value")).alias("pnl_impact")
        )
        .collect()
    )

# Track precise evaluation speeds
t_start = time.time()
stressed_df = compute_stressed_portfolio(base_portfolio, shocks)
processing_time = time.time() - t_start

# --- STAGE 4: High-Level Portfolio Aggregations ---
total_base_val = stressed_df["base_value"].sum()
total_stress_val = stressed_df["stressed_value"].sum()
total_pnl = stressed_df["pnl_impact"].sum()

# Layout key performance indicators inside containers
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total Base Value", f"${total_base_val/1e6:.2f}M")
with kpi2:
    st.metric("Stressed Value", f"${total_stress_val/1e6:.2f}M", f"{(total_stress_val/total_base_val - 1)*100:.1f}%")
with kpi3:
    # Toggle color design based on gain or loss state
    st.metric("Net Risk PnL Impact", f"${total_pnl/1e6:.2f}M", delta_color="inverse" if total_pnl < 0 else "normal")
with kpi4:
    st.metric("Engine Execution Speed", f"{processing_time*1000:.1f} ms", "Polars Core")

st.markdown("---")

# --- STAGE 5: Rich Data Visualization Section ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🌋 Financial PnL Impact by Asset Class")
    # Group and aggregate data with Polars before passing to charting libraries
    breakdown = (
        stressed_df.group_by("commodity")
        .agg(pl.col("pnl_impact").sum() / 1e6)
        .to_pandas() # Hand over lightweight aggregated subset to Plotly
    )
    
    fig_bar = px.bar(
        breakdown, 
        x="commodity", 
        y="pnl_impact",
        labels={"commodity": "Asset Class", "pnl_impact": "PnL Impact ($ Millions)"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🚨 Tail-Risk Vulnerability: Worst Hit Positions")
    # Instantly sort millions of bytes down to the top outliers
    outliers = (
        stressed_df.sort("pnl_impact")
        .select(["contract_id", "commodity", "position_size", "pnl_impact"])
        .head(10)
        .to_pandas()
    )
    st.dataframe(outliers, use_container_width=True, hide_index=True)

st.subheader("🔍 Dynamic Portfolio Inspection")
st.dataframe(stressed_df.head(100).to_pandas(), use_container_width=True)
