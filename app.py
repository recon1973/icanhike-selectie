
import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
import zipfile
import base64

st.set_page_config(page_title="I Can Hike Selectie", layout="wide")
st.title("🥾 I Can Hike 2026 - Selectie Webapp")

# Upload bestand
uploaded_file = st.file_uploader("📥 Upload deelnemerslijst (.xlsx)", type=["xlsx"])
df = None

# Scorefunctie
def bereken_score(rij):
    score = 0
    if 18 <= rij['Leeftijd'] <= 55:
        score += 1
    score += rij['Fysieke gesteldheid'] / 10 * 3
    score += max(0, (10 - rij['Ervaring']) / 10 * 2)
    score += rij['Motivatie score'] / 20 * 2
    if rij['Militaire achtergrond'] == 'Ja':
        score += 1
    if rij['Medische bijzonderheden'] != 'Geen':
        score -= 1
    return round(score * 10, 1)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['Totaalscore'] = df.apply(bereken_score, axis=1)
    df['Status'] = df['Totaalscore'].apply(lambda x: 'Geselecteerd' if x >= 75 else 'Reserve' if x >= 60 else 'Afgewezen')
    st.success("✅ Deelnemerslijst verwerkt!")
    
    # Toon tabel
    st.dataframe(df)

    # Download alle rapporten
    if st.button("📄 Genereer en download PDF-rapporten"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
            for _, rij in df.iterrows():
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.image("logo.jpeg", x=10, y=10, w=30)
                pdf.set_xy(10, 40)
                regels = [
                    f"Naam: {rij['Naam']}",
                    f"Leeftijd: {rij['Leeftijd']}",
                    f"Geslacht: {rij['Geslacht']}",
                    f"Ervaring: {rij['Ervaring']}",
                    f"Fysieke gesteldheid: {rij['Fysieke gesteldheid']}",
                    f"Motivatie score: {rij['Motivatie score']}",
                    f"Medische bijzonderheden: {rij['Medische bijzonderheden']}",
                    f"Militaire achtergrond: {rij['Militaire achtergrond']}",
                    f"Deelname Invictus Games: {rij['Deelname Invictus Games']}",
                    f"Totaalscore: {rij['Totaalscore']}",
                    f"Status: {rij['Status']}"
                ]
                for regel in regels:
                    pdf.cell(200, 10, txt=regel.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                pdf_file = pdf.output(dest='S').encode('latin-1')
                zf.writestr(f"{rij['Naam'].replace(' ', '_')}_rapport.pdf", pdf_file)
        zip_buffer.seek(0)
        b64 = base64.b64encode(zip_buffer.read()).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="rapporten.zip">📦 Download alle rapporten (ZIP)</a>'
        st.markdown(href, unsafe_allow_html=True)
