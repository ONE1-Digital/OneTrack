import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from sqlalchemy import text

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE TRACK - Workspace", layout="wide", initial_sidebar_state="expanded")

# --- CSS MINIMALISTA, ELEGANTE Y BLANCO ---
st.markdown("""
    <style>
    /* Fondos y contenedores */
    .stApp { background-color: #f4f6f9; }
    
    /* Barra Lateral de Navegación */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }
    [data-testid="stSidebar"] button[data-baseweb="button"] { border-radius: 8px; margin-bottom: 5px; border: 1px solid transparent; transition: all 0.2s;}
    [data-testid="stSidebar"] button[kind="secondary"] { background-color: #f8f9fa; color: #4b5563; border: 1px solid #e5e7eb;}
    [data-testid="stSidebar"] button[kind="secondary"]:hover { background-color: #e2e8f0; }
    [data-testid="stSidebar"] button[kind="primary"] { background-color: #002060 !important; color: #ffffff !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: none;}
    [data-testid="stSidebar"] button p { font-size: 18px !important; font-weight: 900 !important; margin: 0; }

    /* Titulos, Etiquetas y Secciones */
    .section-title { font-size: 26px; font-weight: 900; color: #002060; border-bottom: 3px solid #e5e7eb; padding-bottom: 10px; margin-top: 20px; margin-bottom: 20px; }
    .sub-section-title { font-size: 15px; font-weight: 900; color: #4b5563; margin-top: 25px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;}
    .custom-label { font-size: 14px; font-weight: 900; color: #002060; text-transform: uppercase; margin-bottom: 5px; margin-top: 10px; letter-spacing: 0.5px; }
    
    .img-placeholder { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; height: 120px; display: flex; align-items: center; justify-content: center; padding: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.04);}
    .title-placeholder { display: flex; align-items: center; justify-content: center; height: 160px; background-color: transparent; border: none; box-shadow: none; }
    
    /* Forzar fondo blanco en campos de texto/inputs */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 6px !important;
    }

    /* Tarjetas y Estructura Iniciativas */
    .summary-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #002060; height: 100%; }
    .summary-title { font-size: 14px; color: #4b5563; font-weight: 900; margin-bottom: 5px; text-transform: uppercase;}
    .summary-value { font-size: 28px; color: #002060; font-weight: 900; }
    
    .iniciativa-box { padding: 5px 0; margin-bottom: 10px; }
    .iniciativa-header { font-size: 20px; font-weight: 900; color: #ffffff; background-color: #002060; padding: 10px 20px; border-radius: 8px; display: inline-block; margin-bottom: 10px;}
    .iniciativa-divider { border-top: 3px dashed #cbd5e1; margin: 40px 0; }
    
    /* Tablas Data Grid */
    div[data-testid="stDataFrame"] > div { border: none; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08); background-color: #ffffff; padding: 2px; border: 1px solid #e2e8f0; }
    div[data-testid="stDataFrame"] table th { background-color: #002060 !important; color: #ffffff !important; font-size: 15px !important; font-weight: 900 !important; text-transform: uppercase; text-align: center !important;}
    
    /* Misc */
    .footer-box { border: 1px solid #d1d5db; padding: 6px 15px; font-weight: 900; border-radius: 6px; min-width: 90px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
    .semaforo-container { border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-top: 10px; margin-bottom: 10px;}
    .sem-header { background-color: #002060; color: white; text-align: center; font-weight: 800; padding: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;}
    .sem-label { padding: 8px 15px; font-weight: 800; text-align: right; border-bottom: 1px solid #f9fafb; font-size: 14px; color: black; display: flex; align-items: center; justify-content: flex-end;}
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
trimestres = {"Q1": ["Ene", "Feb", "Mar"], "Q2": ["Abr", "May", "Jun"], "Q3": ["Jul", "Ago", "Sep"], "Q4": ["Oct", "Nov", "Dic"]}
meses_totales = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DEFAULT_LOGO_ONE = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/ONE.png"
DEFAULT_LOGO_CLIENTE = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/MARBER.png"
DEFAULT_LOGO_ONE_TRACK = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/ONE_TRACK_LOGO.png"

# --- CONEXION A BD Y AUTENTICACION ---
conn = st.connection("supabase", type="sql")

def init_db():
    try:
        df = conn.query("SELECT * FROM usuarios LIMIT 1", ttl=0)
        if 'nombre' not in df.columns: raise Exception("Faltan columnas")
    except Exception:
        df_admin = pd.DataFrame([{"username": "admin", "password": "admin", "role": "admin", "nombre": "Admin", "puesto": "Administrador", "empresa": "ONE TRACK", "logo_url": ""}])
        df_admin.to_sql("usuarios", con=conn.engine, if_exists="replace", index=False)

init_db()

# --- FUNCION DUMMY MEJORADA MATEMATICAMENTE ---
def generar_dummy_onetest():
    mult_q = {"Q1": 0.85, "Q2": 0.90, "Q3": 0.98, "Q4": 1.05}
    cols_c = ["Criterio", "Tipo", "Meta", "UM", "< Mejor", "%"]
    cols_t = ["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]

    for q_name, meses in trimestres.items():
        df_k = pd.DataFrame(columns=["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"] + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
        df_k.loc[1] = ["Ventas Mensuales", "Acumulado", 500000.0, "$", "NO", 50.0] + [166666.0, 166666.0 * mult_q[q_name]] * 3
        df_k.loc[2] = ["Satisfacción de Clientes", "Promedio", 95.0, "%", "NO", 50.0] + [95.0, 95.0 * mult_q[q_name]] * 3
        st.session_state[f"df_kpi_{q_name}"] = df_k

    # --- Q1 (1 Iniciativa 100%) ---
    q_n = "Q1"; meses = trimestres[q_n]; st.session_state[f"num_iniciativas_{q_n}"] = 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Expansión de Mercado Norte"
    st.session_state[f"ui_peso_{q_n}_1"] = 100.0
    st.session_state[f"ui_salud_{q_n}_1"] = "🟢 En Tiempo"
    st.session_state[f"ui_obj_{q_n}_1"] = "Conquistar 3 nuevos estados mediante campañas digitales y alianzas locales."
    
    df_c = pd.DataFrame(columns=cols_c + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
    df_c.loc[1] = ["Nuevas Cuentas (B2B)", "Acumulado", 50.0, "U", "NO", 100.0, 15.0, 12.0, 15.0, 18.0, 20.0, 20.0]
    st.session_state[f"df_crit_{q_n}_1"] = df_c
    
    df_t = pd.DataFrame(columns=cols_t)
    df_t.loc[1] = ["1.", "Investigación de Mercado", "Ana", date(2026, 1, 5), date(2026, 1, 15), True]
    df_t.loc[2] = ["1.1", "Contratación de Equipo", "Luis", date(2026, 1, 16), date(2026, 2, 10), True]
    df_t.loc[3] = ["1.2", "Lanzamiento de Campaña", "Carlos", date(2026, 2, 15), date(2026, 3, 20), False]
    st.session_state[f"df_tareas_{q_n}_1"] = df_t

    # --- Q2 (2 Iniciativas: 60% y 40%) ---
    q_n = "Q2"; meses = trimestres[q_n]; st.session_state[f"num_iniciativas_{q_n}"] = 2
    # Iniciativa 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Lanzamiento de Nuevo Producto"
    st.session_state[f"ui_peso_{q_n}_1"] = 60.0
    st.session_state[f"ui_salud_{q_n}_1"] = "🟡 En Riesgo"
    st.session_state[f"ui_obj_{q_n}_1"] = "Lanzar producto Alpha antes del cierre de semestre."
    
    df_c1 = pd.DataFrame(columns=cols_c + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
    df_c1.loc[1] = ["Prototipos validados", "Acumulado", 5.0, "U", "NO", 50.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.0]
    df_c1.loc[2] = ["Preventas cerradas", "Acumulado", 100.0, "U", "NO", 50.0, 20.0, 20.0, 40.0, 40.0, 40.0, 30.0]
    st.session_state[f"df_crit_{q_n}_1"] = df_c1
    
    df_t1 = pd.DataFrame(columns=cols_t)
    df_t1.loc[1] = ["1.", "Diseño de Prototipo", "Ana", date(2026, 4, 1), date(2026, 4, 20), True]
    df_t1.loc[2] = ["2.", "Pruebas de Calidad", "Luis", date(2026, 5, 1), date(2026, 5, 15), True]
    df_t1.loc[3] = ["3.", "Campaña de Preventa", "Carlos", date(2026, 6, 1), date(2026, 6, 25), False]
    st.session_state[f"df_tareas_{q_n}_1"] = df_t1

    # Iniciativa 2
    st.session_state[f"ui_nom_{q_n}_2"] = "Optimización de Costos Operativos"
    st.session_state[f"ui_peso_{q_n}_2"] = 40.0
    st.session_state[f"ui_salud_{q_n}_2"] = "🟢 En Tiempo"
    st.session_state[f"ui_obj_{q_n}_2"] = "Reducir costos operativos en logística."
    
    df_c2 = pd.DataFrame(columns=cols_c + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
    df_c2.loc[1] = ["Ahorro en logística", "Promedio", 15.0, "%", "NO", 100.0, 5.0, 5.0, 10.0, 12.0, 15.0, 15.0]
    st.session_state[f"df_crit_{q_n}_2"] = df_c2
    
    df_t2 = pd.DataFrame(columns=cols_t)
    df_t2.loc[1] = ["1.", "Auditoría Interna", "Sofia", date(2026, 4, 5), date(2026, 4, 25), True]
    df_t2.loc[2] = ["2.", "Renegociación", "Luis", date(2026, 5, 5), date(2026, 5, 20), False]
    df_t2.loc[3] = ["3.", "Implementación Rutas", "Sofia", date(2026, 6, 1), date(2026, 6, 28), False]
    st.session_state[f"df_tareas_{q_n}_2"] = df_t2

    # --- Q3 (1 Iniciativa 100%) ---
    q_n = "Q3"; meses = trimestres[q_n]; st.session_state[f"num_iniciativas_{q_n}"] = 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Certificación ISO 9001"
    st.session_state[f"ui_peso_{q_n}_1"] = 100.0
    st.session_state[f"ui_salud_{q_n}_1"] = "🟢 En Tiempo"
    st.session_state[f"ui_obj_{q_n}_1"] = "Obtener certificación en procesos clave."
    
    df_c = pd.DataFrame(columns=cols_c + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
    df_c.loc[1] = ["Fases completadas", "Acumulado", 3.0, "U", "NO", 100.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
    st.session_state[f"df_crit_{q_n}_1"] = df_c
    
    df_t = pd.DataFrame(columns=cols_t)
    df_t.loc[1] = ["1.", "Diagnóstico Inicial", "Juan", date(2026, 7, 1), date(2026, 7, 15), True]
    df_t.loc[2] = ["2.", "Capacitación de Personal", "Ana", date(2026, 8, 1), date(2026, 8, 20), False]
    df_t.loc[3] = ["3.", "Auditoría Final", "Luis", date(2026, 9, 10), date(2026, 9, 25), False]
    st.session_state[f"df_tareas_{q_n}_1"] = df_t

    # --- Q4 (1 Iniciativa 100%) ---
    q_n = "Q4"; meses = trimestres[q_n]; st.session_state[f"num_iniciativas_{q_n}"] = 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Cierre de Año y Planificación 2027"
    st.session_state[f"ui_peso_{q_n}_1"] = 100.0
    st.session_state[f"ui_salud_{q_n}_1"] = "🟢 En Tiempo"
    st.session_state[f"ui_obj_{q_n}_1"] = "Cerrar métricas anuales y planear presupuesto 2027."
    
    df_c = pd.DataFrame(columns=cols_c + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
    df_c.loc[1] = ["Presupuestos aprob.", "Acumulado", 4.0, "U", "NO", 100.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0]
    st.session_state[f"df_crit_{q_n}_1"] = df_c
    
    df_t = pd.DataFrame(columns=cols_t)
    df_t.loc[1] = ["1.", "Revisión Financiera", "Carlos", date(2026, 10, 5), date(2026, 10, 25), True]
    df_t.loc[2] = ["2.", "Definición Metas", "Ana", date(2026, 11, 1), date(2026, 11, 20), False]
    df_t.loc[3] = ["3.", "Presentación Ejecutiva", "Juan", date(2026, 12, 1), date(2026, 12, 15), False]
    st.session_state[f"df_tareas_{q_n}_1"] = df_t

if 'user_info' not in st.session_state or st.session_state.user_info is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"<div style='text-align:center; margin-bottom:40px;'><img src='{DEFAULT_LOGO_ONE_TRACK}' style='max-height: 200px; object-fit: contain;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='padding:20px; max-width: 400px; margin: 0 auto;'>", unsafe_allow_html=True)
        user = st.text_input("**Usuario**")
        pwd = st.text_input("**Contraseña**", type="password")
        st.write("")
        if st.button("Iniciar Sesión", type="primary", use_container_width=True):
            df_u = conn.query("SELECT * FROM usuarios", ttl=0)
            match = df_u[(df_u['username'] == user) & (df_u['password'] == pwd)]
            if not match.empty:
                st.session_state.user_info = match.iloc[0].to_dict()
                st.session_state.datos_cargados = False
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- PANEL DE ADMINISTRACION ---
if st.session_state.user_info['role'] == 'admin':
    st.markdown("<h2 style='color:#002060; font-weight:900;'>Panel de Administración</h2>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.user_info = None
        st.rerun()
    st.markdown("<div class='sub-section-title'>Gestión de Bases de Clientes</div>", unsafe_allow_html=True)
    df_u = conn.query("SELECT * FROM usuarios", ttl=0)
    df_clients = df_u[df_u['role'] == 'client'].copy()
    edited_clients = st.data_editor(df_clients, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Guardar Usuarios", type="primary"):
        df_admin = df_u[df_u['role'] == 'admin']
        edited_clients['role'] = 'client'
        df_final = pd.concat([df_admin, edited_clients], ignore_index=True)
        df_final.to_sql("usuarios", con=conn.engine, if_exists="replace", index=False)
        st.success("Usuarios actualizados correctamente.")
    st.stop()

# --- CONSTANTES CLIENTE ---
token = st.session_state.user_info['username']

# --- FUNCIONES MATEMATICAS Y COLORES ---
def calc_cump(prog, real, menor_mejor="NO"):
    if prog == 0 and real == 0: return 0.0
    if menor_mejor == "SI": return (prog / real * 100) if real > 0 else 100.0
    else: return (real / prog * 100) if prog > 0 else (100.0 if real > 0 else 0.0)

def ob_color(val, sob, meta, med):
    if val >= sob: return "#00b050" 
    elif val >= meta: return "#92d050" 
    elif val > med: return "#ffff00" 
    else: return "#ff0000" 

def render_footer(df, meses):
    html_footer = "<div style='display:flex; justify-content:flex-start; gap:12px; margin-bottom: 20px; align-items:center;'><div style='font-weight:900; color:#002060; font-size:15px; text-transform:uppercase;'>Avance Mensual:</div>"
    v_sob, v_meta, v_med = float(st.session_state.get("cfg_sob", 100.0)), float(st.session_state.get("cfg_meta", 90.0)), float(st.session_state.get("cfg_med", 89.0))
    for m in meses:
        total_peso, acumulado = 0.0, 0.0
        for i in range(len(df)):
            if str(df["Indicadores Clave de Desempeño (KPIs)"].iloc[i]).strip() != "":
                p, r = float(df[f"{m} Prog"].iloc[i] or 0), float(df[f"{m} Real"].iloc[i] or 0)
                peso = float(df["Peso %"].iloc[i] or 0)
                cump = calc_cump(p, r, str(df["< Mejor"].iloc[i]))
                acumulado += cump * (peso / 100.0)
                total_peso += peso
        avance = (acumulado / (total_peso / 100.0)) if total_peso > 0 else 0.0
        col = ob_color(avance, v_sob, v_meta, v_med)
        txt = "black" if col in ["#ffff00", "#92d050"] else "white"
        html_footer += f"<div class='footer-box' style='background-color:{col}; color:{txt};'>{m}: {avance:.1f}%</div>"
    st.markdown(html_footer + "</div>", unsafe_allow_html=True)

def dibujar_gantt(df_tareas):
    df_plot = df_tareas.copy()
    df_plot = df_plot[df_plot["Tarea"].str.strip() != ""]
    df_plot["Inicio"] = pd.to_datetime(df_plot["Inicio"], errors='coerce')
    df_plot["Fin"] = pd.to_datetime(df_plot["Fin"], errors='coerce')
    df_plot = df_plot.dropna(subset=["Inicio", "Fin"])
    if df_plot.empty: return
    df_plot['Nombre'] = df_plot['Jerarquia'] + " " + df_plot['Tarea']
    df_plot['Estado'] = df_plot['Completado'].apply(lambda x: "Realizado" if x else "Pendiente")
    chart = alt.Chart(df_plot).mark_bar(cornerRadius=4, size=20).encode(
        x=alt.X('Inicio', title='', axis=alt.Axis(format="%d %b", grid=True, gridColor="#f0f2f6")), x2='Fin',
        y=alt.Y('Nombre', sort=None, title='', axis=alt.Axis(labelFontWeight="bold", labelLimit=300)),
        color=alt.Color('Estado', scale=alt.Scale(domain=['Realizado', 'Pendiente'], range=['#002060', '#a0aabf']), legend=alt.Legend(title="Estado", orient="bottom"))
    ).properties(height=alt.Step(40))
    st.altair_chart(chart, use_container_width=True)

# --- CARGA DE DATOS ---
def init_okr_structure(q_name, i, meses):
    if f"ui_nom_{q_name}_{i}" not in st.session_state:
        st.session_state[f"ui_nom_{q_name}_{i}"] = ""
        st.session_state[f"ui_obj_{q_name}_{i}"] = ""
        st.session_state[f"ui_peso_{q_name}_{i}"] = 20.0
        st.session_state[f"ui_salud_{q_name}_{i}"] = "🟢 En Tiempo"
        
        cols_c = ["Criterio", "Tipo", "Meta", "UM", "< Mejor", "%"]
        for m in meses: cols_c.extend([f"{m} Prog", f"{m} Real"])
        df_c = pd.DataFrame(columns=cols_c)
        df_c.index = df_c.index + 1
        st.session_state[f"df_crit_{q_name}_{i}"] = df_c
        
        df_t = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"])
        df_t.index = df_t.index + 1
        st.session_state[f"df_tareas_{q_name}_{i}"] = df_t

def cargar_datos():
    if st.session_state.get('datos_cargados', False): return
    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{token}'", ttl=0)
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{token}'", ttl=0)
        df_crit = conn.query(f"SELECT * FROM okr_criterios WHERE onetrack_id = '{token}'", ttl=0)
        df_tareas = conn.query(f"SELECT * FROM iniciativas_tareas WHERE onetrack_id = '{token}'", ttl=0)
    except Exception:
        df_kpis, df_okrs, df_crit, df_tareas = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    es_nuevo = df_kpis.empty
    
    for q_name in trimestres.keys():
        if not df_okrs.empty and 'OKR_ID' in df_okrs.columns:
            q_okrs = df_okrs[df_okrs['Trimestre_ID'] == q_name] if 'Trimestre_ID' in df_okrs.columns else df_okrs
            if 'OKR_ID' in q_okrs.columns and not q_okrs.empty:
                max_id = q_okrs["OKR_ID"].max()
                st.session_state[f"num_iniciativas_{q_name}"] = int(max_id) if pd.notna(max_id) else 1
            else:
                st.session_state[f"num_iniciativas_{q_name}"] = 1
        else:
            st.session_state[f"num_iniciativas_{q_name}"] = 1

    st.session_state["ui_p_kpis"] = float(df_kpis.iloc[0].get("Peso_Global_KPI", 50.0)) if not es_nuevo else 50.0
    st.session_state["ui_p_okrs"] = float(df_kpis.iloc[0].get("Peso_Global_OKR", 50.0)) if not es_nuevo else 50.0
    st.session_state["cfg_sob"] = float(df_kpis.iloc[0].get("U_SVerde", 100.0)) if not es_nuevo else 100.0
    st.session_state["cfg_meta"] = float(df_kpis.iloc[0].get("U_Verde", 90.0)) if not es_nuevo else 90.0
    st.session_state["cfg_med"] = float(df_kpis.iloc[0].get("U_Amarillo", 80.0)) if not es_nuevo else 80.0
    
    st.session_state["ui_empresa"] = str(df_kpis.iloc[0].get("Empresa", "")) if not es_nuevo else st.session_state.user_info.get("empresa", "")
    st.session_state["ui_dueno"] = str(df_kpis.iloc[0].get("Dueno", "")) if not es_nuevo else st.session_state.user_info.get("nombre", "")
    st.session_state["ui_puesto"] = str(df_kpis.iloc[0].get("Puesto", "")) if not es_nuevo else st.session_state.user_info.get("puesto", "")
    st.session_state["logo_input"] = str(df_kpis.iloc[0].get("Logo_Cliente", "")) if not es_nuevo else st.session_state.user_info.get("logo_url", "")

    for q_name, meses in trimestres.items():
        cols_kpi = ["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"]
        for m in meses: cols_kpi.extend([f"{m} Prog", f"{m} Real"])
        df_k = pd.DataFrame(columns=cols_kpi)

        if not es_nuevo:
            for i in range(len(df_kpis)):
                row = df_kpis.iloc[i]
                new_row = [str(row.get("KPI_Nombre", "")), str(row.get("Tipo", "Promedio")), float(row.get("Meta", 0.0)), str(row.get("UM", "U")), str(row.get("< Mejor", "NO")), float(row.get("Peso_%", 20.0))]
                for m in meses: new_row.extend([float(row.get(f"{m}_P", 0.0)), float(row.get(f"{m}_R", 0.0))])
                df_k.loc[len(df_k) + 1] = new_row
        else:
            df_k.loc[1] = ["", "Promedio", 0.0, "U", "NO", 0.0] + [0.0]*(len(meses)*2)
        
        st.session_state[f"df_kpi_{q_name}"] = df_k

        for i in range(1, st.session_state[f"num_iniciativas_{q_name}"] + 1):
            init_okr_structure(q_name, i, meses)
            
            if not df_okrs.empty and 'OKR_ID' in df_okrs.columns:
                q_okrs_db = df_okrs[df_okrs['Trimestre_ID'] == q_name] if 'Trimestre_ID' in df_okrs.columns else df_okrs
                match_okr = q_okrs_db[q_okrs_db['OKR_ID'] == i]
                if not es_nuevo and not match_okr.empty:
                    row_o = match_okr.iloc[0]
                    st.session_state[f"ui_nom_{q_name}_{i}"] = str(row_o.get("OKR_Nombre", ""))
                    st.session_state[f"ui_obj_{q_name}_{i}"] = str(row_o.get("Objetivo", ""))
                    st.session_state[f"ui_peso_{q_name}_{i}"] = float(row_o.get("Peso_%", 20.0))
                    st.session_state[f"ui_salud_{q_name}_{i}"] = str(row_o.get("Estatus_Salud", "🟢 En Tiempo"))
            
            if not df_crit.empty and 'OKR_ID' in df_crit.columns:
                if 'Trimestre_ID' in df_crit.columns:
                    crit_okr = df_crit[(df_crit['OKR_ID'] == i) & (df_crit['Trimestre_ID'] == q_name)].reset_index(drop=True)
                else:
                    crit_okr = df_crit[(df_crit['OKR_ID'] == i)].reset_index(drop=True)
                    
                if len(crit_okr) > 0:
                    df_c_temp = pd.DataFrame(columns=st.session_state[f"df_crit_{q_name}_{i}"].columns)
                    for c_idx in range(len(crit_okr)):
                        r_c = crit_okr.iloc[c_idx]
                        c_row = [str(r_c.get("Criterio_Nombre", "")), str(r_c.get("Tipo", "Promedio")), float(r_c.get("Meta", 0.0)), str(r_c.get("UM", "U")), str(r_c.get("< Mejor", "NO")), float(r_c.get("Peso_%", 33.3))]
                        for m in meses: c_row.extend([float(r_c.get(f"{m}_P", 0.0)), float(r_c.get(f"{m}_R", 0.0))])
                        df_c_temp.loc[len(df_c_temp) + 1] = c_row
                    st.session_state[f"df_crit_{q_name}_{i}"] = df_c_temp

            if not df_tareas.empty and 'Iniciativa_ID' in df_tareas.columns and 'Trimestre' in df_tareas.columns:
                tar_okr = df_tareas[(df_tareas['Iniciativa_ID'] == i) & (df_tareas['Trimestre'] == q_name)]
                if not tar_okr.empty:
                    df_t = tar_okr[["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]].reset_index(drop=True)
                    df_t["Completado"] = df_t["Completado"].astype(bool)
                    df_t["Inicio"] = pd.to_datetime(df_t["Inicio"]).dt.date
                    df_t["Fin"] = pd.to_datetime(df_t["Fin"]).dt.date
                    df_t.index = df_t.index + 1
                    st.session_state[f"df_tareas_{q_name}_{i}"] = df_t

    st.session_state.datos_cargados = True

cargar_datos()

# --- OPTIMIZACION DE GUARDADO RÁPIDO ---
def guardar_en_bd():
    kpis_data, okrs_data, crit_data, tareas_data = [], [], [], []
    peso_k, peso_o = float(st.session_state.get("ui_p_kpis", 50.0)), float(st.session_state.get("ui_p_okrs", 50.0))
    v_sob, v_meta, v_med = float(st.session_state.get("cfg_sob", 100.0)), float(st.session_state.get("cfg_meta", 90.0)), float(st.session_state.get("cfg_med", 89.0))
    emp, due, pue = st.session_state.get("ui_empresa", ""), st.session_state.get("ui_dueno", ""), st.session_state.get("ui_puesto", "")
    logo_c = st.session_state.get("logo_input", "")

    cols_kpi = ["onetrack_id", "Empresa", "Puesto", "Dueno", "Logo_Cliente", "KPI_Nombre", "Tipo", "Meta", "UM", "< Mejor", "Peso_%", "Peso_Global_KPI", "Peso_Global_OKR", "U_SVerde", "U_Verde", "U_Amarillo"]
    for q_n, meses in trimestres.items():
        for m in meses: cols_kpi.extend([f"{m}_P", f"{m}_R"])
        
    cols_okr = ["onetrack_id", "Trimestre_ID", "OKR_ID", "OKR_Nombre", "Objetivo", "Peso_%", "Estatus_Salud"]
    
    cols_crit = ["onetrack_id", "Trimestre_ID", "OKR_ID", "Criterio_Nombre", "Tipo", "Meta", "UM", "< Mejor", "Peso_%"]
    for q_n, meses in trimestres.items():
        for m in meses: cols_crit.extend([f"{m}_P", f"{m}_R"])
        
    cols_tareas = ["onetrack_id", "Iniciativa_ID", "Trimestre", "Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]

    df_kpi_master = st.session_state.get("df_kpi_Q1", pd.DataFrame())
    if not df_kpi_master.empty:
        for idx, r in df_kpi_master.iterrows():
            k_nom = str(r.get("Indicadores Clave de Desempeño (KPIs)", "")).strip()
            if k_nom:
                row = {
                    "onetrack_id": token, "Empresa": emp, "Puesto": pue, "Dueno": due, "Logo_Cliente": logo_c,
                    "KPI_Nombre": k_nom, "Tipo": r["Tipo"], "Meta": r["Meta"],
                    "UM": r["UM"], "< Mejor": r["< Mejor"], "Peso_%": r["Peso %"],
                    "Peso_Global_KPI": peso_k, "Peso_Global_OKR": peso_o, "U_SVerde": v_sob, "U_Verde": v_meta, "U_Amarillo": v_med
                }
                for q_n, meses in trimestres.items():
                    df_q = st.session_state[f"df_kpi_{q_n}"]
                    if idx in df_q.index and str(df_q.loc[idx, "Indicadores Clave de Desempeño (KPIs)"]).strip() == k_nom:
                        for m in meses:
                            row[f"{m}_P"] = df_q.loc[idx, f"{m} Prog"]
                            row[f"{m}_R"] = df_q.loc[idx, f"{m} Real"]
                    else:
                        matches = df_q[df_q["Indicadores Clave de Desempeño (KPIs)"] == k_nom]
                        if not matches.empty:
                            m_idx = matches.index[0]
                            for m in meses:
                                row[f"{m}_P"] = df_q.loc[m_idx, f"{m} Prog"]
                                row[f"{m}_R"] = df_q.loc[m_idx, f"{m} Real"]
                        else:
                            for m in meses: row[f"{m}_P"], row[f"{m}_R"] = 0.0, 0.0
                kpis_data.append(row)

    for q_n in trimestres.keys():
        for i in range(1, st.session_state.get(f"num_iniciativas_{q_n}", 1) + 1):
            o_nom = st.session_state.get(f"ui_nom_{q_n}_{i}", "")
            if o_nom:
                okrs_data.append({"onetrack_id": token, "Trimestre_ID": q_n, "OKR_ID": i, "OKR_Nombre": o_nom, "Objetivo": st.session_state.get(f"ui_obj_{q_n}_{i}", ""), "Peso_%": float(st.session_state.get(f"ui_peso_{q_n}_{i}", 20.0)), "Estatus_Salud": st.session_state.get(f"ui_salud_{q_n}_{i}", "🟢 En Tiempo")})
                
                df_c = st.session_state.get(f"df_crit_{q_n}_{i}", pd.DataFrame())
                if not df_c.empty:
                    for c_idx, c_row_df in df_c.iterrows():
                        c_nom = c_row_df["Criterio"]
                        if str(c_nom).strip() != "":
                            c_row = {"onetrack_id": token, "Trimestre_ID": q_n, "OKR_ID": i, "Criterio_Nombre": c_nom, "Tipo": c_row_df["Tipo"], "Meta": c_row_df["Meta"], "UM": c_row_df["UM"], "< Mejor": c_row_df["< Mejor"], "Peso_%": c_row_df["%"]}
                            for mx in meses_totales: c_row[f"{mx}_P"], c_row[f"{mx}_R"] = 0.0, 0.0
                            for m in trimestres[q_n]:
                                c_row[f"{m}_P"] = c_row_df[f"{m} Prog"]
                                c_row[f"{m}_R"] = c_row_df[f"{m} Real"]
                            crit_data.append(c_row)
                        
                df_t = st.session_state.get(f"df_tareas_{q_n}_{i}", pd.DataFrame())
                if not df_t.empty:
                    for t_idx, t_row in df_t.iterrows():
                        if str(t_row.get("Tarea", "")).strip() != "":
                            tareas_data.append({"onetrack_id": token, "Iniciativa_ID": i, "Trimestre": q_n, "Jerarquia": t_row.get("Jerarquia", ""), "Tarea": t_row.get("Tarea", ""), "Responsable": t_row.get("Responsable", ""), "Inicio": t_row.get("Inicio"), "Fin": t_row.get("Fin"), "Completado": bool(t_row.get("Completado", False))})

    df_kpis = pd.DataFrame(kpis_data, columns=cols_kpi)
    df_okrs = pd.DataFrame(okrs_data, columns=cols_okr)
    df_crits = pd.DataFrame(crit_data, columns=cols_crit)
    df_tareas = pd.DataFrame(tareas_data, columns=cols_tareas)

    def sync_tabla(df_nuevo, table_name):
        try:
            with conn.engine.begin() as transaction:
                transaction.execute(text(f"DELETE FROM {table_name} WHERE onetrack_id = :token"), {"token": token})
        except Exception: pass
        df_nuevo.to_sql(table_name, con=conn.engine, if_exists='append', index=False)

    sync_tabla(df_kpis, "kpis")
    sync_tabla(df_okrs, "okrs_general")
    sync_tabla(df_crits, "okr_criterios")
    sync_tabla(df_tareas, "iniciativas_tareas")

# --- BARRA LATERAL (NAVEGACION DE PESTAÑAS) ---
if 'vista_actual' not in st.session_state: st.session_state.vista_actual = "Q1"

with st.sidebar:
    st.markdown("<h2 style='color:#002060; font-weight:900;'>NAVEGACIÓN</h2>", unsafe_allow_html=True)
    vistas = ["Q1", "Q2", "Q3", "Q4", "Resumen Anual", "Configuración de Cuenta"]
    for v in vistas:
        b_type = "primary" if st.session_state.vista_actual == v else "secondary"
        if st.button(v, key=f"nav_{v}", use_container_width=True, type=b_type):
            st.session_state.vista_actual = v
            st.rerun()
            
    st.divider()
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.user_info = None
        st.rerun()

# --- UI PRINCIPAL HEADER E IDENTIFICACION ---
c_img1, c_img2, c_img3 = st.columns([1, 2, 1])
with c_img1: 
    st.markdown(f"<div class='img-placeholder' style='border:none; box-shadow:none; background:transparent; justify-content: flex-start;'><img src='{DEFAULT_LOGO_ONE_TRACK}' style='max-height: 120px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)
with c_img2: 
    st.write("") # Espacio en blanco para empujar el logo del cliente a la derecha
with c_img3: 
    logo_c = st.session_state.get("logo_input", "")
    if not logo_c: logo_c = DEFAULT_LOGO_CLIENTE
    st.markdown(f"<div class='img-placeholder'><img src='{logo_c}' style='max-height: 90px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)

c_inf1, c_inf2, c_inf3 = st.columns(3)
with c_inf1:
    st.markdown("<div class='custom-label'>EMPRESA</div>", unsafe_allow_html=True)
    st.text_input("Empresa", key="ui_empresa", label_visibility="collapsed")
with c_inf2:
    st.markdown("<div class='custom-label'>NOMBRE (DUEÑO DEL ONE TRACK)</div>", unsafe_allow_html=True)
    st.text_input("Dueño", key="ui_dueno", label_visibility="collapsed")
with c_inf3:
    st.markdown("<div class='custom-label'>PUESTO</div>", unsafe_allow_html=True)
    st.text_input("Puesto", key="ui_puesto", label_visibility="collapsed")

st.divider()

v_actual_title = f" {st.session_state.vista_actual}" if st.session_state.vista_actual in trimestres else ""
col_t, col_btn = st.columns([4, 1])
with col_t: st.markdown(f"<h2 style='color:#002060; font-weight:900; margin:0;'>Tablero de Control{v_actual_title}</h2>", unsafe_allow_html=True)
with col_btn:
    if st.button("Guardar Cambios", type="primary", use_container_width=True):
        with st.spinner("Sincronizando de forma rápida..."):
            guardar_en_bd()
            st.session_state.datos_cargados = False
        st.success("Guardado exitoso.")
st.write("")

# TARJETA INFORMATIVA NUEVA
st.markdown("""
<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #002060; margin-bottom: 20px;'>
    <p style='margin: 0; color: #4b5563; font-size: 15px;'>
        <strong style='color:#002060;'>Indicadores Clave de Desempeño (KPIs)</strong> &rarr; miden el resultado/desempeño.<br>
        <strong style='color:#002060;'>Iniciativas Estratégicas</strong> &rarr; miden la ejecución para mover esos resultados.
    </p>
</div>
""", unsafe_allow_html=True)

# TARJETAS FRONTALES PONDERACION Y RESULTADOS
col_w, col_s1, col_s2, col_s3 = st.columns([1.5, 1, 1, 1])
with col_w:
    st.markdown("<div class='summary-card' style='padding:15px;'><p class='summary-title'>Ponderación Global</p>", unsafe_allow_html=True)
    c_kpi, c_okr = st.columns(2)
    with c_kpi:
        st.markdown("<div class='custom-label'>INDICADORES CLAVE DE DESEMPEÑO (KPIs) (%)</div>", unsafe_allow_html=True)
        st.number_input("Ind", key="ui_p_kpis", label_visibility="collapsed")
    with c_okr:
        st.markdown("<div class='custom-label'>INICIATIVAS ESTRATÉGICAS (%)</div>", unsafe_allow_html=True)
        st.number_input("Ini", key="ui_p_okrs", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

# --- VISTAS NAVEGABLES ---
if st.session_state.vista_actual in trimestres.keys():
    q_name = st.session_state.vista_actual
    meses_q = trimestres[q_name]
    
    for i in range(1, st.session_state.get(f"num_iniciativas_{q_name}", 1) + 1): init_okr_structure(q_name, i, meses_q)
    
    st.markdown(f"<div class='section-title'>Indicadores Clave de Desempeño (KPIs) - {q_name}</div>", unsafe_allow_html=True)
    render_footer(st.session_state.get(f"df_kpi_{q_name}", pd.DataFrame()), meses_q)
    
    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
    st.session_state[f"df_kpi_{q_name}"] = st.data_editor(
        st.session_state[f"df_kpi_{q_name}"],
        use_container_width=True, hide_index=True, num_rows="dynamic",
        column_config={
            "Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio", "Valor Final"]), 
            "UM": st.column_config.SelectboxColumn(options=["U", "$", "%", "Tiempo"]), 
            "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])
        },
        key=f"ed_kpi_{q_name}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='section-title'>Iniciativas Estratégicas - {q_name}</div>", unsafe_allow_html=True)
    for i in range(1, st.session_state.get(f"num_iniciativas_{q_name}", 1) + 1):
        st.markdown("<div class='iniciativa-box'>", unsafe_allow_html=True)
        
        df_c_prog = st.session_state.get(f"df_crit_{q_name}_{i}", pd.DataFrame())
        acum_ini, tot_peso_ini = 0.0, 0.0
        has_crit = False
        if not df_c_prog.empty:
            for c_idx, row_c in df_c_prog.iterrows():
                if str(row_c["Criterio"]).strip() != "":
                    has_crit = True
                    peso_c = float(row_c["%"] or 0)
                    p_c = sum([float(row_c[f"{m} Prog"] or 0) for m in meses_q])
                    r_c = sum([float(row_c[f"{m} Real"] or 0) for m in meses_q])
                    cump_c = calc_cump(p_c, r_c, str(row_c["< Mejor"]))
                    acum_ini += cump_c * (peso_c / 100.0)
                    tot_peso_ini += peso_c
        cump_crit = (acum_ini / (tot_peso_ini / 100.0)) if tot_peso_ini > 0 else 0.0
        
        df_t_prog = st.session_state.get(f"df_tareas_{q_name}_{i}", pd.DataFrame())
        tot_t, comp = 0, 0
        if not df_t_prog.empty:
            t_validas = df_t_prog[df_t_prog["Tarea"].str.strip() != ""]
            tot_t = len(t_validas)
            comp = t_validas["Completado"].sum() if tot_t > 0 else 0
        cump_tareas = (comp / tot_t * 100.0) if tot_t > 0 else 0.0
        
        if has_crit: avance_ini = (cump_crit * 0.5) + (cump_tareas * 0.5)
        else: avance_ini = cump_tareas
            
        col_ini = ob_color(avance_ini, float(st.session_state.get("cfg_sob", 100.0)), float(st.session_state.get("cfg_meta", 90.0)), float(st.session_state.get("cfg_med", 80.0)))
        txt_col = "black" if col_ini in ["#ffff00", "#92d050"] else "white"

        h_col1, h_col2 = st.columns([1, 2.5])
        with h_col1: st.markdown(f"<div class='iniciativa-header'>Iniciativa #{i}</div>", unsafe_allow_html=True)
        with h_col2: 
            st.markdown(f"""
            <div style='display:flex; gap:10px; justify-content: flex-end;'>
                <div style='background:#f0f2f6; color:#002060; padding: 8px 12px; border-radius:6px; font-weight:900; font-size:12px; border:1px solid #d1d5db;'>CRITERIOS: {cump_crit:.1f}%</div>
                <div style='background:#f0f2f6; color:#002060; padding: 8px 12px; border-radius:6px; font-weight:900; font-size:12px; border:1px solid #d1d5db;'>TAREAS: {cump_tareas:.1f}%</div>
                <div style='background:{col_ini}; color:{txt_col}; padding: 8px 15px; border-radius:6px; font-weight:900; font-size:14px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>AVANCE INTEGRADO: {avance_ini:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        ch1, ch2, ch3 = st.columns([3, 1, 1])
        with ch1:
            st.markdown("<div class='custom-label'>NOMBRE DE LA INICIATIVA</div>", unsafe_allow_html=True)
            st.text_input("Nombre", key=f"ui_nom_{q_name}_{i}", label_visibility="collapsed")
        
        with ch2:
            st.markdown("<div class='custom-label'>PONDERACIÓN (%)</div>", unsafe_allow_html=True)
            st.number_input("Peso", key=f"ui_peso_{q_name}_{i}", label_visibility="collapsed")
        
        with ch3:
            opciones_salud = ["🟢 En Tiempo", "🟡 En Riesgo", "🔴 Retrasado"]
            st.markdown("<div class='custom-label'>ESTATUS ACTUAL</div>", unsafe_allow_html=True)
            st.selectbox("Salud", options=opciones_salud, key=f"ui_salud_{q_name}_{i}", label_visibility="collapsed")
        
        st.markdown("<div class='custom-label'>OBJETIVO</div>", unsafe_allow_html=True)
        st.text_area("Obj", key=f"ui_obj_{q_name}_{i}", height=80, label_visibility="collapsed")
        
        st.markdown("<div class='sub-section-title'>Criterios de Éxito (Medición)</div>", unsafe_allow_html=True)
        st.session_state[f"df_crit_{q_name}_{i}"] = st.data_editor(
            st.session_state[f"df_crit_{q_name}_{i}"],
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio"]), "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])},
            key=f"ed_crit_{q_name}_{i}"
        )
        
        st.markdown("<div class='sub-section-title'>Plan de Tareas y Seguimiento</div>", unsafe_allow_html=True)
        st.session_state[f"df_tareas_{q_name}_{i}"] = st.data_editor(
            st.session_state[f"df_tareas_{q_name}_{i}"],
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"Jerarquia": st.column_config.TextColumn(width="small", help="Ej: 1, 1.1"), "Inicio": st.column_config.DateColumn(format="YYYY-MM-DD"), "Fin": st.column_config.DateColumn(format="YYYY-MM-DD")},
            key=f"ed_tar_{q_name}_{i}"
        )
        
        st.write("")
        dibujar_gantt(st.session_state[f"df_tareas_{q_name}_{i}"])
        st.markdown("</div><hr class='iniciativa-divider'>", unsafe_allow_html=True)

    col_add, col_rem, _ = st.columns([2, 2, 6])
    with col_add:
        if st.button("➕ Añadir Iniciativa", use_container_width=True, key=f"add_{q_name}"):
            st.session_state[f"num_iniciativas_{q_name}"] = st.session_state.get(f"num_iniciativas_{q_name}", 1) + 1
            st.rerun()
    with col_rem:
        if st.button("🗑️ Quitar Iniciativa", use_container_width=True, key=f"rem_{q_name}"):
            if st.session_state.get(f"num_iniciativas_{q_name}", 1) > 1:
                st.session_state[f"num_iniciativas_{q_name}"] -= 1
                st.rerun()

