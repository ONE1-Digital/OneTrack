import streamlit as st
import pandas as pd

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

# --- CSS MINIMALISTA Y ELEGANTE ---
st.markdown("""
    <style>
    /* Estilo de Pestañas Principales y Secundarias (Anidadas) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f0f2f6;
        padding: 5px 10px;
        border-radius: 8px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: transparent;
        border-radius: 5px;
        color: #555;
        font-weight: 600;
        font-size: 14px;
        padding: 0 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #002060 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Semaforo Compacto */
    .semaforo-container { font-size: 12px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden; }
    .sem-header { background-color: #002060; color: white; text-align: center; font-weight: bold; padding: 4px; }
    .sem-row { display: flex; align-items: center; }
    .sem-label { flex: 2; padding: 4px 8px; font-weight: bold; text-align: right; color: black; border-bottom: 1px solid #fff;}
    .sem-val { flex: 1; padding: 4px; text-align: center; }
    
    /* Titulos de Iniciativa */
    .iniciativa-header {
        background-color: #e6e9f0;
        border-left: 5px solid #002060;
        padding: 8px 15px;
        font-weight: bold;
        color: #002060;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
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

# --- INICIALIZACION Y CARGA DE DATOS ---
def init_okr_structure(q_name, i, meses):
    # Cabecera de Iniciativa
    if f"okr_{q_name}_{i}_nom" not in st.session_state:
        st.session_state[f"okr_{q_name}_{i}_nom"] = ""
        st.session_state[f"okr_{q_name}_{i}_obj"] = ""
        st.session_state[f"okr_{q_name}_{i}_fi"] = ""
        st.session_state[f"okr_{q_name}_{i}_ff"] = ""
        st.session_state[f"okr_{q_name}_{i}_peso"] = 20.0
        
        # DataFrame Criterios (5 filas)
        cols_c = ["Criterio", "Tipo", "Meta", "UM", "< Mejor", "%"]
        for m in meses: cols_c.extend([f"Prog {m}", f"Real {m}"])
        df_c = pd.DataFrame(columns=cols_c)
        for _ in range(5): df_c.loc[len(df_c)] = ["", "Promedio", 0.0, "U", "NO", 20.0] + [0.0]*(len(meses)*2)
        st.session_state[f"df_crit_{q_name}_{i}"] = df_c
        
        # DataFrame Tacticas (5 filas)
        cols_t = ["Accion Clave (Tacticas)", "Responsable", "Fecha Inicial", "Fecha Fin", "%"]
        for m in meses: cols_t.extend([f"Prog {m}", f"Real {m}"])
        df_t = pd.DataFrame(columns=cols_t)
        for _ in range(5): df_t.loc[len(df_t)] = ["", "", "", "", 20.0] + [0.0]*(len(meses)*2)
        st.session_state[f"df_tact_{q_name}_{i}"] = df_t

def cargar_datos():
    if st.session_state.get('datos_cargados', False): return
    
    # Valores Globales por defecto
    st.session_state["peso_kpis"], st.session_state["peso_okrs"] = 50.0, 50.0
    st.session_state["v_sob"], st.session_state["v_meta"], st.session_state["v_med"] = 100.0, 90.0, 89.0

    for q_name, meses in trimestres.items():
        # KPIs
        data_kpi = {"No.": ["#1", "#2", "#3", "#4", "#5"], "KPI's Operativos": [""]*5, "Tipo": ["Promedio"]*5, "Meta": [0.0]*5, "UM": ["U"]*5, "< Mejor": ["NO"]*5, "Peso %": [20.0]*5}
        for m in meses:
            data_kpi[f"Prog {m}"] = [0.0]*5
            data_kpi[f"Real {m}"] = [0.0]*5
        st.session_state[f"df_kpi_{q_name}"] = pd.DataFrame(data_kpi)

        # OKRs
        for i in range(1, 6):
            init_okr_structure(q_name, i, meses)

    st.session_state.datos_cargados = True

cargar_datos()

# --- NAVEGACION PRINCIPAL (PESTAÑAS) ---
tab_overview, tab_reportes = st.tabs(["Overview", "Reportes"])

# ==========================================
# PESTAÑA 1: OVERVIEW (CAPTURA CONDENSADA)
# ==========================================
with tab_overview:
    
    # 1. HEADER: TITULO Y BOTON GUARDAR (ARRIBA DERECHA)
    col_t, col_btn = st.columns([4, 1])
    with col_t:
        st.markdown("<h2 style='color:#002060; margin:0;'>Dashboard Operativo ONE Track</h2>", unsafe_allow_html=True)
    with col_btn:
        if st.button("Guardar Cambios", type="primary", use_container_width=True):
            st.success("Datos guardados (Simulacion)")
            # Logica de base de datos iria aqui...

    st.write("")
    
    # 2. PONDERACION Y SEMAFORO COMPACTO
    col_w1, col_w2, col_sem, col_spacer = st.columns([1, 1, 2, 2])
    
    with col_w1:
        st.number_input("Peso Global KPIs (%)", value=st.session_state["peso_kpis"], key="p_kpis")
    with col_w2:
        st.number_input("Peso Global OKRs (%)", value=st.session_state["peso_okrs"], key="p_okrs")
        
    with col_sem:
        st.markdown("""<div class='semaforo-container'><div class='sem-header'>Criterios de Exito</div>""", unsafe_allow_html=True)
        # Filas del semaforo
        c1, c2 = st.columns([2, 1])
        c1.markdown("<div class='sem-label' style='background-color: #00b050;'>Sobresaliente >=</div>", unsafe_allow_html=True)
        v_sob = c2.number_input("sob", value=st.session_state["v_sob"], label_visibility="collapsed", key="v_sob_i")
        
        c3, c4 = st.columns([2, 1])
        c3.markdown("<div class='sem-label' style='background-color: #92d050;'>Meta >= y <</div>", unsafe_allow_html=True)
        v_meta = c4.number_input("meta", value=st.session_state["v_meta"], label_visibility="collapsed", key="v_meta_i")
        
        c5, c6 = st.columns([2, 1])
        c5.markdown("<div class='sem-label' style='background-color: #ffff00;'>Medio > y <=</div>", unsafe_allow_html=True)
        v_med = c6.number_input("med", value=st.session_state["v_med"], label_visibility="collapsed", key="v_med_i")
        
        c7, c8 = st.columns([2, 1])
        c7.markdown("<div class='sem-label' style='background-color: #ff0000; color:white; border:none;'>Bajo <=</div>", unsafe_allow_html=True)
        c8.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:bold; font-size:14px;'>{st.session_state['v_med']}%</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # 3. TABS DE TRIMESTRES
    tabs_q = st.tabs(["Q1", "Q2", "Q3", "Q4"])
    
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_q[q_idx]:
            meses_q = trimestres[q_name]
            
            # --- SECCION KPIs ---
            st.markdown(f"<h3 style='color:#002060;'>KPI's Operativos - {q_name}</h3>", unsafe_allow_html=True)
            st.session_state[f"df_kpi_{q_name}"] = st.data_editor(
                st.session_state[f"df_kpi_{q_name}"],
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                column_config={
                    "No.": st.column_config.TextColumn(disabled=True, width="small"),
                    "Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio", "Valor Final"]),
                    "UM": st.column_config.SelectboxColumn(options=["U", "$", "%", "Horas"]),
                    "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])
                },
                key=f"editor_kpi_{q_name}"
            )

            st.write("")
            st.markdown(f"<h3 style='color:#002060;'>Iniciativas Estrategicas (OKRs) - {q_name}</h3>", unsafe_allow_html=True)
            
            # --- SECCION OKRs (Apilados) ---
            for i in range(1, 6):
                st.markdown(f"<div class='iniciativa-header'>Iniciativa #{i}</div>", unsafe_allow_html=True)
                
                # Header de la Iniciativa
                ch1, ch2, ch3, ch4 = st.columns([3, 1, 1, 1])
                ch1.text_input("Nombre de la Iniciativa", key=f"okr_{q_name}_{i}_nom", label_visibility="collapsed", placeholder="Nombre de la Iniciativa")
                ch2.text_input("Fecha Inicial", key=f"okr_{q_name}_{i}_fi", label_visibility="collapsed", placeholder="Fecha Inicial")
                ch3.text_input("Fecha Fin", key=f"okr_{q_name}_{i}_ff", label_visibility="collapsed", placeholder="Fecha Fin")
                ch4.number_input("Peso %", key=f"okr_{q_name}_{i}_peso", label_visibility="collapsed")
                
                # Objetivo y Criterios
                co1, co2 = st.columns([1, 3])
                with co1:
                    st.text_area("Objetivo:", key=f"okr_{q_name}_{i}_obj", height=150)
                with co2:
                    st.caption("Criterios de Exito")
                    st.session_state[f"df_crit_{q_name}_{i}"] = st.data_editor(
                        st.session_state[f"df_crit_{q_name}_{i}"],
                        use_container_width=True, hide_index=True, num_rows="fixed",
                        column_config={"Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio"]), "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])},
                        key=f"editor_crit_{q_name}_{i}"
                    )
                
                # Tacticas (Acciones Clave)
                st.caption("Accion Clave (Tacticas)")
                st.session_state[f"df_tact_{q_name}_{i}"] = st.data_editor(
                    st.session_state[f"df_tact_{q_name}_{i}"],
                    use_container_width=True, hide_index=True, num_rows="dynamic",
                    key=f"editor_tact_{q_name}_{i}"
                )
                st.write("") # Espaciador entre iniciativas

# ==========================================
# PESTAÑA 2: REPORTES
# ==========================================
with tab_reportes:
    st.title("Reportes")
    st.info("Aqui se construira el dashboard de graficas leyendo la nueva estructura.")
