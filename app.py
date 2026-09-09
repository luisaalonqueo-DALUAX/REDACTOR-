import sys
import subprocess

# Asegurar instalación de fpdf2 en tiempo de ejecución
try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from fpdf import FPDF

import streamlit as st
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Sistema de Documentos Oficiales - Chubut",
    page_icon="🏛️",
    layout="wide"
)

# Estilos personalizados en CSS
st.markdown("""
<style>
    .main-header {
        font-family: 'Verdana', sans-serif;
        color: #003366;
        text-align: center;
        margin-bottom: 20px;
    }
    .status-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #ffeeba;
        font-family: 'Verdana', sans-serif;
        font-size: 0.9em;
        margin-bottom: 20px;
    }
    .doc-preview-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 40px;
        border-radius: 4px;
        font-family: 'Verdana', sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        min-height: 500px;
        position: relative;
    }
    .doc-header-code {
        font-weight: bold;
        font-size: 1.1em;
        color: #2c3e50;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .doc-date {
        text-align: right;
        font-size: 1.0em;
        margin-bottom: 20px;
    }
    .doc-body {
        text-align: justify;
        font-size: 1.0em;
        line-height: 1.6;
        margin-top: 25px;
        margin-bottom: 80px;
        white-space: pre-wrap;
    }
    .doc-footer {
        position: absolute;
        bottom: 20px;
        right: 40px;
        font-weight: bold;
        font-size: 1.0em;
        color: #444;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Generador de Documentación Administrativa")
st.caption("Organismo: DPA-SsFyCP-MP | Gobierno del Chubut")

st.markdown("""
<div class="status-badge">
    🟡 <b>Formato configurado internamente — pendiente de validación oficial</b><br>
    <i>Tipografía oficial: Verdana (10–12pt) | Redacción basada en normativa vigente.</i>
</div>
""", unsafe_allow_html=True)

# Layout de dos columnas
col_input, col_preview = st.columns([1, 1])

with col_input:
    st.subheader("📋 Datos del Trámite")
    
    doc_type = st.selectbox(
        "Tipo de Documento",
        ["Nota", "Memorándum", "Pase", "Informe", "Providencia"]
    )
    
    doc_num = st.text_input("Número Correlativo", value="001/2026")
    
    # Fecha actual por defecto
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    now = datetime.now()
    default_date_str = f"Rw, {now.day} de {meses[now.month-1]} de {now.year}."
    
    fecha_custom = st.text_input("Lugar y Fecha", value=default_date_str)
    
    destinatario = st.text_area(
        "Destinatario / Organismo (opcional para Notas/Memos)",
        value="Al Sr. Director Provincial de Administración\nS / D",
        height=80
    )
    
    asunto = st.text_input("Asunto / Referencia", value="Solicitud de informe técnico")
    
    contenido_instruccion = st.text_area(
        "Contenido / Instrucciones para la Redacción",
        value="Por medio de la presente, me dirijo a usted a fin de solicitar tenga bien disponer la elaboración del informe técnico relativo a las actuaciones del expediente en trámite.",
        height=200
    )
    
    st.button("🔄 Actualizar Vista Previa", use_container_width=True)

# Lógica de Vista Previa y Exportación
with col_preview:
    st.subheader("📄 Vista Previa del Documento")
    
    header_code = f"{doc_type.upper()} N.º {doc_num} — DPA-SsFyCP-MP"
    
    # Render preview
    st.markdown(f"""
    <div class="doc-preview-card">
        <div style="text-align: center; border-bottom: 2px solid #003366; padding-bottom: 10px; margin-bottom: 20px;">
            <h3 style="margin:0; color:#003366; font-family:'Verdana';">GOBIERNO DEL CHUBUT</h3>
            <small style="color:#666;">Ministerio de Producción — DPA-SsFyCP-MP</small>
        </div>
        <div class="doc-date">{fecha_custom}</div>
        <div class="doc-header-code">{header_code}</div>
        <div style="font-weight:bold; margin-bottom: 15px;">ASUNTO: {asunto}</div>
        {'<div style="margin-bottom:15px; font-style:italic;">' + destinatario.replace('\n', '<br>') + '</div>' if destinatario else ''}
        <div class="doc-body">{contenido_instruccion}</div>
        <div class="doc-footer">L.I.A.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generador de PDF compatible con caracteres en español
    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Limpieza de textos para evitar encoding error en FPDF
        def clean_text(txt):
            if not txt:
                return ""
            txt = txt.replace("—", "-").replace("º", "°")
            return txt.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, clean_text("GOBIERNO DEL CHUBUT"), ln=True, align="C")
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, clean_text("Ministerio de Producción - DPA-SsFyCP-MP"), ln=True, align="C")
        pdf.line(10, 25, 200, 25)
        pdf.ln(10)
        
        # Fecha
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, clean_text(fecha_custom), ln=True, align="R")
        pdf.ln(5)
        
        # Encabezado
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, clean_text(header_code), ln=True, align="L")
        pdf.cell(0, 8, clean_text(f"ASUNTO: {asunto}"), ln=True, align="L")
        pdf.ln(5)
        
        # Destinatario
        if destinatario:
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(0, 6, clean_text(destinatario))
            pdf.ln(5)
            
        # Cuerpo del texto
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, clean_text(contenido_instruccion), align="J")
        
        # Pie L.I.A.
        pdf.set_y(-30)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 10, clean_text("L.I.A."), align="R", ln=True)
        
        return pdf.output()

    pdf_bytes = generate_pdf()
    
    st.download_button(
        label="📥 Descargar Documento en PDF",
        data=bytes(pdf_bytes),
        file_name=f"{doc_type}_{doc_num.replace('/', '-')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
