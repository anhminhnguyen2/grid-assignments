import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import base64

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grid Map Assignment",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        [data-testid="stSidebar"] { min-width: 260px; max-width: 260px; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
BUS_OPTIONS = ["MA", "MB", "LA", "LB", "LC"]

BUS_COLORS = {
    "MA": "#1565C0",   # blue
    "MB": "#2E7D32",   # green
    "LA": "#00838F",   # teal
    "LB": "#C62828",   # red
    "LC": "#6A1B9A",   # purple
    "Null": "#9E9E9E", # gray
}

# ─────────────────────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    s = st.secrets["postgres"]
    return psycopg2.connect(
        host=s["host"],
        dbname=s["dbname"],
        user=s["user"],
        password=s["password"],
        port=int(s.get("port", 5432))
    )

@st.cache_data(ttl=5)
def get_scenarios() -> list:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT scenario FROM assignments ORDER BY scenario"
        )
        return [r[0] for r in cur.fetchall()]

@st.cache_data(ttl=5)
def load_meters(scenario: str) -> pd.DataFrame:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT  m.meter_id,
                    m.building_name,
                    m.x_pos,
                    m.y_pos,
                    COALESCE(a.bus, 'Null') AS bus
            FROM    meters m
            LEFT JOIN assignments a
                    ON  a.meter_id = m.meter_id
                    AND a.scenario = %s
            ORDER BY m.building_name
        """, (scenario,))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
    return pd.DataFrame(rows, columns=cols)

def save_assignment(meter_id: str, bus: str, scenario: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO assignments (meter_id, scenario, bus, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (meter_id, scenario)
            DO UPDATE SET bus = EXCLUDED.bus,
                          updated_at = NOW()
        """, (meter_id, scenario, bus))
    conn.commit()
    load_meters.clear()

# ─────────────────────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_image_b64() -> str:
    with open("12_kV_Loop_Circuits_Rev_2-21-2025.jpg", "rb") as f:
        return base64.b64encode(f.read()).decode()

def build_chart(df: pd.DataFrame) -> go.Figure:
    img_b64 = get_image_b64()
    fig = go.Figure()

    # Background diagram image
    fig.add_layout_image(dict(
        source=f"data:image/jpeg;base64,{img_b64}",
        xref="x", yref="y",
        x=0, y=100,
        sizex=100, sizey=100,
        xanchor="left", yanchor="top",
        sizing="stretch",
        layer="below",
        opacity=1.0
    ))

    # One scatter trace per bus so legend matches Tableau
    for bus in BUS_OPTIONS + ["Null"]:
        sub = df[df["bus"] == bus]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["x_pos"],
            y=sub["y_pos"],
            mode="markers",
            name=bus,
            marker=dict(
                color=BUS_COLORS[bus],
                size=11,
                line=dict(color="white", width=1.5),
                symbol="circle",
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Meter: %{customdata[1]}<br>"
                "Bus: " + bus + "<br>"
                "<extra></extra>"
            ),
            customdata=sub[["building_name", "meter_id"]].values,
        ))

    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            showgrid=False, zeroline=False,
            showticklabels=False, fixedrange=True,
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=False, zeroline=False,
            showticklabels=False, fixedrange=True,
        ),
        margin=dict(l=0, r=10, t=5, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            title=dict(text="<b>Substation Meter</b>", font=dict(size=13)),
            x=1.01, y=1.0,
            xanchor="left",
            bgcolor="white",
            bordercolor="#cccccc",
            borderwidth=1,
            font=dict(size=12),
            itemsizing="constant",
        ),
        height=700,
        dragmode=False,
    )
    return fig

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Grid Map Assignment")
    st.divider()

    try:
        scenarios = get_scenarios()
    except Exception as e:
        st.error(f"Database connection failed:\n{e}")
        st.stop()

    if not scenarios:
        st.warning("No scenarios found in the database.")
        st.stop()

    st.markdown("**Assignment**")
    selected_scenario = st.radio(
        label="assignment_radio",
        options=["(All)"] + scenarios,
        index=1,
        label_visibility="collapsed"
    )

    active_scenario = scenarios[0] if selected_scenario == "(All)" else selected_scenario

    st.divider()
    st.markdown("**Reassign Meter**")

    df = load_meters(active_scenario)

    chosen_meter = st.selectbox(
        "Select meter",
        options=df["meter_id"].tolist(),
        format_func=lambda m: (
            f"{m}  —  "
            f"{df.loc[df['meter_id']==m, 'building_name'].values[0]}"
        )
    )

    current_row = df[df["meter_id"] == chosen_meter].iloc[0]
    current_bus = current_row["bus"]

    st.caption(f"Current assignment: **{current_bus}**")

    new_bus = st.selectbox(
        "Reassign to bus",
        options=BUS_OPTIONS,
        index=BUS_OPTIONS.index(current_bus) if current_bus in BUS_OPTIONS else 0
    )

    if st.button("💾  Save Change", use_container_width=True, type="primary"):
        if new_bus == current_bus:
            st.info("Already assigned to that bus — no change made.")
        else:
            try:
                save_assignment(chosen_meter, new_bus, active_scenario)
                st.success(f"✅ **{chosen_meter}** → **{new_bus}**")
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

# ─────────────────────────────────────────────────────────────
# MAIN PANEL
# ─────────────────────────────────────────────────────────────
st.markdown(f"**Scenario: {active_scenario}**")

try:
    fig = build_chart(df)
    st.plotly_chart(fig, use_container_width=True)
except FileNotFoundError:
    st.error(
        "⚠️ Background image not found.  \n"
        "Make sure `12_kV_Loop_Circuits_Rev_2-21-2025.jpg` "
        "is in the root of your GitHub repo."
    )