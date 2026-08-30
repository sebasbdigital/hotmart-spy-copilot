import streamlit as st
import pandas as pd
from google import genai
import os

# Configuración de página estilo SaaS moderno
st.set_page_config(
    page_title="Hotmart Spy & Copilot",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual moderno
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

# Archivo de persistencia de datos
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

# Barra lateral
st.sidebar.title("🔥 Hotmart Spy V1")
api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password", placeholder="Pega tu clave aquí")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Fórmula Orgánica:** Busca productos con comisiones >$20 USD, temperaturas de 20°-75° y cuentas con videos >100k vistas.")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📊 Radar de Ganadores", "➕ Agregar Producto", "🤖 Copiloto IA (Estratega)"])

with tab1:
    st.header("🎯 Radar de Productos y Métricas")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Productos", len(df))
    col2.metric("Mejor Score Ganador", f"{int(df['Score'].max())} pts" if not df.empty else "0")
    col3.metric("Comisión Promedio", f"${df['Comision'].mean():.2f} USD" if not df.empty else "$0")
    
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
                help="Puntuación de 0 a 100",
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
    st.header("➕ Cazar y Analizar Nuevo Producto")
    with st.form("nuevo_producto_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nombre = st.text_input("Nombre del Curso en Hotmart:")
            nicho = st.text_input("Nicho / Categoría (ej: Belleza, Mascotas, Oficios):")
            precio = st.number_input("Precio de Venta ($USD):", min_value=1.0, value=49.0)
            comision = st.number_input("Tu Comisión Limpia ($USD):", min_value=1.0, value=35.0)
        with col_b:
            temperatura = st.number_input("Temperatura en Hotmart (0 a 150):", min_value=0, max_value=150, value=40)
            vistas = st.number_input("Vistas del Video más Viral en TikTok:", min_value=0, value=250000)
            cierre = st.selectbox("Estrategia de Cierre:", ["WhatsApp", "Web Directa"])
            cuenta = st.text_input("Cuenta de Referencia (ej: @cuenta_tiktok):")
            
        submitted = st.form_submit_button("🔥 Calcular Score y Guardar")
        
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
                st.success(f"¡Producto '{nombre}' agregado con éxito! Score Ganador: {score_calc} pts.")
                st.rerun()
            else:
                st.error("Por favor completa al menos el Nombre y el Nicho.")

with tab3:
    st.header("🤖 Copiloto IA: Ganchos, Guiones y Estrategia")
    
    if not api_key:
        st.warning("⚠️ Ingresa tu Gemini API Key en la barra lateral izquierda para activar el Asistente.")
    else:
        try:
            prod_opciones = df["Nombre"].tolist()
            prod_seleccionado = st.selectbox("Selecciona un producto de tu base de datos para analizar:", prod_opciones)
            prod_data = df[df["Nombre"] == prod_seleccionado].iloc[0].to_dict()
            
            if st.button("🚀 Generar Diagnóstico, 5 Hooks Virales y Guion Completo"):
                with st.spinner("La IA está analizando los datos y redactando la estrategia..."):
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    Actúa como un Director Creativo y Estratega de Afiliados Orgánico experto en Hotmart, TikTok y Reels.
                    Analiza este producto:
                    - Nombre: {prod_data['Nombre']}
                    - Nicho: {prod_data['Nicho']}
                    - Precio: ${prod_data['Precio']} USD
                    - Comisión: ${prod_data['Comision']} USD
                    - Temperatura: {prod_data['Temperatura']}°
                    - Vistas Video Viral: {prod_data['Vistas_Viral']}
                    - Cierre: {prod_data['Cierre']}
                    - Score Calculado: {prod_data['Score']} pts

                    Entrega un reporte estructurado, directo y listo para producción:
                    1. 🎯 VEREDICTO DE ELECCIÓN:
                       - ¿Por qué sí o no elegirlo?
                       - Dificultad para crear videos (Baja/Media/Alta) y por qué.
                    2. 🪝 5 GANCHOS (HOOKS) DE ALTO IMPACTO (Primeros 3 segundos):
                       - Hook 1 (Curiosidad Visual): Qué mostrar en pantalla + Texto + Audio.
                       - Hook 2 (Dolor / Deseo): Qué mostrar en pantalla + Texto + Audio.
                       - Hook 3 (Contraintuitivo / Rompe Mitos): Qué mostrar en pantalla + Texto + Audio.
                       - Hook 4 (Pregunta filtro): Qué mostrar en pantalla + Texto + Audio.
                       - Hook 5 (Prueba / Oportunidad): Qué mostrar en pantalla + Texto + Audio.
                    3. 🎬 GUION VIRAL DE 35 SEGUNDOS:
                       - [0-3s] Gancho
                       - [4-15s] Problema y Mecanismo Único
                       - [16-27s] Demostración / Solución
                       - [28-35s] Llamado a la Acción (CTA hacia {prod_data['Cierre']})
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )
                    st.markdown(response.text)
        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}")
