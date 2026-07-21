import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN (ACCESO POR TOKEN) ---
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

if st.session_state.auth_token is None:
    st.title("🛡️ Acceso ONE Track")
    token = st.text_input("Introduce tu palabra de acceso (Token):", type="password")
    if st.button("Entrar al Sistema"):
        if token:
            st.session_state.auth_token = token
            st.rerun()
    st.stop()

token_actual = st.session_state.auth_token

# --- LÓGICA DE CARGA DE DATOS ---
@st.cache_data(ttl=10) # El caché se limpia cada 10 segundos
def cargar_tablas(sheet_name):
    try:
        df_total = conn.read(worksheet=sheet_name)
        # Filtramos por el token del usuario actual
        df_user = df_total[df_total['onetrack_id'] == token_actual]
        return df_user, df_total
    except Exception as e:
        st.error(f"Error leyendo {sheet_name}. Asegúrate de que la pestaña exista y tenga datos.")
        return pd.DataFrame(), pd.DataFrame()

# Cargamos las 4 tablas
df_kpis_user, df_kpis_total = cargar_tablas("KPIs")
df_okrs_user, df_okrs_total = cargar_tablas("OKRs_General")
df_crit_user, df_crit_total = cargar_tablas("OKR_Criterios")
df_hitos_user, df_hitos_total = cargar_tablas("OKR_Hitos")

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.write(f"**Usuario / Token:** {token_actual}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth_token = None
    st.cache_data.clear()
    st.rerun()

st.title(f"🚀 ONE Track: Ciclo Anual")

tab_kpis, tab_okrs = st.tabs(["📊 KPIs (Números Inteligentes)", "🎯 OKRs (Prioridades y Tácticas)"])

# --- PESTAÑA 1: KPIs ---
with tab_kpis:
    st.subheader("Indicadores Generales (Ene - Dic)")
    st.info("Desplázate hacia la derecha para ver todos los meses. Doble clic para editar.")
    
    # Editor de KPIs
    edit_kpis = st.data_editor(df_kpis_user, num_rows="dynamic", use_container_width=True, key="ed_kpis")

# --- PESTAÑA 2: OKRs ---
with tab_okrs:
    st.subheader("Estructura de OKRs")
    
    with st.expander("1. Definición General de OKRs", expanded=True):
        st.write("Agrega aquí tus Objetivos y asígnales un `OKR_ID` único (ej. 1, 2, 3...).")
        edit_okrs = st.data_editor(df_okrs_user, num_rows="dynamic", use_container_width=True, key="ed_okrs")
        
    with st.expander("2. Criterios de Éxito (Métricas)", expanded=False):
        st.write("Asegúrate de que el `OKR_ID` coincida con el objetivo que definiste arriba.")
        edit_crit = st.data_editor(df_crit_user, num_rows="dynamic", use_container_width=True, key="ed_crit")

    with st.expander("3. Hitos y Acciones Clave (Tácticas)", expanded=False):
        st.write("Registra las tareas, fechas y progreso mensual vinculado a cada `OKR_ID`.")
        edit_hitos = st.data_editor(df_hitos_user, num_rows="dynamic", use_container_width=True, key="ed_hitos")

# --- LÓGICA DE GUARDADO GLOBAL ---
st.sidebar.divider()
st.sidebar.markdown("### 💾 Guardar Avance")

def guardar_tabla(df_editado, df_total, sheet_name):
    # Aseguramos que el token esté en todas las filas nuevas
    df_editado['onetrack_id'] = token_actual
    
    # Mantenemos los datos de otros usuarios
    df_otros = df_total[df_total['onetrack_id'] != token_actual]
    
    # Unimos y guardamos
    df_final = pd.concat([df_otros, df_editado], ignore_index=True)
    conn.update(worksheet=sheet_name, data=df_final)

if st.sidebar.button("Sincronizar Todo con la Nube", type="primary"):
    with st.spinner('Guardando en Google Sheets...'):
        guardar_tabla(edit_kpis, df_kpis_total, "KPIs")
        guardar_tabla(edit_okrs, df_okrs_total, "OKRs_General")
        guardar_tabla(edit_crit, df_crit_total, "OKR_Criterios")
        guardar_tabla(edit_hitos, df_hitos_total, "OKR_Hitos")
        
        st.cache_data.clear() # Limpiamos caché para traer lo más nuevo
    st.sidebar.success("¡Datos guardados correctamente!")