import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

# --- CONEXIÓN A SUPABASE (POSTGRESQL) ---
conn = st.connection("supabase", type="sql")

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

# --- LÓGICA DE CARGA DE DATOS (SQL) ---
@st.cache_data(ttl=10)
def cargar_tablas(table_name):
    try:
        # Leemos la tabla desde Supabase
        df_total = conn.query(f"SELECT * FROM {table_name}")
        # Filtramos por el usuario
        df_user = df_total[df_total['onetrack_id'] == token_actual]
        return df_user, df_total
    except Exception:
        # Si es la primera vez y la tabla no existe en la BD, creamos columnas vacías
        return pd.DataFrame([{"onetrack_id": token_actual, "Nombre/ID": "Ejemplo"}]), pd.DataFrame()

df_kpis_user, df_kpis_total = cargar_tablas("kpis")
df_okrs_user, df_okrs_total = cargar_tablas("okrs_general")
df_crit_user, df_crit_total = cargar_tablas("okr_criterios")
df_hitos_user, df_hitos_total = cargar_tablas("okr_hitos")

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.write(f"**Usuario / Token:** {token_actual}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth_token = None
    st.cache_data.clear()
    st.rerun()

st.title(f"🚀 ONE Track: Ciclo Anual")

tab_kpis, tab_okrs = st.tabs(["📊 KPIs", "🎯 OKRs"])

with tab_kpis:
    st.subheader("Indicadores Generales (Ene - Dic)")
    edit_kpis = st.data_editor(df_kpis_user, num_rows="dynamic", use_container_width=True, key="ed_kpis")

with tab_okrs:
    st.subheader("Estructura de OKRs")
    
    with st.expander("1. Definición General de OKRs", expanded=True):
        edit_okrs = st.data_editor(df_okrs_user, num_rows="dynamic", use_container_width=True, key="ed_okrs")
        
    with st.expander("2. Criterios de Éxito (Métricas)", expanded=False):
        edit_crit = st.data_editor(df_crit_user, num_rows="dynamic", use_container_width=True, key="ed_crit")

    with st.expander("3. Hitos y Acciones Clave (Tácticas)", expanded=False):
        edit_hitos = st.data_editor(df_hitos_user, num_rows="dynamic", use_container_width=True, key="ed_hitos")

# --- LÓGICA DE GUARDADO EN BD ---
st.sidebar.divider()
st.sidebar.markdown("### 💾 Guardar Avance")

def guardar_tabla(df_editado, df_total, table_name):
    if df_editado.empty: return
    
    df_editado['onetrack_id'] = token_actual
    
    if not df_total.empty:
        df_otros = df_total[df_total['onetrack_id'] != token_actual]
        df_final = pd.concat([df_otros, df_editado], ignore_index=True)
    else:
        df_final = df_editado
        
    # Escribimos en Supabase. Si la tabla no existe, Pandas la crea automáticamente.
    df_final.to_sql(table_name, con=conn.engine, if_exists='replace', index=False)

if st.sidebar.button("Sincronizar Todo con la Nube", type="primary"):
    with st.spinner('Guardando en Base de Datos...'):
        guardar_tabla(edit_kpis, df_kpis_total, "kpis")
        guardar_tabla(edit_okrs, df_okrs_total, "okrs_general")
        guardar_tabla(edit_crit, df_crit_total, "okr_criterios")
        guardar_tabla(edit_hitos, df_hitos_total, "okr_hitos")
        
        st.cache_data.clear()
    st.sidebar.success("¡Datos guardados correctamente!")

# --- 🧪 CÓDIGO TEMPORAL PARA DATOS DUMMY ---
st.sidebar.divider()
if st.sidebar.button("🧪 Inyectar Datos a 'ONETest'", type="secondary"):
    # Generar nombres de columnas de meses vacíos (Abr a Dic)
    meses_vacios = {f"{m}_{t}": 0 for m in ["Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"] for t in ["P","R"]}
    
    # 1. KPIs Dummy
    kpis_dummy = pd.DataFrame({
        "onetrack_id": ["ONETest"] * 3,
        "KPI_Nombre": ["Ventas Totales", "Defectos de Fábrica", "Satisfacción Cliente"],
        "Tipo": ["Acumulado", "Acumulado", "Promedio"],
        "Meta": [150000, 5, 95], "UM": ["$", "U", "%"], "< Mejor": ["NO", "SI", "NO"], "Peso_%": [50, 25, 25],
        "Ene_P": [50000, 2, 95], "Ene_R": [52000, 0, 92], # Ene: Ventas bien, Cero defectos (super verde)
        "Feb_P": [50000, 2, 95], "Feb_R": [48000, 3, 96], # Feb: Ventas bajan, Defectos suben (rojo)
        "Mar_P": [50000, 1, 95], "Mar_R": [55000, 1, 98], # Mar: Todo en orden
        **meses_vacios
    })

    # 2. OKRs Dummy
    okrs_dummy = pd.DataFrame({
        "onetrack_id": ["ONETest", "ONETest"], "OKR_ID": [1, 2],
        "OKR_Nombre": ["Expansión Nacional", "Eficiencia Operativa"],
        "Objetivo": ["Abrir 3 sucursales", "Reducir tiempos de entrega"], "Peso_%": [60, 40]
    })

    # 3. Criterios Dummy
    crit_dummy = pd.DataFrame({
        "onetrack_id": ["ONETest", "ONETest"], "OKR_ID": [1, 2],
        "Criterio_Nombre": ["Nuevas Sucursales", "Tiempo Promedio Entrega"],
        "Tipo": ["Acumulado", "Promedio"],
        "Meta": [3, 24], "UM": ["U", "Horas"], "< Mejor": ["NO", "SI"], "Peso_%": [100, 100],
        "Ene_P": [0, 48], "Ene_R": [0, 40], "Feb_P": [1, 36], "Feb_R": [1, 30], "Mar_P": [1, 24], "Mar_R": [0, 28],
        **meses_vacios
    })

    # 4. Hitos Dummy
    hitos_dummy = pd.DataFrame({
        "onetrack_id": ["ONETest", "ONETest", "ONETest"], "OKR_ID": [1, 1, 2],
        "Accion_Clave": ["Firma de local Monterrey", "Contratar Gerentes", "Migrar flotilla"],
        "Responsable": ["Ana", "Luis", "Carlos"],
        "Fecha_Inicio": ["2026-01-01", "2026-02-01", "2026-01-15"], "Fecha_Fin": ["2026-01-31", "2026-02-28", "2026-03-30"],
        "Peso_%": [50, 50, 100],
        "Ene_P": [100, 0, 30], "Ene_R": [100, 0, 35], "Feb_P": [0, 100, 30], "Feb_R": [0, 80, 20], "Mar_P": [0, 0, 40], "Mar_R": [0, 0, 10],
        **meses_vacios
    })

    # Ejecutar guardado (aprovechando tu función existente)
    with st.spinner('Inyectando datos...'):
        guardar_tabla(kpis_dummy, df_kpis_total, "kpis")
        guardar_tabla(okrs_dummy, df_okrs_total, "okrs_general")
        guardar_tabla(crit_dummy, df_crit_total, "okr_criterios")
        guardar_tabla(hitos_dummy, df_hitos_total, "okr_hitos")
        st.cache_data.clear()
        st.rerun()
