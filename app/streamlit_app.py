import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Digital Payments Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CHART FORMATTING
# ============================================================

def polish_chart(fig, height=420):

    fig.update_layout(
        height=height,
        margin=dict(
            l=10,
            r=10,
            t=55,
            b=10
        ),
        title=dict(
            x=0,
            xanchor="left"
        ),
        hoverlabel=dict(
            namelength=-1
        ),
        legend=dict(
            title=""
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        gridcolor="rgba(0,0,0,0.08)"
    )

    return fig


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_parquet(
        "data/processed_transactions.parquet"
    )


try:
    df = load_data()

except Exception as e:
    st.error("Could not load the processed dataset.")
    st.code("data/processed_transactions.parquet")
    st.exception(e)
    st.stop()


# ============================================================
# DATA TYPES
# ============================================================

numeric_columns = [
    "amount_usd",
    "hours_since_last_txn",
    "txn_count_last_24h",
    "distance_from_home_km",
    "card_age_months",
    "customer_age",
    "account_balance_usd",
    "cvv_retry_count",
    "velocity_score",
    "merchant_risk_score",
    "prior_disputes",
    "amount_vs_global_avg",
    "amount_to_balance_ratio",
    "composite_risk_flags",
    "anomaly_score",
    "risk_signal",
    "is_fraud",
    "anomaly_flag",
    "behavior_segment"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Payment Intelligence")

st.sidebar.caption(
    "Filter the transaction population used throughout "
    "the dashboard."
)

st.sidebar.divider()

st.sidebar.subheader("Transaction Filters")


# Merchant Category

merchant_options = sorted(
    df["merchant_category"]
    .dropna()
    .unique()
    .tolist()
)

selected_merchants = st.sidebar.multiselect(
    "Merchant Category",
    options=merchant_options,
    default=merchant_options
)


# Channel

channel_options = sorted(
    df["channel"]
    .dropna()
    .unique()
    .tolist()
)

selected_channels = st.sidebar.multiselect(
    "Channel",
    options=channel_options,
    default=channel_options
)


# Authentication

auth_options = sorted(
    df["auth_method"]
    .dropna()
    .unique()
    .tolist()
)

selected_auth = st.sidebar.multiselect(
    "Authentication Method",
    options=auth_options,
    default=auth_options
)


# Risk level

risk_options = [
    "Low",
    "Moderate",
    "Elevated"
]

selected_risk = st.sidebar.multiselect(
    "Risk Level",
    options=risk_options,
    default=risk_options
)


# Behavior segment

segment_options = sorted(
    df["behavior_segment"]
    .dropna()
    .unique()
    .tolist()
)

selected_segments = st.sidebar.multiselect(
    "Behavior Segment",
    options=segment_options,
    default=segment_options
)


# Dataset label

st.sidebar.divider()

st.sidebar.subheader("Dataset Label")

fraud_filter = st.sidebar.radio(
    "Fraud Label",
    options=[
        "All Transactions",
        "Fraud Only",
        "Non-Fraud Only"
    ]
)


# Model signal

st.sidebar.divider()

st.sidebar.subheader("Model Signal")

anomaly_sidebar_filter = st.sidebar.checkbox(
    "Model-flagged anomalies only",
    value=False
)


# ============================================================
# APPLY SIDEBAR FILTERS
# ============================================================

filtered = df[
    df["merchant_category"].isin(selected_merchants)
    & df["channel"].isin(selected_channels)
    & df["auth_method"].isin(selected_auth)
    & df["risk_level"].isin(selected_risk)
    & df["behavior_segment"].isin(selected_segments)
].copy()


if fraud_filter == "Fraud Only":

    filtered = filtered[
        filtered["is_fraud"] == 1
    ]


elif fraud_filter == "Non-Fraud Only":

    filtered = filtered[
        filtered["is_fraud"] == 0
    ]


if anomaly_sidebar_filter:

    filtered = filtered[
        filtered["anomaly_flag"] == 1
    ]


if filtered.empty:

    st.warning(
        "No transactions match the selected filters. "
        "Try broadening your selections."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.caption("ANALYTICS PLATFORM")

st.title("Digital Payments Intelligence")

st.write(
    "Transaction behavior, risk signals, and anomaly monitoring "
    "across digital payment activity."
)

st.divider()


# ============================================================
# PRIMARY KPIs
# ============================================================

st.subheader("Overview Metrics")

st.caption(
    "A snapshot of the currently selected transaction population."
)

total_volume = filtered["amount_usd"].sum()

transaction_count = len(filtered)

average_transaction = filtered["amount_usd"].mean()

fraud_rate = (
    filtered["is_fraud"].mean() * 100
)


kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.metric(
        "Transaction Volume",
        f"${total_volume:,.0f}"
    )


with kpi2:

    st.metric(
        "Transactions",
        f"{transaction_count:,}"
    )


with kpi3:

    st.metric(
        "Average Transaction Value",
        f"${average_transaction:,.2f}"
    )


with kpi4:

    st.metric(
        "Labeled Fraud Rate",
        f"{fraud_rate:.2f}%"
    )


st.write("")


# ============================================================
# MONITORING SNAPSHOT
# ============================================================

st.subheader("Monitoring Snapshot")

st.caption(
    "Analytical signals within the currently selected "
    "transaction population."
)


elevated_count = (
    filtered["risk_level"] == "Elevated"
).sum()


multi_flag_count = (
    filtered["composite_risk_flags"] >= 2
).sum()


anomaly_count = (
    filtered["anomaly_flag"] == 1
).sum()


monitor1, monitor2, monitor3 = st.columns(3)


with monitor1:

    st.metric(
        "Elevated Risk",
        f"{elevated_count:,}"
    )

    st.caption(
        "Transactions classified as Elevated risk"
    )


with monitor2:

    st.metric(
        "Multiple Risk Indicators",
        f"{multi_flag_count:,}"
    )

    st.caption(
        "Transactions with 2 or more indicators"
    )


with monitor3:

    st.metric(
        "Model-Flagged Anomalies",
        f"{anomaly_count:,}"
    )

    st.caption(
        "Transactions flagged by Isolation Forest"
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Overview",
        "Behavior",
        "Risk Monitoring",
        "Transactions"
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tab1:

    st.header("Overview")

    st.caption(
        "A high-level view of transaction activity across "
        "categories, channels, and time of day."
    )


    # --------------------------------------------------------
    # Merchant + Channel
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        merchant_summary = (
            filtered
            .groupby("merchant_category")
            .agg(
                transaction_volume=(
                    "amount_usd",
                    "sum"
                ),
                transactions=(
                    "transaction_id",
                    "count"
                )
            )
            .sort_values(
                "transaction_volume",
                ascending=True
            )
            .reset_index()
        )


        fig_merchant = px.bar(
            merchant_summary,
            x="transaction_volume",
            y="merchant_category",
            orientation="h",
            title="Transaction Volume by Merchant Category",
            labels={
                "transaction_volume":
                    "Transaction Volume (USD)",
                "merchant_category":
                    ""
            },
            hover_data=[
                "transactions"
            ]
        )


        fig_merchant = polish_chart(
            fig_merchant,
            height=500
        )


        st.plotly_chart(
            fig_merchant,
            use_container_width=True
        )


    with col2:

        channel_summary = (
            filtered
            .groupby("channel")
            .size()
            .reset_index(
                name="transactions"
            )
            .sort_values(
                "transactions",
                ascending=True
            )
        )


        fig_channel = px.bar(
            channel_summary,
            x="transactions",
            y="channel",
            orientation="h",
            title="Transaction Count by Channel",
            labels={
                "transactions":
                    "Transactions",
                "channel":
                    ""
            }
        )


        fig_channel = polish_chart(
            fig_channel,
            height=500
        )


        st.plotly_chart(
            fig_channel,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Time of day
    # --------------------------------------------------------

    st.subheader("Transaction Activity")

    st.caption(
        "Transaction count across four time-of-day periods."
    )


    if "time_of_day_period" in filtered.columns:

        period_order = [
            "Morning",
            "Afternoon",
            "Evening",
            "Night"
        ]


        time_summary = (
            filtered
            .groupby("time_of_day_period")
            .agg(
                transactions=(
                    "transaction_id",
                    "count"
                ),
                transaction_volume=(
                    "amount_usd",
                    "sum"
                )
            )
            .reset_index()
        )


        time_summary[
            "time_of_day_period"
        ] = pd.Categorical(
            time_summary[
                "time_of_day_period"
            ],
            categories=period_order,
            ordered=True
        )


        time_summary = time_summary.sort_values(
            "time_of_day_period"
        )


        fig_time = px.bar(
            time_summary,
            x="time_of_day_period",
            y="transactions",
            title="Transaction Activity by Time of Day",
            labels={
                "time_of_day_period":
                    "Time of Day",
                "transactions":
                    "Transactions"
            },
            hover_data=[
                "transaction_volume"
            ]
        )


        fig_time = polish_chart(
            fig_time,
            height=400
        )


        st.plotly_chart(
            fig_time,
            use_container_width=True
        )


# ============================================================
# TAB 2 — BEHAVIOR
# ============================================================

with tab2:

    st.header("Behavior")

    st.caption(
        "Unsupervised KMeans segmentation based on transaction "
        "and behavioral features."
    )


    # --------------------------------------------------------
    # BEHAVIOR SEGMENTS
    # --------------------------------------------------------

    st.markdown("### Behavior Segments")

    st.caption(
        "Transaction groups identified by the KMeans clustering model."
    )

    st.write("")


    segment_summary = (
        filtered
        .groupby("behavior_segment")
        .agg(
            transactions=(
                "transaction_id",
                "count"
            ),
            transaction_volume=(
                "amount_usd",
                "sum"
            ),
            avg_transaction=(
                "amount_usd",
                "mean"
            ),
            avg_velocity=(
                "velocity_score",
                "mean"
            ),
            avg_distance=(
                "distance_from_home_km",
                "mean"
            ),
            avg_merchant_risk=(
                "merchant_risk_score",
                "mean"
            ),
            fraud_count=(
                "is_fraud",
                "sum"
            )
        )
        .reset_index()
    )


    segment_summary["fraud_rate"] = (
        segment_summary["fraud_count"]
        / segment_summary["transactions"]
        * 100
    )


    # --------------------------------------------------------
    # SEGMENT CARDS
    # --------------------------------------------------------

    segment_columns = st.columns(
        len(segment_summary)
    )


    for column, (_, row) in zip(
        segment_columns,
        segment_summary.iterrows()
    ):

        segment_id = int(
            row["behavior_segment"]
        )


        with column:

            st.markdown(
                f"#### Segment {segment_id}"
            )


            st.metric(
                "Transactions",
                f"{int(row['transactions']):,}"
            )


            st.write(
                f"**Transaction value:** "
                f"${row['avg_transaction']:,.2f}"
            )

            st.write(
                f"**Velocity:** "
                f"{row['avg_velocity']:.1f}"
            )

            st.write(
                f"**Distance from home:** "
                f"{row['avg_distance']:.1f} km"
            )

            st.write(
                f"**Merchant risk:** "
                f"{row['avg_merchant_risk']:.1f}"
            )


            if row["avg_transaction"] >= 500:

                st.caption(
                    "High-value transaction pattern"
                )

            elif row["avg_velocity"] >= 20:

                st.caption(
                    "Higher-velocity transaction pattern"
                )

            else:

                st.caption(
                    "Lower-velocity transaction pattern"
                )


    st.divider()


    # --------------------------------------------------------
    # SEGMENT COMPARISON
    # --------------------------------------------------------

    st.subheader("Segment Comparison")

    st.caption(
        "Comparing transaction volume and average transaction value "
        "across the behavioral segments."
    )


    col1, col2 = st.columns(2)


    with col1:

        fig_segment_volume = px.bar(
            segment_summary,
            x="behavior_segment",
            y="transaction_volume",
            title="Transaction Volume by Segment",
            labels={
                "behavior_segment":
                    "Behavior Segment",
                "transaction_volume":
                    "Transaction Volume (USD)"
            }
        )


        fig_segment_volume = polish_chart(
            fig_segment_volume,
            height=430
        )


        fig_segment_volume.update_layout(
            xaxis=dict(
                type="category"
            )
        )


        st.plotly_chart(
            fig_segment_volume,
            use_container_width=True
        )


    with col2:

        fig_segment_value = px.bar(
            segment_summary,
            x="behavior_segment",
            y="avg_transaction",
            title="Average Transaction Value by Segment",
            labels={
                "behavior_segment":
                    "Behavior Segment",
                "avg_transaction":
                    "Average Transaction (USD)"
            }
        )


        fig_segment_value = polish_chart(
            fig_segment_value,
            height=430
        )


        fig_segment_value.update_layout(
            xaxis=dict(
                type="category"
            )
        )


        st.plotly_chart(
            fig_segment_value,
            use_container_width=True
        )


    # --------------------------------------------------------
    # BEHAVIORAL DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("Transaction Behavior")

    st.caption(
        "Relationship between transaction value and transaction velocity."
    )


    scatter_sample = filtered.copy()


    if len(scatter_sample) > 5000:

        scatter_sample = scatter_sample.sample(
            5000,
            random_state=42
        )


    fig_scatter = px.scatter(
        scatter_sample,
        x="velocity_score",
        y="amount_usd",
        size="merchant_risk_score",
        hover_data=[
            "merchant_category",
            "channel",
            "behavior_segment",
            "risk_level"
        ],
        title="Transaction Value vs. Velocity",
        labels={
            "velocity_score":
                "Velocity Score",
            "amount_usd":
                "Transaction Amount (USD)",
            "merchant_risk_score":
                "Merchant Risk Score"
        }
    )


    fig_scatter = polish_chart(
        fig_scatter,
        height=500
    )


    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


    st.info(
        "Behavior segments are unsupervised transaction clusters. "
        "They do not represent customer segments because the dataset "
        "does not contain a customer_id field."
    )


# ============================================================
# TAB 3 — RISK MONITORING
# ============================================================

with tab3:

    st.header("Risk Monitoring")

    st.caption(
        "Review manually defined risk indicators alongside "
        "unsupervised anomaly signals."
    )


    # --------------------------------------------------------
    # RISK SUMMARY
    # --------------------------------------------------------

    risk_summary = (
        filtered
        .groupby("risk_level")
        .agg(
            transactions=(
                "transaction_id",
                "count"
            ),
            fraud_count=(
                "is_fraud",
                "sum"
            ),
            avg_anomaly_score=(
                "anomaly_score",
                "mean"
            )
        )
        .reset_index()
    )


    risk_summary["fraud_rate"] = (
        risk_summary["fraud_count"]
        / risk_summary["transactions"]
        * 100
    )


    risk_order = [
        "Low",
        "Moderate",
        "Elevated"
    ]


    risk_summary["risk_level"] = pd.Categorical(
        risk_summary["risk_level"],
        categories=risk_order,
        ordered=True
    )


    risk_summary = risk_summary.sort_values(
        "risk_level"
    )


    # --------------------------------------------------------
    # RISK KPIs
    # --------------------------------------------------------

    risk1, risk2, risk3 = st.columns(3)


    with risk1:

        st.metric(
            "Elevated Risk",
            f"{elevated_count:,}"
        )

        st.caption(
            "Transactions classified as Elevated"
        )


    with risk2:

        st.metric(
            "2+ Risk Indicators",
            f"{multi_flag_count:,}"
        )

        st.caption(
            "Transactions with multiple indicators"
        )


    with risk3:

        st.metric(
            "Model Anomalies",
            f"{anomaly_count:,}"
        )

        st.caption(
            "Flagged by Isolation Forest"
        )


    st.divider()


    # --------------------------------------------------------
    # RISK LEVEL CHARTS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig_risk = px.bar(
            risk_summary,
            x="risk_level",
            y="transactions",
            title="Transactions by Risk Level",
            labels={
                "risk_level":
                    "Risk Level",
                "transactions":
                    "Transactions"
            }
        )


        fig_risk = polish_chart(
            fig_risk,
            height=420
        )


        st.plotly_chart(
            fig_risk,
            use_container_width=True
        )


    with col2:

        fig_risk_fraud = px.bar(
            risk_summary,
            x="risk_level",
            y="fraud_rate",
            title="Labeled Fraud Rate by Risk Level",
            labels={
                "risk_level":
                    "Risk Level",
                "fraud_rate":
                    "Labeled Fraud Rate (%)"
            }
        )


        fig_risk_fraud = polish_chart(
            fig_risk_fraud,
            height=420
        )


        st.plotly_chart(
            fig_risk_fraud,
            use_container_width=True
        )


    # --------------------------------------------------------
    # RISK INDICATORS
    # --------------------------------------------------------

    st.subheader("Risk Indicators")

    st.caption(
        "Number of manually defined indicators present on each transaction."
    )


    flag_summary = (
        filtered["composite_risk_flags"]
        .value_counts()
        .sort_index()
        .reset_index()
    )


    flag_summary.columns = [
        "risk_flags",
        "transactions"
    ]


    fig_flags = px.bar(
        flag_summary,
        x="risk_flags",
        y="transactions",
        title="Distribution of Risk Indicators",
        labels={
            "risk_flags":
                "Number of Indicators",
            "transactions":
                "Transactions"
        }
    )


    fig_flags = polish_chart(
        fig_flags,
        height=400
    )


    st.plotly_chart(
        fig_flags,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ANOMALY DETECTION
    # --------------------------------------------------------

    st.subheader("Anomaly Detection")

    st.caption(
        "Isolation Forest identifies transactions with behavioral "
        "patterns that differ from the broader dataset."
    )


    fig_anomaly = px.histogram(
        filtered,
        x="anomaly_score",
        nbins=40,
        title="Distribution of Anomaly Scores",
        labels={
            "anomaly_score":
                "Anomaly Score"
        }
    )


    fig_anomaly = polish_chart(
        fig_anomaly,
        height=420
    )


    st.plotly_chart(
        fig_anomaly,
        use_container_width=True
    )


    st.info(
        "The Isolation Forest model was configured with a 5% "
        "contamination parameter during development. Therefore, "
        "approximately 5% of the full dataset is expected to be "
        "flagged as anomalous. This should not be interpreted as "
        "a discovered fraud or anomaly rate."
    )


    # --------------------------------------------------------
    # INVESTIGATION QUEUE
    # --------------------------------------------------------

    st.subheader("Investigation Queue")

    st.caption(
        "Transactions with multiple manually defined risk indicators, "
        "sorted by signal count and anomaly score. These are investigation "
        "signals, not confirmed fraud decisions."
    )


    high_signal = (
        filtered[
            filtered["composite_risk_flags"] >= 2
        ]
        .sort_values(
            [
                "composite_risk_flags",
                "anomaly_flag",
                "anomaly_score"
            ],
            ascending=[
                False,
                False,
                False
            ]
        )
        .head(50)
    )


    display_columns = [
        "transaction_id",
        "amount_usd",
        "merchant_category",
        "channel",
        "auth_method",
        "composite_risk_flags",
        "anomaly_flag",
        "anomaly_score",
        "risk_level",
        "is_fraud"
    ]


    available_columns = [
        column
        for column in display_columns
        if column in high_signal.columns
    ]


    st.dataframe(
        high_signal[
            available_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4 — TRANSACTIONS
# ============================================================

with tab4:

    st.header("Transactions")

    st.caption(
        "Inspect individual transactions and their behavioral "
        "and risk signals."
    )


    st.subheader("Explore Transactions")


    col1, col2 = st.columns(2)


    # Amount filter

    with col1:

        amount_min = float(
            filtered["amount_usd"].min()
        )

        amount_max = float(
            filtered["amount_usd"].max()
        )


        selected_amount = st.slider(
            "Transaction Amount",
            min_value=amount_min,
            max_value=amount_max,
            value=(
                amount_min,
                amount_max
            )
        )


    # Risk indicator filter

    with col2:

        max_flags = int(
            filtered["composite_risk_flags"].max()
        )


        min_flags = st.number_input(
            "Minimum Risk Indicators",
            min_value=0,
            max_value=max_flags,
            value=0,
            step=1
        )


    # Apply explorer filters

    explorer = filtered[
        (filtered["amount_usd"] >= selected_amount[0])
        & (filtered["amount_usd"] <= selected_amount[1])
        & (
            filtered["composite_risk_flags"]
            >= min_flags
        )
    ].copy()


    explorer_columns = [
        "transaction_id",
        "amount_usd",
        "merchant_category",
        "card_type",
        "auth_method",
        "channel",
        "device_type",
        "is_foreign_transaction",
        "hours_since_last_txn",
        "txn_count_last_24h",
        "distance_from_home_km",
        "customer_age",
        "account_balance_usd",
        "is_new_merchant",
        "used_vpn",
        "ip_country_mismatch",
        "billing_shipping_mismatch",
        "cvv_retry_count",
        "velocity_score",
        "time_of_day_hour",
        "day_of_week",
        "is_ai_generated_scam_attempt",
        "merchant_risk_score",
        "prior_disputes",
        "behavior_segment",
        "composite_risk_flags",
        "anomaly_flag",
        "anomaly_score",
        "risk_level",
        "is_fraud"
    ]


    available_explorer_columns = [
        column
        for column in explorer_columns
        if column in explorer.columns
    ]


    st.write(
        f"Showing **{len(explorer):,}** transactions"
    )


    st.dataframe(
        explorer[
            available_explorer_columns
        ].head(500),
        use_container_width=True,
        hide_index=True
    )


    # Download

    csv_data = (
        explorer[
            available_explorer_columns
        ]
        .to_csv(index=False)
        .encode("utf-8")
    )


    st.download_button(
        label="Download Filtered Transactions",
        data=csv_data,
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )


# ============================================================
# METHODOLOGY
# ============================================================

st.divider()

st.subheader("Methodology & Definitions")


method1, method2, method3 = st.columns(3)


with method1:

    st.markdown("**Risk indicators**")

    st.write(
        "Four manually defined signals are counted: "
        "VPN usage, IP-country mismatch, billing/shipping "
        "mismatch, and AI-generated scam-attempt flags."
    )


with method2:

    st.markdown("**Anomaly detection**")

    st.write(
        "Isolation Forest identifies transactions with "
        "unusual behavioral patterns relative to the dataset."
    )


with method3:

    st.markdown("**Behavior segmentation**")

    st.write(
        "KMeans groups transactions based on selected "
        "behavioral and transaction characteristics. "
        "The dataset does not contain a customer ID."
    )


st.caption(
    "Labeled fraud rate uses the dataset's is_fraud field. "
    "Risk indicators and anomaly flags are analytical signals "
    "and should not be interpreted as confirmed fraud decisions."
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Digital Payments & Behavioral Intelligence Platform "
    "· Python · SQL · DuckDB · scikit-learn · Plotly · Streamlit"
)