elif st.session_state.vista_actual == "Configuración de Cuenta":
    st.markdown("<div class='section-title'>Configuración de Cuenta</div>", unsafe_allow_html=True)
    
    # st.markdown("<div class='sub-section-title'>Generar Datos de Prueba (Dummy)</div>", unsafe_allow_html=True)
    # st.info("Presiona este botón para llenar tu tablero actual con datos de ejemplo matemáticamente perfectos. Luego ve a cualquier pestaña y presiona 'Guardar Cambios' para enviarlos a tu base de datos.")
    # if st.button("Llenar tablero con datos Dummy", type="secondary"):
    #     generar_dummy_onetest()
    #     st.rerun()
        
    st.markdown("<br><div class='sub-section-title'>Seguridad de la Cuenta</div>", unsafe_allow_html=True)
    st.write(f"**Usuario Actual (Token de Acceso):** {token}")
    n_pwd = st.text_input("**Nueva Contraseña**", type="password", placeholder="Escribe aquí para cambiar tu contraseña")
    if st.button("Actualizar Contraseña", type="primary"):
        if n_pwd:
            df_us = conn.query("SELECT * FROM usuarios", ttl=0)
            df_us.loc[df_us['username'] == token, 'password'] = n_pwd
            df_us.to_sql("usuarios", con=conn.engine, if_exists="replace", index=False)
            st.success("Contraseña actualizada correctamente.")
        else:
            st.warning("Escribe una contraseña válida.")

