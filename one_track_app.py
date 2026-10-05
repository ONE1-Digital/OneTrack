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
    
    /* Forzar fondo blanco en campos de texto/inputs */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 6px !important;
    }

    /* Tarjetas y Estructura Iniciativas (ALTURA FIJA Y CENTRADA) */
    .summary-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #002060; height: 130px; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    .summary-title { font-size: 14px; color: #4b5563; font-weight: 900; margin-bottom: 5px; text-transform: uppercase;}
    .summary-value { font-size: 28px; color: #002060; font-weight: 900; margin: 0;}
    
    .iniciativa-box { padding: 5px 0; margin-bottom: 10px; }
    .iniciativa-header { font-size: 20px; font-weight: 900; color: #ffffff; background-color: #002060; padding: 10px 20px; border-radius: 8px; display: inline-block; margin-bottom: 15px;}
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

def format_date_spanish(d):
    meses_abrev = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    return f"{d.day} de {meses_abrev[d.month-1]}"

def update_estatus_tareas(df):
    hoy = date.today()
    if "Estatus" not in df.columns:
        df["Estatus"] = "⚪ Pendiente"
    for idx, row in df.iterrows():
        if row.get("Completado", False):
            df.at[idx, "Estatus"] = "🟢 A tiempo"
        else:
            if pd.notnull(row.get("Fin")):
                try:
                    fin = pd.to_datetime(row["Fin"]).date()
                    if fin < hoy:
                        df.at[idx, "Estatus"] = "🔴 Retrasado"
                    else:
                        df.at[idx, "Estatus"] = "🟢 A tiempo"
                except:
                    df.at[idx, "Estatus"] = "🟢 A tiempo"
            else:
                df.at[idx, "Estatus"] = "⚪ Pendiente"
    return df

def update_avance_resultados(df):
    if df.empty: return df
    if "Avance %" not in df.columns: df["Avance %"] = 0.0
    for idx, row in df.iterrows():
        if str(row.get("Nombre", "")).strip() != "":
            try:
                meta = float(row.get("Meta", 0.0))
                real = float(row.get("Real", 0.0))
                menor = str(row.get("< Mejor", "NO"))
                df.at[idx, "Avance %"] = calc_cump(meta, real, menor)
            except:
                df.at[idx, "Avance %"] = 0.0
        else:
            df.at[idx, "Avance %"] = 0.0
    return df

# --- FUNCION DUMMY QUE SERÁ LLAMADA POR CALLBACK ---
def generar_dummy_onetest():
    mult_q = {"Q1": 0.85, "Q2": 0.90, "Q3": 0.98, "Q4": 1.05}
    cols_t = ["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado", "Estatus"]
    cols_out = ["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance %"]

    st.session_state["ui_p_kpis"] = 50.0
    st.session_state["ui_p_okrs"] = 50.0
    st.session_state["cfg_sob"] = 100.0
    st.session_state["cfg_meta"] = 90.0
    st.session_state["cfg_med"] = 80.0

    for q_name, meses in trimestres.items():
        df_k = pd.DataFrame(columns=["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"] + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses])
        df_k.loc[1] = ["Ventas Mensuales", "Acumulado", 500000.0, "$", "NO", 50.0] + [166666.0, 166666.0 * mult_q[q_name]] * 3
        df_k.loc[2] = ["Satisfacción de Clientes", "Promedio", 95.0, "%", "NO", 50.0] + [95.0, 95.0 * mult_q[q_name]] * 3
        st.session_state[f"df_kpi_{q_name}"] = df_k

    # --- Q1 (1 Iniciativa 100%) ---
    q_n = "Q1"; st.session_state[f"num_iniciativas_{q_n}"] = 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Expansión de Mercado Norte"
    st.session_state[f"ui_peso_{q_n}_1"] = 100.0
    st.session_state[f"ui_obj_{q_n}_1"] = "Conquistar 3 nuevos estados mediante campañas digitales y alianzas locales."
    
    df_o = pd.DataFrame(columns=cols_out)
    df_o.loc[1] = ["Abrir sucursales físicas", "U", "NO", 3.0, 2.0, 0.0]
    st.session_state[f"df_outputs_{q_n}_1"] = update_avance_resultados(df_o)
    
    df_t = pd.DataFrame(columns=cols_t)
    df_t.loc[1] = ["1.", "Investigación de Mercado", "Ana", date(2026, 1, 5), date(2026, 1, 15), True, ""]
    df_t.loc[2] = ["1.1", "Contratación de Equipo", "Luis", date(2026, 1, 16), date(2026, 2, 10), True, ""]
    df_t.loc[3] = ["1.2", "Lanzamiento de Campaña", "Carlos", date(2026, 2, 15), date(2026, 3, 20), False, ""]
    st.session_state[f"df_tareas_{q_n}_1"] = update_estatus_tareas(df_t)

    # --- Q2 (2 Iniciativas: 60% y 40%) ---
    q_n = "Q2"; st.session_state[f"num_iniciativas_{q_n}"] = 2
    
    st.session_state[f"ui_nom_{q_n}_1"] = "Lanzamiento de Nuevo Producto"
    st.session_state[f"ui_peso_{q_n}_1"] = 60.0
    st.session_state[f"ui_obj_{q_n}_1"] = "Lanzar producto Alpha antes del cierre de semestre."
    df_o1 = pd.DataFrame(columns=cols_out)
    df_o1.loc[1] = ["Prototipos validados", "U", "NO", 5.0, 5.0, 0.0]
    st.session_state[f"df_outputs_{q_n}_1"] = update_avance_resultados(df_o1)
    
    df_t1 = pd.DataFrame(columns=cols_t)
    df_t1.loc[1] = ["1.", "Diseño de Prototipo", "Ana", date(2026, 4, 1), date(2026, 4, 20), True, ""]
    df_t1.loc[2] = ["2.", "Pruebas de Calidad", "Luis", date(2026, 5, 1), date(2026, 5, 15), True, ""]
    df_t1.loc[3] = ["3.", "Campaña de Preventa", "Carlos", date(2026, 6, 1), date(2026, 6, 25), False, ""]
    st.session_state[f"df_tareas_{q_n}_1"] = update_estatus_tareas(df_t1)

    st.session_state[f"ui_nom_{q_n}_2"] = "Optimización de Costos Operativos"
    st.session_state[f"ui_peso_{q_n}_2"] = 40.0
    st.session_state[f"ui_obj_{q_n}_2"] = "Reducir costos operativos en logística."
    df_o2 = pd.DataFrame(columns=cols_out)
    df_o2.loc[1] = ["Ahorro en logística", "%", "SI", 15.0, 12.0, 0.0]
    st.session_state[f"df_outputs_{q_n}_2"] = update_avance_resultados(df_o2)
    
    df_t2 = pd.DataFrame(columns=cols_t)
    df_t2.loc[1] = ["1.", "Auditoría Interna", "Sofia", date(2026, 4, 5), date(2026, 4, 25), True, ""]
    df_t2.loc[2] = ["2.", "Renegociación", "Luis", date(2026, 5, 5), date(2026, 5, 20), False, ""]
    df_t2.loc[3] = ["3.", "Implementación Rutas", "Sofia", date(2026, 6, 1), date(2026, 6, 28), False, ""]
    st.session_state[f"df_tareas_{q_n}_2"] = update_estatus_tareas(df_t2)

    # --- Q3 (1 Iniciativa 100%) ---
    q_n = "Q3"; st.session_state[f"num_iniciativas_{q_n}"] = 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Certificación ISO 9001"
    st.session_state[f"ui_peso_{q_n}_1"] = 100.0
    st.session_state[f"ui_obj_{q_n}_1"] = "Obtener certificación en procesos clave."
    df_o3 = pd.DataFrame(columns=cols_out)
    df_o3.loc[1] = ["Fases completadas", "U", "NO", 3.0, 2.0, 0.0]
    st.session_state[f"df_outputs_{q_n}_1"] = update_avance_resultados(df_o3)
    
    df_t3 = pd.DataFrame(columns=cols_t)
    df_t3.loc[1] = ["1.", "Diagnóstico Inicial", "Juan", date(2026, 7, 1), date(2026, 7, 15), True, ""]
    df_t3.loc[2] = ["2.", "Capacitación de Personal", "Ana", date(2026, 8, 1), date(2026, 8, 20), False, ""]
    df_t3.loc[3] = ["3.", "Auditoría Final", "Luis", date(2026, 9, 10), date(2026, 9, 25), False, ""]
    st.session_state[f"df_tareas_{q_n}_1"] = update_estatus_tareas(df_t3)

    # --- Q4 (1 Iniciativa 100%) ---
    q_n = "Q4"; st.session_state[f"num_iniciativas_{q_n}"] = 1
    st.session_state[f"ui_nom_{q_n}_1"] = "Cierre de Año y Planificación 2027"
    st.session_state[f"ui_peso_{q_n}_1"] = 100.0
    st.session_state[f"ui_obj_{q_n}_1"] = "Cerrar métricas anuales y planear presupuesto 2027."
    df_o4 = pd.DataFrame(columns=cols_out)
    df_o4.loc[1] = ["Presupuestos aprobados", "U", "NO", 4.0, 4.0, 0.0]
    st.session_state[f"df_outputs_{q_n}_1"] = update_avance_resultados(df_o4)
    
    df_t4 = pd.DataFrame(columns=cols_t)
    df_t4.loc[1] = ["1.", "Revisión Financiera", "Carlos", date(2026, 10, 5), date(2026, 10, 25), True, ""]
    df_t4.loc[2] = ["2.", "Definición Metas", "Ana", date(2026, 11, 1), date(2026, 11, 20), False, ""]
    df_t4.loc[3] = ["3.", "Presentación Ejecutiva", "Juan", date(2026, 12, 1), date(2026, 12, 15), False, ""]
    st.session_state[f"df_tareas_{q_n}_1"] = update_estatus_tareas(df_t4)

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
        html_footer += f"<div class='footer-box' style='background-color:{col}; color:{txt};'>{m}: {avance:.1f
