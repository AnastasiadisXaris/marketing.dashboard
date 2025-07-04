import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Marketing Analytics Dashboard", layout="wide")

st.title("📊 Marketing Analytics Dashboard")

# Ανάγνωση δεδομένων
df = pd.read_csv("marketing_data.csv")

# Επιλογή φίλτρων
channels = st.multiselect("Επιλέξτε Κανάλια:", options=df["channel"].unique(), default=df["channel"].unique())
filtered_df = df[df["channel"].isin(channels)]

# Πίνακας συνολικών
st.subheader("📈 Σύνοψη Καναλιών")
summary = filtered_df.groupby("channel").agg({
    "impressions": "sum",
    "clicks": "sum",
    "conversions": "sum",
    "cost": "sum"
}).reset_index()
summary["CTR (%)"] = (summary["clicks"] / summary["impressions"]) * 100
summary["CPA (€)"] = summary["cost"] / summary["conversions"]

st.dataframe(summary.style.format({"CTR (%)": "{:.2f}", "CPA (€)": "{:.2f}"}))

# Γράφημα
fig = px.bar(summary, x="channel", y="conversions", title="Συγκριτική Απόδοση Καναλιών", text_auto=True)
st.plotly_chart(fig, use_container_width=True)
