import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import plotly.graph_objects as go

from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# ---------------------------------------------------
# STREAMLIT PAGE SETUP
# ---------------------------------------------------

st.set_page_config(layout="wide")

st.title("Geochemical Interpretation Tool")


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("Upload Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

st.sidebar.header("Plot Settings")

field_name = st.sidebar.text_input(
    "Field Name",
    value="Field_A"
)

well_number = st.sidebar.text_input(
    "Well Number",
    value="001"
)


# ---------------------------------------------------
# DATA PROCESSING FUNCTIONS
# ---------------------------------------------------

def convert_to_numeric(df, cols):

    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def calculate_ratios(df):

    df["Ca/Mg"] = df["Ca"] / df["Mg"]
    df["Ti/Mn"] = df["Ti"] / df["Mn"]
    df["Fe/Mn"] = df["Fe"] / df["Mn"]
    df["Sr/Ba"] = df["Sr"] / df["Ba"]
    df["Na/K"] = df["Na"] / df["K"]
    df["V/Cr"] = df["V"] / df["Cr"]

    df["Na+K/Ca+Mg"] = (
        (df["Na"] + df["K"]) /
        (df["Ca"] + df["Mg"])
    )

    return df


# ---------------------------------------------------
# CLASSIFICATION FUNCTIONS
# ---------------------------------------------------

def classify_redox(v_cr, fe_mn):

    if pd.isna(v_cr) and pd.isna(fe_mn):
        return "Unknown"

    if (
        (not pd.isna(v_cr) and v_cr > 4.25)
        or
        (not pd.isna(fe_mn) and fe_mn > 100)
    ):
        return "Anoxic"

    elif (
        (not pd.isna(v_cr) and 2 <= v_cr <= 4.25)
        or
        (not pd.isna(fe_mn) and 50 <= fe_mn <= 100)
    ):
        return "Dysoxic"

    else:
        return "Oxic"


def classify_salinity(sr_ba):

    if sr_ba > 1:
        return "Marine–high salinity"

    elif 0.5 <= sr_ba <= 1:
        return "Brackish"

    else:
        return "Freshwater / restricted"


def classify_weathering(na_k):

    if na_k > 1:
        return "Weak weathering"

    elif 0.5 <= na_k <= 1:
        return "Moderate weathering"

    else:
        return "Intense weathering"


def classify_sediment(ca_mg, nak_camg):

    if nak_camg > 0.5:
        return "Siliciclastic"

    if ca_mg > 5:
        return "Limestone"

    elif 1 <= ca_mg <= 5:
        return "Dolomitic limestone"

    else:
        return "Dolostone"


def classify_ti_mn(ti_mn):

    if ti_mn >= 110:
        return "Continental (alluvial)"

    elif 20 <= ti_mn < 110:
        return "Nearshore, high detrital input"

    elif 7 <= ti_mn < 20:
        return "Shallow marine, variable salinity"

    else:
        return "Open marine / distal"


def apply_classifications(df):

    df["Redox"] = df.apply(
        lambda r: classify_redox(
            r["V/Cr"],
            r["Fe/Mn"]
        ),
        axis=1
    )

    df["Salinity"] = df["Sr/Ba"].apply(
        classify_salinity
    )

    df["Weathering"] = df["Na/K"].apply(
        classify_weathering
    )

    df["Sediment"] = df.apply(
        lambda r: classify_sediment(
            r["Ca/Mg"],
            r["Na+K/Ca+Mg"]
        ),
        axis=1
    )

    df["TiMn_env"] = df["Ti/Mn"].apply(
        classify_ti_mn
    )

    return df


# ---------------------------------------------------
# MATPLOTLIB PLOTTING FUNCTIONS
# ---------------------------------------------------

def plot_ratio_track(ax, x, depth, label):

    ax.plot(
        x,
        depth,
        color="black",
        linewidth=1
    )

    ax.scatter(
        x,
        depth,
        s=10,
        color="black"
    )

    ax.set_ylim(
        depth.max(),
        depth.min()
    )

    ax.grid(
        True,
        linestyle="--",
        alpha=0.4
    )

    ax.xaxis.set_label_position("top")

    ax.set_xlabel(
        label,
        fontsize=14,
        fontweight="bold",
        labelpad=18
    )

    ax.xaxis.tick_top()


def plot_facies_track(
    ax,
    depth,
    facies,
    title,
    colors
):

    for i in range(len(depth) - 1):

        ax.fill_betweenx(
            [depth.iloc[i], depth.iloc[i + 1]],
            0,
            1,
            color=colors.get(
                facies.iloc[i],
                "grey"
            )
        )

    ax.set_ylim(
        depth.max(),
        depth.min()
    )

    ax.set_xticks([])

    ax.set_title(
        title,
        fontsize=14,
        fontweight="bold",
        pad=20
    )

    ax.set_ylabel("Depth")

    legend = [
        Patch(
            facecolor=c,
            edgecolor="k",
            label=l
        )
        for l, c in colors.items()
    ]

    ax.legend(
        handles=legend,
        bbox_to_anchor=(0.5, -0.18),
        loc="lower center",
        fontsize=10,
        frameon=True,
        borderpad=0.6,
        labelspacing=0.4,
        handlelength=1.4,
        handleheight=1.2
    )


# ---------------------------------------------------
# PLOTLY INTERACTIVE PLOT
# ---------------------------------------------------

def plot_ratios_plotly(df, depth, ratios):

    ratio_colors = {
        "V/Cr": "#1f77b4",
        "Fe/Mn": "#aec7e8",
        "Sr/Ba": "#d62728",
        "Na/K": "#f7b6d2",
        "Na+K/Ca+Mg": "#98df8a",
        "Ca/Mg": "#2ca02c",
        "Ti/Mn": "#ff7f0e"
    }

    fig = go.Figure()

    for r in ratios:

        fig.add_trace(
            go.Scatter(
                x=df[r],
                y=depth,
                mode="lines+markers",
                name=r,
                line=dict(
                    color=ratio_colors.get(r, "black"),
                    width=2
                ),
                marker=dict(
                    color=ratio_colors.get(r, "black"),
                    size=6
                ),
                hovertemplate=(
                    f"{r}: %{{x}}"
                    f"<br>Depth: %{{y}}"
                )
            )
        )

    fig.update_yaxes(
        autorange="reversed",
        title_text="Depth"
    )

    fig.update_layout(
        title="Geochemical Ratios",
        xaxis_title="Value",
        yaxis_title="Depth",
        height=600,
        width=1000,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------
# PDF REPORT FUNCTION
# ---------------------------------------------------

def generate_pdf_report(
    fig,
    df,
    depth,
    selected_proxy,
    field_name,
    well_number
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    elements = []

    # TITLE
    title = Paragraph(
        "<b>Geochemical Interpretation Report</b>",
        styles["Title"]
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # FIELD INFO
    field_text = Paragraph(
        f"<b>Field Name:</b> {field_name}<br/>"
        f"<b>Well Number:</b> {well_number}",
        styles["BodyText"]
    )

    elements.append(field_text)
    elements.append(Spacer(1, 10))

    # DEPTH INTERVAL
    depth_text = Paragraph(
        f"<b>Depth Interval:</b> "
        f"{depth.min()} – {depth.max()} m",
        styles["BodyText"] 
    )

    elements.append(depth_text)
    elements.append(Spacer(1, 10))

    # SUMMARY
    dominant_redox = df["Redox"].mode()[0]
    dominant_salinity = df["Salinity"].mode()[0]
    dominant_weathering = df["Weathering"].mode()[0]
    dominant_sediment = df["Sediment"].mode()[0]
    dominant_env = df["TiMn_env"].mode()[0]

    redox_counts = (
        df["Redox"]
        .value_counts(normalize=True) * 100
    )

    redox_text = (
        "<b>Redox Conditions:</b><br/>"
    )

    for k, v in redox_counts.items():

        redox_text += (
            f"{k}: {v:.1f}%<br/>"
        )

    summary = f"""
    <b>Dominant Redox Condition:</b>
    {dominant_redox}<br/><br/>

    {redox_text}<br/>

    <b>Dominant Salinity:</b>
    {dominant_salinity}<br/>

    <b>Weathering Intensity:</b>
    {dominant_weathering}<br/>

    <b>Dominant Sediment Type:</b>
    {dominant_sediment}<br/>

    <b>Depositional Environment:</b>
    {dominant_env}
    """

    elements.append(
        Paragraph(
            summary,
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 20))

    # SAVE FIGURE
    img_buffer = BytesIO()

    fig.savefig(
        img_buffer,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    img_buffer.seek(0)

    report_img = Image(
        img_buffer,
        width=520,
        height=220
    )

    elements.append(report_img)

    # BUILD PDF
    doc.build(elements)

    buffer.seek(0)

    return buffer


# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    elements = [
        "Ca", "Mg", "Ti", "Mn", "Fe",
        "Sr", "Ba", "K", "Na", "V", "Cr"
    ]

    df = convert_to_numeric(
        df,
        elements
    )

    df = calculate_ratios(df)

    df = apply_classifications(df)

    min_depth = int(df["Depth"].min())
    max_depth = int(df["Depth"].max())

    depth_range = st.sidebar.slider(
        "Select Depth Interval",
        min_value=min_depth,
        max_value=max_depth,
        value=(min_depth, max_depth)
    )

    # FILTER BY DEPTH
    df = df[
        (df["Depth"] >= depth_range[0])
        &
        (df["Depth"] <= depth_range[1])
    ]

    depth = df["Depth"]

    # PLOTLY PLOT
    selected_ratios = [
        "V/Cr",
        "Fe/Mn",
        "Sr/Ba",
        "Na/K",
        "Na+K/Ca+Mg",
        "Ca/Mg",
        "Ti/Mn"
    ]

    plot_ratios_plotly(
        df,
        depth,
        selected_ratios
    )

    # MATPLOTLIB PLOT
    fig, axes = plt.subplots(
        1,
        12,
        figsize=(32, 12),
        sharey=True
    )

    plot_ratio_track(
        axes[0],
        df["V/Cr"],
        depth,
        "V/Cr"
    )

    plot_ratio_track(
        axes[1],
        df["Fe/Mn"],
        depth,
        "Fe/Mn"
    )

    plot_ratio_track(
        axes[2],
        df["Sr/Ba"],
        depth,
        "Sr/Ba"
    )

    plot_ratio_track(
        axes[3],
        df["Na/K"],
        depth,
        "Na/K"
    )

    plot_ratio_track(
        axes[4],
        df["Na+K/Ca+Mg"],
        depth,
        "(Na+K)/(Ca+Mg)"
    )

    plot_ratio_track(
        axes[5],
        df["Ca/Mg"],
        depth,
        "Ca/Mg"
    )

    plot_ratio_track(
        axes[6],
        df["Ti/Mn"],
        depth,
        "Ti/Mn"
    )

    plot_facies_track(
        axes[7],
        depth,
        df["Redox"],
        "Redox",
        {
            "Oxic": "skyblue",
            "Dysoxic": "orange",
            "Anoxic": "navy",
            "Unknown": "lightgrey"
        }
    )

    plot_facies_track(
        axes[8],
        depth,
        df["Salinity"],
        "Salinity",
        {
            "Freshwater / restricted": "lightgreen",
            "Brackish": "gold",
            "Marine–high salinity": "darkblue"
        }
    )

    plot_facies_track(
        axes[9],
        depth,
        df["Weathering"],
        "Weathering",
        {
            "Weak weathering": "skyblue",
            "Moderate weathering": "orange",
            "Intense weathering": "red"
        }
    )

    plot_facies_track(
        axes[10],
        depth,
        df["Sediment"],
        "Sediment",
        {
            "Limestone": "gold",
            "Dolomitic limestone": "lightyellow",
            "Dolostone": "khaki",
            "Siliciclastic": "sandybrown"
        }
    )

    plot_facies_track(
        axes[11],
        depth,
        df["TiMn_env"],
        "Depositional Environment",
        {
            "Continental (alluvial)": "darkgreen",
            "Nearshore, high detrital input": "green",
            "Shallow marine, variable salinity": "cyan",
            "Open marine / distal": "blue"
        }
    )

    axes[0].set_ylabel("Depth")

    axes[0].yaxis.set_label_position("left")

    plt.tight_layout(
        rect=[0.03, 0.08, 0.98, 0.95]
    )

    st.pyplot(fig)

    # ---------------------------------------------------
    # PROXY INSPECTOR
    # ---------------------------------------------------

    st.markdown("---")

    st.header(
        "Proxy Inspector & Statistical Summary"
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        st.subheader(
            "🔎 Select Geochemical Ratio"
        )

        selected_proxy = st.selectbox(
            "Choose ratio",
            [
                "V/Cr",
                "Fe/Mn",
                "Sr/Ba",
                "Na/K",
                "Na+K/Ca+Mg",
                "Ca/Mg",
                "Ti/Mn"
            ]
        )

        fig_proxy = go.Figure()

        fig_proxy.add_trace(
            go.Scatter(
                x=df[selected_proxy],
                y=depth,
                mode="lines+markers",
                line=dict(width=3),
                marker=dict(size=6)
            )
        )

        fig_proxy.update_yaxes(
            autorange="reversed"
        )

        fig_proxy.update_layout(
            height=500,
            xaxis_title=selected_proxy,
            showlegend=False
        )

        st.plotly_chart(
            fig_proxy,
            use_container_width=True
        )

    with col2:

        st.subheader(
            "📊 Statistical Interpretation Summary"
        )

        st.markdown(
            f"### Depth Interval: "
            f"{depth.min()} – {depth.max()} m"
        )

        redox_counts = (
            df["Redox"]
            .value_counts(normalize=True) * 100
        )

        dominant_redox = (
            df["Redox"].mode()[0]
        )

        st.markdown(
            f"**Dominant Redox Condition:** "
            f"{dominant_redox}"
        )

        st.markdown(
            "**Redox Conditions:**"
        )

        for k, v in redox_counts.items():

            st.write(
                f"- {k}: {v:.1f}%"
            )

        dominant_salinity = (
            df["Salinity"].mode()[0]
        )

        st.markdown(
            f"**Dominant Salinity:** "
            f"{dominant_salinity}"
        )

        dominant_weathering = (
            df["Weathering"].mode()[0]
        )

        st.markdown(
            f"**Weathering Intensity:** "
            f"{dominant_weathering}"
        )

        dominant_sediment = (
            df["Sediment"].mode()[0]
        )

        st.markdown(
            f"**Dominant Sediment Type:** "
            f"{dominant_sediment}"
        )

        dominant_env = (
            df["TiMn_env"].mode()[0]
        )

        st.markdown(
            f"**Depositional Environment:** "
            f"{dominant_env}"
        )

    # ---------------------------------------------------
    # PDF DOWNLOAD BUTTON
    # ---------------------------------------------------

    pdf_buffer = generate_pdf_report(
        fig,
        df,
        depth,
        selected_proxy,
        field_name,
        well_number
    )

    st.markdown("---")

    st.download_button(
        label="📄 Download Full PDF Report",
        data=pdf_buffer,
        file_name=(
            f"{field_name}_"
            f"geochemical_report.pdf"
        ),
        mime="application/pdf"
    )