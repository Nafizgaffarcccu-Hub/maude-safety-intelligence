
import streamlit as st
from pymongo import MongoClient
import certifi
import os
import pandas as pd
import re
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="MAUDE Medical Device Safety Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# GLOBAL DESIGN SYSTEM
# --------------------------------------------------
st.markdown(
    """
    <style>

    /* ---------------------------------------------
       Main application
       --------------------------------------------- */

    .stApp {
        background-color: #F7F9FC;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* ---------------------------------------------
       Typography
       --------------------------------------------- */

    h1 {
        color: #102A43;
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    h2 {
        color: #173B5E;
        font-weight: 650;
        letter-spacing: -0.015em;
        margin-top: 1.5rem;
    }

    h3 {
        color: #244E73;
        font-weight: 620;
    }

    p {
        line-height: 1.65;
    }

    /* ---------------------------------------------
       Sidebar
       --------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #EEF3F8;
        border-right: 1px solid #DCE5EE;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.4rem;
    }

    section[data-testid="stSidebar"] h1 {
        color: #102A43;
        font-size: 1.55rem;
        line-height: 1.25;
    }

    section[data-testid="stSidebar"] label {
        font-size: 0.95rem;
    }

    /* ---------------------------------------------
       Metric cards
       --------------------------------------------- */

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #DDE6EF;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow:
            0 1px 2px rgba(16, 42, 67, 0.04),
            0 4px 14px rgba(16, 42, 67, 0.035);
        min-height: 108px;
    }

    div[data-testid="stMetricLabel"] {
        color: #526D82;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #102A43;
        font-weight: 700;
    }

    /* ---------------------------------------------
       Inputs
       --------------------------------------------- */

    div[data-baseweb="input"] > div {
        background-color: #FFFFFF;
        border-radius: 9px;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF;
        border-radius: 9px;
    }

    .stTextInput input {
        border-radius: 9px;
    }

    /* ---------------------------------------------
       Buttons
       --------------------------------------------- */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 2.65rem;
        padding-left: 1.15rem;
        padding-right: 1.15rem;
    }

    .stButton > button[kind="primary"] {
        background-color: #176B87;
        border-color: #176B87;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #125A73;
        border-color: #125A73;
    }

    /* ---------------------------------------------
       Data tables
       --------------------------------------------- */

    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #DDE6EF;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---------------------------------------------
       Alerts
       --------------------------------------------- */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ---------------------------------------------
       Horizontal rules
       --------------------------------------------- */

    hr {
        border-color: #DCE5EE;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* ---------------------------------------------
       Captions
       --------------------------------------------- */

    .stCaption {
        color: #6B7F90;
    }

    /* ---------------------------------------------
       Plot containers
       --------------------------------------------- */

    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E1E8F0;
        border-radius: 12px;
        padding: 0.35rem;
    }

    /* ---------------------------------------------
       Expander
       --------------------------------------------- */

    details {
        background-color: #FFFFFF;
        border: 1px solid #DDE6EF;
        border-radius: 9px;
    }

    /* ---------------------------------------------
       Text areas / evidence panels
       --------------------------------------------- */

    textarea {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        line-height: 1.55 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
@st.cache_resource
def get_database():
    mongo_uri = st.secrets.get("MONGO_URI", os.environ.get("MONGO_URI"))
    if not mongo_uri:
        return None

    client = MongoClient(
        mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=15000
    )

    client.admin.command("ping")
    return client["maude_safety_intelligence"]

db = get_database()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown(
    """
    <div style="
        margin-bottom: 1.2rem;
    ">
        <div style="
            font-size: 1.45rem;
            font-weight: 750;
            color: #102A43;
            line-height: 1.2;
        ">
            MAUDE Safety
            <br>
            Intelligence
        </div>
        <div style="
            margin-top: 0.45rem;
            font-size: 0.78rem;
            color: #6B7F90;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        ">
            Research Prototype
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Device Search",
        "Safety Patterns",
        "Trend Analysis",
        "Report Explorer",
        "Unusual Reports",
        "About"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "FDA MAUDE • 2025 data"
)

st.sidebar.caption(
    "Human-centred medical-device adverse-event intelligence"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Medical Device Safety Intelligence")

st.caption(
    "Human-centred exploration of FDA MAUDE medical-device adverse-event reports."
)

st.caption(
    "Research-use notice • Historical adverse-event reports are "
    "organized to support investigation and human review; analytical "
    "patterns do not establish causation."
)

# --------------------------------------------------
# DATABASE STATUS
# --------------------------------------------------
if db is None:
    st.error(
        "Database connection is not configured. "
        "Set the MONGO_URI environment variable before starting the dashboard."
    )
    st.stop()

collection = db["reports"]

try:
    collection.database.client.admin.command("ping")
except Exception:
    st.error(
        "Unable to connect to the MAUDE Safety Intelligence database."
    )
    st.stop()

# --------------------------------------------------
# PAGE PLACEHOLDERS
# --------------------------------------------------
if page == "Overview":

    st.caption("FDA MAUDE • 2025")

    st.header("Safety Intelligence Overview")

    st.caption(
        "Reporting activity, recurring narrative patterns, "
        "and analyst review priorities across the research dataset."
    )

    # Live KPI calculations from MongoDB
    total_reports = collection.count_documents({})

    recurring_reports = collection.count_documents({
        "safety_intelligence.pattern_status": "Recurring pattern identified"
    })

    unclassified_reports = collection.count_documents({
        "safety_intelligence.unusual_flag": True
    })

    # Review Recommended =
    # unclassified reports OR weakly aligned recurring reports
    review_recommended = collection.count_documents({
        "$or": [
            {"safety_intelligence.unusual_flag": True},
            {
                "safety_intelligence.theme_alignment_status":
                "Weakly aligned / review recommended"
            }
        ]
    })

    # Unique Device Profiles =
    # distinct brand + generic name + manufacturer + model + product code
    unique_profiles_pipeline = [
        {
            "$group": {
                "_id": {
                    "brand_name": "$device.brand_name",
                    "generic_name": "$device.generic_name",
                    "manufacturer": "$device.manufacturer",
                    "model_number": "$device.model_number",
                    "product_code": "$device.product_code"
                }
            }
        },
        {"$count": "count"}
    ]

    unique_profiles_result = list(
        collection.aggregate(unique_profiles_pipeline)
    )

    unique_profiles = (
        unique_profiles_result[0]["count"]
        if unique_profiles_result else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Reports",
        f"{total_reports:,}"
    )

    col2.metric(
        "Unique Device Profiles",
        f"{unique_profiles:,}"
    )

    col3.metric(
        "Recurring Pattern Reports",
        f"{recurring_reports:,}"
    )

    col4.metric(
        "Unclassified Reports",
        f"{unclassified_reports:,}"
    )

    col5.metric(
        "Review Recommended",
        f"{review_recommended:,}"
    )

    st.caption(
        "Unique Device Profiles represent distinct combinations of brand, "
        "generic device name, manufacturer, model and product code. "
        "Review Recommended combines unclassified reports and reports "
        "with weak alignment to a recurring narrative pattern."
    )

    st.divider()

    st.subheader("Recurring Pattern Landscape")

    st.caption(
        "Reports are organized by how closely they align with recurring "
        "adverse-event patterns. Categories support prioritization for "
        "human review and do not indicate clinical severity or causation."
    )

    alignment_pipeline = [
        {
            "$group": {
                "_id": "$safety_intelligence.theme_alignment_status",
                "Reports": {"$sum": 1}
            }
        }
    ]

    alignment_raw = list(collection.aggregate(alignment_pipeline))

    alignment_counts = {
        item["_id"]: item["Reports"]
        for item in alignment_raw
        if item["_id"] is not None
    }

    display_names = {
        "Typical of recurring theme": "Typical of Recurring Theme",
        "Moderately aligned with recurring theme": "Moderately Aligned",
        "Weakly aligned / review recommended": "Weakly Aligned — Review Recommended",
        "Unclassified / requires review": "Unclassified — Requires Review"
    }

    preferred_order = [
        "Typical of recurring theme",
        "Moderately aligned with recurring theme",
        "Weakly aligned / review recommended",
        "Unclassified / requires review"
    ]

    pattern_df = pd.DataFrame([
        {
            "Pattern Status": display_names[status],
            "Reports": alignment_counts.get(status, 0)
        }
        for status in preferred_order
    ])

    fig_patterns = px.bar(
        pattern_df,
        x="Reports",
        y="Pattern Status",
        orientation="h",
        text="Reports",
        title="Distribution of Reports by Safety Pattern Alignment"
    )

    fig_patterns.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_patterns.update_layout(
        xaxis_title="Number of Reports",
        yaxis_title="",
        showlegend=False,
        height=430,
        margin=dict(l=20, r=80, t=60, b=40)
    )

    fig_patterns.update_yaxes(
        categoryorder="array",
        categoryarray=list(reversed(pattern_df["Pattern Status"].tolist()))
    )


    fig_patterns.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#334E68",
            size=13
        ),
        title_font=dict(
            color="#173B5E",
            size=18
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13
        )
    )

    fig_patterns.update_xaxes(
        showgrid=True,
        gridcolor="#E8EEF4",
        zeroline=False
    )

    fig_patterns.update_yaxes(
        showgrid=False
    )

    st.plotly_chart(
        fig_patterns,
        use_container_width=True
    )

    st.caption(
        "Review Recommended combines weakly aligned reports and "
        "unclassified reports. These reports warrant additional analyst "
        "attention; the designation is not a statement of device risk."
    )

    st.divider()

    st.subheader("Monthly Reporting Trend")

    st.caption(
        "Monthly report volume shows how adverse-event reporting varied "
        "across 2025. Changes in reporting volume should not be interpreted "
        "as changes in device incidence, causation, or comparative risk."
    )

    monthly_data = pd.DataFrame({
        "Month": [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ],
        "Reports": [
            7472, 7723, 7823, 7921, 7072, 7209,
            8592, 7690, 8464, 8599, 7658, 8649
        ]
    })

    fig_monthly = px.line(
        monthly_data,
        x="Month",
        y="Reports",
        markers=True,
        title="Monthly MAUDE Reports in the 2025 Analysis Dataset"
    )

    fig_monthly.update_traces(
        mode="lines+markers",
        hovertemplate="<b>%{x}</b><br>Reports: %{y:,}<extra></extra>"
    )

    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Reports",
        height=420,
        margin=dict(l=20, r=30, t=60, b=40),
        hovermode="x unified"
    )

    fig_monthly.update_yaxes(
        rangemode="tozero",
        tickformat=","
    )


    fig_monthly.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#334E68",
            size=13
        ),
        title_font=dict(
            color="#173B5E",
            size=18
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13
        )
    )

    fig_monthly.update_xaxes(
        showgrid=False,
        zeroline=False
    )

    fig_monthly.update_yaxes(
        showgrid=True,
        gridcolor="#E8EEF4",
        zeroline=False
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )

    st.caption(
        "The chart describes reporting workload and temporal variation "
        "within the analyzed 2025 MAUDE dataset; it does not measure the "
        "underlying frequency of device-related events."
    )


    st.divider()

    st.subheader("Top Recurring Safety Patterns")

    st.caption(
        "The most frequently represented recurring narrative patterns "
        "within the analyzed 2025 MAUDE reports. Counts represent reports "
        "associated with each pattern and should not be interpreted as "
        "device incidence, causation, or comparative risk."
    )

    top_patterns = pd.DataFrame({
        "Safety Pattern": [
            "Medical Imaging Device Damage / Image Abnormalities",
            "Cardiac Implant Lead Performance / Integrity Issues",
            "Vascular Access Catheter / Port Mechanical Issues",
            "Pulsed Field Ablation Catheter / Sheath Issues",
            "Infusion Pump Flow / Delivery Malfunctions",
            "Foley Catheter Balloon Leakage / Failure",
            "Hip Prosthesis Instability / Dislocation and Revision",
            "Coronary Angioplasty Balloon Rupture",
            "Aortic Valve Deterioration / Valve-in-Valve Intervention",
            "Surgical Suture / Needle Separation or Breakage"
        ],
        "Reports": [
            6960, 3816, 2311, 2177, 1726,
            1684, 1658, 1648, 1612, 1492
        ]
    })

    # Reverse order so largest pattern appears at the top
    top_patterns_plot = top_patterns.sort_values(
        "Reports",
        ascending=True
    )

    fig_top_patterns = px.bar(
        top_patterns_plot,
        x="Reports",
        y="Safety Pattern",
        orientation="h",
        text="Reports",
        title="Top 10 Recurring Narrative Safety Patterns"
    )

    fig_top_patterns.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Reports: %{x:,}<extra></extra>"
    )

    fig_top_patterns.update_layout(
        xaxis_title="Number of Reports",
        yaxis_title="",
        height=570,
        margin=dict(l=20, r=70, t=60, b=40)
    )

    fig_top_patterns.update_xaxes(
        tickformat=",",
        rangemode="tozero"
    )


    fig_top_patterns.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#334E68",
            size=13
        ),
        title_font=dict(
            color="#173B5E",
            size=18
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13
        )
    )

    fig_top_patterns.update_xaxes(
        showgrid=True,
        gridcolor="#E8EEF4",
        zeroline=False
    )

    fig_top_patterns.update_yaxes(
        showgrid=False
    )

    st.plotly_chart(
        fig_top_patterns,
        use_container_width=True
    )

    st.caption(
        "Patterns are derived from recurring narrative structure in the "
        "analysis pipeline and are intended to support exploration and "
        "human review rather than establish clinical conclusions."
    )

