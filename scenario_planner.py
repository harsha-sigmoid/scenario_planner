import streamlit as st
import pandas as pd
from pathlib import Path
import os 
from streamlit_option_menu import option_menu
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# =========================
# 🧠 Budget Scenario Planner Functions
# =========================
def load_backend_data(filepath="backend_data.xlsx"):
    """Simulates loading all scenario data from a backend (Excel or API)."""
    try:
        df_dict = pd.read_excel(filepath, sheet_name=None)
    except FileNotFoundError:
        df_dict = {
            "planned": pd.DataFrame({
                "Channel": ["Display", "FEP", "Search", "Social Media", "Video"],
                "Site" : ["NYT", "FEP_YT", "Search", "Facebook", "Youtube"],
                "Planned Budget": [700000, 500000, 300000, 200000, 600000],
                "Expected CPM": ["$6.5", "$8.5", "$5.5", "$9.5", "6.5"]
            }),
            "recommended": pd.DataFrame({
                "Channel": ["Display", "FEP", "Search", "Social Media", "Video"],
                "Site" : ["NYT", "FEP_YT", "Search", "Facebook", "Youtube"],
                "Recommended Budget": [650000, 520000, 350000, 180000, 450000],
                "Expected CPM": ["$6.3 - $6.8", "$8.1 - $8.9", "$5.0 - $5.5", "$9.3 - $10.0", "$6.3 - $6.8"],
                "IUs": [3500, 8100, 12750, 4000, 7000],
                "ROI": [3.14, 1.414, 3.43, 3.01, 3.14]
            }),
            "simulation": pd.DataFrame({
                "Channel": ["Display", "FEP", "Search", "Social Media", "Video"],
                "Site" : ["NYT", "FEP_YT", "Search", "Facebook", "Youtube"],
                "Planned Budget": [700000, 500000, 300000, 200000, 600000],
                "Exp. CPM (Planned)": ["$6.5 - $7.0", "$8.0 - $8.7", "$5.2 - $5.8", "$9.1 - $9.8", "$6.5 - $7.0"],
                "Recommended Budget": [650000, 520000, 350000, 180000, 450000],
                "Desired Budget": [650000, 500000, 350000, 150000, 450000],
                "Exp. CPM Range": ["$6.3 - $6.8", "$8.1 - $8.9", "$5.0 - $5.5", "$9.3 - $10.0", "$6.3 - $6.8"],
            })
        }
    return df_dict

