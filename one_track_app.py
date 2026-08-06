import streamlit as st
import pandas as pd

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

# --- CSS MINIMALISTA Y ELEGANTE ---
st.markdown("""
    <style>
    /* Estilo de Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #f8f9fa;
        padding: 10px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px;
        color: #555;
        font-weight: 600;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #002060 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Tarjetas de Resumen */
    .summary-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #002060;
    }
    .summary-title { font-size: 14px; color: #666; font-weight: bold; margin-bottom: 10px;}
    .summary-value { font-size: 24px; color: #002060; font-weight: bold; }
    
    /* Ocultar indices de Dataframes */
    thead tr th:first-child {display:none}
    tbody th {display:none}
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

# --- CARGA DE DATOS ---
def cargar_datos_desde_bd():
    if st.session_state.get('datos_cargados', False):
        return

    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{token}'")
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{token}'")
    except Exception:
        df_kpis = pd.DataFrame()
        df_okrs = pd.DataFrame()

    # Cargar Configuración Global
    if not df_kpis.empty:
        st.session_state["peso_kpis"] = float(df_kpis.iloc[0].get("Peso_Global_KPI", 50.0))
        st.session_state["peso_okrs"] = float(df_kpis.iloc[0].get("Peso_Global_OKR", 50.0))
        st.session_state["val_sob"] = float(df_kpis.iloc[0].get("U_SVerde", 100.0))
        st.session_state["val_meta"] = float(df_kpis.iloc[0].get("U_Verde", 90.0))
        st.session_state["val_med"] = float(df_kpis.iloc[0].get("U_Amarillo", 89.0))
    else:
        st.session_state["peso_kpis"], st.session_state["peso_okrs"] = 50.0, 50.0
        st.session_state["val_sob"], st.session_state["val_meta"], st.session_state["val_med"] = 100.0, 90.0, 89.0

    # Inicializar DataFrames por Trimestre
    for q_name, meses in trimestres.items():
        # KPIs
        data_kpi = {"No.": ["#1", "#2", "#3", "#4", "#5"], "KPI's Operativos": ["", "", "", "", ""], "Tipo": ["Promedio"]*5, "Meta": [0.0]*5, "UM": ["U"]*5, "< Mejor": ["NO"]*5, "Peso %": [20.0]*5}
        for m in meses:
            data_kpi[f"Prog {m}"] = [0.0]*5
            data_kpi[f"Real {m}"] = [0.0]*5
        
        if not df_kpis.empty:
            for i in range(min(5, len(df_kpis))):
                row = df_kpis.iloc[i]
                data_kpi["KPI's Operativos"][i] = str(row.get("KPI_Nombre", ""))
                data_kpi["Tipo"][i] = str(row.get("Tipo", "Promedio"))
                data_kpi["Meta"][i] = float(row.get("Meta", 0.0))
                data_kpi["UM"][i] = str(row.get("UM", "U"))
                data_kpi["< Mejor"][i] = str(row.get("< Mejor", "NO"))
                data_kpi["Peso %"][i] = float(row.get("Peso_%", 20.0))
                for m in meses:
                    data_kpi[f"Prog {m}"][i] = float(row.get(f"{m}_P", 0.0))
                    data_kpi[f"Real {m}"][i] = float(row.get(f"{m}_R", 0.0))
                    
        st.session_state[f"df_kpi_{q_name}"] = pd.DataFrame(data_kpi)

        # OKRs (Vista Condensada)
        data_okr = {"No.": ["#1", "#2", "#3", "#4", "#5"], "OKR / Prioridad": ["", "", "", "", ""], "Criterio de Exito": ["", "", "", "", ""], "Hito Clave 1": ["", "", "", "", ""], "Hito Clave 2": ["", "", "", "", ""], "Peso %": [20.0]*5}
        for m in meses:
            data_okr[f"Prog {m}"] = [0.0]*5
            data_okr[f"Real {m}"] = [0.0]*5
            
        if not df_okrs.empty:
            for i in range(min(5, len(df_okrs))):
                row = df_okrs.iloc[i]
                data_okr["OKR / Prioridad"][i] = str(row.get("OKR_Nombre", ""))
                data_okr["Criterio de Exito"][i] = str(row.get("Criterio", ""))
                data_okr["Hito Clave 1"][i] = str(row.get("Hito1", ""))
                data_okr["Hito Clave 2"][i] = str(row.get("Hito2", ""))
                data_okr["Peso %"][i] = float(row.get("Peso_%", 20.0))
                for m in meses:
                    data_okr[f"Prog {m}"][i] = float(row.get(f"{m}_P", 0.0))
                    data_okr[f"Real {m}"][i] = float(row.get(f"{m}_R", 0.0))
                    
        st.session_state[f"df_okr_{q_name}"] = pd.DataFrame(data_okr)

    st.session_state.datos_cargados = True

cargar_datos_desde_bd()

# --- NAVEGACION PRINCIPAL (PESTAÑAS) ---
tab_overview, tab_reportes = st.tabs(["Overview", "Reportes"])

# ==========================================
# PESTAÑA 1: OVERVIEW (CAPTURA CONDENSADA)
# ==========================================
with tab_overview:
    # 1. SECCION SUPERIOR: PONDERACION Y AVANCE GLOBAL
    col_w, col_s1, col_s2, col_s3 = st.columns([1.5, 1, 1, 1])
    
    with col_w:
        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<p class='summary-title'>Ponderacion Global</p>", unsafe_allow_html=True)
        c_kpi, c_okr = st.columns(2)
        peso_k = c_kpi.number_input("KPIs (%)", value=st.session_state["peso_kpis"], key="p_kpis")
        peso_o = c_okr.number_input("OKRs (%)", value=st.session_state["peso_okrs"], key="p_okrs")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_s1:
        st.markdown(f"""
            <div class='summary-card'>
                <p class='summary-title'>Avance KPIs (Q Actual)</p>
                <p class='summary-value'>-- %</p>
            </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
            <div class='summary-card'>
                <p class='summary-title'>Avance OKRs (Q Actual)</p>
                <p class='summary-value'>-- %</p>
            </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
            <div class='summary-card' style='border-top: 4px solid #28a745;'>
                <p class='summary-title'>Total ONE Track</p>
                <p class='summary-value' style='color:#28a745;'>-- %</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("") # Espaciador
    
    # 2. CONFIGURACION DE SEMAFORO Y SELECTOR DE TRIMESTRE
    col_sem, col_q = st.columns([2, 1])
    
    with col_sem:
        # Tabla Visual del Semaforo (Recreando la imagen)
        st.markdown("""
            <div style="background-color: #002060; color: white; text-align: center; font-weight: bold; padding: 5px; border-radius: 5px 5px 0 0;">
                Criterios de Exito
            </div>
        """, unsafe_allow_html=True)
        
        c_l, c_r = st.columns([1, 1])
        with c_l:
            st.markdown("<div style='background-color: #00b050; padding: 10px; color: black; font-weight: bold; text-align: right;'>Sobresaliente >=</div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color: #92d050; padding: 10px; color: black; font-weight: bold; text-align: right;'>Meta >= y < </div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color: #ffff00; padding: 10px; color: black; font-weight: bold; text-align: right;'>Medio > y <= </div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color: #ff0000; padding: 10px; color: white; font-weight: bold; text-align: right;'>Bajo <= </div>", unsafe_allow_html=True)
        
        with c_r:
            v_sob = st.number_input("sob", value=st.session_state["val_sob"], label_visibility="collapsed", key="v_sob")
            
            sc1, sc2 = st.columns(2)
            v_meta = sc1.number_input("meta1", value=st.session_state["val_meta"], label_visibility="collapsed", key="v_meta")
            sc2.markdown(f"<div style='padding: 5px; text-align: center; font-weight:bold;'>{v_sob}%</div>", unsafe_allow_html=True)
            
            sc3, sc4 = st.columns(2)
            v_med = sc3.number_input("med1", value=st.session_state["val_med"], label_visibility="collapsed", key="v_med")
            sc4.markdown(f"<div style='padding: 5px; text-align: center; font-weight:bold;'>{v_meta}%</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='background-color: #ff0000; padding: 10px; color: white; font-weight: bold; text-align: center;'>{v_med}%</div>", unsafe_allow_html=True)

    with col_q:
        st.markdown("<div class='summary-card' style='height: 100%;'>", unsafe_allow_html=True)
        q_seleccionado = st.radio("Gestionar Trimestre:", ["Q1", "Q2", "Q3", "Q4"], horizontal=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Guardar Cambios en BD", type="primary", use_container_width=True):
            with st.spinner("Guardando vista One Pager..."):
                kpis_data, okrs_data = [], []
                
                # Consolidar KPIs de todos los Qs
                for i in range(5):
                    k_nom = st.session_state[f"df_kpi_Q1"]["KPI's Operativos"][i]
                    if k_nom:
                        row = {"onetrack_id": token, "KPI_Nombre": k_nom, "Tipo": st.session_state[f"df_kpi_Q1"]["Tipo"][i], "Meta": st.session_state[f"df_kpi_Q1"]["Meta"][i], "UM": st.session_state[f"df_kpi_Q1"]["UM"][i], "< Mejor": st.session_state[f"df_kpi_Q1"]["< Mejor"][i], "Peso_%": st.session_state[f"df_kpi_Q1"]["Peso %"][i], "Peso_Global_KPI": peso_k, "Peso_Global_OKR": peso_o, "U_SVerde": v_sob, "U_Verde": v_meta, "U_Amarillo": v_med}
                        for q_n, meses in trimestres.items():
                            for m in meses:
                                row[f"{m}_P"] = st.session_state[f"df_kpi_{q_n}"][f"Prog {m}"][i]
                                row[f"{m}_R"] = st.session_state[f"df_kpi_{q_n}"][f"Real {m}"][i]
                        kpis_data.append(row)
                
                # Consolidar OKRs
                for i in range(5):
                    o_nom = st.session_state[f"df_okr_Q1"]["OKR / Prioridad"][i]
                    if o_nom:
                        row = {"onetrack_id": token, "OKR_Nombre": o_nom, "Criterio": st.session_state[f"df_okr_Q1"]["Criterio de Exito"][i], "Hito1": st.session_state[f"df_okr_Q1"]["Hito Clave 1"][i], "Hito2": st.session_state[f"df_okr_Q1"]["Hito Clave 2"][i], "Peso_%": st.session_state[f"df_okr_Q1"]["Peso %"][i]}
                        for q_n, meses in trimestres.items():
                            for m in meses:
                                row[f"{m}_P"] = st.session_state[f"df_okr_{q_n}"][f"Prog {m}"][i]
                                row[f"{m}_R"] = st.session_state[f"df_okr_{q_n}"][f"Real {m}"][i]
                        okrs_data.append(row)

                # Guardado directo (simplificado para la nueva tabla)
                try:
                    df_k_old = conn.query("SELECT * FROM kpis")
                    df_k_fin = pd.concat([df_k_old[df_k_old['onetrack_id'] != token], pd.DataFrame(kpis_data)], ignore_index=True)
                except Exception: df_k_fin = pd.DataFrame(kpis_data)
                
                try:
                    df_o_old = conn.query("SELECT * FROM okrs_general")
                    df_o_fin = pd.concat([df_o_old[df_o_old['onetrack_id'] != token], pd.DataFrame(okrs_data)], ignore_index=True)
                except Exception: df_o_fin = pd.DataFrame(okrs_data)

                df_k_fin.to_sql("kpis", con=conn.engine, if_exists='replace', index=False)
                df_o_fin.to_sql("okrs_general", con=conn.engine, if_exists='replace', index=False)
                st.session_state.datos_cargados = False
            st.success("Guardado exitosamente.")

    st.divider()

    # 3. TABLAS CONDENSADAS (DATA EDITORS)
    meses_act = trimestres[q_seleccionado]
    
    st.markdown(f"<h3 style='color:#002060;'>KPI's Operativos - {q_seleccionado}</h3>", unsafe_allow_html=True)
    st.session_state[f"df_kpi_{q_seleccionado}"] = st.data_editor(
        st.session_state[f"df_kpi_{q_seleccionado}"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "No.": st.column_config.TextColumn(disabled=True, width="small"),
            "Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio", "Valor Final"]),
            "UM": st.column_config.SelectboxColumn(options=["U", "$", "%", "Horas"]),
            "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])
        }
    )

    st.markdown(f"<h3 style='color:#002060;'>OKR's Estrategicos - {q_seleccionado}</h3>", unsafe_allow_html=True)
    st.session_state[f"df_okr_{q_seleccionado}"] = st.data_editor(
        st.session_state[f"df_okr_{q_seleccionado}"],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "No.": st.column_config.TextColumn(disabled=True, width="small")
        }
    )

# ==========================================
# PESTAÑA 2: REPORTES (DASHBOARD)
# ==========================================
with tab_reportes:
    st.title("ONE Track: Reportes")
    st.info("Aqui se construira la nueva visualizacion basada en la estructura One Pager.")
    # (El codigo del dashboard se adaptara en el siguiente paso para leer los nuevos DataFrames planos)
