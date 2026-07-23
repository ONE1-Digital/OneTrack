import streamlit as st
import pandas as pd

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

st.markdown("""
    <style>
    .stExpander { border-left: 5px solid #002060; background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXION A BASE DE DATOS ---
conn = st.connection("supabase", type="sql")

# --- LOGIN ---
if 'auth_token' not in st.session_state or st.session_state.auth_token is None:
    st.title("Acceso ONE Track")
    token = st.text_input("Palabra de acceso (Token):", type="password")
    if st.button("Entrar"):
        st.session_state.auth_token = token
        st.session_state.datos_cargados = False # Bandera para cargar datos solo una vez
        st.rerun()
    st.stop()

token = st.session_state.auth_token

# --- ESTRUCTURA DE MESES POR TRIMESTRE ---
trimestres = {
    "Q1": ["Ene", "Feb", "Mar"],
    "Q2": ["Abr", "May", "Jun"],
    "Q3": ["Jul", "Ago", "Sep"],
    "Q4": ["Oct", "Nov", "Dic"]
}

# --- CARGA DE DATOS DESDE LA NUBE A LA MEMORIA ---
def cargar_datos_desde_bd():
    if st.session_state.get('datos_cargados', False):
        return

    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{token}'")
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{token}'")
        df_crit = conn.query(f"SELECT * FROM okr_criterios WHERE onetrack_id = '{token}'")
    except Exception:
        df_kpis, df_okrs, df_crit = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    for q_name, meses in trimestres.items():
        for i in range(1, 6):
            indice = i - 1 # Indice real del DataFrame (0 a 4)
            
            # --- Mapeo de KPIs ---
            kpi_base = f"kpi_{q_name}_{i}"
            if not df_kpis.empty and indice < len(df_kpis):
                row = df_kpis.iloc[indice]
                st.session_state[f"{kpi_base}_nom"] = str(row.get("KPI_Nombre", ""))
                st.session_state[f"{kpi_base}_tipo"] = str(row.get("Tipo", "Acumulado"))
                st.session_state[f"{kpi_base}_meta"] = float(row.get("Meta", 0.0))
                st.session_state[f"{kpi_base}_um"] = str(row.get("UM", "U"))
                st.session_state[f"{kpi_base}_menor"] = str(row.get("< Mejor", "NO"))
                st.session_state[f"{kpi_base}_peso"] = float(row.get("Peso_%", 20.0))
                for mes in meses:
                    st.session_state[f"{kpi_base}_p_{mes}"] = float(row.get(f"{mes}_P", 0.0))
                    st.session_state[f"{kpi_base}_r_{mes}"] = float(row.get(f"{mes}_R", 0.0))
            else:
                # Valores por defecto si no hay datos
                st.session_state[f"{kpi_base}_nom"] = ""
                st.session_state[f"{kpi_base}_tipo"] = "Acumulado"
                st.session_state[f"{kpi_base}_meta"] = 0.0
                st.session_state[f"{kpi_base}_um"] = "U"
                st.session_state[f"{kpi_base}_menor"] = "NO"
                st.session_state[f"{kpi_base}_peso"] = 20.0
                for mes in meses:
                    st.session_state[f"{kpi_base}_p_{mes}"] = 0.0
                    st.session_state[f"{kpi_base}_r_{mes}"] = 0.0

            # --- Mapeo de OKRs ---
            okr_base = f"okr_{q_name}_{i}"
            if not df_okrs.empty and indice < len(df_okrs):
                row_o = df_okrs.iloc[indice]
                st.session_state[f"{okr_base}_nom"] = str(row_o.get("OKR_Nombre", ""))
                st.session_state[f"{okr_base}_obj"] = str(row_o.get("Objetivo", ""))
                st.session_state[f"{okr_base}_peso"] = float(row_o.get("Peso_%", 20.0))
            else:
                st.session_state[f"{okr_base}_nom"] = ""
                st.session_state[f"{okr_base}_obj"] = ""
                st.session_state[f"{okr_base}_peso"] = 20.0

            if not df_crit.empty and indice < len(df_crit):
                row_c = df_crit.iloc[indice]
                st.session_state[f"{okr_base}_crit"] = str(row_c.get("Criterio_Nombre", ""))
                st.session_state[f"{okr_base}_crit_meta"] = float(row_c.get("Meta", 0.0))
                for mes in meses:
                    st.session_state[f"{okr_base}_p_{mes}"] = float(row_c.get(f"{mes}_P", 0.0))
                    st.session_state[f"{okr_base}_r_{mes}"] = float(row_c.get(f"{mes}_R", 0.0))
            else:
                st.session_state[f"{okr_base}_crit"] = ""
                st.session_state[f"{okr_base}_crit_meta"] = 0.0
                for mes in meses:
                    st.session_state[f"{okr_base}_p_{mes}"] = 0.0
                    st.session_state[f"{okr_base}_r_{mes}"] = 0.0

    st.session_state.datos_cargados = True

# Ejecutamos la carga antes de pintar la interfaz
cargar_datos_desde_bd()

# --- FUNCIONES DE INTERFAZ (CELULAS DE CAPTURA) ---
def renderizar_celula_kpi(indice, q_name, meses):
    kpi_base = f"kpi_{q_name}_{indice}"
    
    with st.expander(f"KPI #{indice} - [Clic para editar]", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.text_input("Nombre del KPI", key=f"{kpi_base}_nom")
        c2.selectbox("Tipo", ["Acumulado", "Promedio", "Valor Final"], key=f"{kpi_base}_tipo")
        c3.number_input("Meta Trimestral", key=f"{kpi_base}_meta")
        
        c4, c5, c6 = st.columns(3)
        c4.selectbox("Unidad de Medida", ["U", "$", "%", "Horas"], key=f"{kpi_base}_um")
        c5.selectbox("Menor es Mejor?", ["NO", "SI"], key=f"{kpi_base}_menor")
        c6.number_input("Peso (%)", key=f"{kpi_base}_peso")
        
        st.divider()
        st.write("Avance Mensual")
        
        m_cols = st.columns(3)
        for i, mes in enumerate(meses):
            with m_cols[i]:
                st.markdown(f"**{mes}**")
                st.number_input("Programado", key=f"{kpi_base}_p_{mes}")
                st.number_input("Real", key=f"{kpi_base}_r_{mes}")

def renderizar_celula_okr(indice, q_name, meses):
    okr_base = f"okr_{q_name}_{indice}"
    
    with st.expander(f"OKR #{indice} - [Clic para editar]", expanded=False):
        st.text_input("Nombre del OKR (Prioridad)", key=f"{okr_base}_nom")
        st.text_area("Objetivo Estrategico", height=68, key=f"{okr_base}_obj")
        st.number_input("Peso Global del OKR (%)", key=f"{okr_base}_peso")
        
        st.divider()
        st.write("Criterio de Exito Principal")
        col_c1, col_c2 = st.columns(2)
        col_c1.text_input("Nombre del Criterio", key=f"{okr_base}_crit")
        col_c2.number_input("Meta del Criterio", key=f"{okr_base}_crit_meta")
        
        st.write("Avance del Criterio")
        m_cols = st.columns(3)
        for i, mes in enumerate(meses):
            with m_cols[i]:
                st.markdown(f"**{mes}**")
                st.number_input("Prog.", key=f"{okr_base}_p_{mes}")
                st.number_input("Real", key=f"{okr_base}_r_{mes}")

# --- NAVEGACION PRINCIPAL ---
st.sidebar.title("Panel de Control")
st.sidebar.caption("Sesion Activa")

menu = st.sidebar.radio("Navegacion:", ["Entrada de Datos", "Dashboard de Resultados"])

st.sidebar.divider()
if st.sidebar.button("Cerrar Sesion"):
    st.session_state.auth_token = None
    st.session_state.datos_cargados = False
    st.rerun()

# --- SECCION 1: ENTRADA DE DATOS ---
st.sidebar.divider()
    
    # Funcion para empaquetar y guardar en la base de datos
    def guardar_en_bd():
        # 1. Recolectar KPIs (5 en total, uniendo los 4 trimestres)
        kpis_data = []
        okrs_data = []
        crit_data = []
        
        for i in range(1, 6):
            # Tomamos la configuracion base (nombres, metas, pesos) del Q1
            kpi_row = {
                "onetrack_id": token,
                "KPI_Nombre": st.session_state.get(f"kpi_Q1_{i}_nom", ""),
                "Tipo": st.session_state.get(f"kpi_Q1_{i}_tipo", "Acumulado"),
                "Meta": st.session_state.get(f"kpi_Q1_{i}_meta", 0.0),
                "UM": st.session_state.get(f"kpi_Q1_{i}_um", "U"),
                "< Mejor": st.session_state.get(f"kpi_Q1_{i}_menor", "NO"),
                "Peso_%": st.session_state.get(f"kpi_Q1_{i}_peso", 20.0)
            }
            
            okr_row = {
                "onetrack_id": token,
                "OKR_ID": i,
                "OKR_Nombre": st.session_state.get(f"okr_Q1_{i}_nom", ""),
                "Objetivo": st.session_state.get(f"okr_Q1_{i}_obj", ""),
                "Peso_%": st.session_state.get(f"okr_Q1_{i}_peso", 20.0)
            }
            
            crit_row = {
                "onetrack_id": token,
                "OKR_ID": i,
                "Criterio_Nombre": st.session_state.get(f"okr_Q1_{i}_crit", ""),
                "Meta": st.session_state.get(f"okr_Q1_{i}_crit_meta", 0.0)
            }
            
            # Recorremos los trimestres para recolectar los meses y añadirlos a la misma fila
            for q_name, meses in trimestres.items():
                for mes in meses:
                    kpi_row[f"{mes}_P"] = st.session_state.get(f"kpi_{q_name}_{i}_p_{mes}", 0.0)
                    kpi_row[f"{mes}_R"] = st.session_state.get(f"kpi_{q_name}_{i}_r_{mes}", 0.0)
                    
                    crit_row[f"{mes}_P"] = st.session_state.get(f"okr_{q_name}_{i}_p_{mes}", 0.0)
                    crit_row[f"{mes}_R"] = st.session_state.get(f"okr_{q_name}_{i}_r_{mes}", 0.0)
            
            # Solo guardamos si el usuario le puso nombre al KPI/OKR
            if kpi_row["KPI_Nombre"] != "": kpis_data.append(kpi_row)
            if okr_row["OKR_Nombre"] != "": 
                okrs_data.append(okr_row)
                crit_data.append(crit_row)
                
        # Convertimos a DataFrames
        df_kpis = pd.DataFrame(kpis_data)
        df_okrs = pd.DataFrame(okrs_data)
        df_crit = pd.DataFrame(crit_data)
        
        # Funcion interna de sincronizacion segura con Supabase
        def sync_tabla(df_nuevo, table_name):
            if df_nuevo.empty: return
            try:
                df_total = conn.query(f"SELECT * FROM {table_name}")
                df_otros = df_total[df_total['onetrack_id'] != token]
                df_final = pd.concat([df_otros, df_nuevo], ignore_index=True)
            except Exception:
                df_final = df_nuevo
            df_final.to_sql(table_name, con=conn.engine, if_exists='replace', index=False)

        # Ejecutamos el guardado
        sync_tabla(df_kpis, "kpis")
        sync_tabla(df_okrs, "okrs_general")
        sync_tabla(df_crit, "okr_criterios")

    if st.sidebar.button("Guardar Cambios", type="primary"):
        with st.spinner("Sincronizando con la nube..."):
            guardar_en_bd()
            # Reiniciamos la bandera de carga para que al cambiar de menu traiga lo mas nuevo
            st.session_state.datos_cargados = False 
        st.sidebar.success("Datos guardados exitosamente.")

# --- SECCION 2: DASHBOARD DE RESULTADOS ---
elif menu == "Dashboard de Resultados":
    st.title("ONE Track: Visualizacion de Resultados")
    
    tabs_dash = st.tabs(["Resultados Q1", "Resultados Q2", "Resultados Q3", "Resultados Q4", "Resumen Anual"])
    
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_dash[q_idx]:
            st.header(f"Dashboard {q_name}")
            st.info(f"Aqui se mostraran los semaforos y graficas de rendimiento para los meses de {', '.join(trimestres[q_name])}.")
            
    with tabs_dash[4]:
        st.header("Dashboard Anual")
        st.info("Aqui visualizaremos el condensado global comparando el desempeño de los 4 trimestres.")
    with tabs_dash[4]:
        st.header("Dashboard Anual")
        st.info("Aqui visualizaremos el condensado global comparando el desempeño de los 4 trimestres.")

