import streamlit as st
import pandas as pd

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

st.markdown("""
    <style>
    .stExpander { border-left: 5px solid #002060; background-color: #f8f9fa; }
    .metric-card { padding: 15px; border-radius: 8px; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-title { margin: 0 0 5px 0; font-size: 18px; font-weight: bold; color: white;}
    .metric-data { margin: 0; font-size: 14px; opacity: 0.9; }
    .metric-perc { margin: 10px 0 0 0; font-size: 28px; font-weight: bold; }
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
        st.session_state.datos_cargados = False
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

    # Cargar configuracion global del semaforo desde el primer KPI (si existe)
    if not df_kpis.empty:
        st.session_state["global_u_ama"] = float(df_kpis.iloc[0].get("U_Amarillo", 80.0))
        st.session_state["global_u_ver"] = float(df_kpis.iloc[0].get("U_Verde", 100.0))
        st.session_state["global_u_sve"] = float(df_kpis.iloc[0].get("U_SVerde", 115.0))
    else:
        st.session_state["global_u_ama"] = 80.0
        st.session_state["global_u_ver"] = 100.0
        st.session_state["global_u_sve"] = 115.0

    for q_name, meses in trimestres.items():
        for i in range(1, 6):
            indice = i - 1 
            
            # Carga KPIs
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
                st.session_state[f"{kpi_base}_nom"] = ""
                st.session_state[f"{kpi_base}_tipo"] = "Acumulado"
                st.session_state[f"{kpi_base}_meta"] = 0.0
                st.session_state[f"{kpi_base}_um"] = "U"
                st.session_state[f"{kpi_base}_menor"] = "NO"
                st.session_state[f"{kpi_base}_peso"] = 20.0
                for mes in meses:
                    st.session_state[f"{kpi_base}_p_{mes}"] = 0.0
                    st.session_state[f"{kpi_base}_r_{mes}"] = 0.0

            # Carga OKRs
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

cargar_datos_desde_bd()

# --- FUNCIONES DE INTERFAZ (ENTRADA) ---
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

# --- LOGICA DEL DASHBOARD ---
def calcular_cumplimiento(prog, real, menor_mejor):
    if prog == 0 and real == 0: return 0.0
    if menor_mejor == "SI":
        return (prog / real * 100) if real > 0 else 100.0
    else:
        return (real / prog * 100) if prog > 0 else (100.0 if real > 0 else 0.0)

def obtener_color(cump, ama, ver, sve):
    if cump >= sve: return "#004d00"
    elif cump >= ver: return "#28a745"
    elif cump >= ama: return "#ffc107"
    else: return "#dc3545"

def dibujar_tarjeta(titulo, subtitulo, prog, real, um, cump, color):
    st.markdown(f"""
        <div class="metric-card" style="background-color: {color}; color: {'black' if color == '#ffc107' else 'white'};">
            <p class="metric-title" style="color: {'black' if color == '#ffc107' else 'white'};">{titulo}</p>
            <p class="metric-data">{subtitulo}</p>
            <p class="metric-data">Prog: {prog:,.2f} {um} | Real: {real:,.2f} {um}</p>
            <p class="metric-perc">{cump:.1f}%</p>
        </div>
    """, unsafe_allow_html=True)

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
if menu == "Entrada de Datos":
    st.title("ONE Track: Captura de Datos")
    
    # Se agrega la pestaña de Configuración Global
    tabs_datos = st.tabs(["Configuracion Global", "Q1 (Ene-Mar)", "Q2 (Abr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dic)"])
    
    with tabs_datos[0]:
        st.header("Configuracion de Semaforo Global")
        st.write("Establece los limites de cumplimiento (%) aplicables para todos los KPIs y OKRs.")
        
        # Sliders graficos interactivos
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.slider("Limite Minimo: Amarillo (%)", min_value=0.0, max_value=100.0, step=1.0, key="global_u_ama", help="Cualquier valor menor a este sera marcado en Rojo.")
            st.slider("Limite Minimo: Verde (%)", min_value=50.0, max_value=120.0, step=1.0, key="global_u_ver")
        with col_s2:
            st.slider("Limite Minimo: Super Verde (%)", min_value=100.0, max_value=200.0, step=1.0, key="global_u_sve", help="Desempeño sobresaliente.")
            
        st.info("Nota: Estos limites aplicaran automaticamente a todas tus celdas en el Dashboard.")
    
    # Renderizamos los trimestres (tabs del 1 al 4)
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_datos[q_idx + 1]:
            meses_q = trimestres[q_name]
            
            st.header(f"Planificacion {q_name}")
            
            st.subheader("1. KPIs (Numeros Inteligentes)")
            for i in range(1, 6): 
                renderizar_celula_kpi(i, q_name, meses_q)
                
            st.subheader("2. OKRs (Prioridades)")
            for i in range(1, 6): 
                renderizar_celula_okr(i, q_name, meses_q)
                
    st.sidebar.divider()
    
    def guardar_en_bd():
        kpis_data = []
        okrs_data = []
        crit_data = []
        
        # Recuperamos la configuracion global
        g_ama = st.session_state.get("global_u_ama", 80.0)
        g_ver = st.session_state.get("global_u_ver", 100.0)
        g_sve = st.session_state.get("global_u_sve", 115.0)
        
        for i in range(1, 6):
            kpi_row = {
                "onetrack_id": token,
                "KPI_Nombre": st.session_state.get(f"kpi_Q1_{i}_nom", ""),
                "Tipo": st.session_state.get(f"kpi_Q1_{i}_tipo", "Acumulado"),
                "Meta": st.session_state.get(f"kpi_Q1_{i}_meta", 0.0),
                "UM": st.session_state.get(f"kpi_Q1_{i}_um", "U"),
                "< Mejor": st.session_state.get(f"kpi_Q1_{i}_menor", "NO"),
                "Peso_%": st.session_state.get(f"kpi_Q1_{i}_peso", 20.0),
                "U_Amarillo": g_ama,
                "U_Verde": g_ver,
                "U_SVerde": g_sve
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
                "Meta": st.session_state.get(f"okr_Q1_{i}_crit_meta", 0.0),
                "U_Amarillo": g_ama,
                "U_Verde": g_ver,
                "U_SVerde": g_sve
            }
            
            for q_name, meses in trimestres.items():
                for mes in meses:
                    kpi_row[f"{mes}_P"] = st.session_state.get(f"kpi_{q_name}_{i}_p_{mes}", 0.0)
                    kpi_row[f"{mes}_R"] = st.session_state.get(f"kpi_{q_name}_{i}_r_{mes}", 0.0)
                    
                    crit_row[f"{mes}_P"] = st.session_state.get(f"okr_{q_name}_{i}_p_{mes}", 0.0)
                    crit_row[f"{mes}_R"] = st.session_state.get(f"okr_{q_name}_{i}_r_{mes}", 0.0)
            
            if kpi_row["KPI_Nombre"] != "": kpis_data.append(kpi_row)
            if okr_row["OKR_Nombre"] != "": 
                okrs_data.append(okr_row)
                crit_data.append(crit_row)
                
        df_kpis = pd.DataFrame(kpis_data)
        df_okrs = pd.DataFrame(okrs_data)
        df_crit = pd.DataFrame(crit_data)
        
        def sync_tabla(df_nuevo, table_name):
            if df_nuevo.empty: return
            try:
                df_total = conn.query(f"SELECT * FROM {table_name}")
                df_otros = df_total[df_total['onetrack_id'] != token]
                df_final = pd.concat([df_otros, df_nuevo], ignore_index=True)
            except Exception:
                df_final = df_nuevo
            df_final.to_sql(table_name, con=conn.engine, if_exists='replace', index=False)

        sync_tabla(df_kpis, "kpis")
        sync_tabla(df_okrs, "okrs_general")
        sync_tabla(df_crit, "okr_criterios")

    if st.sidebar.button("Guardar Cambios", type="primary"):
        with st.spinner("Sincronizando con la nube..."):
            guardar_en_bd()
            st.session_state.datos_cargados = False 
        st.sidebar.success("Datos guardados exitosamente.")

# --- SECCION 2: DASHBOARD DE RESULTADOS ---
elif menu == "Dashboard de Resultados":
    st.title("ONE Track: Dashboard Estrategico")
    
    # Recuperar configuracion global para pintar
    g_ama = st.session_state.get("global_u_ama", 80.0)
    g_ver = st.session_state.get("global_u_ver", 100.0)
    g_sve = st.session_state.get("global_u_sve", 115.0)
    
    tabs_dash = st.tabs(["Resultados Q1", "Resultados Q2", "Resultados Q3", "Resultados Q4", "Resumen Anual"])
    
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_dash[q_idx]:
            meses_q = trimestres[q_name]
            st.header(f"Desempeño {q_name}")
            
            # --- RENDERIZAR KPIs ---
            st.subheader("Indicadores Clave (KPIs)")
            kpi_cols = st.columns(5)
            for i in range(1, 6):
                nombre = st.session_state.get(f"kpi_{q_name}_{i}_nom", "")
                if nombre != "":
                    t_prog = sum([st.session_state.get(f"kpi_{q_name}_{i}_p_{m}", 0.0) for m in meses_q])
                    t_real = sum([st.session_state.get(f"kpi_{q_name}_{i}_r_{m}", 0.0) for m in meses_q])
                    um = st.session_state.get(f"kpi_{q_name}_{i}_um", "")
                    menor_mejor = st.session_state.get(f"kpi_{q_name}_{i}_menor", "NO")
                    
                    cump = calcular_cumplimiento(t_prog, t_real, menor_mejor)
                    color = obtener_color(cump, g_ama, g_ver, g_sve)
                    
                    with kpi_cols[i-1]:
                        dibujar_tarjeta(nombre, "KPI Trimestral", t_prog, t_real, um, cump, color)

            st.divider()
            
            # --- RENDERIZAR OKRs ---
            st.subheader("Prioridades (OKRs)")
            okr_cols = st.columns(5)
            for i in range(1, 6):
                nombre = st.session_state.get(f"okr_{q_name}_{i}_nom", "")
                if nombre != "":
                    crit_nom = st.session_state.get(f"okr_{q_name}_{i}_crit", "Criterio")
                    t_prog = sum([st.session_state.get(f"okr_{q_name}_{i}_p_{m}", 0.0) for m in meses_q])
                    t_real = sum([st.session_state.get(f"okr_{q_name}_{i}_r_{m}", 0.0) for m in meses_q])
                    
                    cump = calcular_cumplimiento(t_prog, t_real, "NO")
                    color = obtener_color(cump, g_ama, g_ver, g_sve)
                    
                    with okr_cols[i-1]:
                        dibujar_tarjeta(nombre, crit_nom, t_prog, t_real, "U", cump, color)
                        
    with tabs_dash[4]:
        st.header("Dashboard Anual")
        st.info("La vista anual sumara el esfuerzo de los 4 trimestres usando la misma logica visual.")
