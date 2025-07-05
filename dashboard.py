import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import datetime
from pdf_generator import generate_pdf


st.set_page_config(page_title="Marketing Analytics Dashboard", layout="wide")

st.title("📊 Marketing Analytics Dashboard")

# --- Επιλογή δεδομένων (Demo ή Upload) ---
st.sidebar.header("Επιλογή δεδομένων")
data_source = st.sidebar.radio("Επιλέξτε δεδομένα για ανάλυση:", ("Demo CSV", "Ανέβασμα δικού μου αρχείου CSV"))

@st.cache_data
def load_sample_data():
    return pd.read_csv("marketing_data.csv")

if data_source == "Demo CSV":
    df = load_sample_data()
else:
    uploaded_file = st.sidebar.file_uploader("📂 Ανεβάστε το CSV αρχείο σας", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("✅ Φορτώθηκε το αρχείο σας!")
        except Exception as e:
            st.sidebar.error(f"❌ Σφάλμα στο αρχείο: {e}")
            df = load_sample_data()
            st.sidebar.info("Χρησιμοποιούνται δείγματα δεδομένων.")
    else:
        st.sidebar.warning("⚠️ Παρακαλώ ανεβάστε το αρχείο CSV για να συνεχίσετε.")
        st.stop()

# --- Βασικοί υπολογισμοί (αν δεν υπάρχουν ήδη) ---
for col in ['ctr', 'cpa']:
    if col not in df.columns:
        if col == 'ctr' and 'clicks' in df.columns and 'impressions' in df.columns:
            df['ctr'] = (df['clicks'] / df['impressions']) * 100
        elif col == 'cpa' and 'cost' in df.columns and 'conversions' in df.columns:
            # Προσοχή σε διαιρέσεις με μηδέν
            df['cpa'] = df.apply(lambda x: x['cost'] / x['conversions'] if x['conversions'] > 0 else 0, axis=1)
df['ctr'] = df['ctr'].round(2)
df['cpa'] = df['cpa'].round(2)

st.markdown("""
📘 **Πώς να χρησιμοποιήσεις το upload CSV:**

1. Κάνε **download** το αρχείο παραδείγματος από το κουμπί παρακάτω.
2. Συμπλήρωσε τα δικά σου δεδομένα με τις ίδιες στήλες:
   - `channel,date,impressions,clicks,conversions,cost`
3. Ανεβάστε το στο πεδίο **Upload CSV**.
4. Εφάρμοσε φίλτρα και δες τα αποτελέσματα!

```python
demo_data = pd.DataFrame({/* όπως παραπάνω */})
csv_buffer = io.StringIO()
demo_data.to_csv(csv_buffer, index=False)
st.download_button("📥 Κατέβασε παράδειγμα CSV", data=csv_buffer.getvalue(),
                   file_name="demo_marketing_data.csv", mime="text/csv")


# --- Sidebar Φίλτρα ---
st.sidebar.header("Φίλτρα")

channels = st.sidebar.multiselect("Επιλέξτε Κανάλια", options=df["channel"].unique(), default=df["channel"].unique())

filtered_df = df[df["channel"].isin(channels)]

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

max_cost = int(df['cost'].max())
cost_slider = st.sidebar.slider("Φιλτράρισμα με Κόστος έως (€)", 0, max_cost, max_cost)
filtered_df = filtered_df[filtered_df['cost'] <= cost_slider]

# --- Βασικά Metrics ---
st.subheader("📌 Βασικά Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Συνολικές Εμφανίσεις", f"{int(filtered_df['impressions'].sum()):,}")
col2.metric("Συνολικά Κλικ", f"{int(filtered_df['clicks'].sum()):,}")
col3.metric("Συνολικές Μετατροπές", f"{int(filtered_df['conversions'].sum()):,}")
avg_cpa = filtered_df['cost'].sum() / filtered_df['conversions'].sum() if filtered_df['conversions'].sum() > 0 else 0
col4.metric("Μέσο CPA (€)", f"{avg_cpa:.2f}")

# --- Tabs για Γραφήματα, Δεδομένα και Εξαγωγή ---
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
    summary["CPA (€)"] = summary.apply(lambda x: x["cost"] / x["conversions"] if x["conversions"] > 0 else 0, axis=1)
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

# Συνάρτηση για δημιουργία PDF (έξω από tab blocks)
def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Marketing Analytics Report", ln=True, align='C')
    pdf.ln(10)

    col_width = pdf.w / (len(dataframe.columns) + 1)
    row_height = pdf.font_size * 1.5
    for col_name in dataframe.columns:
        pdf.cell(col_width, row_height, col_name, border=1)
    pdf.ln(row_height)

    for _, row in dataframe.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

with tab3:
    st.markdown("### 📥 Κατέβασε τα φιλτραρισμένα δεδομένα")

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Κατέβασε CSV Αρχείο",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
        key="download_csv"
    )

    pdf_bytes = generate_pdf(filtered_df)
    st.download_button(
        label="Κατέβασε Αναφορά PDF",
        data=pdf_bytes,
        file_name="marketing_report.pdf",
        mime="application/pdf",
        key="download_pdf"
    )
