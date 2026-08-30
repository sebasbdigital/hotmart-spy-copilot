import streamlit as st
import pandas as pd
from google import genai
import os

st.set_page_config(
    page_title="Hotmart Spy & Copilot",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        background-color: #1a1c23;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2d3139;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "hotmart_products.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame([
            {
                "Nombre": "Curso Resina Epoxica",
                "Nicho": "Manualidades",
                "Precio": 49.0,
                "Comision": 35.0,
                "Temperatura": 45,
                "Vistas_Viral": 350000,
                "Cierre": "WhatsApp",
                "Cuenta_TikTok": "@resina_emprende",
                "Score": 93
            },
            {
                "Nombre": "Curso Excel Básico",
                "Nicho": "Ofimática",
                "Precio": 15.0,
                "Comision": 6.0,
                "Temperatura": 150,
                "Vistas_Viral": 15000,
                "Cierre": "Web Directa",
                "Cuenta_TikTok": "@excel_tips",
                "Score": 36
            },
            {
                "Nombre": "Hidroponía Casera",
                "Nicho": "Jardinería / Hogar",
                "Precio": 39.0,
                "Comision": 27.99,
                "Temperatura": 21,
                "Vistas_Viral": 8400000,
                "Cierre": "WhatsApp",
                "Cuenta_TikTok": "@metododehidrocultivo",
                "Score": 89
            }
        ])
        df.to_csv(DATA_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def calculate_score(comision, temperatura, vistas, cierre):
    score = 0
    if comision >= 35: score += 30
    elif comision >= 20: score += 22
    elif comision >= 10: score += 14
    else: score += 5
    
    if 20 <= temperatura <= 75: score += 25
    elif 75 < temperatura <= 150: score += 16
    elif temperatura < 20: score += 8
    else: score += 5
    
    if vistas >= 500000: score += 35
    elif vistas >= 100000: score += 28
    elif vistas >= 30000: score += 18
    elif vistas > 0: score += 8
    
    if "whatsapp" in str(cierre).lower(): score += 10
    else: score += 7
    
    return min(100, score)

df = load_data()

st.sidebar.title("Hotmart Spy V1")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", placeholder="Pega tu clave aqui")

st.sidebar.markdown("---")
st.sidebar.info("Estrategia Organica TikTok + Instagram:\n- 0 a 1k: Curiosidad y seguidores.\n- 1k a 3k: Puente a Instagram / Comentarios.\n- 3k+: Venta directa por WhatsApp.")

tab1, tab2, tab3 = st.tabs(["Radar de Ganadores", "Agregar Producto", "Copiloto IA (Estratega)"])

with tab1:
    st.header("Radar de Productos y Metricas")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Productos", len(df))
    col2.metric("Mejor Score Ganador", f"{int(df['Score'].max())} pts" if not df.empty else "0")
    col3.metric("Comision Promedio", f"${df['Comision'].mean():.2f} USD" if not df.empty else "$0")
    
    st.markdown("---")
    
    nichos = ["Todos"] + list(df["Nicho"].unique())
    nicho_sel = st.selectbox("Filtrar por Nicho:", nichos)
    
    df_filtered = df if nicho_sel == "Todos" else df[df["Nicho"] == nicho_sel]
    df_filtered = df_filtered.sort_values(by="Score", ascending=False)
    
    st.dataframe(
        df_filtered,
        use_container_width=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score Ganador",
                help="Puntuacion de 0 a 100",
                format="%d pts",
                min_value=0,
                max_value=100,
            ),
            "Precio": st.column_config.NumberColumn(format="$%.2f USD"),
            "Comision": st.column_config.NumberColumn(format="$%.2f USD"),
            "Vistas_Viral": st.column_config.NumberColumn(format="%d"),
        },
        hide_index=True
    )

