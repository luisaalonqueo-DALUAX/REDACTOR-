import streamlit as st
import sqlite3
import re
from datetime import datetime

# Configuración de la página en modo ancho
st.set_page_config(
    page_title="Redactor de Documentos Oficiales - Chubut",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES Y LIMPIEZA
# ---------------------------------------------------------
MESES_ESPANOL = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def obtener_fecha_actual_espanol():
    hoy = datetime.now()
    mes = MESES_ESPANOL[hoy.month]
    return f"Rawson, {hoy.day} de {mes} de {hoy.year}.-"

def limpiar_texto(texto):
    if not texto:
        return ""
    # Quita espacios dobles o múltiples redundantes
    texto_limpio = re.sub(r'[ \t]+', ' ', texto)
    return texto_limpio.strip()

# ---------------------------------------------------------
# BASE DE DATOS LOCAL Y AUTOCOMPLETADO DE DESTINATARIOS
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS destinatarios_frecuentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE
        )
    ''')
    
    frecuentes = [
        "Departamento Sueldos",
        "Mesa General de Entradas y Salidas - Ministerio de Producción",
        "Ministerio de Producción\nDirección General de Asuntos Legales\nAbg. Norma Navarro\nSU DESPACHO:",
        "División Sueldos y Cargas Sociales",
        "Subsecretaría de Financiamiento y Comercio para la Producción"
    ]
    for dest in frecuentes:
        c.execute('INSERT OR IGNORE INTO destinatarios_frecuentes (nombre) VALUES (?)', (dest,))
        
    conn.commit()
    conn.close()

def obtener_destinatarios_frecuentes():
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    c.execute('SELECT nombre FROM destinatarios_frecuentes ORDER BY nombre ASC')
    filas = c.fetchall()
    conn.close()
    return [f[0] for f in filas]

def guardar_destinatario_nuevo(nombre):
    if nombre and len(nombre.strip()) > 3:
        conn = sqlite3.connect("documentos.db")
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO destinatarios_frecuentes (nombre) VALUES (?)', (limpiar_texto(nombre),))
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
    guardar_destinatario_nuevo(destinatario)

def obtener_todos_documentos():
    conn = sqlite3.connect("documentos.db")
    c = conn.cursor()
    c.execute('SELECT id, tipo, numero, anio, fecha, destinatario, asunto FROM documentos ORDER BY id DESC')
    registros = c.fetchall()
    conn.close()
    return registros

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
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------
st.title("📝 Redactor de Documentos Oficiales")
st.subheader("Gobierno de la Provincia del Chubut - Ministerio de Producción")

pestana1, pestana2 = st.tabs(["✍️ Redactar Documento", "🔍 Buscador e Índice General"])

with pestana1:
    col_redaccion, col_indice = st.columns([2, 1])
    
    with col_indice:
        st.markdown("### 📋 Índice de Correlatividad")
        st.caption("Historial de números utilizados y motivo de emisión")
        
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
            st.info("Aún no hay documentos registrados en el índice.")

    with col_redaccion:
        anio_actual = str(datetime.now().year)
        
        st.markdown("### 1. Verificación de Destino (Autocompletado)")
        
        opciones_destinatarios = ["-- Escribir un nuevo destinatario --"] + obtener_destinatarios_frecuentes()
        destinatario_seleccionado = st.selectbox("Seleccionar un destinatario habitual:", opciones_destinatarios)
        
        if destinatario_seleccionado == "-- Escribir un nuevo destinatario --":
            destinatario_input = st.text_input("Ingresa Destinatario o Área de Destino:", value="")
        else:
            destinatario_input = destinatario_seleccionado

        destinatario_input = limpiar_texto(destinatario_input)
        
        # Sugerencia y verificación normativa
        sugerencia = "Nota Oficial"
        explicacion = "Las comunicaciones dirigidas a Asuntos Legales u otros Ministerios/Direcciones externas deben canalizarse como Nota Oficial."
        
        dest_lower = destinatario_input.lower()
        if any(p in dest_lower for p in ["sueldos", "división", "departamento sueldos", "liquidacion", "costos"]):
            sugerencia = "Memorándum"
            explicacion = "Las comunicaciones internas dirigidas a dependencias como el Departamento Sueldos se tramitan como Memorándum."
        elif any(p in dest_lower for p in ["mesa", "entradas", "acumular", "salidas"]):
            sugerencia = "Pase Administrativo"
            explicacion = "Los giros de actuaciones a Mesa de Entradas o pedidos de acumulación de expedientes corresponden a un Pase Administrativo (se imprime por duplicado)."
        
        if destinatario_input:
            st.info(f"💡 **Verificación Normativa:** Según el destino ingresado, corresponde un/a **{sugerencia}**.\n\n_{explicacion}_")

        tipo_doc = st.selectbox(
            "Tipo de Documento a emitir:",
            ["Nota Oficial", "Memorándum", "Pase Administrativo"],
            index=["Nota Oficial", "Memorándum", "Pase Administrativo"].index(sugerencia)
        )

        ultimo_num = obtener_ultimo_numero(tipo_doc, anio_actual)
        siguiente_num = ultimo_num + 1

        st.warning(f"📌 Último número emitido para **{tipo_doc}** en {anio_actual}: **{ultimo_num}**. Próximo número disponible: **{siguiente_num}**.")

        with st.form("form_redaccion"):
            c1, c2 = st.columns(2)
            with c1:
                num_doc = st.number_input("Número Correlativo:", value=siguiente_num, step=1)
                anio_doc = st.text_input("Año:", value=anio_actual)
            with c2:
                lugar_fecha = st.text_input("Lugar y Fecha (A la derecha):", value=obtener_fecha_actual_espanol())
                iniciales = st.text_input("Iniciales al pie:", value="L.I.A.")

            st.markdown("---")
            
            if tipo_doc == "Memorándum":
                de_persona = st.text_input("Producido por:", value="Departamento de Administración de Personal")
                para_persona = st.text_input("Para Información:", value=destinatario_input if destinatario_input else "Departamento Sueldos")
                asunto_ref = st.text_input("Ref. / Expte.:", value="Expte: N° 1729/2026-MP- Reclamo Adicional...")
                cuerpo = st.text_area("Cuerpo del Memorándum:", height=180)
                
                de_persona = limpiar_texto(de_persona)
                para_persona = limpiar_texto(para_persona)
                dest_final = f"Producido por: {de_persona}\nPara Información: {para_persona}"
            elif tipo_doc == "Pase Administrativo":
                dest_final = destinatario_input if destinatario_input else "Mesa General de Entradas y Salidas\nMinisterio de Producción\nSU DESPACHO"
                st.text_area("Destinatario / Repartición:", value=dest_final)
                asunto_ref = st.text_input("Ref. / Expte. a acumular:", value="Acumulación de Expediente N° 3091/2023...")
                cuerpo = st.text_area("Cuerpo del Pase:", height=180, value="Por medio del presente me dirijo a usted, con el fin de solicitar acumular Expediente Nº 3091/2023 – MAGIyC – constan 14 fojas, al Expediente 1612/2024 el mismo consta con 30 fojas cuyo extracto exprese lo siguiente:\n\nS/ Recaratular Expte. N°3498/2023 UEP.MAGYC-Ref. Pase N° 471/2023 SAP-UEP-MAGIyC “Baja por fallecimiento del agente OLATE, Juan Carlos”.\n\nUna vez cumplido vuelva a este Departamento de Personal, para proseguir con el trámite administrativo correspondiente.")
            else: # Nota Oficial
                dest_final = destinatario_input if destinatario_input else "Ministerio de Producción\nDirección General de Asuntos Legales\nAbg. Norma Navarro\nSU DESPACHO:"
                st.text_area("Destinatario completo:", value=dest_final)
                asunto_ref = st.text_input("Ref. / Expte.:")
                cuerpo = st.text_area("Cuerpo de la Nota:", height=180)

            asunto_ref = limpiar_texto(asunto_ref)
            cuerpo = limpiar_texto(cuerpo)
            
            submitted = st.form_submit_button("🚀 Generar Documento y Guardar en el Índice")

        if submitted:
            guardar_documento(tipo_doc, num_doc, anio_doc, lugar_fecha, dest_final, asunto_ref, cuerpo, iniciales)
            st.success(f"✅ Registrado en el índice general: **{tipo_doc} N° {num_doc}/{anio_doc}**.")
            st.rerun()

        leyenda_oficial = "“Año de la Innovación y Modernización del Estado de la Provincia del Chubut”"
        contacto_pie = "Mariano Moreno y Luis Costa | Rawson | Chubut (Teléfono 280-4485125/126)"
        
        if tipo_doc == "Memorándum":
            pie_formateado = f"Memo Nº {siguiente_num}/{anio_actual} –DAP- SsFyCP-MP ({iniciales})"
            doc_encabezado_texto = f"{dest_final}"
            doc_cuerpo_completo = f"{cuerpo}\n\nSin más que agregar, saludo a usted muy atentamente.\n\n\n{pie_formateado}"
            es_duplicado = False
        elif tipo_doc == "Pase Administrativo":
            pie_formateado = f"Pase N° {siguiente_num}/{anio_actual}-dap-SsFyCP-MP({iniciales})"
            doc_encabezado_texto = f"{dest_final}"
            doc_cuerpo_completo = f"{cuerpo}\n\n\n{pie_formateado}"
            es_duplicado = True
        else: # Nota Oficial
            pie_formateado = f"Nota N° {siguiente_num}/{anio_actual} DAP-SsFyCP- Ministerio de Producción ({iniciales})"
            doc_encabezado_texto = f"{dest_final}"
            doc_cuerpo_completo = f"De mi mayor consideración:\n\n{cuerpo}\n\nSin otro particular, saludo a Ud. atentamente.\n\n\n({iniciales}) {pie_formateado}"
            es_duplicado = False

        st.markdown("---")
        st.subheader("📄 Vista Previa e Impresión del Documento")
        
        def generar_html_bloque():
            ref_div = f'<div style="text-align: right; font-size: 11pt; margin-bottom: 15px;"><strong>Ref.:</strong> {asunto_ref}</div>' if asunto_ref else ''
            return f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <span style="font-style: italic; font-size: 10pt; font-weight: bold; color: #2d3748;">{leyenda_oficial}</span>
            </div>
            <div style="border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px; display: flex; align-items: center; gap: 12px;">
                <div style="text-align: left; border-right: 3px solid #ed8936; padding-right: 12px;">
                    <strong style="font-size: 13pt; color: #1a202c; display: block; line-height: 1.1;">Gobierno<br>del Chubut</strong>
                </div>
                <div style="text-align: left; padding-left: 2px;">
                    <strong style="font-size: 13pt; color: #1a202c; display: block; line-height: 1.1;">Ministerio de<br>Producción</strong>
                </div>
            </div>
            <div style="text-align: right; font-weight: bold; font-size: 11pt; margin-bottom: 15px;">{lugar_fecha}</div>
            <div style="font-size: 11pt; margin-bottom: 15px; white-space: pre-line;">{doc_encabezado_texto}</div>
            {ref_div}
            <div style="font-size: 11pt; line-height: 1.5; margin-bottom: 25px; white-space: pre-line; text-align: justify;">{doc_cuerpo_completo}</div>
            <div style="font-size: 8pt; color: gray; text-align: center; margin-top: 25px; border-top: 1px solid #eee; padding-top: 5px;">{contacto_pie}</div>
            """

        bloque_unico = generar_html_bloque()
        
        if es_duplicado:
            html_imprimir = f"""
            <div id="documento-imprimir" style="font-family: Verdana, Geneva, sans-serif; padding: 20px; border: 1px solid #ccc; background-color: #fff; line-height: 1.5;">
                {bloque_unico}
                <div style="border-top: 2px dashed #a0aec0; margin: 30px 0; text-align: center; font-size: 9pt; color: #718096; padding-top: 5px;">
                    ✂️ ORIGINAL Y DUPLICADO EN LA MISMA HOJA
                </div>
                {bloque_unico}
            </div>
            """
        else:
            html_imprimir = f"""
            <div id="documento-imprimir" style="font-family: Verdana, Geneva, sans-serif; padding: 25px; border: 1px solid #ccc; background-color: #fff; line-height: 1.5;">
                {bloque_unico}
            </div>
            """
        
        st.markdown(html_imprimir, unsafe_allow_html=True)
        
        doc_texto_descarga = f"{lugar_fecha}\n\n{doc_encabezado_texto}\nRef.: {asunto_ref}\n\n{doc_cuerpo_completo}"
        if es_duplicado:
            doc_texto_descarga += f"\n\n==================== DUPLICADO ====================\n\n{lugar_fecha}\n\n{doc_encabezado_texto}\nRef.: {asunto_ref}\n\n{doc_cuerpo_completo}"

        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                label="📥 Descargar Documento (.txt)",
                data=doc_texto_descarga,
                file_name=f"{tipo_doc.lower().replace(' ', '_')}_{siguiente_num}_{anio_actual}.txt",
                mime="text/plain"
            )
        with col_btn2:
            st.markdown("""
                <button onclick="window.print()" style="background-color: #2b6cb0; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold; width: 100%;">
                    🖨️ Imprimir o Guardar como PDF
                </button>
            """, unsafe_allow_html=True)

with pestana2:
    st.markdown("### 🔍 Buscador General de Documentos")
    busqueda = st.text_input("Buscar por expediente, motivo, asunto, destinatario o tipo:", value="")
    
    resultados = buscar_documentos(busqueda)
    
    if resultados:
        for item in resultados:
            doc_id, t_doc, n_doc, a_doc, f_doc, d_doc, as_doc = item
            with st.expander(f"📌 {t_doc} N° {n_doc}/{a_doc} — Ref: {as_doc}"):
                st.write(f"**Fecha:** {f_doc}")
                st.write(f"**Destinatario:** {d_doc}")
                st.write(f"**Referencia / Motivo:** {as_doc}")
    else:
        st.info("No se encontraron documentos registrados con ese criterio de búsqueda.")