# --- CÁLCULOS Y PESTAÑA RESUMEN ANUAL ---
def get_mes_cump(m, q_name):
    t_peso_k, acum_k = 0.0, 0.0
    df_kpi = st.session_state.get(f"df_kpi_{q_name}", pd.DataFrame())
    if not df_kpi.empty:
        for i in range(len(df_kpi)):
            if str(df_kpi["Indicadores Clave de Desempeño (KPIs)"].iloc[i]).strip():
                p = float(df_kpi[f"{m} Prog"].iloc[i] or 0)
                r = float(df_kpi[f"{m} Real"].iloc[i] or 0)
                peso = float(df_kpi["Peso %"].iloc[i] or 0)
                cump = calc_cump(p, r, str(df_kpi["< Mejor"].iloc[i]))
                acum_k += cump * (peso / 100.0); t_peso_k += peso
    res_k = (acum_k / (t_peso_k / 100.0)) if t_peso_k > 0 else 0.0

    t_peso_o, acum_o = 0.0, 0.0
    for i in range(1, st.session_state.get(f"num_iniciativas_{q_name}", 1) + 1):
        if str(st.session_state.get(f"ui_nom_{q_name}_{i}", "")).strip():
            peso_o = float(st.session_state.get(f"ui_peso_{q_name}_{i}", 0.0))
            df_c = st.session_state.get(f"df_crit_{q_name}_{i}", pd.DataFrame())
            p_t, r_t = 0.0, 0.0
            has_crit = False
            if not df_c.empty:
                for c_i, row_c in df_c.iterrows():
                    if str(row_c["Criterio"]).strip():
                        has_crit = True
                        p_t += float(row_c[f"{m} Prog"] or 0)
                        r_t += float(row_c[f"{m} Real"] or 0)
            cump_o_crit = calc_cump(p_t, r_t, "NO") if has_crit else 0.0
            
            df_tar = st.session_state.get(f"df_tareas_{q_name}_{i}", pd.DataFrame())
            t_valid = df_tar[df_tar["Tarea"].str.strip() != ""] if not df_tar.empty else pd.DataFrame()
            tot_t = len(t_valid)
            cump_o_tar = (t_valid["Completado"].sum() / tot_t * 100.0) if tot_t > 0 else 0.0
            
            if has_crit: cump_o_ini = (cump_o_crit * 0.5) + (cump_o_tar * 0.5)
            else: cump_o_ini = cump_o_tar
                
            acum_o += cump_o_ini * (peso_o / 100.0); t_peso_o += peso_o
    res_o = (acum_o / (t_peso_o / 100.0)) if t_peso_o > 0 else 0.0

    t_peso_tot = float(st.session_state.get("ui_p_kpis", 50.0)) + float(st.session_state.get("ui_p_okrs", 50.0))
    res_tot = ((res_k * (float(st.session_state.get("ui_p_kpis", 50.0)) / 100.0)) + (res_o * (float(st.session_state.get("ui_p_okrs", 50.0)) / 100.0))) / (t_peso_tot / 100.0) if t_peso_tot > 0 else 0.0
    return res_k, res_o, res_tot

