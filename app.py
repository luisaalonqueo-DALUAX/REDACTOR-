import streamlit as st
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# 1. BASE DE DATOS LOCAL PARA CORRELATIVIDAD Y BÚSQUEDA
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

def buscar_documentos(query=""):
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    if query:
        c.execute('''
            SELECT id, tipo, numero, anio, fecha, destinatario, asunto 
            FROM documentos 
            WHERE destinatario LIKE ? OR asunto LIKE ? OR cuerpo LIKE ? OR tipo LIKE ?
            ORDER BY id DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    else:
        c.execute('SELECT id, tipo, numero, anio, fecha, destinatario, asunto FROM documentos ORDER BY id DESC')
    registros = c.fetchall()
    conn.close()
    return registros

init_db()

# ---------------------------------------------------------
# 2. CONFIGURACIÓN DE PÁGINA Y PESTAÑAS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Redactor de Documentos Oficiales - Chubut",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Redactor de Documentos Oficiales")
st.subheader("Gobierno de la Provincia del Chubut - Ministerio de Producción")

pestana1, pestana2 = st.tabs(["✍️ Redactar Documento", "🔍 Índice y Histórico"])

# ---------------------------------------------------------
# PESTAÑA 1: REDACCIÓN Y VERIFICACIÓN REGLAMENTARIA
# ---------------------------------------------------------
with pestana1:
    anio_actual = str(datetime.now().year)
    
    st.markdown("### 1. Verificación de Destino y Regla Administrativa")
    
    destinatario_input = st.text_input("Ingresa Destinatario o Área de Destino:", value="")
    
    # Evaluación reglamentaria del tipo de documento
    sugerencia = "Nota Oficial"
    explicacion = "Las comunicaciones dirigidas a Asuntos Legales u otros Ministerios/Direcciones externas deben canalizarse como Nota Oficial."
    
    dest_lower = destinatario_input.lower()
    if any(p in dest_lower for p in ["sueldos", "división", "liquidacion", "costos"]):
        sugerencia = "Memorándum"
        explicacion = "Las comunicaciones internas dentro de la misma Subsecretaría (ej. División Sueldos) se tramitan como Memorándum."
    elif any(p in dest_lower for p in ["mesa", "entradas", "acumular", "salidas"]):
        sugerencia = "Pase Administrativo"
        explicacion = "Los giros de actuaciones a Mesa de Entradas o pedidos de acumulación de expedientes corresponden a un Pase Administrativo."
    
    if destinatario_input:
        st.info(f"💡 **Verificación Normativa:** Según el destino ingresado, corresponde un/a **{sugerencia}**.\n\n_{explicacion}_")

    tipo_doc = st.selectbox(
        "Tipo de Documento a emitir:",
        ["Nota Oficial", "Memorándum", "Pase Administrativo"],
        index=["Nota Oficial", "Memorándum", "Pase Administrativo"].index(sugerencia)
    )

    # Cálculo automático del número correlativo
    ultimo_num = obtener_ultimo_numero(tipo_doc, anio_actual)
    siguiente_num = ultimo_num + 1

    st.warning(f"📌 Último número emitido para **{tipo_doc}** en {anio_actual}: **{ultimo_num}**. Próximo número disponible: **{siguiente_num}**.")

    with st.form("form_redaccion"):
        col1, col2 = st.columns(2)
        with col1:
            num_doc = st.number_input("Número Correlativo:", value=siguiente_num, step=1)
            anio_doc = st.text_input("Año:", value=anio_actual)
        with col2:
            lugar_fecha = st.text_input("Lugar y Fecha (Derecha):", value=f"Rawson, {datetime.now().strftime('%d de %B de %Y')}")
            iniciales = st.text_input("Iniciales al pie (Izquierda):", value="L.I.A.")

        st.markdown("---")
        
        if tipo_doc == "Memorándum":
            de_persona = st.text_input("DE:", value="Departamento de Administración de Personal")
            para_persona = st.text_input("PARA:", value=destinatario_input if destinatario_input else "División Sueldos")
            asunto_ref = st.text_input("Ref. / Expte. (Derecha):")
            cuerpo = st.text_area("Cuerpo del Memorándum:", height=180)
            dest_final = f"DE: {de_persona}\nPARA: {para_persona}"
        elif tipo_doc == "Pase Administrativo":
            dest_final = destinatario_input if destinatario_input else "Mesa General de Entradas y Salidas - Ministerio de Producción"
            st.text_input("Destinatario / Repartición:", value=dest_final)
            asunto_ref = st.text_input("Ref. / Expte. a acumular (Derecha):", value="Expediente N° ...")
            cuerpo = st.text_area("Cuerpo / Indicaciones del Pase:", height=180)
        else: # Nota Oficial
            dest_final = destinatario_input if destinatario_input else "Ministerio de Producción\nDirección General de Asuntos Legales\nAbg. Norma Navarro\nSU DESPACHO:"
            st.text_area("Destinatario completo:", value=dest_final)
            asunto_ref = st.text_input("Ref. / Expte. (Derecha):")
            cuerpo = st.text_area("Cuerpo de la Nota:", height=180)

        submitted = st.form_submit_button("🚀 Generar Documento y Registrar Correlatividad")

    if submitted:
        # Guardar correlativo en base de datos
        guardar_documento(tipo_doc, num_doc, anio_doc, lugar_fecha, dest_final, asunto_ref, cuerpo, iniciales)
        st.success(f"✅ Documento generado y registrado en el índice general: **{tipo_doc} N° {num_doc}/{anio_doc}**.")
        
        st.markdown("---")
        st.subheader("📄 Vista Previa del Documento")
        
        leyenda_oficial = '"Año de la Innovación y Modernización del Estado de la Provincia del Chubut"'
        contacto_pie = "Mariano Moreno y Luis Costa | Rawson | Chubut (Teléfono 280-4485125/126)"
        
        # Header oficial con membrete a la izquierda y leyenda en el centro
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
        st.markdown(f"<div style='text-align: right; font-weight: bold; margin-bottom: 15px;'>{lugar_fecha}</div>", unsafe_allow_html=True)
        
        ref_html = f"<div style='text-align: right; margin-bottom: 20px;'><strong>Ref.:</strong> {asunto_ref}</div>"
        
        if tipo_doc == "Memorándum":
            pie_formateado = f"Memo N° {num_doc}/{anio_doc} DAP-SsFyCP ({iniciales})"
            st.markdown(f"**MEMORÁNDUM**\n\n**{dest_final}**\n")
            st.markdown(ref_html, unsafe_allow_html=True)
            doc_cuerpo = f"{cuerpo}\n\nSin otro particular, saludo a usted muy atentamente.\n\n({iniciales}) {pie_formateado}"
        elif tipo_doc == "Pase Administrativo":
            pie_formateado = f"Pase N° {num_doc}/{anio_doc} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
            st.markdown(f"**A:** {dest_final}\n")
            st.markdown(ref_html, unsafe_allow_html=True)
            doc_cuerpo = f"{cuerpo}\n\n({iniciales}) {pie_formateado}"
        else:
            pie_formateado = f"Nota N° {num_doc}/{anio_doc} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
            st.markdown(f"{dest_final}\n")
            st.markdown(ref_html, unsafe_allow_html=True)
            doc_cuerpo = f"De mi mayor consideración:\n\n{cuerpo}\n\nSin otro particular, saludo a Ud. atentamente.\n\n({iniciales}) {pie_formateado}"
        
        st.markdown(doc_cuerpo)
        st.markdown(f"<p style='font-size: 10px; color: gray; text-align: center; margin-top: 30px;'>{contacto_pie}</p>", unsafe_allow_html=True)
        
        doc_texto_completo = f"{lugar_fecha}\nRef.: {asunto_ref}\n\n{doc_cuerpo}"
        
        st.download_button(
            label="📥 Descargar Documento (.txt)",
            data=doc_texto_completo,
            file_name=f"{tipo_doc.lower().replace(' ', '_')}_{num_doc}_{anio_doc}.txt",
            mime="text/plain"
        )

# ---------------------------------------------------------
# PESTAÑA 2: ÍNDICE Y BÚSQUEDA HISTÓRICA
# ---------------------------------------------------------
with pestana2:
    st.markdown("### 🔍 Buscador e Índice de Documentos Registrados")
    busqueda = st.text_input("Buscar por número, expediente, asunto o destinatario:", value="")
    
    resultados = buscar_documentos(busqueda)
    
    if resultados:
        for item in resultados:
            doc_id, t_doc, n_doc, a_doc, f_doc, d_doc, as_doc = item
            with st.expander(f"📌 {t_doc} N° {n_doc}/{a_doc} - Ref: {as_doc}"):
                st.write(f"**Fecha:** {f_doc}")
                st.write(f"**Destinatario:** {d_doc}")
                st.write(f"**Referencia:** {as_doc}")
    else:
        st.info("No hay documentos registrados que coincidan con la búsqueda.")
