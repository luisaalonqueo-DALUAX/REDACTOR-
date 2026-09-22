import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Redactor de Documentos Oficiales - Chubut",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Redactor de Documentos Oficiales")
st.subheader("Gobierno de la Provincia del Chubut - Ministerio de Producción")

# Formulario principal
with st.form("form_documento"):
    tipo_doc = st.selectbox(
        "Tipo de documento:",
        ["Nota Oficial", "Memorándum", "Pase Administrativo"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        num_doc = st.text_input("Número de Documento:", value="____")
        anio_doc = st.text_input("Año:", value="2026")
    with col2:
        lugar_fecha = st.text_input("Lugar y Fecha (Izquierda):", value=f"Rawson, {datetime.now().strftime('%d de %B de %Y')}")
        iniciales = st.text_input("Iniciales al pie (Izquierda):", value="L.I.A.")

    st.markdown("---")
    
    if tipo_doc == "Memorándum":
        de_persona = st.text_input("DE:", value="Departamento de Administración de Personal")
        para_persona = st.text_input("PARA:", value="División Sueldos")
        asunto_ref = st.text_input("Ref. / Expte. (Izquierda):")
        cuerpo = st.text_area("Cuerpo del Memorándum:", height=180)
    elif tipo_doc == "Pase Administrativo":
        destinatario = st.text_input("Destinatario / Repartición:", value="Mesa General de Entradas y Salidas - Ministerio de Producción")
        asunto_ref = st.text_input("Ref. / Expte. a acumular (Izquierda):", value="Expediente N° ...")
        cuerpo = st.text_area("Cuerpo / Indicaciones del Pase:", height=180)
    else: # Nota Oficial
        destinatario = st.text_area("Destinatario (Nombre, Cargo y Despacho):", value="Ministerio de Producción\nDirección General de Asuntos Legales\nAbg. Norma Navarro\nSU DESPACHO:")
        asunto_ref = st.text_input("Ref. / Expte. (Izquierda):")
        cuerpo = st.text_area("Cuerpo de la Nota:", height=180)

    st.markdown("---")
    submitted = st.form_submit_button("🚀 Generar Documento Formateado")

# Renderizado del documento generado
if submitted:
    st.markdown("---")
    st.subheader("📄 Vista Previa del Documento Generado")
    
    leyenda_oficial = '"Año de la Innovación y Modernización del Estado de la Provincia del Chubut"'
    contacto_pie = "Mariano Moreno y Luis Costa | Rawson | Chubut (Teléfono 280-4485125/126)"
    
    # Encabezado con Membrete Oficial + Leyenda Central
    encabezado_html = f"""
    <div style="border-bottom: 2px solid #1a365d; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="text-align: left;">
                <p style="margin:0; font-size: 11px; font-weight: bold; color: #1a365d;">GOBIERNO DE LA PROVINCIA DEL CHUBUT</p>
                <p style="margin:0; font-size: 11px; font-weight: bold; color: #1a365d;">MINISTERIO DE PRODUCCIÓN</p>
                <p style="margin:0; font-size: 10px; color: #4a5568;">Subsecretaría de Financiamiento y Comercio para la Producción</p>
                <p style="margin:0; font-size: 10px; font-weight: bold; color: #2d3748;">Departamento de Administración de Personal</p>
            </div>
            <div style="text-align: center; flex-grow: 1; padding: 0 15px;">
                <p style="font-style: italic; font-size: 12px; font-weight: bold; color: #2b6cb0; margin: 0;">{leyenda_oficial}</p>
            </div>
        </div>
    </div>
    """
    st.markdown(encabezado_html, unsafe_allow_html=True)
    
    # Formato con Alineaciones a la Izquierda exactas al documento
    if tipo_doc == "Memorándum":
        pie_formateado = f"Memo N° {num_doc}/{anio_doc} DAP-SsFyCP ({iniciales})"
        doc_texto = f"{lugar_fecha}\n\n**MEMORÁNDUM**\n\n**DE:** {de_persona}\n**PARA:** {para_persona}\n\n**Ref.:** {asunto_ref}\n\n{cuerpo}\n\nSin otro particular, saludo a usted muy atentamente.\n\n({iniciales}) {pie_formateado}"
    elif tipo_doc == "Pase Administrativo":
        pie_formateado = f"Pase N° {num_doc}/{anio_doc} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
        doc_texto = f"{lugar_fecha}\n\n**A:** {destinatario}\n\n**Ref.:** {asunto_ref}\n\n{cuerpo}\n\n({iniciales}) {pie_formateado}"
    else:
        pie_formateado = f"Nota N° {num_doc}/{anio_doc} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
        doc_texto = f"{lugar_fecha}\n\n{destinatario}\n\n**Ref.:** {asunto_ref}\n\nDe mi mayor consideración:\n\n{cuerpo}\n\nSin otro particular, saludo a Ud. atentamente.\n\n({iniciales}) {pie_formateado}"

    st.markdown(doc_texto)
    st.markdown(f"<p style='font-size: 10px; color: gray; text-align: center; margin-top: 30px;'>{contacto_pie}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.download_button(
        label="📥 Descargar Documento (.txt)",
        data=doc_texto,
        file_name=f"{tipo_doc.lower().replace(' ', '_')}_{num_doc}_{anio_doc}.txt",
        mime="text/plain"
    )