anual_data, line_mensual = [], []
for q, meses in trimestres.items():
    acum_k_q, acum_o_q, acum_tot_q = 0.0, 0.0, 0.0
    for m in meses:
        rk, ro, rtot = get_mes_cump(m, q)
        anual_data.append({"Mes": m, "Indicadores Clave de Desempeño (KPIs)": rk/100.0, "Iniciativas Estratégicas": ro/100.0, "Integrado": rtot/100.0, "Trimestre": q, "Resultado Q": None})
        line_mensual.extend([{"Mes": m, "Tipo": "Indicadores Clave de Desempeño (KPIs)", "Valor": rk}, {"Mes": m, "Tipo": "Iniciativas Estratégicas", "Valor": ro}, {"Mes": m, "Tipo": "Desempeño Integrado", "Valor": rtot}])
        acum_k_q += rk; acum_o_q += ro; acum_tot_q += rtot
    anual_data[-1]["Resultado Q"] = (acum_tot_q / 3.0) / 100.0

df_anual = pd.DataFrame(anual_data)

# CALCULO REACTIVO TARJETAS FRONTALES
if st.session_state.vista_actual in trimestres.keys():
    q_sel = st.session_state.vista_actual
    df_q = df_anual[df_anual["Trimestre"] == q_sel]
    res_k_total = df_q["Indicadores Clave de Desempeño (KPIs)"].mean() * 100
    res_o_total = df_q["Iniciativas Estratégicas"].mean() * 100
    res_tot_final = df_q["Integrado"].mean() * 100
    l_kpi, l_okr, l_tot = "Indicadores Clave de Desempeño (KPIs)", "Iniciativas Estratégicas", "Total ONE TRACK"