st.set_page_config(
    page_title="Budget Scenario Planner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Function to Inject CSS Safely ---
def apply_custom_css(css_file: str = "styles.css"):
    """
    Inject custom CSS that works both locally and on Streamlit Cloud.
    If styles.css is missing, this function silently skips.
    """
    css_path = Path(__file__).parent / css_file
    if css_path.exists():
        css_content = css_path.read_text()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {css_path}")

def display_aggrid_table(dataframe, fit_columns=True):
    """
    Streamlit AgGrid table styled with theme-matched green headers, beige rows,
    centered text, rounded corners, and Streamlit aesthetic consistency.
    No ghost column issue on resize.
    """
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    
    # --- Cell style ---
    cell_style = JsCode("""
    function(params) {
        return {
            'textAlign': 'center',
            'fontSize': '16px',
            'color': '#042b0b',
            'backgroundColor': (params.node.rowIndex % 2 === 0) ? '#f5f1e9' : '#efe6d4',
            'borderRight': '1px solid #c9dbc9',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '8px',
        };
    }
    """)

    # --- Header style ---
    header_style = JsCode("""
    function(params) {
        return {
            'textAlign': 'center',
            'color': 'white',
            'fontWeight': '700',
            'fontSize': '16px',
            'backgroundColor': '#154c29',
            'borderRight': '1px solid #c9dbc9',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
        };
    }
    """)

    # Apply styles to all columns
    for col in dataframe.columns:
        gb.configure_column(
            col,
            cellStyle=cell_style,
            headerStyle=header_style,
            headerClass = "streamlit-custom",
            minWidth=100,               # Slightly larger min width
            suppressSizeToFit=False,
            wrapHeaderText = True
        )

    # --- JS Auto-resize Fix ---
    # When the grid is loaded or resized, this ensures columns fit exactly
    grid_size_handler = JsCode("""
        function(params) {
            params.api.sizeColumnsToFit();
        }
    """)

    gb.configure_grid_options(
        onGridSizeChanged=grid_size_handler,   # 👈 Key line
        headerHeight=50,
        rowHeight=48,
        domLayout='autoHeight',
        suppressHorizontalScroll=False,        # Allow natural scroll when needed
        suppressMovableColumns=True,
        suppressColumnVirtualisation=True,
        suppressSizeToFit=False
    )

    gridOptions = gb.build()

    # --- Custom CSS for outer AgGrid wrapper ---
    st.markdown("""
    <style>
    .ag-header-cell-label {
        justify-content: center;
    }
    .ag-theme-streamlit-custom {
        border: 2px solid #154c29 !important;
        border-radius: 12px !important;
        background-color: #f5f1e9 !important;
        overflow: hidden !important;
        box-shadow: 0 4px 10px rgba(21,76,41,0.15) !important;
    }

    .ag-theme-streamlit-custom .ag-root-wrapper {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    .ag-theme-streamlit-custom .ag-header {
        background-color: #154c29 !important;
    }

    .ag-theme-streamlit-custom .ag-header-cell-label {
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        textAlign
        justify-content: center !important;
    }

    .ag-theme-streamlit-custom .ag-row-hover {
        background-color: #e8f5e9 !important;
    }

    .ag-theme-streamlit-custom .ag-cell {
        border-right: 1px solid #c9dbc9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Render AgGrid ---
    response = AgGrid(
        dataframe,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,  # 👈 Critical: ensures perfect fit at load
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
        theme='streamlit-custom',
        height=400,
    )

    return response['data']


def get_period_options(horizon):
    """Return period options based on selected horizon."""
    period_mapping = {
        "Quarterly": ["Q1", "Q2", "Q3", "Q4"],
        "Half-yearly": ["H1", "H2"],
        "Annual": ["Full year"]
    }
    return period_mapping.get(horizon, [])

def scenario_planner_app():
    """Budget Scenario Planner application with production styling and tabs"""
    apply_custom_css()
    
    # Initialize session state for scenarios
    if "original_simulation" not in st.session_state:
        st.session_state.original_simulation = load_backend_data()["simulation"].copy()
    
    # Initialize scenario storage
    if "scenario_counter" not in st.session_state:
        st.session_state.scenario_counter = 0
    
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    # Header with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Budget Scenario Planner")

    # =========================
    # Configuration Section
    # =========================
    col1, col2, col3, col4, col5=  st.columns([1,1,1,1.15,1])

    with col1:
        st.markdown("<h3 class='unified-filter-title'>Year</h3>", unsafe_allow_html=True)
        year = st.number_input("Year", min_value=2020, max_value=2030, value=2025, label_visibility="collapsed")
    
    with col2:
        st.markdown("<h3 class='unified-filter-title'>Horizon</h3>", unsafe_allow_html=True)
        horizon = st.selectbox("Horizon", ["Quarterly", "Half-yearly", "Annual"], label_visibility="collapsed")
    
    with col3:
        st.markdown("<h3 class='unified-filter-title'>Period</h3>", unsafe_allow_html=True)
        # Get period options based on selected horizon
        period_options = get_period_options(horizon)
        period = st.selectbox("Period", period_options, label_visibility="collapsed")
    
    with col5:
        st.markdown("<h3 class='unified-filter-title'>Brand</h3>", unsafe_allow_html=True)
        brand = st.selectbox("Brand", ["Select Brand", "Brand A", "Brand B", "Brand C"], label_visibility="collapsed")
    
    with col4:
        st.markdown("<h3 class='unified-filter-title'>Segment</h3>", unsafe_allow_html=True)
        product_segment = st.selectbox("Product Segment", ["Select Segment","Bath", "LDS", "LLS"], label_visibility="collapsed")
    
    st.markdown("")
                
    # Check if brand is selected
    if brand == "Select Brand":
        st.markdown("""
        <div style="background-color: #d4edda; border: 2px solid #155724; border-radius: 8px; padding: 15px; border-left: 5px solid #155724;">
            <div style="color: #155724; font-size: 16px; font-weight: bold; display: flex; align-items: center; gap: 10px;">
                <span>👆</span>
                <span>Please select a valid brand from the above configuration to view results.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Check if segment is selected
    if product_segment == "Select Segment":
        st.markdown("""
        <div style="background-color: #d4edda; border: 2px solid #155724; border-radius: 8px; padding: 15px; border-left: 5px solid #155724;">
            <div style="color: #155724; font-size: 16px; font-weight: bold; display: flex; align-items: center; gap: 10px;">
                <span>👆</span>
                <span>Please select a valid segment from the above configuration to view results.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Configuration display
    config = {
        "year": year,
        "horizon": horizon,
        "period": period,
        "brand": brand,
        "segment": product_segment
    }

    st.markdown(f"""
    <div class="config-caption">
        Year: <strong>{year}</strong> | Period: <strong>{period}</strong> | Horizon: <strong>{horizon}</strong> | Segment: <strong>{product_segment}</strong> | Brand: <strong>{brand}</strong>
    </div>
    """, unsafe_allow_html=True)

    backend_data = load_backend_data()

    st.markdown("---")

    # =========================
    # TAB STRUCTURE
    # =========================
    tab_options = [
        "Planned Budget", 
        "Recommended Budget", 
        "Scenario Simulation", 
        "Scenario Comparison"
    ]

    selected_tab = option_menu(
        menu_title=None,
        options=tab_options,
        icons=["clipboard-data", "check-circle", "bullseye", "graph-up"],
        menu_icon="cast",
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#f7efe6"
            },
            "icon-selected": {
                "color": "white", 
                "font-size": "20px"
            },
            "nav-link": {
                "font-size": "18px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#e0dacb",
                "color": "black"
            },
            "nav-link-selected": {
                "background-color": "#042b0b",
                "color": "white",
                "font-weight": "bold"
            }
        },
    )

    # =========================
    # TAB 1: PLANNED BUDGET
    # =========================
    if selected_tab == "Planned Budget":
        st.header("Planned Budget View")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Total Spends</div>
                <div class="metric-value">$1,700,000</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Expected ROI</div>
                <div class="metric-value">1.5x</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Expected IUs</div>
                <div class="metric-value">40,000</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 📊 Budget Breakdown by Channel")
        display_aggrid_table(backend_data["planned"])
        
    # =========================
    # TAB 2: RECOMMENDED BUDGET
    # =========================
    elif selected_tab == "Recommended Budget":
        st.header("Recommended Budget View")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Total Spends</div>
                <div class="metric-value">$1,650,000</div>
                <div class="metric-delta">📉 - $50,000</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Expected ROI</div>
                <div class="metric-value">1.72x</div>
                <div class="metric-delta">📈 +0.22</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Expected IUs</div>
                <div class="metric-value">45,867</div>
                <div class="metric-delta">📈 +5,867</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### Optimized Budget Allocation")
        display_aggrid_table(backend_data["recommended"])

    # =========================
    # TAB 3: SCENARIO SIMULATION
    # =========================
    elif selected_tab == "Scenario Simulation":
        st.header("Scenario Simulation")
        
        # Initialize session state for editable data
        if "edited_simulation" not in st.session_state:
            st.session_state["edited_simulation"] = backend_data["simulation"].copy()

        st.markdown("#### 📈 Expected Impact Analysis")
        
        impact_col1, impact_col2, impact_col3 = st.columns(3)
        
        with impact_col1:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Total Spends</div>
                <div class="metric-value">$1,650,000</div>
                <div class="metric-delta">📉 - $50,000</div>
            </div>
            """, unsafe_allow_html=True)
        
        with impact_col2:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Expected ROI</div>
                <div class="metric-value">1.18x</div>
                <div class="metric-delta">📈 +0.05</div>
            </div>
            """, unsafe_allow_html=True)
        
        with impact_col3:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Expected Uplift</div>
                <div class="metric-value">6.87%</div>
                <div class="metric-delta">📈 +0.87%</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        
        # Add custom CSS to remove padding after the table
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(> .ag-theme-streamlit-custom) {
            padding-bottom: 0px !important;
            margin-bottom: 0px !important;
        }
        
        /* Remove padding from the AgGrid container specifically */
        .ag-theme-streamlit-custom {
            margin-bottom: 0px !important;
        }
        
        /* Remove any extra space after the grid */
        div[data-testid="stVerticalBlock"]:has(> .ag-theme-streamlit-custom) {
            padding-bottom: 0px !important;
            margin-bottom: 0px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("#### 📝 Interactive Budget Editor")
        
        st.markdown("""
            <div style="background-color: #d1ecf1; border: 2px solid #0c5460; border-radius: 8px; padding: 15px; border-left: 5px solid #0c5460; margin-bottom: 20px;">
                <div style="color: #0c5460; font-size: 15px; font-weight: 600;">
                    You may directly edit the Desired Budget and CPM columns by double-clicking on the cell! Changes are saved automatically in memory until logout.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- Editable AgGrid table ---
        edited_df = display_aggrid_table_edit(
            st.session_state["edited_simulation"].reset_index(drop=True))
        
        # Update session state with edited data
        st.session_state["edited_simulation"] = edited_df.copy()
        
        # Button for ROI calculation and scenario saving
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Update ROI", use_container_width=True):
                # Calculate ROI logic here
                total_desired_budget = edited_df["Desired Budget"].sum()
                st.success(f"✅ ROI Updated! Total Budget: **${total_desired_budget:,.0f}**")
        
        with col2:
            if st.button("Save Scenario", use_container_width=True):
                st.session_state.scenario_counter += 1
                scenario_name = f"comp_df{st.session_state.scenario_counter}"
                st.session_state.saved_scenarios[scenario_name] = edited_df.copy()
                st.success(f"✅ Scenario saved as **{scenario_name}**!")
        
        # Display saved scenarios
        if st.session_state.saved_scenarios:
            st.markdown("---")
            st.markdown("#### 💾 Saved Scenarios")
            for scenario_name, scenario_data in st.session_state.saved_scenarios.items():
                with st.expander(f"📁 {scenario_name} - Total Budget: ${scenario_data['Desired Budget'].sum():,}"):
                    st.dataframe(scenario_data, use_container_width=True)
            
    # =========================
    # TAB 4: SCENARIO COMPARISON
    # =========================
    elif selected_tab == "Scenario Comparison":
        st.header("📊 Scenario Comparison")
        
        if not st.session_state.saved_scenarios:
            st.info("No scenarios saved yet. Go to 'Scenario Simulation' tab to create and save scenarios.")
            return
        
        st.markdown("#### 🔍 Select Scenarios to Compare")
        
        # Scenario selection
        available_scenarios = list(st.session_state.saved_scenarios.keys())
        selected_scenarios = st.multiselect(
            "Choose scenarios to compare:",
            options=available_scenarios,
            default=available_scenarios[:min(2, len(available_scenarios))]  # Default to first 2 scenarios
        )
        
        if not selected_scenarios:
            st.warning("Please select at least one scenario to compare.")
            return
        
        st.markdown("---")
        st.markdown("#### 📋 Scenario Comparison")
        
        # Create comparison data
        comparison_data = []
        
        # Add original data
        original_df = st.session_state.original_simulation
        original_total = original_df["Desired Budget"].sum()
        comparison_data.append({
            "Scenario": "Original",
            "Total Budget": f"${original_total:,}",
            "Channel Count": len(original_df),
            "Status": "Baseline"
        })
        
        # Add selected scenarios
        for scenario_name in selected_scenarios:
            scenario_df = st.session_state.saved_scenarios[scenario_name]
            scenario_total = scenario_df["Desired Budget"].sum()
            budget_change = scenario_total - original_total
            change_percent = (budget_change / original_total) * 100 if original_total > 0 else 0
            
            comparison_data.append({
                "Scenario": scenario_name,
                "Total Budget": f"${scenario_total:,}",
                "Budget Change": f"{budget_change:+,} ({change_percent:+.1f}%)",
                "Channel Count": len(scenario_df),
                "Status": "Custom"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df.set_index("Scenario"), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📊 Detailed Budget Comparison by Channel")
        
        # Create detailed comparison table
        detailed_comparison = original_df[["Channel", "Desired Budget"]].copy()
        detailed_comparison = detailed_comparison.rename(columns={"Desired Budget": "Original Budget"})
        
        for scenario_name in selected_scenarios:
            scenario_df = st.session_state.saved_scenarios[scenario_name]
            scenario_budgets = scenario_df[["Channel", "Desired Budget"]].rename(
                columns={"Desired Budget": f"{scenario_name} Budget"}
            )
            detailed_comparison = detailed_comparison.merge(
                scenario_budgets, on="Channel", how="left"
            )
        
        # Calculate differences
        for scenario_name in selected_scenarios:
            detailed_comparison[f"{scenario_name} vs Original"] = (
                detailed_comparison[f"{scenario_name} Budget"] - detailed_comparison["Original Budget"]
            )
        
        st.dataframe(detailed_comparison.set_index("Channel"), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🎯 Key Insights")
        
        # Generate insights
        if selected_scenarios:
            latest_scenario = selected_scenarios[-1]
            latest_df = st.session_state.saved_scenarios[latest_scenario]
            
            # Calculate changes
            total_change = latest_df["Desired Budget"].sum() - original_total
            avg_change = (latest_df["Desired Budget"] - original_df["Desired Budget"]).mean()
            max_increase_channel = detailed_comparison.loc[
                detailed_comparison[f"{latest_scenario} vs Original"].idxmax(), "Channel"
            ]
            max_decrease_channel = detailed_comparison.loc[
                detailed_comparison[f"{latest_scenario} vs Original"].idxmin(), "Channel"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Budget Allocation Changes:**")
                st.write(f"""
                - **Total Budget Change:** ${total_change:+,}
                - **Average Channel Change:** ${avg_change:+,.0f}
                - **Max Increase:** {max_increase_channel}
                - **Max Decrease:** {max_decrease_channel}
                """)
            
            with col2:
                st.markdown("**Recommendations:**")
                if total_change > 0:
                    st.write("""
                    ✅ Overall budget increase detected
                    📈 Consider reallocating from lower-performing channels
                    🔍 Review CPM efficiency for increased budgets
                    """)
                else:
                    st.write("""
                    ✅ Overall budget reduction achieved
                    📊 Focus on maintaining ROI with reduced spend
                    🎯 Optimize channel mix for efficiency
                    """)

def display_aggrid_table_edit(dataframe, fit_columns=True):
    """
    Streamlit AgGrid table styled with theme-matched green headers, beige rows,
    centered text, rounded corners, and Streamlit aesthetic consistency.
    Allows selective column editability (Desired Budget, Expected CPM Range).
    """
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    
    # --- Cell style ---
    cell_style = JsCode("""
    function(params) {
        return {
            'textAlign': 'center',
            'fontSize': '16px',
            'color': '#042b0b',
            'backgroundColor': (params.node.rowIndex % 2 === 0) ? '#f5f1e9' : '#efe6d4',
            'borderRight': '1px solid #c9dbc9',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '8px',
        };
    }
    """)

    # --- Header style ---
    header_style = JsCode("""
    function(params) {
        return {
            'textAlign': 'center',
            'color': 'white',
            'fontWeight': '700',
            'fontSize': '16px',
            'backgroundColor': '#154c29',
            'borderRight': '1px solid #c9dbc9',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
        };
    }
    """)

    # --- Editable column rules ---
    editable_columns = ["Desired Budget", "Exp. CPM Range"]

    # --- Configure columns ---
    for col in dataframe.columns:
        gb.configure_column(
            col,
            editable=(col in editable_columns),
            cellEditor='agSelectCellEditor' if col == "Exp. CPM Range" else None,
            cellEditorParams={'values': ["$6.3 - $6.8", "$8.1 - $8.9", "$5.0 - $5.5", "$9.3 - $10.0", "$6.3 - $6.8"]} if col == "Exp. CPM Range" else None,
            cellStyle=cell_style,
            headerStyle=header_style,
            headerClass="streamlit-custom",
            minWidth=120,
            suppressSizeToFit=False,
            wrapHeaderText=True
        )

    # --- JS Auto-resize Fix ---
    grid_size_handler = JsCode("""
        function(params) {
            params.api.sizeColumnsToFit();
        }
    """)

    gb.configure_grid_options(
        onGridSizeChanged=grid_size_handler,
        headerHeight=50,
        rowHeight=48,
        domLayout='autoHeight',
        suppressHorizontalScroll=False,
        suppressMovableColumns=True,
        suppressColumnVirtualisation=True,
        suppressSizeToFit=False,
    )

    gridOptions = gb.build()

    # --- Custom CSS for outer AgGrid wrapper ---
    st.markdown("""
    <style>
    .ag-header-cell-label {
        justify-content: center;
    }
    .ag-theme-streamlit-custom {
        border: 2px solid #154c29 !important;
        border-radius: 12px !important;
        background-color: #f5f1e9 !important;
        overflow: hidden !important;
        box-shadow: 0 4px 10px rgba(21,76,41,0.15) !important;
    }

    .ag-theme-streamlit-custom .ag-root-wrapper {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    .ag-theme-streamlit-custom .ag-header {
        background-color: #154c29 !important;
    }

    .ag-theme-streamlit-custom .ag-header-cell-label {
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        justify-content: center !important;
    }

    .ag-theme-streamlit-custom .ag-row-hover {
        background-color: #e8f5e9 !important;
    }

    .ag-theme-streamlit-custom .ag-cell {
        border-right: 1px solid #c9dbc9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Render AgGrid ---
    response = AgGrid(
        dataframe,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        theme='streamlit-custom',
        key="scenario_simulation_grid",        
    )

    return response["data"]

# Run the app
if __name__ == "__main__":
    scenario_planner_app()