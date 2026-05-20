# Stress-Test-App
Polars-accelerated commodities risk engine simulating systemic macroeconomic shocks across 100,000 active contract positions in under 20ms.

High-Performance Macro Stress-Testing Engine
An interactive, low-latency risk engine prototype designed to simulate macroeconomic market shocks across a large-scale commodities portfolio.

#**The Architecture & First Principles**
Legacy financial data systems frequently suffer from performance bottlenecks when running heavy scenarios row-by-row over massive datasets. This prototype tackles that scale challenge by decoupling the analytics pipeline:

Vectorized Processing Engine: Built on Polars, utilizing multi-threaded C++ operations and lazy query execution graphs to process vector mathematics instantly across the drive.

Optimized Execution Boundary: Evaluates market price shock distributions, updates contract positions, and aggregates net portfolio PnL impacts across 100,000 active positions in less than 20 milliseconds.

Decoupled Data Architecture: Heavy transformations, sorting, and conditional evaluations are computed entirely down in the native memory layer before passing lightweight, fully calculated data structures to the visual presentation framework.

#**Tech Stack**
Language: Python

Data Core: Polars Engine (Lazy Evaluation), NumPy

Interface & Reporting: Streamlit

Data Visualization: Plotly Express

#**Local Installation & Execution**
Ensure you are running inside your preferred Python or Anaconda environment, then install the dependencies and launch the native host server:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/commodity-stress-test.git
cd commodity-stress-test

# Install optimized packages
pip install streamlit polars plotly numpy pandas

# Launch the interactive web runtime
python -m streamlit run app.py
```