else:
    res_k_total, res_o_total = df_anual["Indicadores Clave de Desempeño (KPIs)"].mean() * 100, df_anual["Iniciativas Estratégicas"].mean() * 100
    res_tot_final = df_anual["Integrado"].mean() * 100
    l_kpi, l_okr, l_tot = "Indicadores Clave de Desempeño (KPIs)", "Iniciativas Estratégicas", "Total ONE TRACK"

v_sob, v_meta, v_med = float(st.session_state.get("cfg_sob", 100.0)), float(st.session_state.get("cfg_meta", 90.0)), float(st.session_state.get("cfg_med", 89.0))
c_kpi, c_okr, c_tot = ob_color(res_k_total, v_sob, v_meta, v_med), ob_color(res_o_total, v_sob, v_meta, v_med), ob_color(res_tot_final, v_sob, v_meta, v_med)
txt_kpi, txt_okr, txt_tot = ("black" if c_kpi in ["#ffff00", "#92d050"] else "white"), ("black" if c_okr in ["#ffff00", "#92d050"] else "white"), ("black" if c_tot in ["#ffff00", "#92d050"] else "white")

with col_s1: st.markdown(f"<div class='summary-card' style='background-color:{c_kpi};'><p class='summary-title' style='color:{txt_kpi};'>{l_kpi}</p><p class='summary-value' style='color:{txt_kpi};'>{res_k_total:.0f} %</p></div>", unsafe_allow_html=True)
with col_s2: st.markdown(f"<div class='summary-card' style='background-color:{c_okr};'><p class='summary-title' style='color:{txt_okr};'>{l_okr}</p><p class='summary-value' style='color:{txt_okr};'>{res_o_total:.0f} %</p></div>", unsafe_allow_html=True)
with col_s3: st.markdown(f"<div class='summary-card' style='background-color:{c_tot};'><p class='summary-title' style='color:{txt_tot};'>{l_tot}</p><p class='summary-value' style='color:{txt_tot};'>{res_tot_final:.0f} %</p></div>", unsafe_allow_html=True)

