import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Youth Literacy Gender Parity Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a237e;
        text-align: center;
        padding: 0.5rem 0;
    }
    .sub-header {
        font-size: 0.92rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .insight-box {
        background-color: #f0f4ff;
        border-left: 4px solid #1a237e;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Data loading and preprocessing

# ─── Load & Process Data ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('WB_GS_SE_ADT_1524_LT_FM_ZS_WIDEF.csv')
    year_cols = [col for col in df.columns if str(col).strip().isdigit()]
    keep_cols = ['REF_AREA', 'REF_AREA_LABEL'] + year_cols
    df = df[keep_cols].copy()
    df.columns = ['Code', 'Country'] + year_cols
    df_long = df.melt(
        id_vars=['Code', 'Country'],
        value_vars=year_cols,
        var_name='Year',
        value_name='GPI'
    )
    df_long['Year'] = df_long['Year'].astype(int)
    df_long = df_long.dropna(subset=['GPI'])
    df_long['GPI'] = df_long['GPI'].round(4)
    return df_long

# Separate country-level data from regional aggregates

# World Bank regional aggregate codes (not individual countries)
REGION_CODES = {
    'AFE', 'AFW', 'ARB', 'CSS', 'CEB', 'EAR', 'EAS', 'ECA', 'ECS',
    'EMU', 'EUU', 'FCS', 'HIC', 'HPC', 'IBD', 'IBT', 'IDA', 'IDB',
    'IDX', 'LAC', 'LCN', 'LDC', 'LIC', 'LMC', 'LMY', 'LTE', 'MEA',
    'MIC', 'MNA', 'NAC', 'OED', 'OSS', 'PRE', 'PSS', 'PST', 'SAS',
    'SSA', 'SSF', 'SST', 'TEA', 'TEC', 'TLA', 'TMN', 'TSA', 'TSS',
    'UMC', 'WLD'
}

MAIN_REGIONS = {
    'AFE': 'Africa (East & South)',
    'AFW': 'Africa (West & Central)',
    'ARB': 'Arab World',
    'EAS': 'East Asia & Pacific',
    'ECS': 'Europe & Central Asia',
    'LAC': 'Latin America & Caribbean',
    'MEA': 'Middle East & N. Africa',
    'NAC': 'North America',
    'SAS': 'South Asia',
    'SSF': 'Sub-Saharan Africa',
    'WLD': 'World'
}

df_all = load_data()
df_countries = df_all[~df_all['Code'].isin(REGION_CODES)].copy()
df_regions   = df_all[df_all['Code'].isin(MAIN_REGIONS.keys())].copy()
df_regions['Region'] = df_regions['Code'].map(MAIN_REGIONS)

# Sidebar controls

# ─── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔧 Dashboard Controls")
    st.markdown("---")

    available_years = sorted(df_countries['Year'].unique())

    selected_year = st.slider(
        "📅 Select Year",
        min_value=int(min(available_years)),
        max_value=int(max(available_years)),
        value=2020,
        step=1,
        help="Used for the World Map and Rankings tabs"
    )

    st.markdown("---")

    all_countries = sorted(df_countries['Country'].unique())
    default_list  = ['India', 'Pakistan', 'Nigeria', 'Brazil', 'China', 'Afghanistan']
    default_list  = [c for c in default_list if c in all_countries]

    selected_countries = st.multiselect(
        "🌍 Countries for Trend Analysis",
        options=all_countries,
        default=default_list[:5],
        help="Choose countries to compare in the Trend Analysis tab"
    )

    st.markdown("---")
    st.info(
        "**ℹ️ About GPI**\n\n"
        "- GPI **= 1.0** → Perfect parity\n"
        "- GPI **< 1.0** → Male advantage\n"
        "- GPI **> 1.0** → Female advantage\n\n"
        "*Source: World Bank / UNESCO*"
    )

# ─── Header ─────────────────────────────────────────────────────
st.markdown(
    '<div class="main-header">📚 Youth Literacy Gender Parity Dashboard</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">'
    'Gender Parity Index for Youth Literacy (Ages 15–24) | '
    '217 Economies | 1970–2022 | World Bank Gender Statistics'
    '</div>',
    unsafe_allow_html=True
)

# ─── KPI Metrics ────────────────────────────────────────────────
year_data      = df_countries[df_countries['Year'] == selected_year].copy()
prev_year      = max(selected_year - 5, int(min(available_years)))
year_data_prev = df_countries[df_countries['Year'] == prev_year].copy()

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg     = year_data['GPI'].mean()
    avg_old = year_data_prev['GPI'].mean()
    st.metric("🌐 Global Avg GPI", f"{avg:.3f}", f"{avg - avg_old:+.3f} vs {prev_year}")
with col2:
    below = int((year_data['GPI'] < 0.97).sum())
    st.metric("⚠️ Countries Below Parity", below, help="GPI < 0.97 (male literacy significantly higher)")
with col3:
    above = int((year_data['GPI'] > 1.03).sum())
    st.metric("✅ Countries Above Parity", above, help="GPI > 1.03 (female literacy higher)")
with col4:
    count = int(year_data['Country'].nunique())
    st.metric("📊 Countries with Data", count)

st.markdown("---")

# ─── Tabs ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ World Map",
    "📈 Trend Analysis",
    "🏆 Country Rankings",
    "🌍 Regional Analysis"
])