with tab2:
    st.header("Cazar y Analizar Nuevo Producto")
    with st.form("nuevo_producto_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nombre = st.text_input("Nombre del Curso en Hotmart:")
            nicho = st.text_input("Nicho / Categoria (ej: Belleza, Mascotas, Oficios):")
            precio = st.number_input("Precio de Venta ($USD):", min_value=1.0, value=49.0)
            comision = st.number_input("Tu Comision Limpia ($USD):", min_value=1.0, value=35.0)
        with col_b:
            temperatura = st.number_input("Temperatura en Hotmart (0 a 150):", min_value=0, max_value=150, value=40)
            vistas = st.number_input("Vistas del Video mas Viral en TikTok:", min_value=0, value=250000)
            cierre = st.selectbox("Estrategia de Cierre:", ["WhatsApp", "Web Directa"])
            cuenta = st.text_input("Cuenta de Referencia (ej: @cuenta_tiktok):")
            
        submitted = st.form_submit_button("Calcular Score y Guardar")
        
        if submitted:
            if nombre and nicho:
                score_calc = calculate_score(comision, temperatura, vistas, cierre)
                nuevo_prod = {
                    "Nombre": nombre,
                    "Nicho": nicho,
                    "Precio": precio,
                    "Comision": comision,
                    "Temperatura": temperatura,
                    "Vistas_Viral": vistas,
                    "Cierre": cierre,
                    "Cuenta_TikTok": cuenta,
                    "Score": score_calc
                }
                df = pd.concat([df, pd.DataFrame([nuevo_prod])], ignore_index=True)
                save_data(df)
                st.success(f"Producto '{nombre}' agregado con exito. Score Ganador: {score_calc} pts.")
                st.rerun()
            else:
                st.error("Por favor completa al menos el Nombre y el Nicho.")

with tab3:
    st.header("Copiloto IA: Estratega Progresivo (Crecimiento a Ventas)")
    
    if not api_key:
        st.warning("Ingresa tu Gemini API Key en la barra lateral izquierda para activar el Asistente.")
    else:
        try:
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                prod_opciones = df["Nombre"].tolist()
                prod_seleccionado = st.selectbox("Selecciona el producto:", prod_opciones)
            with col_sel2:
                fase_estrategica = st.selectbox(
                    "En que fase esta tu cuenta actualmente?",
                    [
                        "Fase 1: Crecimiento y Seguidores (0 a 1k) - Cero Venta",
                        "Fase 2: Comunidad y Puente a Instagram (1k a 3k) - Lead Magnet",
                        "Fase 3: Cierre de Ventas por WhatsApp (3k+ seguidores)"
                    ]
                )
            
            prod_data = df[df["Nombre"] == prod_seleccionado].iloc[0].to_dict()
            
            if st.button("Generar Estrategia y Guiones para esta Fase"):
                with st.spinner("Conectando con la IA y redactando estrategia..."):
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    Actua como un Director Creativo y Estratega de Crecimiento en TikTok e Instagram para afiliados de Hotmart.
                    
                    DATOS DEL PRODUCTO:
                    - Nombre: {prod_data['Nombre']}
                    - Nicho: {prod_data['Nicho']}
                    - Comision: ${prod_data['Comision']} USD
                    - Vistas Viral Referencia: {prod_data['Vistas_Viral']}
                    
                    FASE ACTUAL DE LA CUENTA:
                    - {fase_estrategica}
                    
                    REGLAS OBLIGATORIAS POR FASE:
                    - Si es FASE 1 (0 a 1k): NO VENDAS NADA. El objetivo es SOLO viralizar, ganar seguidores y guardados. El llamado a la accion (CTA) debe ser 'Sigueme para ver la parte 2' o 'Guarda este tip para cuando lo intentes'.
                    - Si es FASE 2 (1k a 3k): El objetivo es llevar trafico hacia el boton de Instagram o pedir comentarios como 'Comenta HUERTO para enviarte la guia gratuita por privado'.
                    - Si es FASE 3 (3k+): Objetivo vender el curso con oferta irresistible y cierre por WhatsApp.

                    ENTREGA TU REPORTE CON ESTA ESTRUCTURA:
                    1. ENFOQUE DE LA FASE: Metrica principal y objetivo de esta semana.
                    2. 5 HOOKS VIRALES (Primeros 3 segundos):
                       - Hook 1 (Curiosidad Visual): Que mostrar + Texto + Audio.
                       - Hook 2 (Dolor / Error comun): Que mostrar + Texto + Audio.
                       - Hook 3 (Contraintuitivo): Que mostrar + Texto + Audio.
                       - Hook 4 (Pregunta filtro): Que mostrar + Texto + Audio.
                       - Hook 5 (Resultado rapido): Que mostrar + Texto + Audio.
                    3. 2 GUIONES COMPLETOS DE 30 SEGUNDOS (Segundo a segundo con Visual, Texto, Voz y el CTA exacto de la fase).
                    4. ESTRATEGIA SINCRONIZADA TIKTOK + INSTAGRAM (Que publicar en TikTok y como apalancarlo en Instagram).
                    """
                    
                    # Lista de modelos con respaldo automático
                    modelos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro"]
                    respuesta_texto = None
                    
                    for mod in modelos:
                        try:
                            res = client.models.generate_content(
                                model=mod,
                                contents=prompt
                            )
                            if res and res.text:
                                respuesta_texto = res.text
                                break
                        except Exception:
                            continue
                            
                    if respuesta_texto:
                        st.markdown(respuesta_texto)
                    else:
                        st.error("Los servidores de IA están saturados temporalmente. Intenta nuevamente en 30 segundos.")
        except Exception as e:
            st.error(f"Error: {e}")
