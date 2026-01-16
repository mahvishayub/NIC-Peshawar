# =====================================================
# NIC PESHAWAR ANALYTICS DASHBOARD (GA / POWER BI STYLE)
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="NIC Peshawar Dashboard - Phase 1",
    layout="wide"
)

# =====================================================
# GLOBAL STYLE
# =====================================================

st.markdown("""
<style>
/* =========================
   GLOBAL BACKGROUND
   ========================= */
.stApp {
    background-color: #f8fafc;
}

/* =========================
   KPI CARDS
   ========================= */
.kpi-card {
    padding: 18px 16px;
    border-radius: 16px;
    color: white;
    text-align: center;
    min-height: 100px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    box-shadow: 0 8px 16px rgba(0,0,0,0.08);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 22px rgba(0,0,0,0.12);
}

.kpi-title {
    font-size: 13px;
    opacity: 0.85;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.3;
}

/* =========================
   SECTION TITLES
   ========================= */
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 36px;
    margin-bottom: 14px;
    color: #1f2937;

    border-left: 5px solid #2563eb;
    padding-left: 12px;
}

/* =========================
   KPI COLOR GRADIENTS
   ========================= */
.kpi-blue {
    background: linear-gradient(135deg, #2563eb, #1e40af);
}

.kpi-green {
    background: linear-gradient(135deg, #16a34a, #15803d);
}

.kpi-purple {
    background: linear-gradient(135deg, #7c3aed, #5b21b6);
}

.kpi-amber {
    background: linear-gradient(135deg, #f59e0b, #d97706);
}

/* =========================
   STREAMLIT TABS STYLING
   ========================= */
div[data-baseweb="tab-list"] {
    gap: 18px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 18px;
}

div[data-baseweb="tab-list"] button {
    font-size: 15px;
    font-weight: 600;
    color: #6b7280;
    padding: 10px 6px;
    background: none;
}

div[data-baseweb="tab-list"] button:hover {
    color: #2563eb;
}

div[data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
}

/* =========================
   SMALL RESPONSIVE TWEAK
   ========================= */
@media (max-width: 768px) {
    .kpi-value {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)



# =====================================================
# HELPERS
# =====================================================
def clean_cols(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
    )
    return df

def to_numeric_safe(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = (
                df[c]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

def format_pkr(v):
    if v >= 1_000_000_000:
        return f"₨ {v/1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"₨ {v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"₨ {v/1_000:.1f}K"
    return f"₨ {int(v)}"

def format_num(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return str(int(v))

# =====================================================
# LOAD DATA
# =====================================================
DATA_PATH = "../raw_data/NIC Peshawar Phase 1.xlsx"

main_df = pd.read_excel(DATA_PATH, sheet_name="Main")
startup_df = pd.read_excel(DATA_PATH, sheet_name="Startupwise")

main_df = clean_cols(main_df)
startup_df = clean_cols(startup_df)

main_df["Cohort"] = main_df["Cohort"].astype(str)
startup_df["Cohort"] = startup_df["Cohort"].astype(str)

# numeric cleaning (CRITICAL FIX)
main_df = to_numeric_safe(
    main_df,
    [
        "ApplicationReceived",
        "InterviewsConducted",
        "StartupsIncubated",
        "StartupsGraduated",
        "TotalJobs",
        "Revenue",
        "Investment",
        "FemaleFounders",
        "Idea/MVPStage",
        "GrowthStage",
        "Acceleration /ScaleStage"
    ]
)

startup_df = to_numeric_safe(
    startup_df,
    ["DirectJobs", "IndirectJobs", "TotalJobs", "Revenue", "Investment (In USD)"]
)

# =====================================================
# SIDEBAR FILTER
# =====================================================
st.sidebar.title("Filters")

cohorts = sorted(main_df["Cohort"].unique())
selected_cohorts = st.sidebar.multiselect(
    "Select Cohort(s)",
    cohorts,
    default=cohorts
)

main_f = main_df[main_df["Cohort"].isin(selected_cohorts)]

# =====================================================
# HEADER
# =====================================================
st.title("📊 NIC Peshawar")
st.caption("Cohort-wise overview • Startup analytics • ML insights")

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "📘 Startupwise Analytics",
    "🤖 ML Insights"
])


# =====================================================
# TAB 1 — OVERVIEW (MAIN SHEET ONLY)
# =====================================================
with tab1:
    # -------------------------------------------------
    # PROGRAM SNAPSHOT
    # -------------------------------------------------
    st.markdown("<div class='section-title'>Program Snapshot</div>", unsafe_allow_html=True)

    apps = main_f["ApplicationReceived"].sum()
    interviews = main_f["InterviewsConducted"].sum()
    incubated = main_f["StartupsIncubated"].sum()
    graduated = main_f["StartupsGraduated"].sum()
    jobs = main_f["TotalJobs"].sum()
    revenue = main_f["Revenue"].sum()
    investment = main_f["Investment"].sum()
    female = main_f["FemaleFounders"].sum()

    # ---- TOP KPI ROW ----
    k1, k2, k3, k4, k5 = st.columns(5)
    for col, title, val in zip(
        [k1, k2, k3, k4, k5],
        ["Applications", "Incubated", "Graduated", "Jobs Created", "Female Founders"],
        [apps, incubated, graduated, jobs, female]
    ):
        col.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-title'>{title}</div>
                <div class='kpi-value'>{format_num(val)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # spacing between KPI rows
    st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

    # ---- REVENUE / INVESTMENT KPI ROW ----
    k6, k7 = st.columns(2)
    k6.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Total Revenue</div>
            <div class='kpi-value'>{format_pkr(revenue)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    k7.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Total Investment</div>
            <div class='kpi-value'>{format_pkr(investment)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # APPLICATION CONVERSION FLOW
    # -------------------------------------------------
    st.markdown("<div class='section-title'>Application Conversion Flow</div>", unsafe_allow_html=True)

    progress_df = pd.DataFrame({
        "Stage": ["Applications", "Interviews", "Incubated", "Graduated"],
        "Count": [apps, interviews, incubated, graduated]
    })

    fig_progress = px.bar(
        progress_df,
        x="Count",
        y="Stage",
        orientation="h",
        text="Count",
        color="Stage",
        color_discrete_sequence=["#2563eb", "#1e40af", "#1d4ed8", "#3b82f6"]
    )
    fig_progress.update_layout(
        height=320,
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#e5e7eb"),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_progress, use_container_width=True)

    # -------------------------------------------------
    # COHORT COMPARISON (SUMMARY)
    # -------------------------------------------------
    st.markdown("<div class='section-title'>Cohort Comparison</div>", unsafe_allow_html=True)

    compare_df = main_f[
        ["Cohort", "ApplicationReceived", "StartupsIncubated", "StartupsGraduated"]
    ].melt(
        id_vars="Cohort",
        var_name="Metric",
        value_name="Count"
    )

    fig_compare = px.bar(
        compare_df,
        x="Cohort",
        y="Count",
        color="Metric",
        barmode="group",
        height=380,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_compare.update_layout(
        plot_bgcolor="white",
        legend_title_text="",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # -------------------------------------------------
    # COHORT COMPARISON – DEEP DIVE
    # -------------------------------------------------
    st.markdown("<div class='section-title'>Cohort Comparison – Deep Dive</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    all_cohorts = sorted(main_df["Cohort"].unique())

    primary_cohort = c1.selectbox(
        "Primary Cohort",
        all_cohorts,
        index=len(all_cohorts) - 1
    )

    compare_cohort = c2.selectbox(
        "Compare With",
        all_cohorts,
        index=max(len(all_cohorts) - 2, 0)
    )

    primary_df = main_df[main_df["Cohort"] == primary_cohort]
    compare_df = main_df[main_df["Cohort"] == compare_cohort]

    comparison_df = pd.DataFrame({
        "Metric": [
            "Applications",
            "Incubated",
            "Graduated",
            "Jobs Created",
            "Revenue (PKR)",
            "Investment (PKR)"
        ],
        primary_cohort: [
            primary_df["ApplicationReceived"].sum(),
            primary_df["StartupsIncubated"].sum(),
            primary_df["StartupsGraduated"].sum(),
            primary_df["TotalJobs"].sum(),
            primary_df["Revenue"].sum(),
            primary_df["Investment"].sum()
        ],
        compare_cohort: [
            compare_df["ApplicationReceived"].sum(),
            compare_df["StartupsIncubated"].sum(),
            compare_df["StartupsGraduated"].sum(),
            compare_df["TotalJobs"].sum(),
            compare_df["Revenue"].sum(),
            compare_df["Investment"].sum()
        ]
    })

    fig_deep = px.bar(
        comparison_df.melt(
            id_vars="Metric",
            var_name="Cohort",
            value_name="Value"
        ),
        x="Metric",
        y="Value",
        color="Cohort",
        barmode="group",
        height=420,
        color_discrete_sequence=["#2563eb", "#f59e0b"]
    )
    fig_deep.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    st.plotly_chart(fig_deep, use_container_width=True)

    # % CHANGE TABLE
    comparison_df["Change (%)"] = (
        (comparison_df[primary_cohort] - comparison_df[compare_cohort])
        / comparison_df[compare_cohort].replace(0, 1)
    ) * 100

    delta_df = comparison_df[["Metric", "Change (%)"]].copy()
    delta_df["Change (%)"] = delta_df["Change (%)"].round(1)

    st.markdown("**📈 Change vs Comparison Cohort**")
    st.dataframe(delta_df, use_container_width=True)

    # -------------------------------------------------
# AUTO-GENERATED INSIGHTS
# -------------------------------------------------
st.markdown("### 📌 Key Insights")

insights = []

for _, row in delta_df.iterrows():
    metric = row["Metric"]
    change = row["Change (%)"]

    if abs(change) < 3:
        continue  # ignore very small changes

    direction = "increased" if change > 0 else "decreased"
    insights.append(
        f"• **{metric}** {direction} by **{abs(change):.1f}%** compared to the selected cohort."
    )

if insights:
    for insight in insights:
        st.markdown(insight)
else:
    st.markdown("• Performance remained largely stable across key indicators.")


    # -------------------------------------------------
    # STARTUP STAGE DISTRIBUTION
    # -------------------------------------------------
    st.markdown("<div class='section-title'>Startup Stage Distribution</div>", unsafe_allow_html=True)

    stage_df = main_f[
        ["Idea/MVPStage", "GrowthStage", "Acceleration /ScaleStage"]
    ].sum().reset_index()

    stage_df.columns = ["Stage", "Count"]

    fig_stage = px.bar(
        stage_df,
        x="Stage",
        y="Count",
        color="Stage",
        height=350,
        color_discrete_sequence=["#2563eb", "#16a34a", "#f59e0b"]
    )
    fig_stage.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    st.plotly_chart(fig_stage, use_container_width=True)


# =====================================================
# TAB 2 — STARTUPWISE ANALYTICS
# =====================================================
with tab2:
    st.markdown("<div class='section-title'>Startupwise Analytics</div>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)

    cohort_f = f1.multiselect("Cohort", startup_df["Cohort"].unique())
    vertical_f = f2.multiselect("Vertical", startup_df["Vertical"].dropna().unique())
    tech_f = f3.multiselect("Technology", startup_df["Technology"].dropna().unique())
    gender_f = f4.multiselect("Gender", startup_df["Gender"].dropna().unique())

    df_s = startup_df.copy()
    if cohort_f: df_s = df_s[df_s["Cohort"].isin(cohort_f)]
    if vertical_f: df_s = df_s[df_s["Vertical"].isin(vertical_f)]
    if tech_f: df_s = df_s[df_s["Technology"].isin(tech_f)]
    if gender_f: df_s = df_s[df_s["Gender"].isin(gender_f)]

    fig_jobs = px.bar(
        df_s,
        x="Startup",
        y="TotalJobs",
        color="Vertical",
        height=400
    )
    st.plotly_chart(fig_jobs, use_container_width=True)

    st.dataframe(
        df_s[
            ["Startup", "Cohort", "Vertical", "Technology",
             "Graduation", "TotalJobs", "Revenue", "Investment (In USD)"]
        ],
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Startupwise Data (CSV)",
        df_s.to_csv(index=False),
        "startupwise_filtered.csv",
        "text/csv"
    )

# =====================================================
# TAB 3 — ML INSIGHTS
# =====================================================
with tab3:
    st.markdown("<div class='section-title'>ML Insights – Graduation Probability</div>", unsafe_allow_html=True)

    pred_path = "../ml_pipeline/outputs/predictions.csv"

    if os.path.exists(pred_path):
        pred_df = pd.read_csv(pred_path)

        fig_prob = px.histogram(
            pred_df,
            x="Graduation_Probability",
            nbins=20,
            color="Risk_Band",
            color_discrete_map={
                "High": "#16a34a",
                "Medium": "#f59e0b",
                "Low": "#dc2626"
            }
        )
        fig_prob.update_layout(height=350)
        st.plotly_chart(fig_prob, use_container_width=True)

        st.dataframe(pred_df, use_container_width=True)

        st.download_button(
            "⬇️ Download ML Predictions (CSV)",
            pred_df.to_csv(index=False),
            "ml_predictions.csv",
            "text/csv"
        )
    else:
        st.warning("ML predictions not found. Please run model_training.py.")
