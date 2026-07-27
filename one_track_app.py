import streamlit as st
import pandas as pd

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

st.markdown("""
    <style>
    .stExpander { border-left: 5px solid #002060; background-color: #f8f9fa; }
    .metric-card { padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-title { margin: 0 0 5px 0; font-size: 18px; font-weight: bold; }
    .metric-data { margin: 0; font-size: 14px; opacity: 0.9; }
    .metric-perc { margin: 10px 0 0 0; font-size: 28px; font-weight: bold; }
    .hito-text { font-size: 13px; margin: 2px 0; padding: 5px; background-color: rgba(255,255,255,0.2); border-radius: 4px; }
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

# --- ESTRUCTURA DE MESES ---
trimestres = {
    "Q1": ["Ene", "Feb", "Mar"],
    "Q2": ["Abr", "May", "Jun"],
    "Q3": ["Jul", "Ago", "Sep"],
    "Q4": ["Oct", "Nov", "Dic"]
}
todos_los_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# --- CARGA DE DATOS ---
def cargar_datos_desde_bd():
    if st.session_state.get('datos_cargados', False):
        return

    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{token}'")
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{token}'")
        df_crit = conn.query(f"SELECT * FROM okr_criterios WHERE onetrack_id = '{token}'")
        df_hitos = conn.query(f"SELECT * FROM okr_hitos WHERE onetrack_id = '{token}'")
    except Exception:
        df_kpis, df_okrs, df_crit, df_hitos = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
            
            # KPIs
            kpi_base = f"kpi_{q_name}_{i}"
            if not df_kpis.empty and indice < len(df_kpis):
                row = df_kpis.iloc[indice]
                st.session_state[f"{kpi_base}_nom"] = str(row.get("KPI_Nombre", ""))
                st.session_state[f"{kpi_base}_um"] = str(row.get("UM", "U"))
                st.session_state[f"{kpi_base}_menor"] = str(row.get("< Mejor", "NO"))
                for mes in meses:
                    st.session_state[f"{kpi_base}_p_{mes}"] = float(row.get(f"{mes}_P", 0.0))
                    st.session_state[f"{kpi_base}_r_{mes}"] = float(row.get(f"{mes}_R", 0.0))
            else:
                st.session_state[f"{kpi_base}_nom"] = ""
                st.session_state[f"{kpi_base}_um"] = "U"
                st.session_state[f"{kpi_base}_menor"] = "NO"
                for mes in meses:
                    st.session_state[f"{kpi_base}_p_{mes}"] = 0.0
                    st.session_state[f"{kpi_base}_r_{mes}"] = 0.0

            # OKRs y Criterios
            okr_base = f"okr_{q_name}_{i}"
            if not df_okrs.empty and indice < len(df_okrs):
                row_o = df_okrs.iloc[indice]
                st.session_state[f"{okr_base}_nom"] = str(row_o.get("OKR_Nombre", ""))
            else:
                st.session_state[f"{okr_base}_nom"] = ""

            if not df_crit.empty and indice < len(df_crit):
                row_c = df_crit.iloc[indice]
                st.session_state[f"{okr_base}_crit"] = str(row_c.get("Criterio_Nombre", ""))
                for mes in meses:
                    st.session_state[f"{okr_base}_p_{mes}"] = float(row_c.get(f"{mes}_P", 0.0))
                    st.session_state[f"{okr_base}_r_{mes}"] = float(row_c.get(f"{mes}_R", 0.0))
            else:
                st.session_state[f"{okr_base}_crit"] = ""
                for mes in meses:
                    st.session_state[f"{okr_base}_p_{mes}"] = 0.0
                    st.session_state[f"{okr_base}_r_{mes}"] = 0.0
            
            # Hitos (Actividades) - 2 por OKR
            hitos_del_okr = df_hitos[df_hitos['OKR_ID'] == i] if not df_hitos.empty else pd.DataFrame()
            for h in range(1, 3):
                hito_base = f"hito_{q_name}_{i}_{h}"
                if len(hitos_del_okr) >= h:
                    row_h = hitos_del_okr.iloc[h-1]
                    st.session_state[f"{hito_base}_nom"] = str(row_h.get("Accion_Clave", ""))
                    for mes in meses:
                        st.session_state[f"{hito_base}_p_{mes}"] = float(row_h.get(f"{mes}_P", 0.0))
                        st.session_state[f"{hito_base}_r_{mes}"] = float(row_h.get(f"{mes}_R", 0.0))
                else:
                    st.session_state[f"{hito_base}_nom"] = ""
                    for mes in meses:
                        st.session_state[f"{hito_base}_p_{mes}"] = 0.0
                        st.session_state[f"{hito_base}_r_{mes}"] = 0.0

    st.session_state.datos_cargados = True

cargar_datos_desde_bd()

# --- FUNCIONES DE INTERFAZ (ENTRADA) ---
def renderizar_celula_kpi(indice, q_name, meses):
    kpi_base = f"kpi_{q_name}_{indice}"
    with st.expander(f"KPI #{indice} - [Clic para editar]", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.text_input("Nombre del KPI", key=f"{kpi_base}_nom")
        c2.selectbox("Unidad de Medida", ["U", "$", "%", "Horas"], key=f"{kpi_base}_um")
        c3.selectbox("Menor es Mejor?", ["NO", "SI"], key=f"{kpi_base}_menor")
        
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
        
        st.divider()
        st.write("Criterio de Exito Principal (Metrica)")
        st.text_input("Nombre del Criterio", key=f"{okr_base}_crit")
        m_cols = st.columns(3)
        for i, mes in enumerate(meses):
            with m_cols[i]:
                st.markdown(f"**{mes}**")
                st.number_input("Prog. (Criterio)", key=f"{okr_base}_p_{mes}")
                st.number_input("Real (Criterio)", key=f"{okr_base}_r_{mes}")
        
        st.divider()
        st.write("Actividades Clave (Hitos)")
        for h in range(1, 3):
            st.text_input(f"Nombre Actividad {h}", key=f"hito_{q_name}_{indice}_{h}_nom")
            h_cols = st.columns(3)
            for i, mes in enumerate(meses):
                with h_cols[i]:
                    st.number_input(f"Prog %", key=f"hito_{q_name}_{indice}_{h}_p_{mes}")
                    st.number_input(f"Real %", key=f"hito_{q_name}_{indice}_{h}_r_{mes}")

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

def dibujar_grafica(prog_list, real_list, meses):
    df = pd.DataFrame({
        "Programado": prog_list,
        "Real": real_list
    }, index=meses)
    st.bar_chart(df)

def dibujar_tarjeta_kpi(titulo, prog, real, um, cump, color, prog_list, real_list, meses):
    txt_color = 'black' if color == '#ffc107' else 'white'
    st.markdown(f"""
        <div class="metric-card" style="background-color: {color}; color: {txt_color};">
            <p class="metric-title" style="color: {txt_color};">{titulo}</p>
            <p class="metric-data">Prog: {prog:,.2f} {um} | Real: {real:,.2f} {um}</p>
            <p class="metric-perc">{cump:.1f}%</p>
        </div>
    """, unsafe_allow_html=True)
    dibujar_grafica(prog_list, real_list, meses)

def dibujar_tarjeta_okr(titulo, crit_nom, prog, real, cump, color, hitos_data):
    txt_color = 'black' if color == '#ffc107' else 'white'
    
    hitos_html = ""
    for hito in hitos_data:
        if hito['nombre']:
            h_cump = calcular_cumplimiento(hito['prog'], hito['real'], "NO")
            hitos_html += f"<div class='hito-text' style='color:{txt_color}; border: 1px solid {txt_color};'>Actividad: {hito['nombre']} | Avance: {h_cump:.1f}%</div>"

    st.markdown(f"""
        <div class="metric-card" style="background-color: {color}; color: {txt_color};">
            <p class="metric-title" style="color: {txt_color};">{titulo}</p>
            <p class="metric-data"><b>Criterio:</b> {crit_nom}</p>
            <p class="metric-data">Prog: {prog:,.2f} | Real: {real:,.2f}</p>
            <p class="metric-perc">{cump:.1f}%</p>
            <hr style="margin: 10px 0; border-color: {txt_color}; opacity: 0.3;">
            <p class="metric-data" style="margin-bottom: 5px;"><b>Avance de Actividades:</b></p>
            {hitos_html}
        </div>
    """, unsafe_allow_html=True)

# --- NAVEGACION PRINCIPAL ---
st.sidebar.title("Panel de Control")
menu = st.sidebar.radio("Navegacion:", ["Entrada de Datos", "Dashboard de Resultados"])

st.sidebar.divider()
if st.sidebar.button("Cerrar Sesion"):
    st.session_state.auth_token = None
    st.session_state.datos_cargados = False
    st.rerun()

# --- SECCION 1: ENTRADA DE DATOS ---
if menu == "Entrada de Datos":
    st.title("ONE Track: Captura de Datos")
    
    tabs_datos = st.tabs(["Configuracion Global", "Q1 (Ene-Mar)", "Q2 (Abr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dic)"])
    
    with tabs_datos[0]:
        st.header("Configuracion de Semaforo")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.slider("Limite Minimo: Amarillo (%)", min_value=0.0, max_value=100.0, step=1.0, key="global_u_ama")
            st.slider("Limite Minimo: Verde (%)", min_value=50.0, max_value=120.0, step=1.0, key="global_u_ver")
        with col_s2:
            st.slider("Limite Minimo: Super Verde (%)", min_value=100.0, max_value=200.0, step=1.0, key="global_u_sve")
    
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_datos[q_idx + 1]:
            st.subheader("1. KPIs")
            for i in range(1, 6): renderizar_celula_kpi(i, q_name, trimestres[q_name])
            st.subheader("2. OKRs (Prioridades y Actividades)")
            for i in range(1, 6): renderizar_celula_okr(i, q_name, trimestres[q_name])
                
    st.sidebar.divider()
    
    def guardar_en_bd():
        kpis_data, okrs_data, crit_data, hitos_data = [], [], [], []
        g_ama = st.session_state.get("global_u_ama", 80.0)
        g_ver = st.session_state.get("global_u_ver", 100.0)
        g_sve = st.session_state.get("global_u_sve", 115.0)
        
        for i in range(1, 6):
            k_nom = st.session_state.get(f"kpi_Q1_{i}_nom", "")
            if k_nom:
                kpi_row = {"onetrack_id": token, "KPI_Nombre": k_nom, "UM": st.session_state.get(f"kpi_Q1_{i}_um", "U"), "< Mejor": st.session_state.get(f"kpi_Q1_{i}_menor", "NO"), "U_Amarillo": g_ama, "U_Verde": g_ver, "U_SVerde": g_sve}
                for q_n, meses in trimestres.items():
                    for mes in meses:
                        kpi_row[f"{mes}_P"] = st.session_state.get(f"kpi_{q_n}_{i}_p_{mes}", 0.0)
                        kpi_row[f"{mes}_R"] = st.session_state.get(f"kpi_{q_n}_{i}_r_{mes}", 0.0)
                kpis_data.append(kpi_row)
            
            o_nom = st.session_state.get(f"okr_Q1_{i}_nom", "")
            if o_nom:
                okrs_data.append({"onetrack_id": token, "OKR_ID": i, "OKR_Nombre": o_nom})
                
                crit_row = {"onetrack_id": token, "OKR_ID": i, "Criterio_Nombre": st.session_state.get(f"okr_Q1_{i}_crit", ""), "U_Amarillo": g_ama, "U_Verde": g_ver, "U_SVerde": g_sve}
                for q_n, meses in trimestres.items():
                    for mes in meses:
                        crit_row[f"{mes}_P"] = st.session_state.get(f"okr_{q_n}_{i}_p_{mes}", 0.0)
                        crit_row[f"{mes}_R"] = st.session_state.get(f"okr_{q_n}_{i}_r_{mes}", 0.0)
                crit_data.append(crit_row)
                
                for h in range(1, 3):
                    h_nom = st.session_state.get(f"hito_Q1_{i}_{h}_nom", "")
                    if h_nom:
                        hito_row = {"onetrack_id": token, "OKR_ID": i, "Accion_Clave": h_nom}
                        for q_n, meses in trimestres.items():
                            for mes in meses:
                                hito_row[f"{mes}_P"] = st.session_state.get(f"hito_{q_n}_{i}_{h}_p_{mes}", 0.0)
                                hito_row[f"{mes}_R"] = st.session_state.get(f"hito_{q_n}_{i}_{h}_r_{mes}", 0.0)
                        hitos_data.append(hito_row)
                        
        def sync_tabla(df_nuevo, table_name):
            if df_nuevo.empty: return
            try:
                df_total = conn.query(f"SELECT * FROM {table_name}")
                df_otros = df_total[df_total['onetrack_id'] != token]
                df_final = pd.concat([df_otros, df_nuevo], ignore_index=True)
            except Exception:
                df_final = df_nuevo
            df_final.to_sql(table_name, con=conn.engine, if_exists='replace', index=False)

        sync_tabla(pd.DataFrame(kpis_data), "kpis")
        sync_tabla(pd.DataFrame(okrs_data), "okrs_general")
        sync_tabla(pd.DataFrame(crit_data), "okr_criterios")
        sync_tabla(pd.DataFrame(hitos_data), "okr_hitos")

    if st.sidebar.button("Guardar Cambios", type="primary"):
        with st.spinner("Sincronizando..."):
            guardar_en_bd()
            st.session_state.datos_cargados = False 
        st.sidebar.success("Guardado exitosamente.")

# --- SECCION 2: DASHBOARD ---
elif menu == "Dashboard de Resultados":
    st.title("ONE Track: Dashboard Estrategico")
    
    g_ama = st.session_state.get("global_u_ama", 80.0)
    g_ver = st.session_state.get("global_u_ver", 100.0)
    g_sve = st.session_state.get("global_u_sve", 115.0)
    
    tabs_dash = st.tabs(["Resultados Q1", "Resultados Q2", "Resultados Q3", "Resultados Q4", "Resumen Anual"])
    
    # Trimestres Individuales
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_dash[q_idx]:
            meses_q = trimestres[q_name]
            
            st.subheader("Indicadores Clave (KPIs)")
            kpi_cols = st.columns(3) # Diseño a 3 columnas para que las graficas se vean bien
            for i in range(1, 6):
                nombre = st.session_state.get(f"kpi_Q1_{i}_nom", "") # El nombre se define en Q1
                if nombre:
                    p_list = [st.session_state.get(f"kpi_{q_name}_{i}_p_{m}", 0.0) for m in meses_q]
                    r_list = [st.session_state.get(f"kpi_{q_name}_{i}_r_{m}", 0.0) for m in meses_q]
                    t_prog, t_real = sum(p_list), sum(r_list)
                    um = st.session_state.get(f"kpi_Q1_{i}_um", "")
                    menor_mejor = st.session_state.get(f"kpi_Q1_{i}_menor", "NO")
                    
                    cump = calcular_cumplimiento(t_prog, t_real, menor_mejor)
                    color = obtener_color(cump, g_ama, g_ver, g_sve)
                    
                    with kpi_cols[(i-1) % 3]:
                        dibujar_tarjeta_kpi(nombre, t_prog, t_real, um, cump, color, p_list, r_list, meses_q)

            st.divider()
            
            st.subheader("Prioridades y Actividades (OKRs)")
            okr_cols = st.columns(3)
            for i in range(1, 6):
                nombre = st.session_state.get(f"okr_Q1_{i}_nom", "")
                if nombre:
                    crit_nom = st.session_state.get(f"okr_Q1_{i}_crit", "Criterio")
                    t_prog = sum([st.session_state.get(f"okr_{q_name}_{i}_p_{m}", 0.0) for m in meses_q])
                    t_real = sum([st.session_state.get(f"okr_{q_name}_{i}_r_{m}", 0.0) for m in meses_q])
                    
                    cump = calcular_cumplimiento(t_prog, t_real, "NO")
                    color = obtener_color(cump, g_ama, g_ver, g_sve)
                    
                    # Recolectar datos de hitos del trimestre
                    hitos_data = []
                    for h in range(1, 3):
                        h_nom = st.session_state.get(f"hito_Q1_{i}_{h}_nom", "")
                        if h_nom:
                            hp = sum([st.session_state.get(f"hito_{q_name}_{i}_{h}_p_{m}", 0.0) for m in meses_q])
                            hr = sum([st.session_state.get(f"hito_{q_name}_{i}_{h}_r_{m}", 0.0) for m in meses_q])
                            hitos_data.append({"nombre": h_nom, "prog": hp, "real": hr})
                    
                    with okr_cols[(i-1) % 3]:
                        dibujar_tarjeta_okr(nombre, crit_nom, t_prog, t_real, cump, color, hitos_data)
                        
    # Dashboard Anual (Acumulado 12 meses)
    with tabs_dash[4]:
        st.header("Consolidado Anual (Ene - Dic)")
        
        st.subheader("Indicadores Clave (KPIs)")
        kpi_cols_a = st.columns(3)
        for i in range(1, 6):
            nombre = st.session_state.get(f"kpi_Q1_{i}_nom", "")
            if nombre:
                p_list_anual = []
                r_list_anual = []
                for q, meses in trimestres.items():
                    for m in meses:
                        p_list_anual.append(st.session_state.get(f"kpi_{q}_{i}_p_{m}", 0.0))
                        r_list_anual.append(st.session_state.get(f"kpi_{q}_{i}_r_{m}", 0.0))
                
                t_prog, t_real = sum(p_list_anual), sum(r_list_anual)
                um = st.session_state.get(f"kpi_Q1_{i}_um", "")
                menor_mejor = st.session_state.get(f"kpi_Q1_{i}_menor", "NO")
                cump = calcular_cumplimiento(t_prog, t_real, menor_mejor)
                color = obtener_color(cump, g_ama, g_ver, g_sve)
                
                with kpi_cols_a[(i-1) % 3]:
                    dibujar_tarjeta_kpi(nombre, t_prog, t_real, um, cump, color, p_list_anual, r_list_anual, todos_los_meses)

        st.divider()
        
        st.subheader("Prioridades y Actividades (OKRs)")
        okr_cols_a = st.columns(3)
        for i in range(1, 6):
            nombre = st.session_state.get(f"okr_Q1_{i}_nom", "")
            if nombre:
                crit_nom = st.session_state.get(f"okr_Q1_{i}_crit", "Criterio")
                t_prog, t_real = 0.0, 0.0
                hitos_data_anual = [{"nombre": st.session_state.get(f"hito_Q1_{i}_{h}_nom", ""), "prog": 0.0, "real": 0.0} for h in range(1, 3)]
                
                for q, meses in trimestres.items():
                    for m in meses:
                        t_prog += st.session_state.get(f"okr_{q}_{i}_p_{m}", 0.0)
                        t_real += st.session_state.get(f"okr_{q}_{i}_r_{m}", 0.0)
                        for h in range(1, 3):
                            if hitos_data_anual[h-1]["nombre"]:
                                hitos_data_anual[h-1]["prog"] += st.session_state.get(f"hito_{q}_{i}_{h}_p_{m}", 0.0)
                                hitos_data_anual[h-1]["real"] += st.session_state.get(f"hito_{q}_{i}_{h}_r_{m}", 0.0)
                
                cump = calcular_cumplimiento(t_prog, t_real, "NO")
                color = obtener_color(cump, g_ama, g_ver, g_sve)
                
                with okr_cols_a[(i-1) % 3]:
                    dibujar_tarjeta_okr(nombre, crit_nom, t_prog, t_real, cump, color, hitos_data_anual)
