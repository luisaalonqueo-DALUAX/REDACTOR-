import streamlit as st
import sqlite3
from datetime import datetime

# Configuración de la página en modo ancho (wide) para permitir la columna lateral
st.set_page_config(
    page_title="Redactor de Documentos Oficiales - Chubut",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------------
# BASE DE DATOS LOCAL
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            numero INTEGER,
            anio TEXT,
            fecha TEXT,
            destinatario TEXT,
            asunto TEXT,
            cuerpo TEXT,
            iniciales TEXT
        )
    ''')
    conn.commit()
    conn.close()

def obtener_ultimo_numero(tipo, anio):
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    c.execute("SELECT MAX(numero) FROM documentos WHERE tipo = ? AND anio = ?", (tipo, anio))
    res = c.fetchone()[0]
    conn.close()
    return res if res else 0

def guardar_documento(tipo, numero, anio, fecha, destinatario, asunto, cuerpo, iniciales):
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO documentos (tipo, numero, anio, fecha, destinatario, asunto, cuerpo, iniciales)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tipo, numero, anio, fecha, destinatario, asunto, cuerpo, iniciales))
    conn.commit()
    conn.close()

def obtener_todos_documentos():
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    c.execute('SELECT id, tipo, numero, anio, fecha, destinatario, asunto FROM documentos ORDER BY id DESC')
    registros = c.fetchall()
    conn.close()
    return registros

init_db()

st.title("📝 Redactor de Documentos Oficiales")
st.subheader("Gobierno de la Provincia del Chubut - Ministerio de Producción")

# ---------------------------------------------------------
# ESTRUCTURA EN 2 COLUMNAS (REDACCIÓN + ÍNDICE LATERAL)
# ---------------------------------------------------------
col_redaccion, col_indice = st.columns([2, 1])

# ---------------------------------------------------------
# COLUMNA LATERAL: ÍNDICE DE NUMERACIÓN
# ---------------------------------------------------------
with col_indice:
    st.markdown("### 📋 Índices / Correlatividad")
    st.caption("Historial de números utilizados y motivo")
    
    docs_registrados = obtener_todos_documentos()
    
    if docs_registrados:
        for doc in docs_registrados:
            d_id, d_tipo, d_num, d_anio, d_fecha, d_dest, d_asunto = doc
            st.markdown(f"**{d_tipo} N° {d_num}/{d_anio}**")
            st.markdown(f"• **Fecha:** {d_fecha}")
            st.markdown(f"• **Motivo/Ref:** {d_asunto}")
            st.markdown(f"• **Destino:** {d_dest[:40]}...")
            st.markdown("---")
    else:
        st.info("Aún no se han registrado números en el índice.")

# ---------------------------------------------------------
# COLUMNA PRINCIPAL: REDACCIÓN Y GENERACIÓN PDF
# ---------------------------------------------------------
with col_redaccion:
    anio_actual = str(datetime.now().year)
    
    st.markdown("### 1. Datos del Documento")
    destinatario_input = st.text_input("Ingresa Destinatario / Sector:", value="")
    
    # Sugerencia automática
    sugerencia = "Nota Oficial"
    dest_lower = destinatario_input.lower()
    if any(p in dest_lower for p in ["sueldos", "división", "liquidacion", "costos"]):
        sugerencia = "Memorándum"
    elif any(p in dest_lower for p in ["mesa", "entradas", "acumular", "salidas"]):
        sugerencia = "Pase Administrativo"
        
    tipo_doc = st.selectbox(
        "Tipo de Documento:",
        ["Nota Oficial", "Memorándum", "Pase Administrativo"],
        index=["Nota Oficial", "Memorándum", "Pase Administrativo"].index(sugerencia)
    )

    ultimo_num = obtener_ultimo_numero(tipo_doc, anio_actual)
    siguiente_num = ultimo_num + 1

    st.info(f"📌 Próximo número correlativo sugerido: **{siguiente_num}** (Último emitido: {ultimo_num})")

    with st.form("form_redaccion"):
        c1, c2 = st.columns(2)
        with c1:
            num_doc = st.number_input("Número Correlativo:", value=siguiente_num, step=1)
            anio_doc = st.text_input("Año:", value=anio_actual)
        with c2:
            lugar_fecha = st.text_input("Lugar y Fecha:", value=f"Rawson, {datetime.now().strftime('%d de %B de %Y')}")
            iniciales = st.text_input("Iniciales al pie:", value="L.I.A.")

        st.markdown("---")
        
        if tipo_doc == "Memorándum":
            de_persona = st.text_input("DE:", value="Departamento de Administración de Personal")
            para_persona = st.text_input("PARA:", value=destinatario_input if destinatario_input else "División Sueldos")
            asunto_ref = st.text_input("Ref. / Expte. (Motivo):")
            cuerpo = st.text_area("Cuerpo del Memorándum:", height=150)
            dest_final = f"DE: {de_persona} | PARA: {para_persona}"
        elif tipo_doc == "Pase Administrativo":
            dest_final = destinatario_input if destinatario_input else "Mesa General de Entradas y Salidas - Ministerio de Producción"
            st.text_input("Destinatario / Repartición:", value=dest_final)
            asunto_ref = st.text_input("Ref. / Expte. a acumular (Motivo):", value="Expediente N° ...")
            cuerpo = st.text_area("Cuerpo / Indicaciones del Pase:", height=150)
        else: # Nota Oficial
            dest_final = destinatario_input if destinatario_input else "Ministerio de Producción\nDirección General de Asuntos Legales\nAbg. Norma Navarro\nSU DESPACHO:"
            st.text_area("Destinatario completo:", value=dest_final)
            asunto_ref = st.text_input("Ref. / Expte. (Motivo):")
            cuerpo = st.text_area("Cuerpo de la Nota:", height=150)

        submitted = st.form_submit_button("🚀 Generar y Registrar en el Índice")

    if submitted:
        guardar_documento(tipo_doc, num_doc, anio_doc, lugar_fecha, dest_final, asunto_ref, cuerpo, iniciales)
        st.success(f"✅ Registrado en el índice: **{tipo_doc} N° {num_doc}/{anio_doc}**.")
        st.rerun()

    # Vista Previa e Impresión en PDF
    leyenda_oficial = '"Año de la Innovación y Modernización del Estado de la Provincia del Chubut"'
    contacto_pie = "Mariano Moreno y Luis Costa | Rawson | Chubut (Teléfono 280-4485125/126)"
    
    if tipo_doc == "Memorándum":
        pie_formateado = f"Memo N° {siguiente_num}/{anio_actual} DAP-SsFyCP ({iniciales})"
        doc_encabezado_texto = f"MEMORÁNDUM\n{dest_final}"
    elif tipo_doc == "Pase Administrativo":
        pie_formateado = f"Pase N° {siguiente_num}/{anio_actual} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
        doc_encabezado_texto = f"A: {dest_final}"
    else:
        pie_formateado = f"Nota N° {siguiente_num}/{anio_actual} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
        doc_encabezado_texto = f"{dest_final}"

    st.markdown("---")
    st.subheader("🖨️ Vista Previa e Impresión en PDF")
    
    # HTML imprimible estilizado para PDF
    html_imprimir = f"""
    <div id="documento-imprimir" style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd;">
        <div style="border-bottom: 2px solid #1a365d; padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
            <div style="text-align: left;">
                <strong style="font-size: 11px; color: #1a365d;">GOBIERNO DE LA PROVINCIA DEL CHUBUT</strong><br>
                <strong style="font-size: 11px; color: #1a365d;">MINISTERIO DE PRODUCCIÓN</strong><br>
                <span style="font-size: 10px; color: #4a5568;">Subsecretaría de Financiamiento y Comercio para la Producción</span><br>
                <strong style="font-size: 10px; color: #2d3748;">Departamento de Administración de Personal</strong>
            </div>
            <div style="text-align: center; flex-grow: 1;">
                <span style="font-style: italic; font-size: 11px; font-weight: bold; color: #2b6cb0;">{leyenda_oficial}</span>
            </div>
        </div>
        <div style="text-align: right; font-weight: bold; font-size: 12px; margin-bottom: 15px;">{lugar_fecha}</div>
        <div style="text-align: right; font-size: 12px; margin-bottom: 20px;"><strong>Ref.:</strong> {asunto_ref}</div>
        <div style="font-size: 12px; margin-bottom: 20px; white-space: pre-line;">{doc_encabezado_texto}</div>
        <div style="font-size: 12px; line-height: 1.6; margin-bottom: 30px; white-space: pre-line;">{cuerpo}</div>
        <div style="font-size: 12px; font-weight: bold; margin-top: 40px;">({iniciales}) {pie_formateado}</div>
        <div style="font-size: 9px; color: gray; text-align: center; margin-top: 40px; border-top: 1px solid #eee; padding-top: 5px;">{contacto_pie}</div>
    </div>
    """
    
    st.markdown(html_imprimir, unsafe_allow_html=True)
    
    # Botón directo para disparar la impresión / Guardar como PDF
    st.markdown("""
        <br>
        <button onclick="window.print()" style="background-color: #2b6cb0; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold;">
            🖨️ Imprimir o Guardar como PDF
        </button>
    """, unsafe_allow_html=True)
