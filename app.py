import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import plotly.graph_objects as go


# Streamlit page setup
st.set_page_config(layout="wide")
st.title("Geochemical Interpretation Tool")

# Sidebar: Upload data
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])

#Data processing functions
def convert_to_numeric(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def calculate_ratios(df):
    df["Ca/Mg"] = df["Ca"] / df["Mg"]
    df["Ti/Mn"] = df["Ti"] / df["Mn"]
    df["Fe/Mn"] = df["Fe"] / df["Mn"]
    df["Sr/Ba"] = df["Sr"] / df["Ba"]
    df["Na/K"]  = df["Na"] / df["K"]
    df["V/Cr"]  = df["V"]  / df["Cr"]
    df["Na+K/Ca+Mg"] = (df["Na"] + df["K"]) / (df["Ca"] + df["Mg"])
    return df

#Classification functions
def classify_redox(v_cr, fe_mn):
    if pd.isna(v_cr) and pd.isna(fe_mn):
        return "Unknown"
    if (not pd.isna(v_cr) and v_cr > 4.25) or (not pd.isna(fe_mn) and fe_mn > 100):
        return "Anoxic"
    elif (not pd.isna(v_cr) and 2 <= v_cr <= 4.25) or (not pd.isna(fe_mn) and 50 <= fe_mn <= 100):
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
    df["Redox"] = df.apply(lambda r: classify_redox(r["V/Cr"], r["Fe/Mn"]), axis=1)
    df["Salinity"] = df["Sr/Ba"].apply(classify_salinity)
    df["Weathering"] = df["Na/K"].apply(classify_weathering)
    df["Sediment"] = df.apply(lambda r: classify_sediment(r["Ca/Mg"], r["Na+K/Ca+Mg"]), axis=1)
    df["TiMn_env"] = df["Ti/Mn"].apply(classify_ti_mn)
    return df


#Matplotlib plotting functions
def plot_ratio_track(ax, x, depth, label):
    ax.plot(x, depth, color="black", linewidth=1)
    ax.scatter(x, depth, s=10, color="black")
    ax.set_ylim(depth.max(), depth.min())
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.set_label_position("top")
    ax.set_xlabel(label, fontsize=10, fontweight="bold") 
    ax.xaxis.tick_top() 

def plot_facies_track(ax, depth, facies, title, colors):
    for i in range(len(depth) - 1):
        ax.fill_betweenx(
            [depth.iloc[i], depth.iloc[i + 1]],
            0, 1,
            color=colors.get(facies.iloc[i], "grey")
        )
    ax.set_ylim(depth.max(), depth.min())
    ax.set_xticks([])
    ax.set_title(title)
    ax.set_ylabel("Depth")
    legend = [Patch(facecolor=c, edgecolor="k", label=l) for l, c in colors.items()]
    ax.legend(handles=legend, bbox_to_anchor=(0.5, -0.1), loc="lower center", fontsize=8, frameon=False)

#Plotly interactive function
def plot_ratios_plotly(df, depth, ratios):
    ratio_colors = {
        "V/Cr": "#1f77b4",          # Blue
        "Fe/Mn": "#aec7e8",         # Light Blue
        "Sr/Ba": "#d62728",         # Red
        "Na/K": "#f7b6d2",          # Light Pink
        "Na+K/Ca+Mg": "#98df8a",    # Light Green
        "Ca/Mg": "#2ca02c",         # Green
        "Ti/Mn": "#ff7f0e"          # Orange
    }
    fig = go.Figure()
    for r in ratios:
        fig.add_trace(
            go.Scatter(
                x=df[r],
                y=depth,
                mode="lines+markers",
                name=r,
                line=dict(color=ratio_colors.get(r, "black"), width=2),
                marker=dict(color=ratio_colors.get(r, "black"), size=6),
                hovertemplate=f"{r}: %{{x}}<br>Depth: %{{y}}"
            )
        )
    fig.update_yaxes(autorange="reversed", title_text="Depth")
    fig.update_layout(
        title="Geochemical Ratios",
        xaxis_title="Value",
        yaxis_title="Depth",
        height=600,
        width=1000,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

#Run app after file upload
if uploaded_file:

    df = pd.read_excel(uploaded_file)

    #Convert to numeric
    elements = ["Ca","Mg","Ti","Mn","Fe","Sr","Ba","K","Na","V","Cr"]
    df = convert_to_numeric(df, elements)

    #Calculate ratios and classifications
    df = calculate_ratios(df)
    df = apply_classifications(df)

    #Sidebar: Depth range
    st.sidebar.header("Plot Settings")
    min_depth = int(df["Depth"].min())
    max_depth = int(df["Depth"].max())
    depth_range = st.sidebar.slider(
        "Select Depth Interval",
        min_value=min_depth,
        max_value=max_depth,
        value=(min_depth, max_depth)
    )

    #Filter by depth
    df = df[(df["Depth"] >= depth_range[0]) & (df["Depth"] <= depth_range[1])]
    depth = df["Depth"]

    
    #Interactive Plotly plot
    selected_ratios = ["V/Cr", "Fe/Mn", "Sr/Ba", "Na/K", "Na+K/Ca+Mg", "Ca/Mg", "Ti/Mn"]
    plot_ratios_plotly(df, depth, selected_ratios)

   
    #Static Matplotlib plot
    fig, axes = plt.subplots(1, 12, figsize=(26, 10), sharey=True)

    plot_ratio_track(axes[0], df["V/Cr"], depth, "V/Cr")
    plot_ratio_track(axes[1], df["Fe/Mn"], depth, "Fe/Mn")
    plot_ratio_track(axes[2], df["Sr/Ba"], depth, "Sr/Ba")
    plot_ratio_track(axes[3], df["Na/K"], depth, "Na/K")
    plot_ratio_track(axes[4], df["Na+K/Ca+Mg"], depth, "(Na+K)/(Ca+Mg)")
    plot_ratio_track(axes[5], df["Ca/Mg"], depth, "Ca/Mg")
    plot_ratio_track(axes[6], df["Ti/Mn"], depth, "Ti/Mn")

    plot_facies_track(axes[7], depth, df["Redox"], "Redox",
                      {"Oxic":"skyblue","Dysoxic":"orange","Anoxic":"navy","Unknown":"lightgrey"})

    plot_facies_track(axes[8], depth, df["Salinity"], "Salinity",
                      {"Freshwater / restricted":"lightgreen","Brackish":"gold","Marine–high salinity":"darkblue"})

    plot_facies_track(axes[9], depth, df["Weathering"], "Weathering",
                      {"Weak weathering":"skyblue","Moderate weathering":"orange","Intense weathering":"red"})

    plot_facies_track(axes[10], depth, df["Sediment"], "Sediment",
                      {"Limestone":"gold","Dolomitic limestone":"lightyellow",
                       "Dolostone":"khaki","Siliciclastic":"sandybrown"})

    plot_facies_track(axes[11], depth, df["TiMn_env"], "Depositional Environment",
                      {"Continental (alluvial)":"darkgreen","Nearshore, high detrital input":"green",
                       "Shallow marine, variable salinity":"cyan","Open marine / distal":"blue"})

    axes[0].set_ylabel("Depth")
    axes[0].yaxis.set_label_position("left")
    plt.tight_layout(rect=[0.03, 0.05, 0.98, 0.95])
    st.pyplot(fig) 

#Creation of Proxy Inspector & Statistical Summary
    st.markdown("---")
    st.header("Proxy Inspector & Statistical Summary")

    col1, col2 = st.columns([1, 1])

    with col1:

        st.subheader("🔎 Select Geochemical Ratio")

        selected_proxy = st.selectbox(
            "Choose ratio",
            ["V/Cr", "Fe/Mn", "Sr/Ba", "Na/K", "Na+K/Ca+Mg", "Ca/Mg", "Ti/Mn"]
        )

        fig_proxy = go.Figure()

        fig_proxy.add_trace(
            go.Scatter(
                x=df[selected_proxy],
                y=depth,
                mode="lines+markers",
                name=selected_proxy,
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate=f"{selected_proxy}: %{{x}}<br>Depth: %{{y}}"
            )
        )

        fig_proxy.update_yaxes(autorange="reversed", title_text="Depth")

        fig_proxy.update_layout(
            height=500,
            margin=dict(l=40, r=20, t=40, b=20),
            xaxis_title=selected_proxy,
            showlegend=False
        )

        st.plotly_chart(fig_proxy, use_container_width=True)

    with col2:

        st.subheader("📊 Statistical Interpretation Summary")

        st.markdown(f"### Depth Interval: {depth.min()} – {depth.max()}")

    # ---- Redox ----
        redox_counts = df["Redox"].value_counts(normalize=True) * 100
        dominant_redox = df["Redox"].mode()[0]

        st.markdown(f"**Dominant Redox Condition:** {dominant_redox}")
        st.markdown("**Redox Conditions:**")
        for k, v in redox_counts.items():
            st.write(f"- {k}: {v:.1f}%")

    # ---- Salinity ----
        dominant_salinity = df["Salinity"].mode()[0]
        st.markdown(f"**Dominant Salinity:** {dominant_salinity}")

    # ---- Weathering ----
        dominant_weathering = df["Weathering"].mode()[0]
        st.markdown(f"**Weathering Intensity:** {dominant_weathering}")

    # ---- Sediment ----
        dominant_sediment = df["Sediment"].mode()[0]
        st.markdown(f"**Dominant Sediment Type:** {dominant_sediment}")

    # ---- Depositional Environment ----
        dominant_env = df["TiMn_env"].mode()[0]
        st.markdown(f"**Depositional Environment:** {dominant_env}")