elif page == "Device Search":

    st.caption("FDA MAUDE • 2025")
    st.header("Device Search")

    st.caption(
        "Search adverse-event reports by device brand, generic name, "
        "manufacturer, model number, or FDA product code."
    )

    search_term = st.text_input(
        "Search device information",
        placeholder="Example: MICRA, MEDTRONIC, MI2355A, DYB"
    )

    if search_term:


        clean_term = search_term.strip()
        safe_term = re.escape(clean_term)

        search_query = {
            "$or": [
                {
                    "device.brand_name": {
                        "$regex": safe_term,
                        "$options": "i"
                    }
                },
                {
                    "device.generic_name": {
                        "$regex": safe_term,
                        "$options": "i"
                    }
                },
                {
                    "device.manufacturer": {
                        "$regex": safe_term,
                        "$options": "i"
                    }
                },
                {
                    "device.model_number": {
                        "$regex": safe_term,
                        "$options": "i"
                    }
                },
                {
                    "device.product_code": {
                        "$regex": safe_term,
                        "$options": "i"
                    }
                }
            ]
        }

        matching_count = collection.count_documents(search_query)

        # ----------------------------------------------
        # DEVICE SAFETY SUMMARY
        # ----------------------------------------------

        recurring_query = {
            "$and": [
                search_query,
                {
                    "safety_intelligence.pattern_status":
                    "Recurring pattern identified"
                }
            ]
        }

        unclassified_query = {
            "$and": [
                search_query,
                {
                    "safety_intelligence.unusual_flag": True
                }
            ]
        }

        weak_query = {
            "$and": [
                search_query,
                {
                    "safety_intelligence.theme_alignment_status":
                    "Weakly aligned / review recommended"
                }
            ]
        }

        recurring_count = collection.count_documents(
            recurring_query
        )

        unclassified_count = collection.count_documents(
            unclassified_query
        )

        weak_count = collection.count_documents(
            weak_query
        )

        review_count = weak_count + unclassified_count

        st.subheader("Device Safety Summary")

        k1, k2, k3, k4 = st.columns(4)

        k1.metric(
            "Matching Reports",
            f"{matching_count:,}"
        )

        k2.metric(
            "Recurring Pattern Reports",
            f"{recurring_count:,}"
        )

        k3.metric(
            "Review Recommended",
            f"{review_count:,}"
        )

        k4.metric(
            "Unclassified Reports",
            f"{unclassified_count:,}"
        )

        st.caption(
            "Review Recommended combines weakly aligned and unclassified "
            "reports for analyst attention. These indicators describe "
            "reporting patterns and do not establish device risk or causation."
        )


        if recurring_count > 0:

            st.subheader("Recurring Safety Patterns")

            st.caption(
                "Most frequently represented recurring narrative patterns "
                "within the current search results."
            )

            pattern_pipeline = [
                {
                    "$match": {
                        "$and": [
                            search_query,
                            {
                                "safety_intelligence.pattern_status":
                                "Recurring pattern identified"
                            }
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": "$safety_intelligence.cluster_theme",
                        "Reports": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "_id": {
                            "$nin": [
                                None,
                                "",
                                "Unclassified / requires review"
                            ]
                        }
                    }
                },
                {"$sort": {"Reports": -1}},
                {"$limit": 5}
            ]

            pattern_results = list(
                collection.aggregate(pattern_pipeline)
            )

            if pattern_results:

                pattern_df = pd.DataFrame([
                    {
                        "Safety Pattern": item["_id"],
                        "Reports": item["Reports"]
                    }
                    for item in pattern_results
                ])

                pattern_plot_df = pattern_df.sort_values(
                    "Reports",
                    ascending=True
                )

                fig_device_patterns = px.bar(
                    pattern_plot_df,
                    x="Reports",
                    y="Safety Pattern",
                    orientation="h",
                    text="Reports",
                    title="Top Recurring Patterns in Current Search"
                )

                fig_device_patterns.update_traces(
                    texttemplate="%{text:,}",
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Reports: %{x:,}<extra></extra>"
                    )
                )

                fig_device_patterns.update_layout(
                    xaxis_title="Number of Reports",
                    yaxis_title="",
                    height=400,
                    margin=dict(
                        l=20,
                        r=60,
                        t=60,
                        b=40
                    )
                )

                fig_device_patterns.update_xaxes(
                    rangemode="tozero",
                    tickformat=","
                )

                st.plotly_chart(
                    fig_device_patterns,
                    use_container_width=True
                )

                st.caption(
                    "Pattern counts describe recurring narrative structure "
                    "within the selected reports and should not be interpreted "
                    "as incidence, causation, or comparative device risk."
                )

        if matching_count == 0:

            st.warning(
                "No matching reports found. Try another brand, manufacturer, "
                "generic name, model number, or product code."
            )

        else:

            cursor = collection.find(
                search_query,
                {
                    "_id": 0,
                    "report_id": 1,
                    "device.brand_name": 1,
                    "device.generic_name": 1,
                    "device.manufacturer": 1,
                    "device.model_number": 1,
                    "device.product_code": 1,
                    "safety_intelligence.cluster_theme": 1,
                    "safety_intelligence.theme_alignment_status": 1
                }
            ).limit(100)

            rows = []

            for record in cursor:

                device = record.get("device", {})
                safety = record.get("safety_intelligence", {})

                rows.append({
                    "Report ID": record.get("report_id"),
                    "Brand": device.get("brand_name"),
                    "Generic Name": device.get("generic_name"),
                    "Manufacturer": device.get("manufacturer"),
                    "Model": device.get("model_number"),
                    "Product Code": device.get("product_code"),
                    "Safety Pattern": safety.get("cluster_theme"),
                    "Alignment": safety.get("theme_alignment_status")
                })

            results_df = pd.DataFrame(rows)

            st.caption(
                f"Showing up to 100 of {matching_count:,} matching reports."
            )

            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True
            )


            st.divider()

            st.subheader("Report Evidence")

            st.caption(
                "Select a matching report to inspect the original MAUDE "
                "narrative and its associated safety-intelligence context."
            )

            available_report_ids = (
                results_df["Report ID"]
                .dropna()
                .astype(str)
                .tolist()
            )

            if available_report_ids:

                selected_report_id = st.selectbox(
                    "Select Report ID",
                    available_report_ids
                )

                # report_id is stored as a string in MongoDB
                report_lookup_id = str(selected_report_id)

                selected_report = collection.find_one(
                    {"report_id": report_lookup_id},
                    {
                        "_id": 0,
                        "report_id": 1,
                        "device": 1,
                        "report": 1,
                        "safety_intelligence": 1,
                        "evidence": 1,
                        "review": 1
                    }
                )

                if selected_report:

                    device_info = selected_report.get("device", {})
                    report_info = selected_report.get("report", {})
                    safety_info = selected_report.get(
                        "safety_intelligence", {}
                    )
                    evidence_info = selected_report.get("evidence", {})
                    review_info = selected_report.get("review", {})

                    st.markdown(
                        "### Report "
                        + str(selected_report.get("report_id"))
                    )

                    d1, d2, d3 = st.columns(3)

                    with d1:
                        st.caption("Brand")
                        st.write(
                            device_info.get("brand_name")
                            or "Not available"
                        )

                    with d2:
                        st.caption("Manufacturer")
                        st.write(
                            device_info.get("manufacturer")
                            or "Not available"
                        )

                    with d3:
                        st.caption("Product Code")
                        st.write(
                            device_info.get("product_code")
                            or "Not available"
                        )

                    st.markdown("#### Safety Context")

                    s1, s2 = st.columns(2)

                    with s1:
                        st.caption("Recurring Pattern")
                        st.write(
                            safety_info.get("cluster_theme")
                            or "Unclassified"
                        )

                    with s2:
                        st.caption("Pattern Alignment")
                        st.write(
                            safety_info.get(
                                "theme_alignment_status"
                            )
                            or "Not available"
                        )

                    st.markdown("#### Report Information")

                    r1, r2, r3 = st.columns(3)

                    r1.metric(
                        "Date Received",
                        str(
                            report_info.get(
                                "date_received",
                                "Not available"
                            )
                        )
                    )

                    r2.metric(
                        "Narratives",
                        report_info.get("narrative_count", 0)
                    )

                    r3.metric(
                        "Word Count",
                        report_info.get("word_count", 0)
                    )

                    st.markdown("#### Original MAUDE Narrative")

                    original_narrative = evidence_info.get(
                        "original_narrative"
                    )

                    if original_narrative:

                        st.text_area(
                            "Original report evidence",
                            value=original_narrative,
                            height=220,
                            disabled=True,
                            label_visibility="collapsed"
                        )

                    else:

                        st.warning(
                            "Original narrative is not available "
                            "for this report."
                        )

                    st.markdown("#### Human Review")

                    review_status = review_info.get(
                        "review_status",
                        "Not reviewed"
                    )

                    st.write(
                        "Review Status: " + str(review_status)
                    )

                    st.caption(
                        "The original narrative is provided as evidence "
                        "for professional interpretation. Pattern labels "
                        "and alignment categories are analytical aids and "
                        "do not establish causation or clinical conclusions."
                    )

                else:

                    st.warning(
                        "The selected report could not be retrieved."
                    )

    else:

        st.info(
            "Enter a device brand, generic name, manufacturer, "
            "model number, or product code to begin."
        )

