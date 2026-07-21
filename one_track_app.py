import streamlit as st
import pandas as pd

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

# Ocultar elementos visuales por defecto de Streamlit para un look mas limpio
st.markdown("""
    <style>
    .stExpander { border-left: 5px solid #002060; background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if 'auth_token' not in st.session_state or st.session_state.auth_token is None:
    st.title("Acceso ONE Track")
    token = st.text_input("Palabra de acceso (Token):", type="password")
    if st.button("Entrar"):
        st.session_state.auth_token = token
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

# --- FUNCIONES DE INTERFAZ (LAS CELULAS DE CAPTURA) ---
def renderizar_celula_kpi(indice, meses):
    with st.expander(f"KPI #{indice} - [Clic para editar]", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.text_input("Nombre del KPI", key=f"kpi_nom_{indice}_{meses[0]}")
        c2.selectbox("Tipo", ["Acumulado", "Promedio", "Valor Final"], key=f"kpi_tipo_{indice}_{meses[0]}")
        c3.number_input("Meta Trimestral", value=0.0, key=f"kpi_meta_{indice}_{meses[0]}")
        
        c4, c5, c6 = st.columns(3)
        c4.selectbox("Unidad de Medida", ["U", "$", "%", "Horas"], key=f"kpi_um_{indice}_{meses[0]}")
        c5.selectbox("Menor es Mejor?", ["NO", "SI"], key=f"kpi_menor_{indice}_{meses[0]}")
        c6.number_input("Peso (%)", value=20, key=f"kpi_peso_{indice}_{meses[0]}")
        
        st.divider()
        st.write("Avance Mensual")
        
        m_cols = st.columns(3)
        for i, mes in enumerate(meses):
            with m_cols[i]:
                st.markdown(f"**{mes}**")
                st.number_input("Programado", value=0.0, key=f"kpi_p_{indice}_{mes}")
                st.number_input("Real", value=0.0, key=f"kpi_r_{indice}_{mes}")

def renderizar_celula_okr(indice, meses):
    with st.expander(f"OKR #{indice} - [Clic para editar]", expanded=False):
        st.text_input("Nombre del OKR (Prioridad)", key=f"okr_nom_{indice}_{meses[0]}")
        st.text_area("Objetivo Estrategico", key=f"okr_obj_{indice}_{meses[0]}", height=68)
        st.number_input("Peso Global del OKR (%)", value=20, key=f"okr_peso_{indice}_{meses[0]}")
        
        st.divider()
        st.write("Criterio de Exito Principal")
        col_c1, col_c2 = st.columns(2)
        col_c1.text_input("Nombre del Criterio", key=f"okr_crit_{indice}_{meses[0]}")
        col_c2.number_input("Meta del Criterio", value=0.0, key=f"okr_crit_meta_{indice}_{meses[0]}")
        
        st.write("Avance del Criterio")
        m_cols = st.columns(3)
        for i, mes in enumerate(meses):
            with m_cols[i]:
                st.markdown(f"**{mes}**")
                st.number_input("Prog.", value=0.0, key=f"okr_p_{indice}_{mes}")
                st.number_input("Real", value=0.0, key=f"okr_r_{indice}_{mes}")

# --- NAVEGACION PRINCIPAL ---
st.sidebar.title("Panel de Control")
st.sidebar.caption("Sesion Activa")

# Submenu de navegacion
menu = st.sidebar.radio("Navegacion:", ["Entrada de Datos", "Dashboard de Resultados"])

st.sidebar.divider()
if st.sidebar.button("Cerrar Sesion"):
    st.session_state.auth_token = None
    st.rerun()

# --- SECCION 1: ENTRADA DE DATOS ---
if menu == "Entrada de Datos":
    st.title("ONE Track: Captura de Datos")
    
    tabs_datos = st.tabs(["Q1 (Ene-Mar)", "Q2 (Abr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dic)"])
    
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_datos[q_idx]:
            meses_q = trimestres[q_name]
            
            st.header(f"Planificacion {q_name}")
            
            st.subheader("1. KPIs (Numeros Inteligentes)")
            for i in range(1, 6): 
                renderizar_celula_kpi(i, meses_q)
                
            st.subheader("2. OKRs (Prioridades)")
            for i in range(1, 6): 
                renderizar_celula_okr(i, meses_q)
                
    st.sidebar.divider()
    if st.sidebar.button("Guardar Cambios", type="primary"):
        st.sidebar.success("Estructura lista para conectar a base de datos.")

# --- SECCION 2: DASHBOARD DE RESULTADOS ---
elif menu == "Dashboard de Resultados":
    st.title("ONE Track: Visualizacion de Resultados")
    
    tabs_dash = st.tabs(["Resultados Q1", "Resultados Q2", "Resultados Q3", "Resultados Q4", "Resumen Anual"])
    
    for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        with tabs_dash[q_idx]:
            st.header(f"Dashboard {q_name}")
            st.info(f"Aqui se mostraran los semaforos y graficas de rendimiento para los meses de {', '.join(trimestres[q_name])}.")
            # Espacio reservado para los calculos de semaforos que programaremos
            
    with tabs_dash[4]:
        st.header("Dashboard Anual")
        st.info("Aqui visualizaremos el condensado global comparando el desempeño de los 4 trimestres.")

