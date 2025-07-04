import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import base64
import datetime

st.set_page_config(page_title="Marketing Analytics Dashboard", layout="wide")

st.title("📊 Marketing Analytics Dashboard")

# --- Sidebar for upload or sample data
uploaded_file = st.sidebar.file_uploader("📂 Ανεβάστε το CSV αρχείο σας", type=["csv"])

@st.cache_data
def load_sample_data():
    return pd.read_csv("marketing_data.csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("✅ Φορτώθηκε το αρχείο σας!")
    except Exception as e:
        st.sidebar.error(f"❌ Σφάλμα στο αρχείο: {e}")
        df = load_sample_data()
else:
    df = load_sample_data()
    st.sidebar.info("Χρησιμοποιούνται δείγματα δεδομένων.")

# Βασικοί υπολογισμοί (αν δεν υπάρχουν ήδη)
for col in ['ctr', 'cpa']:
    if col not in df.columns:
        if col == 'ctr' and 'clicks' in df.columns and 'impressions' in df.columns:
            df['ctr'] = (df['clicks'] / df['impressions']) * 100
        elif col == 'cpa' and 'cost' in df.columns and 'conversions' in df.columns:
            df['cpa'] = df['cost'] / df['conversions']
df['ctr'] = df['ctr'].round(2)
df['cpa'] = df['cpa'].round(2)

# --- Filters Sidebar ---
st.sidebar.header("Φίλτρα")

channels = st.sidebar.multiselect("Επιλέξτε Κανάλια", options=df["channel"].unique(), default=df["channel"].unique())

filtered_df = df[df["channel"].isin(channels)]

# Αν υπάρχει στήλη 'date', πρόσθεσε date picker
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input("Επιλέξτε εύρος ημερομηνιών", [min_date, max_date])
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(date_range[0])) & 
            (filtered_df['date'] <= pd.to_datetime(date_range[1]))
        ]

# Slider για κόστος
max_cost = int(df['cost'].max())
cost_slider = st.sidebar.slider("Φιλτράρισμα με Κόστος έως (€)", 0, max_cost, max_cost)
filtered_df = filtered_df[filtered_df['cost'] <= cost_slider]

# --- KPIs in Cards ---
st.subheader("📌 Βασικά Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Συνολικές Εμφανίσεις", f"{int(filtered_df['impressions'].sum()):,}")
col2.metric("Συνολικά Κλικ", f"{int(filtered_df['clicks'].sum()):,}")
col3.metric("Συνολικές Μετατροπές", f"{int(filtered_df['conversions'].sum()):,}")
avg_cpa = filtered_df['cost'].sum() / filtered_df['conversions'].sum() if filtered_df['conversions'].sum() > 0 else 0
col4.metric("Μέσο CPA (€)", f"{avg_cpa:.2f}")

# --- Tabs for charts and data
tab1, tab2, tab3 = st.tabs(["Γραφήματα 📈", "Δεδομένα 🗃️", "Εξαγωγή 📤"])

with tab1:
    st.markdown("### 📊 Απόδοση ανά Κανάλι")
    summary = filtered_df.groupby("channel").agg({
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "cost": "sum"
    }).reset_index()
    summary["CTR (%)"] = (summary["clicks"] / summary["impressions"]) * 100
    summary["CPA (€)"] = summary["cost"] / summary["conversions"]
    summary = summary.round({"CTR (%)":2, "CPA (€)":2})

    fig1 = px.bar(summary, x="channel", y="conversions", title="Μετατροπές ανά Κανάλι", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(summary, x="channel", y="CTR (%)", title="CTR (%) ανά Κανάλι", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(summary, x="CPA (€)", y="conversions", color="channel", size="impressions", 
                      title="CPA vs Μετατροπές (Bubble Size: Impressions)", size_max=60)
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.dataframe(filtered_df)

with tab3:
    st.markdown("### 📥 Κατέβασε τα φιλτραρισμένα δεδομένα")

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Κατέβασε CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )

    # PDF Export function
    def generate_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Marketing Analytics Report", ln=True, align='C')
        pdf.ln(10)

        # Header
        col_width = pdf.w / (len(dataframe.columns) + 1)
        row_height = pdf.font_size * 1.5
        for col_name in dataframe.columns:
            pdf.cell(col_width, row_height, col_name, border=1)
        pdf.ln(row_height)

        # Rows
        for _, row in dataframe.iterrows():
            for item in row:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)
        
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        return pdf_output.getvalue()

    pdf_bytes = generate_pdf(filtered_df)

    st.download_button(
        label="Κατέβασε PDF",
        data=pdf_bytes,
        file_name="marketing_report.pdf",
        mime="application/pdf"
    )