elif page == "Safety Patterns":

    st.caption("FDA MAUDE • 2025")
    st.header("Safety Pattern Investigation")

    st.caption(
        "Explore recurring narrative patterns identified across the "
        "2025 MAUDE analysis dataset and inspect the reports associated "
        "with each pattern."
    )

    pattern_catalogue = list(
        collection.aggregate([
            {
                "$match": {
                    "safety_intelligence.pattern_status":
                    "Recurring pattern identified"
                }
            },
            {
                "$group": {
                    "_id": "$safety_intelligence.cluster_theme",
                    "report_count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "_id": {"$nin": [None, ""]}
                }
            },
            {
                "$sort": {
                    "report_count": -1
                }
            }
        ])
    )

    pattern_names = [
        item["_id"]
        for item in pattern_catalogue
    ]

    st.metric(
        "Recurring Safety Patterns",
        f"{len(pattern_names):,}"
    )

    selected_pattern = st.selectbox(
        "Select a safety pattern",
        pattern_names,
        key="selected_safety_pattern"
    )

    if selected_pattern:

        pattern_query = {
            "safety_intelligence.cluster_theme":
            selected_pattern
        }

        total_pattern_reports = collection.count_documents(
            pattern_query
        )

        typical_count = collection.count_documents({
            "$and": [
                pattern_query,
                {
                    "safety_intelligence.theme_alignment_status":
                    "Typical of recurring theme"
                }
            ]
        })

        moderate_count = collection.count_documents({
            "$and": [
                pattern_query,
                {
                    "safety_intelligence.theme_alignment_status":
                    "Moderately aligned with recurring theme"
                }
            ]
        })

        weak_count = collection.count_documents({
            "$and": [
                pattern_query,
                {
                    "safety_intelligence.theme_alignment_status":
                    "Weakly aligned / review recommended"
                }
            ]
        })

        st.subheader(selected_pattern)

        p1, p2, p3, p4 = st.columns(4)

        p1.metric(
            "Pattern Reports",
            f"{total_pattern_reports:,}"
        )

        p2.metric(
            "Typical",
            f"{typical_count:,}"
        )

        p3.metric(
            "Moderately Aligned",
            f"{moderate_count:,}"
        )

        p4.metric(
            "Weak — Review Recommended",
            f"{weak_count:,}"
        )

        st.caption(
            "Alignment describes how closely individual narratives match "
            "the recurring pattern representation. It does not measure "
            "clinical severity, causation, or comparative device risk."
        )

        # --------------------------------------------------
        # FEATURE 3.2 — PATTERN-ASSOCIATED DEVICE PROFILE
        # --------------------------------------------------

        st.divider()

        st.subheader("Devices Associated With This Reporting Pattern")

        st.caption(
            "These counts describe device and manufacturer names appearing "
            "in reports assigned to the selected narrative pattern. "
            "They should not be interpreted as comparative safety rates."
        )

        generic_device_results = list(
            collection.aggregate([
                {
                    "$match": {
                        "safety_intelligence.cluster_theme":
                        selected_pattern
                    }
                },
                {
                    "$group": {
                        "_id": "$device.generic_name",
                        "reports": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "_id": {"$nin": [None, ""]}
                    }
                },
                {
                    "$sort": {
                        "reports": -1
                    }
                },
                {
                    "$limit": 10
                }
            ])
        )

        manufacturer_results = list(
            collection.aggregate([
                {
                    "$match": {
                        "safety_intelligence.cluster_theme":
                        selected_pattern
                    }
                },
                {
                    "$group": {
                        "_id": "$device.manufacturer",
                        "reports": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "_id": {"$nin": [None, ""]}
                    }
                },
                {
                    "$sort": {
                        "reports": -1
                    }
                },
                {
                    "$limit": 10
                }
            ])
        )

        device_table = [
            {
                "Generic Device Name": item["_id"],
                "Reports": item["reports"]
            }
            for item in generic_device_results
        ]

        manufacturer_table = [
            {
                "Manufacturer": item["_id"],
                "Reports": item["reports"]
            }
            for item in manufacturer_results
        ]

        device_col, manufacturer_col = st.columns(2)

        with device_col:

            st.markdown("**Top Generic Device Names**")

            if device_table:
                st.dataframe(
                    device_table,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(
                    "No generic device names available "
                    "for this pattern."
                )

        with manufacturer_col:

            st.markdown("**Top Manufacturers in Reports**")

            if manufacturer_table:
                st.dataframe(
                    manufacturer_table,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(
                    "No manufacturer information available "
                    "for this pattern."
                )

        # --------------------------------------------------
        # FEATURE 3.3 — HIGH-ALIGNMENT REPORT EVIDENCE
        # --------------------------------------------------

        st.divider()

        st.subheader("High-Alignment Report Evidence")

        st.caption(
            "These reports are highly aligned with the selected recurring "
            "narrative pattern. They are examples for analyst inspection, "
            "not clinical validation of the pattern."
        )

        representative_reports = list(
            collection.find(
                {
                    "safety_intelligence.cluster_theme":
                    selected_pattern,

                    "safety_intelligence.theme_alignment_status":
                    "Typical of recurring theme"
                },
                {
                    "_id": 0,
                    "report_id": 1,
                    "device.brand_name": 1,
                    "device.generic_name": 1,
                    "device.manufacturer": 1,
                    "report.date_received": 1,
                    "report.word_count": 1,
                    "safety_intelligence.theme_similarity": 1,
                    "safety_intelligence.theme_similarity_percentile": 1,
                    "evidence.original_narrative": 1
                }
            ).sort(
                "safety_intelligence.theme_similarity_percentile",
                -1
            ).limit(10)
        )

        if representative_reports:

            report_options = {
                str(item.get("report_id")): item
                for item in representative_reports
            }

            selected_evidence_report = st.selectbox(
                "Select a high-alignment report",
                list(report_options.keys()),
                key="pattern_evidence_report"
            )

            selected_record = report_options[
                selected_evidence_report
            ]

            device_info = selected_record.get(
                "device", {}
            )

            report_info = selected_record.get(
                "report", {}
            )

            safety_info = selected_record.get(
                "safety_intelligence", {}
            )

            evidence_info = selected_record.get(
                "evidence", {}
            )

            e1, e2, e3, e4 = st.columns(4)

            e1.metric(
                "Report ID",
                str(selected_record.get(
                    "report_id", "Unknown"
                ))
            )

            e2.metric(
                "Date Received",
                str(report_info.get(
                    "date_received", "Unknown"
                ))
            )

            percentile = safety_info.get(
                "theme_similarity_percentile"
            )

            if isinstance(percentile, (int, float)):
                percentile_display = (
                    f"{percentile * 100:.1f}%"
                )
            else:
                percentile_display = "Unavailable"

            e3.metric(
                "Pattern Alignment Percentile",
                percentile_display
            )

            e4.metric(
                "Word Count",
                str(report_info.get(
                    "word_count", "Unknown"
                ))
            )

            st.markdown("**Device Information**")

            st.write(
                "Brand:",
                device_info.get(
                    "brand_name", "Not available"
                )
            )

            st.write(
                "Generic device:",
                device_info.get(
                    "generic_name", "Not available"
                )
            )

            st.write(
                "Manufacturer:",
                device_info.get(
                    "manufacturer", "Not available"
                )
            )

            narrative = evidence_info.get(
                "original_narrative"
            )

            with st.expander(
                "View Original MAUDE Narrative",
                expanded=False
            ):

                if narrative:

                    st.write(narrative)

                else:

                    st.info(
                        "Original narrative is not "
                        "available for this report."
                    )

            st.caption(
                "The original narrative is preserved as source evidence. "
                "Pattern alignment supports review prioritization and "
                "should not be interpreted as proof of causation."
            )

        else:

            st.info(
                "No high-alignment reports are available "
                "for this safety pattern."
            )


        # --------------------------------------------------
        # FEATURE 3.4 — WEAK-ALIGNMENT REVIEW QUEUE
        # --------------------------------------------------

        st.divider()

        st.subheader("Reports Requiring Pattern Review")

        st.caption(
            "These reports were assigned to the selected recurring pattern "
            "but have comparatively weak alignment with that pattern. "
            "They are surfaced for analyst inspection rather than treated "
            "as confirmed examples."
        )

        weak_review_reports = list(
            collection.find(
                {
                    "safety_intelligence.cluster_theme":
                    selected_pattern,

                    "safety_intelligence.theme_alignment_status":
                    "Weakly aligned / review recommended"
                },
                {
                    "_id": 0,
                    "report_id": 1,
                    "device.brand_name": 1,
                    "device.generic_name": 1,
                    "device.manufacturer": 1,
                    "report.date_received": 1,
                    "report.word_count": 1,
                    "safety_intelligence.theme_similarity": 1,
                    "safety_intelligence.theme_similarity_percentile": 1,
                    "evidence.original_narrative": 1,
                    "review.review_status": 1
                }
            ).sort(
                "safety_intelligence.theme_similarity_percentile",
                1
            ).limit(10)
        )

        if weak_review_reports:

            weak_options = {
                str(item.get("report_id")): item
                for item in weak_review_reports
            }

            selected_weak_report = st.selectbox(
                "Select a report requiring review",
                list(weak_options.keys()),
                key="pattern_weak_review_report"
            )

            weak_record = weak_options[
                selected_weak_report
            ]

            weak_device = weak_record.get(
                "device", {}
            )

            weak_report_info = weak_record.get(
                "report", {}
            )

            weak_safety = weak_record.get(
                "safety_intelligence", {}
            )

            weak_evidence = weak_record.get(
                "evidence", {}
            )

            weak_review = weak_record.get(
                "review", {}
            )

            weak_percentile = weak_safety.get(
                "theme_similarity_percentile"
            )

            if isinstance(
                weak_percentile,
                (int, float)
            ):
                weak_rank_display = (
                    f"Bottom "
                    f"{weak_percentile * 100:.1f}%"
                )
            else:
                weak_rank_display = "Unavailable"

            w1, w2, w3, w4 = st.columns(4)

            w1.metric(
                "Report ID",
                str(weak_record.get(
                    "report_id", "Unknown"
                ))
            )

            w2.metric(
                "Date Received",
                str(weak_report_info.get(
                    "date_received", "Unknown"
                ))
            )

            w3.metric(
                "Similarity Rank Within Pattern",
                weak_rank_display
            )

            w4.metric(
                "Review Status",
                str(weak_review.get(
                    "review_status",
                    "Not reviewed"
                ))
            )

            st.warning(
                "This report has weak similarity to the selected "
                "recurring pattern and should be reviewed before "
                "the pattern assignment is relied upon."
            )

            st.markdown("**Device Information**")

            st.write(
                "Brand:",
                weak_device.get(
                    "brand_name", "Not available"
                )
            )

            st.write(
                "Generic device:",
                weak_device.get(
                    "generic_name", "Not available"
                )
            )

            st.write(
                "Manufacturer:",
                weak_device.get(
                    "manufacturer", "Not available"
                )
            )

            weak_narrative = weak_evidence.get(
                "original_narrative"
            )

            with st.expander(
                "View Original MAUDE Narrative",
                expanded=False
            ):

                if weak_narrative:
                    st.write(weak_narrative)

                else:
                    st.info(
                        "Original narrative is not "
                        "available for this report."
                    )

            st.caption(
                "Weak alignment is an analytical prioritization signal. "
                "It does not establish that the report is erroneous, "
                "clinically unusual, or unrelated to the device."
            )

        else:

            st.info(
                "No weak-alignment reports were identified "
                "for this recurring pattern."
            )


elif page == "Trend Analysis":

    st.caption("FDA MAUDE • 2025")
    st.header("Trend Analysis")

    st.caption(
        "Explore how MAUDE reporting volume and analyst-review workload "
        "vary across the 2025 analysis period."
    )

    monthly_trends = list(
        collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "$substr": [
                            "$report.date_received",
                            0,
                            7
                        ]
                    },
                    "total_reports": {
                        "$sum": 1
                    },
                    "review_recommended": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$or": [
                                        {
                                            "$eq": [
                                                "$safety_intelligence.unusual_flag",
                                                True
                                            ]
                                        },
                                        {
                                            "$eq": [
                                                "$safety_intelligence.theme_alignment_status",
                                                "Weakly aligned / review recommended"
                                            ]
                                        }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    }
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ])
    )

    month_labels = {
        "2025/01": "Jan",
        "2025/02": "Feb",
        "2025/03": "Mar",
        "2025/04": "Apr",
        "2025/05": "May",
        "2025/06": "Jun",
        "2025/07": "Jul",
        "2025/08": "Aug",
        "2025/09": "Sep",
        "2025/10": "Oct",
        "2025/11": "Nov",
        "2025/12": "Dec"
    }

    trend_rows = []

    for item in monthly_trends:

        month_value = item.get("_id", "")
        total = item.get("total_reports", 0)
        review = item.get("review_recommended", 0)

        review_share = (
            review / total * 100
            if total else 0
        )

        trend_rows.append({
            "Month": month_labels.get(
                month_value,
                month_value
            ),
            "Total Reports": total,
            "Review Recommended": review,
            "Review Share (%)": round(
                review_share,
                1
            )
        })

    if trend_rows:

        import pandas as pd

        total_year_reports = sum(
            row["Total Reports"]
            for row in trend_rows
        )

        total_year_review = sum(
            row["Review Recommended"]
            for row in trend_rows
        )

        overall_review_share = (
            total_year_review /
            total_year_reports * 100
            if total_year_reports else 0
        )

        t1, t2, t3 = st.columns(3)

        t1.metric(
            "2025 Reports",
            f"{total_year_reports:,}"
        )

        t2.metric(
            "Review Recommended",
            f"{total_year_review:,}"
        )

        t3.metric(
            "Review Workload Share",
            f"{overall_review_share:.1f}%"
        )

        st.divider()

        st.subheader(
            "Monthly Reporting and Review Workload"
        )

        month_order = [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ]

        trend_df = pd.DataFrame(
            trend_rows
        )

        trend_df["Month"] = pd.Categorical(
            trend_df["Month"],
            categories=month_order,
            ordered=True
        )

        trend_df = trend_df.sort_values(
            "Month"
        )

        volume_df = trend_df.set_index(
            "Month"
        )[
            [
                "Total Reports",
                "Review Recommended"
            ]
        ]

        st.line_chart(
            volume_df,
            use_container_width=True
        )

        st.subheader(
            "Monthly Review Workload Share"
        )

        share_df = trend_df.set_index(
            "Month"
        )[
            ["Review Share (%)"]
        ]

        st.line_chart(
            share_df,
            use_container_width=True
        )

        st.caption(
            "Monthly variation reflects reporting volume and the share "
            "of reports prioritized by this analytical workflow for "
            "review. It should not be interpreted as a change in device "
            "safety, adverse-event incidence, or comparative risk."
        )

    else:

        st.info(
            "No monthly trend data are available."
        )


    # =====================================================
    # Feature 4.2 — Pattern-Specific Monthly Trends
    # =====================================================

    st.divider()

    st.subheader(
        "Pattern-Specific Monthly Trends"
    )

    st.caption(
        "Explore how reports associated with a recurring safety "
        "pattern are distributed across 2025."
    )

    pattern_catalogue = list(
        collection.aggregate([
            {
                "$match": {
                    "safety_intelligence.pattern_status":
                    "Recurring pattern identified",
                    "safety_intelligence.cluster_theme": {
                        "$nin": [None, ""]
                    }
                }
            },
            {
                "$group": {
                    "_id":
                    "$safety_intelligence.cluster_theme",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "count": -1,
                    "_id": 1
                }
            }
        ])
    )

    trend_pattern_names = [
        row["_id"]
        for row in pattern_catalogue
    ]

    if trend_pattern_names:

        selected_trend_pattern = st.selectbox(
            "Select a recurring safety pattern",
            trend_pattern_names,
            key="trend_selected_safety_pattern"
        )

        pattern_monthly_data = list(
            collection.aggregate([
                {
                    "$match": {
                        "safety_intelligence.cluster_theme":
                        selected_trend_pattern
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$substr": [
                                "$report.date_received",
                                0,
                                7
                            ]
                        },
                        "reports": {
                            "$sum": 1
                        },
                        "typical": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$eq": [
                                            "$safety_intelligence.theme_alignment_status",
                                            "Typical of recurring theme"
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        },
                        "moderate": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$eq": [
                                            "$safety_intelligence.theme_alignment_status",
                                            "Moderately aligned with recurring theme"
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        },
                        "weak": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$eq": [
                                            "$safety_intelligence.theme_alignment_status",
                                            "Weakly aligned / review recommended"
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {
                        "_id": 1
                    }
                }
            ])
        )

        if pattern_monthly_data:

            month_labels = {
                "01": "Jan",
                "02": "Feb",
                "03": "Mar",
                "04": "Apr",
                "05": "May",
                "06": "Jun",
                "07": "Jul",
                "08": "Aug",
                "09": "Sep",
                "10": "Oct",
                "11": "Nov",
                "12": "Dec"
            }

            pattern_trend_rows = []

            for row in pattern_monthly_data:

                month_code = row["_id"][-2:]

                pattern_trend_rows.append({
                    "Month":
                    month_labels.get(
                        month_code,
                        row["_id"]
                    ),
                    "Total Reports":
                    row["reports"],
                    "Typical":
                    row["typical"],
                    "Moderate":
                    row["moderate"],
                    "Weak — Review Recommended":
                    row["weak"]
                })

            pattern_trend_df = pd.DataFrame(
                pattern_trend_rows
            )

            pattern_month_order = [
                "Jan", "Feb", "Mar", "Apr",
                "May", "Jun", "Jul", "Aug",
                "Sep", "Oct", "Nov", "Dec"
            ]

            pattern_trend_df["Month"] = pd.Categorical(
                pattern_trend_df["Month"],
                categories=pattern_month_order,
                ordered=True
            )

            pattern_trend_df = (
                pattern_trend_df
                .sort_values("Month")
            )

            pattern_total = int(
                pattern_trend_df[
                    "Total Reports"
                ].sum()
            )

            st.metric(
                "2025 Reports for Selected Pattern",
                f"{pattern_total:,}"
            )

            st.markdown(
                "**Monthly Reporting Volume**"
            )

            st.line_chart(
                pattern_trend_df.set_index(
                    "Month"
                )[["Total Reports"]],
                use_container_width=True
            )

            st.markdown(
                "**Monthly Pattern Alignment Composition**"
            )

            st.line_chart(
                pattern_trend_df.set_index(
                    "Month"
                )[
                    [
                        "Typical",
                        "Moderate",
                        "Weak — Review Recommended"
                    ]
                ],
                use_container_width=True
            )

            st.caption(
                "These charts describe reporting patterns within "
                "the selected recurring narrative theme. Changes "
                "over time should not be interpreted as changes in "
                "adverse-event incidence, device safety, severity, "
                "or comparative risk."
            )

        else:

            st.info(
                "No monthly data are available for the "
                "selected pattern."
            )

    else:

        st.info(
            "No recurring safety patterns are available."
        )



    # =====================================================
    # Feature 4.3 — Device-Specific Reporting Trends
    # =====================================================

    st.divider()

    st.subheader(
        "Device-Specific Reporting Trends"
    )

    st.caption(
        "Search across brand, generic device name, manufacturer, "
        "model number, or product code to explore monthly reporting "
        "patterns for matching records."
    )

    trend_device_search = st.text_input(
        "Search device information",
        placeholder=(
            "Example: MICRA, Medtronic, model number, "
            "or product code"
        ),
        key="trend_device_search"
    )

    if trend_device_search.strip():

        escaped_trend_search = re.escape(
            trend_device_search.strip()
        )

        trend_device_filter = {
            "$or": [
                {
                    "device.brand_name": {
                        "$regex": escaped_trend_search,
                        "$options": "i"
                    }
                },
                {
                    "device.generic_name": {
                        "$regex": escaped_trend_search,
                        "$options": "i"
                    }
                },
                {
                    "device.manufacturer": {
                        "$regex": escaped_trend_search,
                        "$options": "i"
                    }
                },
                {
                    "device.model_number": {
                        "$regex": escaped_trend_search,
                        "$options": "i"
                    }
                },
                {
                    "device.product_code": {
                        "$regex": escaped_trend_search,
                        "$options": "i"
                    }
                }
            ]
        }

        device_trend_data = list(
            collection.aggregate([
                {
                    "$match":
                    trend_device_filter
                },
                {
                    "$group": {
                        "_id": {
                            "$substr": [
                                "$report.date_received",
                                0,
                                7
                            ]
                        },
                        "reports": {
                            "$sum": 1
                        },
                        "review_recommended": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$or": [
                                            {
                                                "$eq": [
                                                    "$safety_intelligence.unusual_flag",
                                                    True
                                                ]
                                            },
                                            {
                                                "$eq": [
                                                    "$safety_intelligence.theme_alignment_status",
                                                    "Weakly aligned / review recommended"
                                                ]
                                            }
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {
                        "_id": 1
                    }
                }
            ])
        )

        if device_trend_data:

            device_month_labels = {
                "01": "Jan",
                "02": "Feb",
                "03": "Mar",
                "04": "Apr",
                "05": "May",
                "06": "Jun",
                "07": "Jul",
                "08": "Aug",
                "09": "Sep",
                "10": "Oct",
                "11": "Nov",
                "12": "Dec"
            }

            device_trend_rows = []

            for row in device_trend_data:

                month_code = row["_id"][-2:]

                reports = row["reports"]
                review = row["review_recommended"]

                review_share = (
                    review / reports * 100
                    if reports else 0
                )

                device_trend_rows.append({
                    "Month":
                    device_month_labels.get(
                        month_code,
                        row["_id"]
                    ),
                    "Total Reports":
                    reports,
                    "Review Recommended":
                    review,
                    "Review Share (%)":
                    review_share
                })

            device_trend_df = pd.DataFrame(
                device_trend_rows
            )

            device_month_order = [
                "Jan", "Feb", "Mar", "Apr",
                "May", "Jun", "Jul", "Aug",
                "Sep", "Oct", "Nov", "Dec"
            ]

            device_trend_df["Month"] = pd.Categorical(
                device_trend_df["Month"],
                categories=device_month_order,
                ordered=True
            )

            device_trend_df = (
                device_trend_df
                .sort_values("Month")
            )

            device_total = int(
                device_trend_df[
                    "Total Reports"
                ].sum()
            )

            device_review_total = int(
                device_trend_df[
                    "Review Recommended"
                ].sum()
            )

            device_review_share = (
                device_review_total
                / device_total
                * 100
                if device_total else 0
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Matching Reports",
                f"{device_total:,}"
            )

            col2.metric(
                "Review Recommended",
                f"{device_review_total:,}"
            )

            col3.metric(
                "Review Workload Share",
                f"{device_review_share:.1f}%"
            )

            st.markdown(
                "**Monthly Reporting Volume**"
            )

            st.line_chart(
                device_trend_df.set_index(
                    "Month"
                )[
                    [
                        "Total Reports",
                        "Review Recommended"
                    ]
                ],
                use_container_width=True
            )

            st.markdown(
                "**Monthly Review Workload Share**"
            )

            st.line_chart(
                device_trend_df.set_index(
                    "Month"
                )[["Review Share (%)"]],
                use_container_width=True
            )

            st.caption(
                "Results reflect adverse-event reports matching the "
                "entered device information. Reporting volume and "
                "review-prioritization indicators do not establish "
                "adverse-event incidence, causation, device safety, "
                "severity, or comparative risk."
            )

        else:

            st.info(
                "No reports matched this device search."
            )

    else:

        st.info(
            "Enter device information to explore its "
            "monthly reporting pattern."
        )


elif page == "Report Explorer":

    st.caption("FDA MAUDE • 2025")
    st.header("Report Explorer")

    st.caption(
        "Investigate an individual MAUDE adverse-event report, "
        "its device information, analytical context, original "
        "narrative evidence, and review status."
    )

    # =====================================================
    # Feature 5.2 — Flexible Report Discovery
    # =====================================================

    st.subheader("Discover Reports")

    st.caption(
        "Narrow the evidence pool using device information, month, "
        "recurring safety pattern, and review category."
    )

    discovery_device = st.text_input(
        "Device information",
        placeholder=(
            "Brand, generic name, manufacturer, "
            "model number, or product code"
        ),
        key="explorer_discovery_device"
    )

    discovery_col1, discovery_col2 = st.columns(2)

    with discovery_col1:

        discovery_month = st.selectbox(
            "Month",
            [
                "All months",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December"
            ],
            key="explorer_discovery_month"
        )

    with discovery_col2:

        discovery_review = st.selectbox(
            "Review category",
            [
                "All reports",
                "Review Recommended",
                "Unclassified",
                "Weak Alignment",
                "Routine"
            ],
            key="explorer_discovery_review"
        )

    discovery_pattern_catalogue = list(
        collection.aggregate([
            {
                "$match": {
                    "safety_intelligence.pattern_status":
                    "Recurring pattern identified",
                    "safety_intelligence.cluster_theme": {
                        "$nin": [None, ""]
                    }
                }
            },
            {
                "$group": {
                    "_id":
                    "$safety_intelligence.cluster_theme"
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ])
    )

    discovery_pattern_names = [
        row["_id"]
        for row in discovery_pattern_catalogue
    ]

    discovery_pattern = st.selectbox(
        "Safety pattern",
        ["All patterns"] + discovery_pattern_names,
        key="explorer_discovery_pattern"
    )

    run_discovery = st.button(
        "Find Reports",
        key="explorer_find_reports",
        type="primary"
    )

    if run_discovery:

        discovery_conditions = []

        # ---------------------------------------------
        # Device filter
        # ---------------------------------------------

        if discovery_device.strip():

            escaped_discovery_device = re.escape(
                discovery_device.strip()
            )

            discovery_conditions.append({
                "$or": [
                    {
                        "device.brand_name": {
                            "$regex":
                            escaped_discovery_device,
                            "$options": "i"
                        }
                    },
                    {
                        "device.generic_name": {
                            "$regex":
                            escaped_discovery_device,
                            "$options": "i"
                        }
                    },
                    {
                        "device.manufacturer": {
                            "$regex":
                            escaped_discovery_device,
                            "$options": "i"
                        }
                    },
                    {
                        "device.model_number": {
                            "$regex":
                            escaped_discovery_device,
                            "$options": "i"
                        }
                    },
                    {
                        "device.product_code": {
                            "$regex":
                            escaped_discovery_device,
                            "$options": "i"
                        }
                    }
                ]
            })

        # ---------------------------------------------
        # Month filter
        # ---------------------------------------------

        discovery_month_codes = {
            "January": "01",
            "February": "02",
            "March": "03",
            "April": "04",
            "May": "05",
            "June": "06",
            "July": "07",
            "August": "08",
            "September": "09",
            "October": "10",
            "November": "11",
            "December": "12"
        }

        if discovery_month != "All months":

            selected_month_code = (
                discovery_month_codes[
                    discovery_month
                ]
            )

            discovery_conditions.append({
                "report.date_received": {
                    "$regex":
                    "^2025/"
                    + selected_month_code
                }
            })

        # ---------------------------------------------
        # Pattern filter
        # ---------------------------------------------

        if discovery_pattern != "All patterns":

            discovery_conditions.append({
                "safety_intelligence.cluster_theme":
                discovery_pattern
            })

        # ---------------------------------------------
        # Review-category filter
        # ---------------------------------------------

        if discovery_review == "Review Recommended":

            discovery_conditions.append({
                "$or": [
                    {
                        "safety_intelligence.unusual_flag":
                        True
                    },
                    {
                        "safety_intelligence.theme_alignment_status":
                        "Weakly aligned / review recommended"
                    }
                ]
            })

        elif discovery_review == "Unclassified":

            discovery_conditions.append({
                "safety_intelligence.unusual_flag":
                True
            })

        elif discovery_review == "Weak Alignment":

            discovery_conditions.append({
                "safety_intelligence.theme_alignment_status":
                "Weakly aligned / review recommended"
            })

        elif discovery_review == "Routine":

            discovery_conditions.append({
                "safety_intelligence.unusual_flag":
                {"$ne": True},
                "safety_intelligence.theme_alignment_status": {
                    "$ne":
                    "Weakly aligned / review recommended"
                }
            })

        # ---------------------------------------------
        # Build final MongoDB filter
        # ---------------------------------------------

        if discovery_conditions:

            final_discovery_filter = {
                "$and": discovery_conditions
            }

        else:

            final_discovery_filter = {}

        discovery_match_count = (
            collection.count_documents(
                final_discovery_filter
            )
        )

        discovery_results = list(
            collection.find(
                final_discovery_filter,
                {
                    "_id": 0,
                    "report_id": 1,
                    "report.date_received": 1,
                    "device.brand_name": 1,
                    "device.generic_name": 1,
                    "device.manufacturer": 1,
                    "device.product_code": 1,
                    "safety_intelligence.cluster_theme": 1,
                    "safety_intelligence.theme_alignment_status": 1,
                    "safety_intelligence.unusual_flag": 1,
                    "review.review_status": 1
                }
            )
            .sort("report.date_received", -1)
            .limit(100)
        )

        st.metric(
            "Matching Reports",
            f"{discovery_match_count:,}"
        )

        if discovery_results:

            discovery_table_rows = []

            for doc in discovery_results:

                device = doc.get(
                    "device", {}
                )

                report = doc.get(
                    "report", {}
                )

                safety = doc.get(
                    "safety_intelligence", {}
                )

                review = doc.get(
                    "review", {}
                )

                if safety.get(
                    "unusual_flag"
                ) is True:

                    review_reason = (
                        "Unclassified"
                    )

                elif (
                    safety.get(
                        "theme_alignment_status"
                    )
                    ==
                    "Weakly aligned / review recommended"
                ):

                    review_reason = (
                        "Weak alignment"
                    )

                else:

                    review_reason = (
                        "Routine"
                    )

                discovery_table_rows.append({
                    "Report ID":
                    doc.get("report_id"),
                    "Date":
                    report.get(
                        "date_received"
                    ),
                    "Brand":
                    device.get(
                        "brand_name"
                    ),
                    "Generic Device":
                    device.get(
                        "generic_name"
                    ),
                    "Manufacturer":
                    device.get(
                        "manufacturer"
                    ),
                    "Product Code":
                    device.get(
                        "product_code"
                    ),
                    "Safety Pattern":
                    safety.get(
                        "cluster_theme"
                    ),
                    "Review Reason":
                    review_reason,
                    "Human Review":
                    review.get(
                        "review_status"
                    )
                })

            discovery_df = pd.DataFrame(
                discovery_table_rows
            )

            st.dataframe(
                discovery_df,
                use_container_width=True,
                hide_index=True
            )

            if discovery_match_count > 100:

                st.caption(
                    "Showing the 100 most recent matching "
                    f"reports out of {discovery_match_count:,}. "
                    "Refine the filters to narrow the evidence pool."
                )

            else:

                st.caption(
                    f"Showing all {discovery_match_count:,} "
                    "matching reports."
                )

            discovered_report_ids = [
                str(report_id)
                for report_id in discovery_df[
                    "Report ID"
                ].tolist()
                if report_id is not None
            ]

            selected_discovered_report = st.selectbox(
                "Select a report for investigation",
                [""] + discovered_report_ids,
                format_func=lambda x: (
                    "Choose a Report ID..."
                    if x == ""
                    else x
                ),
                key="explorer_discovered_report"
            )

            if selected_discovered_report:

                st.session_state[
                    "explorer_selected_report_id"
                ] = selected_discovered_report

                st.success(
                    "Report "
                    + selected_discovered_report
                    + " selected for investigation below."
                )

            st.caption(
                "Select a Report ID above or enter a different "
                "Report ID manually in Direct Report Investigation."
            )

        else:

            st.warning(
                "No reports matched the selected filters."
            )

    st.divider()

    st.subheader(
        "Direct Report Investigation"
    )

    selected_default_report = st.session_state.get(
        "explorer_selected_report_id",
        ""
    )

    report_search_id = st.text_input(
        "Enter MAUDE Report ID",
        value=selected_default_report,
        placeholder="Example: 23905663",
        key="report_explorer_id"
    )

    if report_search_id.strip():

        explorer_report = collection.find_one(
            {
                "report_id":
                str(report_search_id.strip())
            },
            {
                "_id": 0,
                "report_id": 1,
                "device": 1,
                "report": 1,
                "safety_intelligence": 1,
                "evidence": 1,
                "review": 1,
                "safety_notice": 1
            }
        )

        if explorer_report:

            report_info = explorer_report.get(
                "report", {}
            )

            device_info = explorer_report.get(
                "device", {}
            )

            safety_info = explorer_report.get(
                "safety_intelligence", {}
            )

            evidence_info = explorer_report.get(
                "evidence", {}
            )

            review_info = explorer_report.get(
                "review", {}
            )

            # ---------------------------------------------
            # Report Summary
            # ---------------------------------------------

            st.subheader("Report Summary")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Report ID",
                explorer_report.get(
                    "report_id", "Not available"
                )
            )

            c2.metric(
                "Date Received",
                report_info.get(
                    "date_received", "Not available"
                )
            )

            c3.metric(
                "Narratives",
                report_info.get(
                    "narrative_count", 0
                )
            )

            c4.metric(
                "Word Count",
                report_info.get(
                    "word_count", 0
                )
            )

            # ---------------------------------------------
            # Device Information
            # ---------------------------------------------

            st.subheader("Device Information")

            d1, d2 = st.columns(2)

            with d1:

                st.markdown(
                    f"**Brand:** "
                    f"{device_info.get('brand_name') or 'Not available'}"
                )

                st.markdown(
                    f"**Generic Device Name:** "
                    f"{device_info.get('generic_name') or 'Not available'}"
                )

                st.markdown(
                    f"**Manufacturer:** "
                    f"{device_info.get('manufacturer') or 'Not available'}"
                )

            with d2:

                st.markdown(
                    f"**Model Number:** "
                    f"{device_info.get('model_number') or 'Not available'}"
                )

                st.markdown(
                    f"**Product Code:** "
                    f"{device_info.get('product_code') or 'Not available'}"
                )

                st.markdown(
                    f"**Unique Narratives:** "
                    f"{report_info.get('unique_narrative_count', 'Not available')}"
                )

            # ---------------------------------------------
            # Safety Pattern Context
            # ---------------------------------------------

            st.subheader(
                "Safety Pattern Context"
            )

            pattern_status = safety_info.get(
                "pattern_status"
            )

            cluster_theme = safety_info.get(
                "cluster_theme"
            )

            alignment_status = safety_info.get(
                "theme_alignment_status"
            )

            similarity_percentile = safety_info.get(
                "theme_similarity_percentile"
            )

            unusual_flag = safety_info.get(
                "unusual_flag", False
            )

            if unusual_flag:

                st.warning(
                    "This report was not assigned to a recurring "
                    "narrative pattern and has been prioritized "
                    "for analyst review."
                )

                st.markdown(
                    "**Pattern Context:** "
                    "Unclassified / requires review"
                )

            else:

                st.markdown(
                    f"**Recurring Narrative Pattern:** "
                    f"{cluster_theme or 'Not available'}"
                )

                st.markdown(
                    f"**Pattern Status:** "
                    f"{pattern_status or 'Not available'}"
                )

                st.markdown(
                    f"**Alignment:** "
                    f"{alignment_status or 'Not available'}"
                )

                if similarity_percentile is not None:

                    percentile_value = float(
                        similarity_percentile
                    )

                    if percentile_value >= 0.5:
                        top_share = (
                            1 - percentile_value
                        ) * 100

                        similarity_text = (
                            f"Top {top_share:.1f}% "
                            f"within this recurring pattern"
                        )

                    else:
                        bottom_share = (
                            percentile_value * 100
                        )

                        similarity_text = (
                            f"Bottom {bottom_share:.1f}% "
                            f"within this recurring pattern"
                        )

                    st.markdown(
                        "**Similarity Rank Within Pattern:** "
                        + similarity_text
                    )

            st.caption(
                "The recurring pattern is analytical context derived "
                "from similarities across report narratives. It is not "
                "a confirmed diagnosis, causal determination, severity "
                "assessment, or clinical validation of this report."
            )

            # ---------------------------------------------
            # Original Evidence
            # ---------------------------------------------

            st.subheader(
                "Original MAUDE Narrative"
            )

            original_narrative = evidence_info.get(
                "original_narrative"
            )

            if original_narrative:

                st.text_area(
                    "Original report evidence",
                    value=original_narrative,
                    height=260,
                    disabled=True,
                    key=(
                        "explorer_narrative_"
                        + str(
                            explorer_report.get(
                                "report_id"
                            )
                        )
                    )
                )

            else:

                st.info(
                    "Original narrative evidence is "
                    "not available for this report."
                )

            # ---------------------------------------------
            # Human Review
            # ---------------------------------------------

            st.subheader(
                "Human Review Status"
            )

            review_status = (
                review_info.get("review_status")
                or "Not reviewed"
            )

            review_notes = review_info.get(
                "review_notes"
            )

            r1, r2 = st.columns(2)

            r1.metric(
                "Review Status",
                review_status
            )

            r2.metric(
                "Review Priority",
                (
                    "Review Recommended"
                    if (
                        unusual_flag
                        or alignment_status
                        == "Weakly aligned / review recommended"
                    )
                    else "Routine"
                )
            )

            if review_notes:

                st.markdown(
                    f"**Review Notes:** "
                    f"{review_notes}"
                )

            else:

                st.caption(
                    "No analyst review notes have been "
                    "recorded for this report."
                )

            st.info(
                "This interface supports evidence review and "
                "prioritization. Analytical indicators should be "
                "interpreted alongside the original MAUDE narrative "
                "and appropriate professional judgment."
            )

        else:

            st.warning(
                "No report was found with that MAUDE Report ID."
            )

    else:

        st.info(
            "Enter a MAUDE Report ID to begin an "
            "individual report investigation."
        )

elif page == "Unusual Reports":

    st.caption("FDA MAUDE • 2025")
    st.header("Analyst Review Queue")

    st.caption(
        "Prioritized reports that may benefit from additional "
        "analyst review. Two analytical pathways are shown separately."
    )

    # =====================================================
    # Review Queue Counts
    # =====================================================

    unclassified_filter = {
        "safety_intelligence.unusual_flag": True
    }

    weak_filter = {
        "safety_intelligence.theme_alignment_status":
        "Weakly aligned / review recommended"
    }

    unclassified_total = collection.count_documents(
        unclassified_filter
    )

    weak_total = collection.count_documents(
        weak_filter
    )

    review_queue_total = (
        unclassified_total + weak_total
    )

    q1, q2, q3 = st.columns(3)

    q1.metric(
        "Review Recommended",
        f"{review_queue_total:,}"
    )

    q2.metric(
        "Unclassified",
        f"{unclassified_total:,}"
    )

    q3.metric(
        "Weak Alignment",
        f"{weak_total:,}"
    )

    st.info(
        "Review Recommended is an analyst-prioritization category. "
        "It combines reports that were not assigned to a recurring "
        "pattern with reports that were assigned but have comparatively "
        "weak alignment. It does not indicate device risk, severity, "
        "causation, or report validity."
    )

    # =====================================================
    # Queue Selection
    # =====================================================

    st.subheader(
        "Analyst Review Queue"
    )

    queue_type = st.radio(
        "Review pathway",
        [
            "Unclassified Reports",
            "Weak-Alignment Reports"
        ],
        horizontal=True,
        key="unusual_queue_type"
    )

    if queue_type == "Unclassified Reports":

        st.markdown(
            "### Unclassified Reports"
        )

        st.caption(
            "These reports were not assigned to one of the recurring "
            "narrative patterns identified by the analytical workflow. "
            "They are preserved for human review rather than being "
            "forced into a recurring pattern."
        )

        queue_results = list(
            collection.find(
                unclassified_filter,
                {
                    "_id": 0,
                    "report_id": 1,
                    "report.date_received": 1,
                    "report.word_count": 1,
                    "device.brand_name": 1,
                    "device.generic_name": 1,
                    "device.manufacturer": 1,
                    "device.product_code": 1,
                    "review.review_status": 1
                }
            )
            .sort("report.date_received", -1)
            .limit(100)
        )

        queue_rows = []

        for doc in queue_results:

            report = doc.get(
                "report", {}
            )

            device = doc.get(
                "device", {}
            )

            review = doc.get(
                "review", {}
            )

            queue_rows.append({
                "Report ID":
                doc.get("report_id"),
                "Date":
                report.get("date_received"),
                "Brand":
                device.get("brand_name"),
                "Generic Device":
                device.get("generic_name"),
                "Manufacturer":
                device.get("manufacturer"),
                "Product Code":
                device.get("product_code"),
                "Word Count":
                report.get("word_count"),
                "Review Status":
                review.get("review_status")
            })

        if queue_rows:

            queue_df = pd.DataFrame(
                queue_rows
            )

            st.dataframe(
                queue_df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                f"Showing the 100 most recent reports "
                f"from {unclassified_total:,} unclassified reports."
            )

        else:

            st.info(
                "No unclassified reports are available."
            )

    else:

        st.markdown(
            "### Weak-Alignment Reports"
        )

        st.caption(
            "These reports were assigned to a recurring narrative "
            "pattern but fall toward the lower end of semantic "
            "similarity within that pattern. They are prioritized "
            "for review without assuming the assignment is incorrect."
        )

        queue_results = list(
            collection.find(
                weak_filter,
                {
                    "_id": 0,
                    "report_id": 1,
                    "report.date_received": 1,
                    "device.brand_name": 1,
                    "device.generic_name": 1,
                    "device.manufacturer": 1,
                    "device.product_code": 1,
                    "safety_intelligence.cluster_theme": 1,
                    "safety_intelligence.theme_similarity_percentile": 1,
                    "review.review_status": 1
                }
            )
            .sort(
                "safety_intelligence.theme_similarity_percentile",
                1
            )
            .limit(100)
        )

        queue_rows = []

        for doc in queue_results:

            report = doc.get(
                "report", {}
            )

            device = doc.get(
                "device", {}
            )

            safety = doc.get(
                "safety_intelligence", {}
            )

            review = doc.get(
                "review", {}
            )

            percentile = safety.get(
                "theme_similarity_percentile"
            )

            if percentile is not None:

                bottom_rank = (
                    float(percentile) * 100
                )

                rank_text = (
                    f"Bottom {bottom_rank:.1f}%"
                )

            else:

                rank_text = "Not available"

            queue_rows.append({
                "Report ID":
                doc.get("report_id"),
                "Date":
                report.get("date_received"),
                "Brand":
                device.get("brand_name"),
                "Generic Device":
                device.get("generic_name"),
                "Manufacturer":
                device.get("manufacturer"),
                "Product Code":
                device.get("product_code"),
                "Assigned Pattern":
                safety.get("cluster_theme"),
                "Similarity Rank":
                rank_text,
                "Review Status":
                review.get("review_status")
            })

        if queue_rows:

            queue_df = pd.DataFrame(
                queue_rows
            )

            st.dataframe(
                queue_df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Showing the 100 lowest-alignment reports "
                f"from {weak_total:,} weak-alignment reports."
            )

        else:

            st.info(
                "No weak-alignment reports are available."
            )

    st.caption(
        "Queue position and analytical classification are prioritization "
        "signals only. Original MAUDE evidence should be reviewed before "
        "drawing conclusions about an individual report or device."
    )

    # =====================================================
    # Feature 6.2 — Review Queue Evidence Inspector
    # =====================================================

    st.divider()

    st.subheader(
        "Review Queue Evidence Inspector"
    )

    st.caption(
        "Select a prioritized report to inspect why it entered "
        "the review queue and examine its original MAUDE evidence."
    )

    queue_report_ids = [
        str(doc.get("report_id"))
        for doc in queue_results
        if doc.get("report_id") is not None
    ]

    if queue_report_ids:

        selected_queue_report = st.selectbox(
            "Select a prioritized Report ID",
            queue_report_ids,
            key=(
                "unusual_evidence_report_"
                + queue_type
            )
        )

        selected_queue_doc = collection.find_one(
            {
                "report_id":
                str(selected_queue_report)
            },
            {
                "_id": 0,
                "report_id": 1,
                "device": 1,
                "report": 1,
                "safety_intelligence": 1,
                "evidence": 1,
                "review": 1
            }
        )

        if selected_queue_doc:

            queue_report_info = (
                selected_queue_doc.get(
                    "report", {}
                )
            )

            queue_device_info = (
                selected_queue_doc.get(
                    "device", {}
                )
            )

            queue_safety_info = (
                selected_queue_doc.get(
                    "safety_intelligence", {}
                )
            )

            queue_evidence_info = (
                selected_queue_doc.get(
                    "evidence", {}
                )
            )

            queue_review_info = (
                selected_queue_doc.get(
                    "review", {}
                )
            )

            # ---------------------------------------------
            # Report Summary
            # ---------------------------------------------

            e1, e2, e3, e4 = st.columns(4)

            e1.metric(
                "Report ID",
                selected_queue_doc.get(
                    "report_id",
                    "Not available"
                )
            )

            e2.metric(
                "Date Received",
                queue_report_info.get(
                    "date_received",
                    "Not available"
                )
            )

            e3.metric(
                "Narratives",
                queue_report_info.get(
                    "narrative_count",
                    0
                )
            )

            e4.metric(
                "Word Count",
                queue_report_info.get(
                    "word_count",
                    0
                )
            )

            # ---------------------------------------------
            # Why Prioritized
            # ---------------------------------------------

            st.markdown(
                "### Why This Report Was Prioritized"
            )

            queue_unusual = queue_safety_info.get(
                "unusual_flag",
                False
            )

            queue_alignment = queue_safety_info.get(
                "theme_alignment_status"
            )

            queue_pattern = queue_safety_info.get(
                "cluster_theme"
            )

            queue_percentile = queue_safety_info.get(
                "theme_similarity_percentile"
            )

            if queue_unusual:

                st.warning(
                    "Unclassified / requires review"
                )

                st.write(
                    "This report was not assigned to one of "
                    "the recurring narrative patterns identified "
                    "by the analytical workflow. It was preserved "
                    "for analyst review rather than being forced "
                    "into a recurring pattern."
                )

            elif (
                queue_alignment
                ==
                "Weakly aligned / review recommended"
            ):

                st.warning(
                    "Weak alignment / review recommended"
                )

                st.markdown(
                    "**Assigned Recurring Pattern:** "
                    + str(
                        queue_pattern
                        or "Not available"
                    )
                )

                if queue_percentile is not None:

                    queue_bottom_rank = (
                        float(queue_percentile)
                        * 100
                    )

                    if queue_bottom_rank < 0.1:
                        queue_rank_text = "Bottom <0.1%"
                    else:
                        queue_rank_text = (
                            f"Bottom {queue_bottom_rank:.1f}%"
                        )

                    st.markdown(
                        "**Similarity Rank Within Pattern:** "
                        + queue_rank_text
                    )

                st.write(
                    "The report was assigned to the recurring "
                    "pattern above, but its narrative has "
                    "comparatively weak semantic alignment "
                    "within that pattern. This is a review "
                    "priority signal, not proof that the "
                    "assignment is incorrect."
                )

            # ---------------------------------------------
            # Device Information
            # ---------------------------------------------

            st.markdown(
                "### Device Information"
            )

            di1, di2 = st.columns(2)

            with di1:

                st.markdown(
                    "**Brand:** "
                    + str(
                        queue_device_info.get(
                            "brand_name"
                        )
                        or "Not available"
                    )
                )

                st.markdown(
                    "**Generic Device Name:** "
                    + str(
                        queue_device_info.get(
                            "generic_name"
                        )
                        or "Not available"
                    )
                )

                st.markdown(
                    "**Manufacturer:** "
                    + str(
                        queue_device_info.get(
                            "manufacturer"
                        )
                        or "Not available"
                    )
                )

            with di2:

                st.markdown(
                    "**Model Number:** "
                    + str(
                        queue_device_info.get(
                            "model_number"
                        )
                        or "Not available"
                    )
                )

                st.markdown(
                    "**Product Code:** "
                    + str(
                        queue_device_info.get(
                            "product_code"
                        )
                        or "Not available"
                    )
                )

                st.markdown(
                    "**Human Review Status:** "
                    + str(
                        queue_review_info.get(
                            "review_status"
                        )
                        or "Not reviewed"
                    )
                )

            # ---------------------------------------------
            # Original Evidence
            # ---------------------------------------------

            st.markdown(
                "### Original MAUDE Narrative"
            )

            queue_original_narrative = (
                queue_evidence_info.get(
                    "original_narrative"
                )
            )

            if queue_original_narrative:

                st.text_area(
                    "Original report evidence",
                    value=queue_original_narrative,
                    height=280,
                    disabled=True,
                    key=(
                        "unusual_narrative_"
                        + str(
                            selected_queue_report
                        )
                        + "_"
                        + queue_type
                    )
                )

            else:

                st.info(
                    "Original narrative evidence is "
                    "not available for this report."
                )

            st.caption(
                "Review prioritization identifies reports that "
                "may benefit from additional inspection. It does "
                "not establish that a report is erroneous, clinically "
                "unusual, severe, device-caused, or evidence of "
                "comparative device risk."
            )

        else:

            st.warning(
                "The selected report could not be retrieved."
            )

    else:

        st.info(
            "No reports are available in this review queue."
        )



elif page == "About":

    st.header(
        "About MAUDE Safety Intelligence"
    )

    st.caption(
        "A research prototype for human-centred exploration "
        "and review prioritization of FDA MAUDE medical-device "
        "adverse-event reports."
    )

    st.subheader(
        "Purpose"
    )

    st.write(
        "MAUDE Safety Intelligence is designed to help analysts "
        "navigate large collections of medical-device adverse-event "
        "narratives while preserving access to the original report "
        "evidence. The system organizes recurring narrative patterns, "
        "supports device- and report-level investigation, and surfaces "
        "reports that may benefit from additional human review."
    )

    st.subheader(
        "Analyst Workflow"
    )

    workflow_col1, workflow_col2 = st.columns(2)

    with workflow_col1:

        st.markdown(
            "**Explore reporting activity**<br>"
            "Review overall reporting volume and recurring "
            "narrative patterns.",
            unsafe_allow_html=True
        )

        st.markdown(
            "**Investigate devices**<br>"
            "Search device information and examine reports "
            "associated with matching records.",
            unsafe_allow_html=True
        )

        st.markdown(
            "**Investigate safety patterns**<br>"
            "Explore recurring narrative themes, associated "
            "device profiles, and representative evidence.",
            unsafe_allow_html=True
        )

    with workflow_col2:

        st.markdown(
            "**Examine trends**<br>"
            "Explore monthly reporting patterns without treating "
            "report counts as incidence or comparative risk.",
            unsafe_allow_html=True
        )

        st.markdown(
            "**Review original evidence**<br>"
            "Move from analytical summaries back to the original "
            "MAUDE narrative for individual report inspection.",
            unsafe_allow_html=True
        )

        st.markdown(
            "**Prioritize additional review**<br>"
            "Surface unclassified and weakly aligned reports "
            "without forcing uncertain records into a pattern.",
            unsafe_allow_html=True
        )

    st.subheader(
        "Review Prioritization"
    )

    st.write(
        "The Review Recommended category combines two analytical "
        "pathways: reports that were not assigned to a recurring "
        "narrative pattern, and reports that were assigned to a "
        "pattern but show comparatively weak alignment within it. "
        "These indicators are intended to guide analyst attention, "
        "not to determine whether a report is clinically unusual, "
        "incorrect, severe, or device-caused."
    )

    st.subheader(
        "Data Scope"
    )

    scope1, scope2, scope3 = st.columns(3)

    scope1.metric(
        "Dataset",
        "FDA MAUDE"
    )

    scope2.metric(
        "Analysis Period",
        "2025"
    )

    scope3.metric(
        "Reports",
        "94,872"
    )

    st.write(
        "The prototype uses medical-device information and free-text "
        "adverse-event narratives from the 2025 FDA MAUDE data used "
        "in this research workflow."
    )

    st.subheader(
        "Responsible Interpretation"
    )

    st.warning(
        "MAUDE is a passive adverse-event reporting system. "
        "The presence, frequency, or analytical grouping of reports "
        "in this prototype should not be interpreted as proof of "
        "causation, incidence, device safety, clinical severity, "
        "or comparative risk."
    )

    st.write(
        "Recurring patterns and review-prioritization indicators are "
        "analytical aids. Conclusions about individual reports or "
        "medical devices require examination of the underlying "
        "evidence and appropriate professional judgment."
    )

    st.subheader(
        "Research Status"
    )

    st.info(
        "This system is a research prototype intended for analytical "
        "exploration and human-centred review support. It is not a "
        "clinical decision-support system, regulatory determination, "
        "or substitute for professional safety assessment."
    )

st.divider()

st.caption(
    "Safety notice: MAUDE reports are safety signals and should not be "
    "interpreted as proof of device causation, incidence, or comparative risk."
)