# Tab 1 - World Map
# ════════════════════════════════════════════════════════════════
# TAB 1: WORLD MAP
# ════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"Global Youth Literacy GPI — {selected_year}")

    fig_map = px.choropleth(
        year_data,
        locations='Code',
        color='GPI',
        hover_name='Country',
        hover_data={'GPI': ':.3f', 'Code': False},
        color_continuous_scale='RdYlGn',
        range_color=[0.5, 1.3],
        color_continuous_midpoint=1.0,
        labels={'GPI': 'GPI'}
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
        coloraxis_colorbar=dict(
            title="GPI",
            tickvals=[0.5, 0.7, 0.85, 1.0, 1.15, 1.3],
            ticktext=["0.5\n(Male adv.)", "0.7", "0.85", "1.0\n(Parity)", "1.15", "1.3\n(Female adv.)"]
        ),
        height=520,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("🟢 Green = Female literacy higher  |  🟡 Yellow = Near parity  |  🔴 Red = Male literacy higher")

    if not year_data.empty:
        lowest  = year_data.nsmallest(1, 'GPI').iloc[0]
        highest = year_data.nlargest(1, 'GPI').iloc[0]
        ca, cb  = st.columns(2)
        with ca:
            st.markdown(
                f'<div class="insight-box">🔴 <strong>Lowest GPI ({selected_year}):</strong> '
                f'{lowest["Country"]} — GPI = {lowest["GPI"]:.3f}. '
                f'Males significantly outnumber females in youth literacy.</div>',
                unsafe_allow_html=True
            )
        with cb:
            st.markdown(
                f'<div class="insight-box">🟢 <strong>Highest GPI ({selected_year}):</strong> '
                f'{highest["Country"]} — GPI = {highest["GPI"]:.3f}. '
                f'Females lead in youth literacy rates.</div>',
                unsafe_allow_html=True
            )

# Tab 2 - Trend Analysis

# ════════════════════════════════════════════════════════════════
# TAB 2: TREND ANALYSIS
# ════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("GPI Trend Over Time — Country Comparison")

    if not selected_countries:
        st.warning("Please select at least one country in the sidebar to view trends.")
    else:
        df_trend = df_countries[df_countries['Country'].isin(selected_countries)]

        fig_line = px.line(
            df_trend,
            x='Year',
            y='GPI',
            color='Country',
            markers=True,
            title="Youth Literacy GPI Over Time (1970–2022)",
            labels={'GPI': 'Gender Parity Index', 'Year': 'Year'}
        )
        fig_line.add_hline(
            y=1.0,
            line_dash="dash",
            line_color="black",
            annotation_text="Parity Line (GPI = 1.0)",
            annotation_position="top right"
        )
        fig_line.update_traces(marker=dict(size=5))
        fig_line.update_layout(
            height=460,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("**Summary Statistics**")
        summary = df_trend.groupby('Country')['GPI'].agg(
            Min='min', Max='max', Average='mean', Years_of_Data='count'
        ).round(3)
        st.dataframe(summary, use_container_width=True)

        with st.expander("📋 View Full Raw Data Table"):
            pivot = df_trend.pivot_table(index='Country', columns='Year', values='GPI').round(3)
            st.dataframe(pivot, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 3: COUNTRY RANKINGS
# ════════════════════════════════════════════════════════════════
with tab3:
    st.subheader(f"Country Rankings by GPI — {selected_year}")

    ctrl1, ctrl2 = st.columns([1, 2])
    with ctrl1:
        n_rank = st.slider("Number of countries", 5, 30, 15, key='rank_n')
    with ctrl2:
        rank_type = st.radio(
            "Show ranking",
            ["⬇️ Bottom — Lowest GPI (Male Advantage)", "⬆️ Top — Highest GPI (Female Advantage)"],
            horizontal=True
        )

    if "Bottom" in rank_type:
        ranked    = year_data.nsmallest(n_rank, 'GPI').sort_values('GPI', ascending=True)
        cscale    = 'Reds_r'
        bar_title = f"Bottom {n_rank} Countries by GPI ({selected_year}) — Lowest Gender Parity"
    else:
        ranked    = year_data.nlargest(n_rank, 'GPI').sort_values('GPI', ascending=True)
        cscale    = 'Greens'
        bar_title = f"Top {n_rank} Countries by GPI ({selected_year}) — Females Lead in Literacy"

    fig_bar = px.bar(
        ranked,
        x='GPI',
        y='Country',
        orientation='h',
        color='GPI',
        color_continuous_scale=cscale,
        title=bar_title,
        text='GPI',
        labels={'GPI': 'Gender Parity Index'}
    )
    fig_bar.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig_bar.add_vline(x=1.0, line_dash="dash", line_color="black", annotation_text="Parity (1.0)")
    fig_bar.update_layout(
        height=max(400, n_rank * 28),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 4: REGIONAL ANALYSIS
# ════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Regional GPI Analysis")

    all_region_names = sorted(df_regions['Region'].dropna().unique())
    default_regions  = ['Africa (East & South)', 'Arab World', 'South Asia',
                        'East Asia & Pacific', 'World']
    default_regions  = [r for r in default_regions if r in all_region_names]

    sel_regions = st.multiselect(
        "Select Regions to Compare",
        options=all_region_names,
        default=default_regions
    )

    df_reg_plot = df_regions[df_regions['Region'].isin(sel_regions)]

    col_r1, col_r2 = st.columns([3, 2])

    with col_r1:
        fig_reg = px.line(
            df_reg_plot,
            x='Year',
            y='GPI',
            color='Region',
            title="Regional Youth Literacy GPI Over Time",
            labels={'GPI': 'Gender Parity Index'}
        )
        fig_reg.add_hline(
            y=1.0, line_dash="dash", line_color="black",
            annotation_text="Parity (1.0)", annotation_position="top right"
        )
        fig_reg.update_layout(height=420, hovermode='x unified')
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_r2:
        reg_yr = df_regions[
            (df_regions['Year'] == selected_year) &
            (df_regions['Region'].isin(sel_regions))
        ].sort_values('GPI')

        fig_reg_bar = px.bar(
            reg_yr,
            x='GPI',
            y='Region',
            orientation='h',
            color='GPI',
            color_continuous_scale='RdYlGn',
            range_color=[0.7, 1.1],
            title=f"Regional GPI Snapshot — {selected_year}",
            text='GPI'
        )
        fig_reg_bar.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_reg_bar.add_vline(x=1.0, line_dash="dash", line_color="black")
        fig_reg_bar.update_layout(height=420, coloraxis_showscale=False)
        st.plotly_chart(fig_reg_bar, use_container_width=True)

# ─── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "📊 Data: World Bank Gender Statistics | UNESCO Institute for Statistics | "
    "Dashboard: Vishud Perera (w2055134) | 5DATA004C — University of Westminster"
)