if st.session_state.vista_actual == "Resumen Anual":
    st.markdown("<div class='section-title'>Resumen Anual del Desempeño</div>", unsafe_allow_html=True)
    
    with st.expander("⚙️ Configuración de Semáforos (Criterios de Éxito)", expanded=False):
        st.info("Estos rangos definen qué colores se mostrarán automáticamente en tus recuadros de avance de todo el año.")
        col_sem, col_space = st.columns([2, 3])
        with col_sem:
            st.markdown("""<div class='semaforo-container'><div class='sem-header'>Criterios de Éxito</div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns([2, 1])
            c1.markdown("<div class='sem-label' style='background-color:#00b050; color:white;'>Sobresaliente</div>", unsafe_allow_html=True)
            st.number_input("sob", key="cfg_sob", label_visibility="collapsed")
            
            c3, c4 = st.columns([2, 1])
            c3.markdown("<div class='sem-label' style='background-color:#92d050; color:white;'>Meta</div>", unsafe_allow_html=True)
            st.number_input("meta", key="cfg_meta", label_visibility="collapsed")
            
            c5, c6 = st.columns([2, 1])
            c5.markdown("<div class='sem-label' style='background-color:#ffff00;'>Medio</div>", unsafe_allow_html=True)
            st.number_input("med", key="cfg_med", label_visibility="collapsed")
            
            c7, c8 = st.columns([2, 1])
            c7.markdown("<div class='sem-label' style='background-color:#ff0000; color:white; border:none;'>Bajo</div>", unsafe_allow_html=True)
            c8.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:800; font-size:16px;'>{st.session_state.get('cfg_med', 80.0)}%</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    col_ta, col_ch = st.columns([1.2, 1])
    with col_ta:
        st.markdown("<div class='sub-section-title'>Desempeño Mensual y Trimestral</div>", unsafe_allow_html=True)
        st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
        st.dataframe(df_anual.style.format({"Indicadores Clave de Desempeño (KPIs)": "{:.0%}", "Iniciativas Estratégicas": "{:.0%}", "Integrado": "{:.0%}", "Resultado Q": "{:.0%}"}), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_ch:
        st.markdown("<div class='sub-section-title' style='text-align:center;'>Desempeño Trimestral</div>", unsafe_allow_html=True)
        df_q = df_anual.dropna(subset=["Resultado Q"])[["Trimestre", "Resultado Q"]].copy()
        df_q["Resultado Q"] = df_q["Resultado Q"] * 100
        ch_q = alt.Chart(df_q).mark_line(point=True, color="#d95f02", strokeWidth=3).encode(
            x=alt.X('Trimestre', sort=None, title='', axis=alt.Axis(labelFontWeight="bold")),
            y=alt.Y('Resultado Q', title='', scale=alt.Scale(domain=[0, 120]), axis=alt.Axis(gridColor="#f0f2f6")),
            tooltip=['Trimestre', 'Resultado Q']
        ).properties(height=280)
        text_q = ch_q.mark_text(align='center', baseline='bottom', dy=-10, fontWeight='bold', color="#002060").encode(text=alt.Text('Resultado Q:Q', format='.0f'))
        st.altair_chart(ch_q + text_q, use_container_width=True)

    st.divider()
    st.markdown("<div class='sub-section-title' style='text-align:center;'>Tendencia de Desempeño Mensual</div>", unsafe_allow_html=True)
    df_m = pd.DataFrame(line_mensual)
    
    ch_m = alt.Chart(df_m).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Mes', sort=meses_totales, title='', axis=alt.Axis(labelFontWeight="bold")),
        y=alt.Y('Valor', title='', scale=alt.Scale(domain=[0, 120]), axis=alt.Axis(gridColor="#f0f2f6")),
        color=alt.Color('Tipo', scale=alt.Scale(domain=['Indicadores Clave de Desempeño (KPIs)', 'Iniciativas Estratégicas', 'Desempeño Integrado'], range=['#002060', '#4B8BBE', '#808080']), legend=alt.Legend(title="", orient='bottom', labelFontWeight="bold")),
        tooltip=['Mes', 'Tipo', 'Valor']
    ).properties(height=350)
    st.altair_chart(ch_m, use_container_width=True)
