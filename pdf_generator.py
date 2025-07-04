from fpdf import FPDF

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
