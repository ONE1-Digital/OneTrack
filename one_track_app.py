from datetime import date
import altair as alt
import pandas as pd
from sqlalchemy import text
import streamlit as st
import streamlit.components.v1 as components

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE TRACK - Workspace", layout="wide", initial_sidebar_state="expanded")

# --- CSS MINIMALISTA, ELEGANTE Y BLANCO ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }
    [data-testid="stSidebar"] button[data-baseweb="button"] { border-radius: 8px; margin-bottom: 5px; border: 1px solid transparent; transition: all 0.2s;}
    [data-testid="stSidebar"] button[kind="secondary"] { background-color: #f8f9fa; color: #4b5563; border: 1px solid #e5e7eb;}
    [data-testid="stSidebar"] button[kind="secondary"]:hover { background-color: #e2e8f0; }
    [data-testid="stSidebar"] button[kind="primary"] { background-color: #002060 !important; color: #ffffff !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: none;}
    [data-testid="stSidebar"] button p { font-size: 18px !important; font-weight: 900 !important; margin: 0; }
    .section-title { font-size: 26px; font-weight: 900; color: #002060; border-bottom: 3px solid #e5e7eb; padding-bottom: 10px; margin-top: 20px; margin-bottom: 20px; }
    .sub-section-title { font-size: 16px; font-weight: 900; color: #002060; margin-top: 28px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; border-left: 4px solid #002060; padding-left: 10px;}
    .custom-label { font-size: 13px; font-weight: 900; color: #002060; text-transform: uppercase; margin-bottom: 5px; margin-top: 10px; letter-spacing: 0.5px; }
    .img-placeholder { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; height: 120px; display: flex; align-items: center; justify-content: center; padding: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.04);}
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 6px !important; }
    .summary-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #002060; height: 130px; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    .summary-title { font-size: 14px; color: #4b5563; font-weight: 900; margin-bottom: 5px; text-transform: uppercase;}
    .summary-value { font-size: 28px; color: #002060; font-weight: 900; margin: 0;}
    .iniciativa-box { padding: 5px 0; margin-bottom: 10px; }
    .iniciativa-header { font-size: 20px; font-weight: 900; color: #ffffff; background-color: #002060; padding: 10px 20px; border-radius: 8px; display: inline-block; margin-bottom: 15px;}
    .iniciativa-divider { border-top: 3px dashed #cbd5e1; margin: 40px 0; }
    div[data-testid="stDataFrame"] > div { border: none; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08); background-color: #ffffff; padding: 2px; border: 1px solid #e2e8f0; }
    div[data-testid="stDataFrame"] table th { background-color: #002060 !important; color: #ffffff !important; font-size: 15px !important; font-weight: 900 !important; text-transform: uppercase; text-align: center !important;}
    .footer-box { border: 1px solid #d1d5db; padding: 6px 15px; font-weight: 900; border-radius: 6px; min-width: 90px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
    .interval-box { border-radius: 8px; padding: 12px 18px; margin-bottom: 10px; font-weight: 800; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
    .guide-callout { background-color: #ffffff; padding: 18px 22px; border-radius: 10px; border-left: 5px solid #002060; box-shadow: 0 2px 5px rgba(0,0,0,0.03); margin: 15px 0 20px 0; font-size: 14.5px; line-height: 1.6; color: #334155;}
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
trimestres = {"Q1": ["Ene", "Feb", "Mar"], "Q2": ["Abr", "May", "Jun"], "Q3": ["Jul", "Ago", "Sep"], "Q4": ["Oct", "Nov", "Dic"]}
meses_totales = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DEFAULT_LOGO_CLIENTE = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/MARBER.png"
DEFAULT_LOGO_ONE_TRACK = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/ONE_TRACK_LOGO.png"

# --- CONEXION A BASE DE DATOS ---
conn = st.connection("supabase", type="sql")

def init_db():
    try:
        df = conn.query("SELECT * FROM usuarios LIMIT 1", ttl=0)
        if 'nombre' not in df.columns: raise Exception("Faltan columnas")
    except Exception:
        df_admin = pd.DataFrame([{"username": "admin", "password": "admin", "role": "admin", "nombre": "Admin", "puesto": "Administrador", "empresa": "ONE TRACK", "logo_url": ""}])
        df_admin.to_sql("usuarios", con=conn.engine, if_exists="replace", index=False)

init_db()

# ==============================================================================
# FASE 1: BÓVEDA DE ESTADO Y ENLACES (ANTI-DOBLE INPUT)
# ==============================================================================
if "perm_store" not in st.session_state:
    st.session_state.perm_store = {}

def get_store(key, default=None):
    return st.session_state.perm_store.get(key, default)

def set_store(key, val):
    st.session_state.perm_store[key] = val

def safe_float(val, default=0.0):
    if val is None or pd.isna(val):
        return float(default)
    try:
        return float(val)
    except (ValueError, TypeError):
        return float(default)

def safe_str(val, default=""):
    if val is None or pd.isna(val):
        return default
    s = str(val).strip()
    return default if s in ["None", "nan", "NaN"] else s

def get_col_ci(row, col_name, default=""):
    for k in row.index:
        if str(k).strip().lower() == col_name.lower():
            return safe_str(row[k], default)
    return default

def to_date_or_none(val):
    if val is None or pd.isna(val) or str(val).strip() == "":
        return None
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None

def bind_text_input(label, key, default=""):
    if key not in st.session_state:
        val = get_store(key, default)
        st.session_state[key] = safe_str(val, default)
    st.text_input(label, key=key, label_visibility="collapsed")
    set_store(key, st.session_state[key])

def bind_text_area(label, key, default="", height=70):
    if key not in st.session_state:
        val = get_store(key, default)
        st.session_state[key] = safe_str(val, default)
    st.text_area(label, key=key, height=height, label_visibility="collapsed")
    set_store(key, st.session_state[key])

def bind_number_input(label, key, default=0.0):
    if key not in st.session_state:
        val = get_store(key, default)
        st.session_state[key] = safe_float(val, default)
    st.number_input(label, key=key, label_visibility="collapsed")
    set_store(key, st.session_state[key])

# ==============================================================================
# FASE 2: FORMULAS MATEMATICAS Y COLORIMETRIA
# ==============================================================================
def calc_cump(prog, real, menor_mejor="NO"):
    prog = safe_float(prog, 0.0)
    real = safe_float(real, 0.0)
    if prog == 0 and real == 0: return 0.0
    if menor_mejor == "SI": return (prog / real * 100) if real > 0 else 100.0
    else: return (real / prog * 100) if prog > 0 else (100.0 if real > 0 else 0.0)

def ob_color(val, c_rojo=79.0, c_amarillo=89.0, c_verde=100.0):
    val = safe_float(val, 0.0)
    if val > c_verde: return "#00b050"
    elif val > c_amarillo: return "#92d050"
    elif val > c_rojo: return "#ffff00"
    else: return "#ff0000"

def ob_circle(val, c_rojo=79.0, c_amarillo=89.0, c_verde=100.0):
    val = safe_float(val, 0.0)
    if val > c_verde: return "🟢"
    elif val > c_amarillo: return "🟢"
    elif val > c_rojo: return "🟡"
    else: return "🔴"

def format_date_spanish(d):
    meses_abrev = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    return f"{d.day} de {meses_abrev[d.month-1]}"

def update_estatus_tareas(df):
    if df is None or df.empty: return df
    df_res = df.copy().reset_index(drop=True)
    hoy = date.today()
    if "Estatus" not in df_res.columns: df_res["Estatus"] = "⚪ Pendiente"
    if "Completado" not in df_res.columns: df_res["Completado"] = False
    df_res["Completado"] = df_res["Completado"].fillna(False).astype(bool)
    if "Inicio" in df_res.columns:
        df_res["Inicio"] = df_res["Inicio"].apply(to_date_or_none)
    if "Fin" in df_res.columns:
        df_res["Fin"] = df_res["Fin"].apply(to_date_or_none)
    for idx, row in df_res.iterrows():
        if row.get("Completado", False):
            df_res.at[idx, "Estatus"] = "🟢 A tiempo"
        else:
            fin = row.get("Fin")
            if fin is not None:
                try:
                    if fin < hoy: df_res.at[idx, "Estatus"] = "🔴 Retrasado"
                    else: df_res.at[idx, "Estatus"] = "🟢 A tiempo"
                except Exception:
                    df_res.at[idx, "Estatus"] = "🟢 A tiempo"
            else:
                df_res.at[idx, "Estatus"] = "⚪ Pendiente"
    return df_res

def update_avance_resultados(df):
    if df is None or df.empty: return df
    df_res = df.copy().reset_index(drop=True)
    if "Avance %" not in df_res.columns: df_res["Avance %"] = 0.0
    for idx, row in df_res.iterrows():
        if safe_str(row.get("Nombre", "")) != "":
            meta = safe_float(row.get("Meta", 0.0), 0.0)
            real = safe_float(row.get("Real", 0.0), 0.0)
            menor = safe_str(row.get("< Mejor", "NO"), "NO")
            df_res.at[idx, "Avance %"] = calc_cump(meta, real, menor)
        else:
            df_res.at[idx, "Avance %"] = 0.0
    return df_res

def calcular_sem_kpis(df, meses, c_rojo, c_amarillo, c_verde):
    if df is None or df.empty: return df
    df_res = df.copy().reset_index(drop=True)
    for idx, row in df_res.iterrows():
        menor = safe_str(row.get("< Mejor", "NO"), "NO")
        for m in meses:
            p = safe_float(row.get(f"{m} Prog", 0.0), 0.0)
            r = safe_float(row.get(f"{m} Real", 0.0), 0.0)
            if p == 0.0 and r == 0.0:
                df_res.at[idx, f"{m} Semáforo"] = "⚪"
            else:
                cump = calc_cump(p, r, menor)
                df_res.at[idx, f"{m} Semáforo"] = ob_circle(cump, c_rojo, c_amarillo, c_verde)
    return df_res

def render_footer(df, meses):
    html_footer = "<div style='display:flex; justify-content:flex-start; gap:12px; margin-bottom: 20px; align-items:center;'><div style='font-weight:900; color:#002060; font-size:15px; text-transform:uppercase;'>Avance Mensual:</div>"
    c_rojo = safe_float(get_store("cfg_corte_rojo", 79.0), 79.0)
    c_amarillo = safe_float(get_store("cfg_corte_amarillo", 89.0), 89.0)
    c_verde = safe_float(get_store("cfg_corte_verde", 100.0), 100.0)
    for m in meses:
        total_peso, acumulado = 0.0, 0.0
        if df is not None and not df.empty:
            for i in range(len(df)):
                if safe_str(df["Indicadores Clave de Desempeño (KPIs)"].iloc[i]) != "":
                    p = safe_float(df[f"{m} Prog"].iloc[i], 0.0)
                    r = safe_float(df[f"{m} Real"].iloc[i], 0.0)
                    peso = safe_float(df["Peso %"].iloc[i], 0.0)
                    cump = calc_cump(p, r, safe_str(df["< Mejor"].iloc[i], "NO"))
                    acumulado += cump * (peso / 100.0)
                    total_peso += peso
        avance = (acumulado / (total_peso / 100.0)) if total_peso > 0 else 0.0
        col = ob_color(avance, c_rojo, c_amarillo, c_verde)
        txt = "black" if col in ["#ffff00", "#92d050"] else "white"
        html_footer += f"<div class='footer-box' style='background-color:{col}; color:{txt};'>{m}: {avance:.1f}%</div>"
    st.markdown(html_footer + "</div>", unsafe_allow_html=True)

def dibujar_gantt(df_tareas):
    if df_tareas is None or df_tareas.empty: return
    df_plot = df_tareas.copy()
    df_plot = df_plot[df_plot["Tarea"].fillna("").astype(str).str.strip() != ""]
    df_plot["Inicio"] = pd.to_datetime(df_plot["Inicio"], errors='coerce')
    df_plot["Fin"] = pd.to_datetime(df_plot["Fin"], errors='coerce')
    df_plot = df_plot.dropna(subset=["Inicio", "Fin"])
    if df_plot.empty: return
    df_plot = df_plot.sort_values(by="Jerarquia")
    df_plot['Nombre'] = df_plot['Jerarquia'].fillna("").astype(str) + " " + df_plot['Tarea'].fillna("").astype(str)
    df_plot['Estado_Visual'] = df_plot['Completado'].apply(lambda x: "Realizado" if x else "Pendiente")
    chart = alt.Chart(df_plot).mark_bar(cornerRadius=4, size=20).encode(
        x=alt.X('Inicio', title='', axis=alt.Axis(format="%d %b", grid=True, gridColor="#f0f2f6")), x2='Fin',
        y=alt.Y('Nombre', sort=df_plot['Nombre'].tolist(), title='', axis=alt.Axis(labelFontWeight="bold", labelLimit=300)),
        color=alt.Color('Estado_Visual', scale=alt.Scale(domain=['Realizado', 'Pendiente'], range=['#002060', '#a0aabf']), legend=alt.Legend(title="Estado", orient="bottom"))
    ).properties(height=alt.Step(40))
    st.altair_chart(chart, use_container_width=True)

def get_mes_cump(m, q_name):
    t_peso_k, acum_k = 0.0, 0.0
    df_kpi = st.session_state.get(f"live_kpi_{q_name}", get_store(f"df_kpi_{q_name}", pd.DataFrame()))
    if df_kpi is not None and not df_kpi.empty:
        for i in range(len(df_kpi)):
            if safe_str(df_kpi["Indicadores Clave de Desempeño (KPIs)"].iloc[i]) != "":
                p = safe_float(df_kpi[f"{m} Prog"].iloc[i], 0.0)
                r = safe_float(df_kpi[f"{m} Real"].iloc[i], 0.0)
                peso = safe_float(df_kpi["Peso %"].iloc[i], 0.0)
                cump = calc_cump(p, r, safe_str(df_kpi["< Mejor"].iloc[i], "NO"))
                acum_k += cump * (peso / 100.0)
                t_peso_k += peso
    res_k = (acum_k / (t_peso_k / 100.0)) if t_peso_k > 0 else 0.0

    t_peso_o, acum_o = 0.0, 0.0
    num_i = int(safe_float(get_store(f"num_iniciativas_{q_name}", 1), 1))
    for i in range(1, num_i + 1):
        if safe_str(get_store(f"ui_nom_{q_name}_{i}", "")) != "":
            peso_o = safe_float(get_store(f"ui_peso_{q_name}_{i}", 0.0), 0.0)
            df_o = st.session_state.get(f"live_out_{q_name}_{i}", get_store(f"df_outputs_{q_name}_{i}", pd.DataFrame()))
            df_o = update_avance_resultados(df_o)
            cump_resultados = 0.0
            if df_o is not None and not df_o.empty:
                valid_o = df_o[df_o["Nombre"].fillna("").astype(str).str.strip() != ""]
                if not valid_o.empty:
                    cump_resultados = safe_float(valid_o["Avance %"].mean(), 0.0)
            acum_o += cump_resultados * (peso_o / 100.0)
            t_peso_o += peso_o
    res_o = (acum_o / (t_peso_o / 100.0)) if t_peso_o > 0 else 0.0

    p_k = safe_float(get_store("ui_p_kpis", 50.0), 50.0)
    p_o = safe_float(get_store("ui_p_okrs", 50.0), 50.0)
    t_peso_tot = p_k + p_o
    res_tot = ((res_k * (p_k / 100.0)) + (res_o * (p_o / 100.0))) / (t_peso_tot / 100.0) if t_peso_tot > 0 else 0.0
    return res_k, res_o, res_tot

# ==============================================================================
# FASE 3: RUTINAS DE BASE DE DATOS Y GESTIÓN DE DATOS
# ==============================================================================
def commit_live_edits():
    c_r = safe_float(get_store("cfg_corte_rojo", 79.0), 79.0)
    c_a = safe_float(get_store("cfg_corte_amarillo", 89.0), 89.0)
    c_v = safe_float(get_store("cfg_corte_verde", 100.0), 100.0)
    for q in trimestres.keys():
        if f"live_kpi_{q}" in st.session_state:
            df_k = calcular_sem_kpis(st.session_state[f"live_kpi_{q}"], trimestres[q], c_r, c_a, c_v)
            set_store(f"df_kpi_{q}", df_k)
        num_i = int(safe_float(get_store(f"num_iniciativas_{q}", 1), 1))
        for i in range(1, num_i + 1):
            if f"live_out_{q}_{i}" in st.session_state:
                set_store(f"df_outputs_{q}_{i}", update_avance_resultados(st.session_state[f"live_out_{q}_{i}"]))
            if f"live_tar_{q}_{i}" in st.session_state:
                set_store(f"df_tareas_{q}_{i}", update_estatus_tareas(st.session_state[f"live_tar_{q}_{i}"]))

def init_okr_structure(q_name, i):
    if f"ui_nom_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_nom_{q_name}_{i}", "")
    if f"ui_obj_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_obj_{q_name}_{i}", "")
    if f"ui_peso_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_peso_{q_name}_{i}", 20.0)
    if f"ui_rec_talento_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_rec_talento_{q_name}_{i}", "")
    if f"ui_rec_presupuesto_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_rec_presupuesto_{q_name}_{i}", "")
    if f"ui_rec_infra_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_rec_infra_{q_name}_{i}", "")
    if f"ui_rec_tec_{q_name}_{i}" not in st.session_state.perm_store: set_store(f"ui_rec_tec_{q_name}_{i}", "")
    
    if f"df_outputs_{q_name}_{i}" not in st.session_state.perm_store:
        df_o = pd.DataFrame(columns=["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance %"])
        set_store(f"df_outputs_{q_name}_{i}", df_o)
        
    if f"df_tareas_{q_name}_{i}" not in st.session_state.perm_store:
        df_t = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado", "Estatus"])
        set_store(f"df_tareas_{q_name}_{i}", df_t)

def sync_usuario_info(user_token):
    """Jala directamente Empresa, Nombre, Puesto y Logo desde la tabla usuarios."""
    try:
        df_user_db = conn.query(f"SELECT * FROM usuarios WHERE username = '{user_token}' LIMIT 1", ttl=0)
    except Exception:
        df_user_db = pd.DataFrame()

    empresa_val = ""
    nombre_val = ""
    puesto_val = ""
    logo_val = ""

    if not df_user_db.empty:
        row_u = df_user_db.iloc[0]
        empresa_val = get_col_ci(row_u, "empresa", "")
        nombre_val = get_col_ci(row_u, "nombre", "")
        puesto_val = get_col_ci(row_u, "puesto", "")
        logo_val = get_col_ci(row_u, "logo_url", "")

    if not empresa_val:
        empresa_val = safe_str(st.session_state.user_info.get("empresa", ""), "ONE TRACK")
    if not nombre_val:
        nombre_val = safe_str(st.session_state.user_info.get("nombre", ""), "")
    if not puesto_val:
        puesto_val = safe_str(st.session_state.user_info.get("puesto", ""), "")
    if not logo_val:
        logo_val = safe_str(st.session_state.user_info.get("logo_url", ""), DEFAULT_LOGO_CLIENTE)

    set_store("ui_empresa", empresa_val)
    set_store("ui_dueno", nombre_val)
    set_store("ui_puesto", puesto_val)
    set_store("ui_logo_cliente", logo_val)

    st.session_state["ui_empresa"] = empresa_val
    st.session_state["ui_dueno"] = nombre_val
    st.session_state["ui_puesto"] = puesto_val
    st.session_state.user_info["empresa"] = empresa_val
    st.session_state.user_info["nombre"] = nombre_val
    st.session_state.user_info["puesto"] = puesto_val
    st.session_state.user_info["logo_url"] = logo_val

def cargar_datos():
    if get_store("datos_cargados", False): return
    if 'user_info' not in st.session_state or st.session_state.user_info is None: return
    user_token = st.session_state.user_info['username']

    # Jalar directamente Nombre, Puesto, Empresa y Logo de la BD de usuarios
    sync_usuario_info(user_token)

    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{user_token}'", ttl=0)
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{user_token}'", ttl=0)
        df_outputs_db = conn.query(f"SELECT * FROM iniciativas_outputs WHERE onetrack_id = '{user_token}'", ttl=0)
        df_tareas = conn.query(f"SELECT * FROM iniciativas_tareas WHERE onetrack_id = '{user_token}'", ttl=0)
    except Exception:
        df_kpis, df_okrs, df_outputs_db, df_tareas = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    es_nuevo = df_kpis.empty

    for q_name in trimestres.keys():
        if not df_okrs.empty and 'OKR_ID' in df_okrs.columns:
            q_okrs = df_okrs[df_okrs['Trimestre_ID'].astype(str).str.strip() == q_name]
            max_id = pd.to_numeric(q_okrs["OKR_ID"], errors='coerce').max() if not q_okrs.empty else 1
            set_store(f"num_iniciativas_{q_name}", int(max_id) if pd.notna(max_id) and max_id >= 1 else 1)
        else:
            set_store(f"num_iniciativas_{q_name}", 1)

    set_store("ui_p_kpis", safe_float(df_kpis.iloc[0].get("Peso_Global_KPI", 50.0), 50.0) if not es_nuevo else 50.0)
    set_store("ui_p_okrs", safe_float(df_kpis.iloc[0].get("Peso_Global_OKR", 50.0), 50.0) if not es_nuevo else 50.0)
    set_store("cfg_corte_rojo", safe_float(df_kpis.iloc[0].get("U_Amarillo", 79.0), 79.0) if not es_nuevo else 79.0)
    set_store("cfg_corte_amarillo", safe_float(df_kpis.iloc[0].get("U_Verde", 89.0), 89.0) if not es_nuevo else 89.0)
    set_store("cfg_corte_verde", safe_float(df_kpis.iloc[0].get("U_SVerde", 100.0), 100.0) if not es_nuevo else 100.0)

    c_r = safe_float(get_store("cfg_corte_rojo", 79.0), 79.0)
    c_a = safe_float(get_store("cfg_corte_amarillo", 89.0), 89.0)
    c_v = safe_float(get_store("cfg_corte_verde", 100.0), 100.0)

    for q_name, meses in trimestres.items():
        cols_kpi = ["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"]
        for m in meses: cols_kpi.extend([f"{m} Prog", f"{m} Real", f"{m} Semáforo"])
        df_k = pd.DataFrame(columns=cols_kpi)

        if not es_nuevo:
            unique_kpis = df_kpis.drop_duplicates(subset=["KPI_Nombre"])
            rows_k = []
            for _, row in unique_kpis.iterrows():
                new_row = [
                    safe_str(row.get("KPI_Nombre", "")),
                    safe_str(row.get("Tipo", "Promedio"), "Promedio"),
                    safe_float(row.get("Meta", 0.0), 0.0),
                    safe_str(row.get("UM", "U"), "U"),
                    safe_str(row.get("< Mejor", "NO"), "NO"),
                    safe_float(row.get("Peso_%", 20.0), 20.0)
                ]
                for m in meses:
                    new_row.extend([safe_float(row.get(f"{m}_P", 0.0), 0.0), safe_float(row.get(f"{m}_R", 0.0), 0.0), "⚪"])
                rows_k.append(new_row)
            df_k = pd.DataFrame(rows_k, columns=cols_kpi).reset_index(drop=True)
            df_k = calcular_sem_kpis(df_k, meses, c_r, c_a, c_v)
        else:
            row_empty = ["", "Promedio", 0.0, "U", "NO", 0.0]
            for _ in meses: row_empty.extend([0.0, 0.0, "⚪"])
            df_k = pd.DataFrame([row_empty], columns=cols_kpi).reset_index(drop=True)
        
        set_store(f"df_kpi_{q_name}", df_k)

        num_i = int(safe_float(get_store(f"num_iniciativas_{q_name}", 1), 1))
        for i in range(1, num_i + 1):
            init_okr_structure(q_name, i)

            if not df_okrs.empty and 'OKR_ID' in df_okrs.columns:
                match_okr = df_okrs[(df_okrs['Trimestre_ID'].astype(str).str.strip() == q_name) & (pd.to_numeric(df_okrs['OKR_ID'], errors='coerce') == i)]
                if not match_okr.empty:
                    row_o = match_okr.iloc[0]
                    set_store(f"ui_nom_{q_name}_{i}", safe_str(row_o.get("OKR_Nombre", "")))
                    set_store(f"ui_obj_{q_name}_{i}", safe_str(row_o.get("Objetivo", "")))
                    set_store(f"ui_peso_{q_name}_{i}", safe_float(row_o.get("Peso_%", 20.0), 20.0))
                    set_store(f"ui_rec_talento_{q_name}_{i}", safe_str(row_o.get("Recurso_Talento", "")))
                    set_store(f"ui_rec_presupuesto_{q_name}_{i}", safe_str(row_o.get("Recurso_Presupuesto", "")))
                    set_store(f"ui_rec_infra_{q_name}_{i}", safe_str(row_o.get("Recurso_Infraestructura", "")))
                    set_store(f"ui_rec_tec_{q_name}_{i}", safe_str(row_o.get("Recurso_Tecnologia", "")))

            if not df_outputs_db.empty and 'Iniciativa_ID' in df_outputs_db.columns:
                out_okr = df_outputs_db[(pd.to_numeric(df_outputs_db['Iniciativa_ID'], errors='coerce') == i) & (df_outputs_db['Trimestre'].astype(str).str.strip() == q_name)]
                if not out_okr.empty:
                    df_o = out_okr[["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance"]].rename(columns={"Avance": "Avance %"}).reset_index(drop=True)
                    set_store(f"df_outputs_{q_name}_{i}", update_avance_resultados(df_o))

            if not df_tareas.empty and 'Iniciativa_ID' in df_tareas.columns and 'Trimestre' in df_tareas.columns:
                tar_okr = df_tareas[(pd.to_numeric(df_tareas['Iniciativa_ID'], errors='coerce') == i) & (df_tareas['Trimestre'].astype(str).str.strip() == q_name)]
                if not tar_okr.empty:
                    df_t = tar_okr[["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]].reset_index(drop=True)
                    df_t["Completado"] = df_t["Completado"].fillna(False).astype(bool)
                    df_t["Inicio"] = df_t["Inicio"].apply(to_date_or_none)
                    df_t["Fin"] = df_t["Fin"].apply(to_date_or_none)
                    set_store(f"df_tareas_{q_name}_{i}", update_estatus_tareas(df_t))

    set_store("datos_cargados", True)

def ensure_db_columns():
    """Garantiza que las tablas existentes en Supabase cuenten con las columnas nuevas."""
    alter_stmts = [
        'ALTER TABLE okrs_general ADD COLUMN IF NOT EXISTS "Recurso_Talento" TEXT',
        'ALTER TABLE okrs_general ADD COLUMN IF NOT EXISTS "Recurso_Presupuesto" TEXT',
        'ALTER TABLE okrs_general ADD COLUMN IF NOT EXISTS "Recurso_Infraestructura" TEXT',
        'ALTER TABLE okrs_general ADD COLUMN IF NOT EXISTS "Recurso_Tecnologia" TEXT',
        'ALTER TABLE okrs_general ADD COLUMN IF NOT EXISTS "Estatus_Salud" TEXT',
        'ALTER TABLE kpis ADD COLUMN IF NOT EXISTS "Logo_Cliente" TEXT',
        'ALTER TABLE kpis ADD COLUMN IF NOT EXISTS "Empresa" TEXT',
        'ALTER TABLE kpis ADD COLUMN IF NOT EXISTS "Puesto" TEXT',
        'ALTER TABLE kpis ADD COLUMN IF NOT EXISTS "Dueno" TEXT',
    ]
    for stmt in alter_stmts:
        try:
            with conn.engine.begin() as tx:
                tx.execute(text(stmt))
        except Exception:
            pass

def guardar_en_bd():
    commit_live_edits()
    if 'user_info' not in st.session_state or st.session_state.user_info is None: return
    user_token = st.session_state.user_info['username']
    kpis_data, okrs_data, tareas_data, outputs_data = [], [], [], []
    
    peso_k = safe_float(get_store("ui_p_kpis", 50.0), 50.0)
    peso_o = safe_float(get_store("ui_p_okrs", 50.0), 50.0)
    c_rojo = safe_float(get_store("cfg_corte_rojo", 79.0), 79.0)
    c_amarillo = safe_float(get_store("cfg_corte_amarillo", 89.0), 89.0)
    c_verde = safe_float(get_store("cfg_corte_verde", 100.0), 100.0)
    emp = safe_str(get_store("ui_empresa", ""))
    due = safe_str(get_store("ui_dueno", ""))
    pue = safe_str(get_store("ui_puesto", ""))
    
    logo_c = safe_str(get_store("ui_logo_cliente", st.session_state.user_info.get("logo_url", DEFAULT_LOGO_CLIENTE)), DEFAULT_LOGO_CLIENTE)

    # Recopilar lista unica de KPIs empezando por Q1
    seen_kpis = []
    kpi_meta_map = {}
    for q_n in trimestres.keys():
        df_q = get_store(f"df_kpi_{q_n}", pd.DataFrame())
        if df_q is not None and not df_q.empty:
            for _, r in df_q.iterrows():
                k_nom = safe_str(r.get("Indicadores Clave de Desempeño (KPIs)", ""))
                if k_nom and k_nom not in seen_kpis:
                    seen_kpis.append(k_nom)
                    kpi_meta_map[k_nom] = {
                        "Tipo": safe_str(r.get("Tipo", "Promedio"), "Promedio"),
                        "Meta": safe_float(r.get("Meta", 0.0), 0.0),
                        "UM": safe_str(r.get("UM", "U"), "U"),
                        "< Mejor": safe_str(r.get("< Mejor", "NO"), "NO"),
                        "Peso_%": safe_float(r.get("Peso %", 0.0), 0.0),
                    }

    for k_nom in seen_kpis:
        meta_info = kpi_meta_map[k_nom]
        row = {
            "onetrack_id": user_token, "Empresa": emp, "Puesto": pue, "Dueno": due, "Logo_Cliente": logo_c,
            "KPI_Nombre": k_nom, "Tipo": meta_info["Tipo"], "Meta": meta_info["Meta"],
            "UM": meta_info["UM"], "< Mejor": meta_info["< Mejor"], "Peso_%": meta_info["Peso_%"],
            "Peso_Global_KPI": peso_k, "Peso_Global_OKR": peso_o, "U_SVerde": c_verde, "U_Verde": c_amarillo, "U_Amarillo": c_rojo
        }
        for q_n, meses in trimestres.items():
            df_q = get_store(f"df_kpi_{q_n}", pd.DataFrame())
            match = df_q[df_q["Indicadores Clave de Desempeño (KPIs)"].fillna("").astype(str).str.strip() == k_nom] if (df_q is not None and not df_q.empty) else pd.DataFrame()
            if not match.empty:
                for m in meses:
                    row[f"{m}_P"] = safe_float(match.iloc[0].get(f"{m} Prog", 0.0), 0.0)
                    row[f"{m}_R"] = safe_float(match.iloc[0].get(f"{m} Real", 0.0), 0.0)
            else:
                for m in meses:
                    row[f"{m}_P"], row[f"{m}_R"] = 0.0, 0.0
        kpis_data.append(row)

    for q_n in trimestres.keys():
        num_i = int(safe_float(get_store(f"num_iniciativas_{q_n}", 1), 1))
        for i in range(1, num_i + 1):
            o_nom = safe_str(get_store(f"ui_nom_{q_n}_{i}", ""))
            if o_nom:
                df_t_prog = update_estatus_tareas(get_store(f"df_tareas_{q_n}_{i}", pd.DataFrame()))
                tot_t = len(df_t_prog[df_t_prog["Tarea"].fillna("").astype(str).str.strip() != ""]) if (df_t_prog is not None and not df_t_prog.empty) else 0
                comp = df_t_prog["Completado"].sum() if tot_t > 0 else 0
                if tot_t == 0: e_calc = "⚪ Sin Tareas"
                elif "🔴 Retrasado" in df_t_prog["Estatus"].values: e_calc = "🔴 Retrasado"
                elif comp == tot_t and tot_t > 0: e_calc = "🟢 Completado"
                else: e_calc = "🟢 En Tiempo"

                okrs_data.append({
                    "onetrack_id": user_token, "Trimestre_ID": q_n, "OKR_ID": i, "OKR_Nombre": o_nom,
                    "Objetivo": safe_str(get_store(f"ui_obj_{q_n}_{i}", "")), "Peso_%": safe_float(get_store(f"ui_peso_{q_n}_{i}", 20.0), 20.0),
                    "Estatus_Salud": e_calc,
                    "Recurso_Talento": safe_str(get_store(f"ui_rec_talento_{q_n}_{i}", "")),
                    "Recurso_Presupuesto": safe_str(get_store(f"ui_rec_presupuesto_{q_n}_{i}", "")),
                    "Recurso_Infraestructura": safe_str(get_store(f"ui_rec_infra_{q_n}_{i}", "")),
                    "Recurso_Tecnologia": safe_str(get_store(f"ui_rec_tec_{q_n}_{i}", ""))
                })

                df_o = update_avance_resultados(get_store(f"df_outputs_{q_n}_{i}", pd.DataFrame()))
                if df_o is not None and not df_o.empty:
                    for _, o_row in df_o.iterrows():
                        if safe_str(o_row.get("Nombre", "")) != "":
                            outputs_data.append({
                                "onetrack_id": user_token, "Iniciativa_ID": i, "Trimestre": q_n,
                                "Nombre": safe_str(o_row.get("Nombre", "")), "UM": safe_str(o_row.get("UM", "U"), "U"),
                                "< Mejor": safe_str(o_row.get("< Mejor", "NO"), "NO"), "Meta": safe_float(o_row.get("Meta", 0.0), 0.0),
                                "Real": safe_float(o_row.get("Real", 0.0), 0.0), "Avance": safe_float(o_row.get("Avance %", 0.0), 0.0)
                            })

                if df_t_prog is not None and not df_t_prog.empty:
                    for _, t_row in df_t_prog.iterrows():
                        if safe_str(t_row.get("Tarea", "")) != "":
                            tareas_data.append({
                                "onetrack_id": user_token, "Iniciativa_ID": i, "Trimestre": q_n,
                                "Jerarquia": safe_str(t_row.get("Jerarquia", "")), "Tarea": safe_str(t_row.get("Tarea", "")),
                                "Responsable": safe_str(t_row.get("Responsable", "")), "Inicio": t_row.get("Inicio"),
                                "Fin": t_row.get("Fin"), "Completado": bool(t_row.get("Completado", False))
                            })

    ensure_db_columns()

    try:
        with conn.engine.begin() as transaction:
            transaction.execute(text("DELETE FROM kpis WHERE onetrack_id = :token"), {"token": user_token})
            transaction.execute(text("DELETE FROM okrs_general WHERE onetrack_id = :token"), {"token": user_token})
            transaction.execute(text("DELETE FROM iniciativas_outputs WHERE onetrack_id = :token"), {"token": user_token})
            transaction.execute(text("DELETE FROM iniciativas_tareas WHERE onetrack_id = :token"), {"token": user_token})
    except Exception:
        pass

    cols_k_all = ["onetrack_id", "Empresa", "Puesto", "Dueno", "Logo_Cliente", "KPI_Nombre", "Tipo", "Meta", "UM", "< Mejor", "Peso_%", "Peso_Global_KPI", "Peso_Global_OKR", "U_SVerde", "U_Verde", "U_Amarillo"]
    for q_n, meses in trimestres.items():
        for m in meses: cols_k_all.extend([f"{m}_P", f"{m}_R"])

    pd.DataFrame(kpis_data, columns=cols_k_all).to_sql("kpis", con=conn.engine, if_exists='append', index=False)
    pd.DataFrame(okrs_data, columns=["onetrack_id", "Trimestre_ID", "OKR_ID", "OKR_Nombre", "Objetivo", "Peso_%", "Estatus_Salud", "Recurso_Talento", "Recurso_Presupuesto", "Recurso_Infraestructura", "Recurso_Tecnologia"]).to_sql("okrs_general", con=conn.engine, if_exists='append', index=False)
    pd.DataFrame(outputs_data, columns=["onetrack_id", "Iniciativa_ID", "Trimestre", "Nombre", "UM", "< Mejor", "Meta", "Real", "Avance"]).to_sql("iniciativas_outputs", con=conn.engine, if_exists='append', index=False)
    pd.DataFrame(tareas_data, columns=["onetrack_id", "Iniciativa_ID", "Trimestre", "Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]).to_sql("iniciativas_tareas", con=conn.engine, if_exists='append', index=False)

# --- SECCION DESCOMENTADA: GENERADOR DE DATOS DUMMY ---
def generar_dummy_onetest():
    mult_q = {"Q1": 0.85, "Q2": 0.90, "Q3": 0.98, "Q4": 1.05}
    cols_t = ["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado", "Estatus"]
    cols_out = ["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance %"]

    if 'user_info' in st.session_state and st.session_state.user_info is not None:
        sync_usuario_info(st.session_state.user_info['username'])

    set_store("ui_p_kpis", 50.0)
    set_store("ui_p_okrs", 50.0)
    set_store("cfg_corte_rojo", 79.0)
    set_store("cfg_corte_amarillo", 89.0)
    set_store("cfg_corte_verde", 100.0)

    for q_name, meses in trimestres.items():
        cols_kpi = ["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"]
        for m in meses: cols_kpi.extend([f"{m} Prog", f"{m} Real", f"{m} Semáforo"])
        
        row1 = ["Ventas Mensuales", "Acumulado", 500000.0, "$", "NO", 50.0]
        for _ in meses: row1.extend([166666.0, round(166666.0 * mult_q[q_name], 2), "⚪"])

        row2 = ["Satisfacción de Clientes", "Promedio", 95.0, "%", "NO", 50.0]
        for _ in meses: row2.extend([95.0, round(95.0 * mult_q[q_name], 2), "⚪"])

        df_k = pd.DataFrame([row1, row2], columns=cols_kpi).reset_index(drop=True)
        df_k = calcular_sem_kpis(df_k, meses, 79.0, 89.0, 100.0)
        set_store(f"df_kpi_{q_name}", df_k)

    # Q1
    q_n = "Q1"; set_store(f"num_iniciativas_{q_n}", 1)
    set_store(f"ui_nom_{q_n}_1", "Expansión de Mercado Norte")
    set_store(f"ui_peso_{q_n}_1", 100.0)
    set_store(f"ui_obj_{q_n}_1", "Conquistar 3 nuevos estados mediante campañas digitales y alianzas locales.")
    set_store(f"ui_rec_talento_{q_n}_1", "1 Director Comercial, 2 Ejecutivos Regionales")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$250,000 MXN para pauta")
    set_store(f"ui_rec_infra_{q_n}_1", "Oficina en Monterrey")
    set_store(f"ui_rec_tec_{q_n}_1", "HubSpot CRM")
    df_o1 = pd.DataFrame([
        ["Abrir sucursales físicas", "U", "NO", 3.0, 2.0, 0.0],
        ["Alianzas comerciales cerradas", "U", "NO", 10.0, 9.0, 0.0]
    ], columns=cols_out).reset_index(drop=True)
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o1))
    df_t1 = pd.DataFrame([
        ["1.", "Investigación de Mercado", "Ana", date(2026, 1, 5), date(2026, 1, 15), True, ""],
        ["1.1", "Contratación de Equipo", "Luis", date(2026, 1, 16), date(2026, 2, 10), True, ""],
        ["1.2", "Lanzamiento de Campaña", "Carlos", date(2026, 2, 15), date(2026, 3, 20), False, ""]
    ], columns=cols_t).reset_index(drop=True)
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t1))

    # Q2
    q_n = "Q2"; set_store(f"num_iniciativas_{q_n}", 2)
    set_store(f"ui_nom_{q_n}_1", "Nuevo Producto Alpha")
    set_store(f"ui_peso_{q_n}_1", 60.0)
    set_store(f"ui_obj_{q_n}_1", "Lanzar producto Alpha antes del cierre de semestre.")
    set_store(f"ui_rec_talento_{q_n}_1", "1 Product Manager")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$180,000 MXN")
    set_store(f"ui_rec_infra_{q_n}_1", "Servidores cloud AWS")
    set_store(f"ui_rec_tec_{q_n}_1", "Figma, GitHub")
    df_o2_1 = pd.DataFrame([["Prototipos validados", "U", "NO", 5.0, 5.0, 0.0]], columns=cols_out).reset_index(drop=True)
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o2_1))
    df_t2_1 = pd.DataFrame([
        ["1.", "Diseño", "Ana", date(2026, 4, 1), date(2026, 4, 20), True, ""],
        ["2.", "Pruebas", "Luis", date(2026, 5, 1), date(2026, 5, 15), True, ""],
        ["3.", "Preventa", "Carlos", date(2026, 6, 1), date(2026, 6, 25), False, ""]
    ], columns=cols_t).reset_index(drop=True)
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t2_1))

    set_store(f"ui_nom_{q_n}_2", "Optimización Costos")
    set_store(f"ui_peso_{q_n}_2", 40.0)
    set_store(f"ui_obj_{q_n}_2", "Reducir costos operativos en logística.")
    set_store(f"ui_rec_talento_{q_n}_2", "Auditor Financiero")
    set_store(f"ui_rec_presupuesto_{q_n}_2", "$50,000 MXN")
    set_store(f"ui_rec_infra_{q_n}_2", "Bodega central")
    set_store(f"ui_rec_tec_{q_n}_2", "Excel Avanzado")
    df_o2_2 = pd.DataFrame([["Ahorro en logística", "%", "SI", 15.0, 12.0, 0.0]], columns=cols_out).reset_index(drop=True)
    set_store(f"df_outputs_{q_n}_2", update_avance_resultados(df_o2_2))
    df_t2_2 = pd.DataFrame([
        ["1.", "Auditoría", "Sofia", date(2026, 4, 5), date(2026, 4, 25), True, ""],
        ["2.", "Renegociación", "Luis", date(2026, 5, 5), date(2026, 5, 20), False, ""],
        ["3.", "Rutas", "Sofia", date(2026, 6, 1), date(2026, 6, 28), False, ""]
    ], columns=cols_t).reset_index(drop=True)
    set_store(f"df_tareas_{q_n}_2", update_estatus_tareas(df_t2_2))

    # Q3
    q_n = "Q3"; set_store(f"num_iniciativas_{q_n}", 1)
    set_store(f"ui_nom_{q_n}_1", "Certificación ISO")
    set_store(f"ui_peso_{q_n}_1", 100.0)
    set_store(f"ui_obj_{q_n}_1", "Obtener certificación en procesos clave.")
    set_store(f"ui_rec_talento_{q_n}_1", "Oficial de Cumplimiento")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$120,000 MXN")
    set_store(f"ui_rec_infra_{q_n}_1", "Salas de capacitación")
    set_store(f"ui_rec_tec_{q_n}_1", "Software de Auditoría")
    df_o3 = pd.DataFrame([["Fases completadas", "U", "NO", 3.0, 2.0, 0.0]], columns=cols_out).reset_index(drop=True)
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o3))
    df_t3 = pd.DataFrame([
        ["1.", "Diagnóstico", "Juan", date(2026, 7, 1), date(2026, 7, 15), True, ""],
        ["2.", "Capacitación", "Ana", date(2026, 8, 1), date(2026, 8, 20), False, ""],
        ["3.", "Auditoría Final", "Luis", date(2026, 9, 10), date(2026, 9, 25), False, ""]
    ], columns=cols_t).reset_index(drop=True)
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t3))

    # Q4
    q_n = "Q4"; set_store(f"num_iniciativas_{q_n}", 1)
    set_store(f"ui_nom_{q_n}_1", "Planificación 2027")
    set_store(f"ui_peso_{q_n}_1", 100.0)
    set_store(f"ui_obj_{q_n}_1", "Cerrar métricas y presupuesto.")
    set_store(f"ui_rec_talento_{q_n}_1", "Equipo Directivo")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$90,000 MXN")
    set_store(f"ui_rec_infra_{q_n}_1", "Sede externa")
    set_store(f"ui_rec_tec_{q_n}_1", "Power BI")
    df_o4 = pd.DataFrame([["Presupuestos aprobados", "U", "NO", 4.0, 4.0, 0.0]], columns=cols_out).reset_index(drop=True)
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o4))
    df_t4 = pd.DataFrame([
        ["1.", "Revisión", "Carlos", date(2026, 10, 5), date(2026, 10, 25), True, ""],
        ["2.", "Metas", "Ana", date(2026, 11, 1), date(2026, 11, 20), False, ""],
        ["3.", "Presentación", "Juan", date(2026, 12, 1), date(2026, 12, 15), False, ""]
    ], columns=cols_t).reset_index(drop=True)
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t4))

def ejecutar_dummy_callback():
    for key in list(st.session_state.keys()):
        if key.startswith("editor_") or key.startswith("ui_") or key.startswith("live_") or key.startswith("cfg_"):
            del st.session_state[key]
    generar_dummy_onetest()
    guardar_en_bd()
    set_store("datos_cargados", True)

# ==============================================================================
# FASE 4: MOTOR DE SIMULACIONES INTERACTIVAS HTML5/JS
# ==============================================================================
ANIMACIONES_HTML = {
    "kpis": {
        "height": 145,
        "html": """
        <style>body { margin: 0; padding: 4px; box-sizing: border-box; }</style>
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead><tr>
                    <th style="background:#002060; color:white; padding:10px 8px; width:25%; text-align:left;">KPI</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:10%; text-align:center;">Tipo</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:9%; text-align:center;">Meta</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:7%; text-align:center;">UM</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:7%; text-align:center;">< Mejor</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:8%; text-align:center;">Peso %</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:11%; text-align:center;">Ene Prog</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:11%; text-align:center;">Ene Real</th>
                    <th style="background:#002060; color:white; padding:10px 8px; width:12%; text-align:center;">Ene Semáforo</th>
                </tr></thead>
                <tbody><tr>
                    <td style="padding:9px 8px; text-align:left; border:1px solid #e2e8f0; font-weight:600; white-space: pre-wrap;"><span id="kpi_nombre"></span></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0;"><span style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:3px 6px; font-size:11px; font-weight:bold;">Acumulado</span></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0;" id="kpi_meta"></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0;"><span style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:3px 6px; font-size:11px; font-weight:bold;">$</span></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0;"><span style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:3px 6px; font-size:11px; font-weight:bold;">NO</span></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0;" id="kpi_peso"></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0;" id="kpi_p1"></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0; font-weight:600;" id="kpi_r1"></td>
                    <td style="padding:9px 8px; text-align:center; border:1px solid #e2e8f0; font-size:16px;" id="kpi_sem">⚪</td>
                </tr></tbody>
            </table>
        </div>
        <script>
            const wait = ms => new Promise(r => setTimeout(r, ms));
            async function loop() {
                while(true) {
                    document.getElementById('kpi_nombre').textContent = ""; document.getElementById('kpi_meta').textContent = "";
                    document.getElementById('kpi_peso').textContent = ""; document.getElementById('kpi_p1').textContent = "";
                    document.getElementById('kpi_r1').textContent = ""; document.getElementById('kpi_sem').textContent = "⚪";
                    await wait(800);
                    let t = "Ventas Nuevos Clientes";
                    let acum = "";
                    for(let i=0; i<t.length; i++) {
                        acum += t[i];
                        document.getElementById('kpi_nombre').textContent = acum;
                        await wait(40);
                    }
                    await wait(300); document.getElementById('kpi_meta').textContent = "500,000";
                    await wait(300); document.getElementById('kpi_peso').textContent = "50 %";
                    await wait(400); document.getElementById('kpi_p1').textContent = "40,000";
                    await wait(400); document.getElementById('kpi_r1').textContent = "42,500";
                    await wait(300); document.getElementById('kpi_sem').textContent = "🟢";
                    await wait(3500);
                }
            } loop();
        </script>
        """
    },
    "iniciativa": {
        "height": 345,
        "html": """
        <style>body { margin: 0; padding: 4px; box-sizing: border-box; }</style>
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 18px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="background:#002060; color:white; padding:8px 16px; border-radius:8px; font-weight:900;">Iniciativa #1</div>
                <div id="pill_cump" style="padding:8px 15px; border-radius:6px; font-weight:900; font-size:13px; color:white; background:#64748b;">CUMPLIMIENTO: 0.0%</div>
            </div>
            <div style="display:grid; grid-template-columns:3fr 1fr 1fr; gap:10px; margin-bottom:10px;">
                <div>
                    <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">NOMBRE</div>
                    <div style="height:35px; border:1px solid #cbd5e1; border-radius:6px; padding:0 8px; display:flex; align-items:center; white-space: pre-wrap; font-size:13px;" id="ini_nom"></div>
                </div>
                <div>
                    <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">PONDERACIÓN (%)</div>
                    <div style="height:35px; border:1px solid #cbd5e1; border-radius:6px; display:flex; align-items:center; justify-content:center; font-weight:bold;" id="ini_peso"></div>
                </div>
                <div>
                    <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">ESTATUS</div>
                    <div style="height:35px; border:1px solid #cbd5e1; border-radius:6px; display:flex; align-items:center; justify-content:center; font-weight:bold; color:#64748b;" id="ini_est">⚪ Sin Tareas</div>
                </div>
            </div>
            <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">OBJETIVO</div>
            <div style="height:55px; border:1px solid #cbd5e1; border-radius:6px; padding:6px 8px; font-size:12.5px; line-height:1.3; margin-bottom:12px; white-space: pre-wrap;" id="ini_obj"></div>
            <table style="width:100%; border-collapse:collapse; font-size:12px; border:1px solid #e2e8f0;">
                <thead><tr style="background:#002060; color:white;"><th style="padding:6px; text-align:left;">Resultado</th><th>UM</th><th>Meta</th><th>Real</th><th>Avance %</th></tr></thead>
                <tbody><tr><td style="padding:6px;" id="r1_nom">-</td><td style="padding:6px; text-align:center;" id="r1_um">-</td><td style="padding:6px; text-align:center;" id="r1_meta">-</td><td style="padding:6px; text-align:center;" id="r1_real">-</td><td style="padding:6px; text-align:center; font-weight:bold;" id="r1_av">-</td></tr></tbody>
            </table>
        </div>
        <script>
            const wait = ms => new Promise(r => setTimeout(r, ms));
            async function loop() {
                while(true) {
                    document.getElementById('ini_nom').textContent = ""; document.getElementById('ini_peso').textContent = "";
                    document.getElementById('ini_obj').textContent = ""; document.getElementById('ini_est').textContent = "⚪ Sin Tareas";
                    document.getElementById('ini_est').style.color = "#64748b"; document.getElementById('pill_cump').textContent = "CUMPLIMIENTO: 0.0%";
                    document.getElementById('pill_cump').style.background = "#64748b"; document.getElementById('r1_nom').textContent = "-";
                    document.getElementById('r1_um').textContent = "-"; document.getElementById('r1_meta').textContent = "-";
                    document.getElementById('r1_real').textContent = "-"; document.getElementById('r1_av').textContent = "-";
                    document.getElementById('r1_av').style.color = "black";
                    await wait(800);

                    let t = "Lanzamiento de Plataforma B2B";
                    let acum = "";
                    for(let i=0; i<t.length; i++) {
                        acum += t[i];
                        document.getElementById('ini_nom').textContent = acum;
                        await wait(35);
                    }

                    await wait(200); document.getElementById('ini_peso').textContent = "60.0";
                    await wait(200); document.getElementById('ini_obj').textContent = "Digitalizar el canal de pedidos mayoristas reduciendo tiempos de captura a 24 horas.";
                    await wait(400); document.getElementById('r1_nom').textContent = "Clientes B2B Activos";
                    document.getElementById('r1_um').textContent = "U"; document.getElementById('r1_meta').textContent = "50";
                    await wait(400); document.getElementById('r1_real').textContent = "50";
                    await wait(200); document.getElementById('r1_av').textContent = "100.0 %";
                    document.getElementById('r1_av').style.color = "#00b050";
                    document.getElementById('pill_cump').textContent = "CUMPLIMIENTO: 100.0%";
                    document.getElementById('pill_cump').style.background = "#00b050";
                    document.getElementById('ini_est').textContent = "🟢 En Tiempo";
                    document.getElementById('ini_est').style.color = "#00b050";
                    await wait(3500);
                }
            } loop();
        </script>
        """
    },
    "gantt": {
        "height": 240,
        "html": """
        <style>body { margin: 0; padding: 4px; box-sizing: border-box; }</style>
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead><tr style="background: #002060; color: white;">
                    <th style="padding: 7px;">Jerarquía</th><th style="padding: 7px; text-align: left;">Tarea</th><th>Responsable</th><th>Fin</th><th>Comp.</th><th>Estatus</th>
                </tr></thead>
                <tbody>
                    <tr>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;">1.</td>
                        <td style="padding:7px; border:1px solid #e2e8f0;">Requerimientos funcionales</td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;">Ana</td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;">12 Feb</td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;"><input type="checkbox" checked disabled></td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0; color:#00b050; font-weight:bold;">🟢 A tiempo</td>
                    </tr>
                    <tr>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;">1.1</td>
                        <td style="padding:7px; border:1px solid #e2e8f0;">Pruebas QA en servidor</td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;">Luis</td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;">25 Feb</td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0;"><input type="checkbox" id="chk2"></td>
                        <td style="padding:7px; text-align:center; border:1px solid #e2e8f0; font-weight:bold; color:#ff0000;" id="st2">🔴 Retrasado</td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:12px; padding-top:8px; border-top:2px dashed #e2e8f0;">
                <div style="display:flex; align-items:center; margin-bottom:5px;">
                    <div style="width:130px; font-weight:bold;">1. Requerimientos</div>
                    <div style="flex:1; background:#f1f5f9; height:16px; border-radius:4px; position:relative;"><div style="width:40%; height:100%; background:#002060; border-radius:4px;"></div></div>
                </div>
                <div style="display:flex; align-items:center;">
                    <div style="width:130px; font-weight:bold;">1.1 Pruebas QA</div>
                    <div style="flex:1; background:#f1f5f9; height:16px; border-radius:4px; position:relative;"><div id="bar2" style="left:40%; width:45%; height:100%; background:#a0aabf; border-radius:4px; position:absolute;"></div></div>
                </div>
            </div>
        </div>
        <script>
            const wait = ms => new Promise(r => setTimeout(r, ms));
            async function loop() {
                while(true) {
                    document.getElementById('chk2').checked = false; document.getElementById('st2').innerText = "🔴 Retrasado";
                    document.getElementById('st2').style.color = "#ff0000"; document.getElementById('bar2').style.background = "#a0aabf";
                    await wait(2000);
                    document.getElementById('chk2').checked = true; await wait(300);
                    document.getElementById('st2').innerText = "🟢 A tiempo"; document.getElementById('st2').style.color = "#00b050";
                    document.getElementById('bar2').style.background = "#002060"; await wait(3500);
                }
            } loop();
        </script>
        """
    },
    "recursos": {
        "height": 215,
        "html": """
        <style>body { margin: 0; padding: 4px; box-sizing: border-box; }</style>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">TALENTO</div>
                <div style="font-size:12px; color:#334155; height:48px; white-space: pre-wrap;" id="txt_tal"></div>
            </div>
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">PRESUPUESTO $</div>
                <div style="font-size:12px; color:#334155; height:48px; white-space: pre-wrap;" id="txt_pre"></div>
            </div>
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">INFRAESTRUCTURA</div>
                <div style="font-size:12px; color:#334155; height:48px; white-space: pre-wrap;" id="txt_inf"></div>
            </div>
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:4px;">TECNOLOGÍA</div>
                <div style="font-size:12px; color:#334155; height:48px; white-space: pre-wrap;" id="txt_tec"></div>
            </div>
        </div>
        <script>
            const wait = ms => new Promise(r => setTimeout(r, ms));
            async function loop() {
                while(true) {
                    document.getElementById('txt_tal').textContent = ""; document.getElementById('txt_pre').textContent = "";
                    document.getElementById('txt_inf').textContent = ""; document.getElementById('txt_tec').textContent = "";
                    await wait(600);
                    document.getElementById('txt_tal').textContent = "1 Tech Lead, 2 Desarrolladores, 1 Analista QA"; await wait(250);
                    document.getElementById('txt_pre').textContent = "$180,000 MXN para licencias y consultoría"; await wait(250);
                    document.getElementById('txt_inf').textContent = "Servidores AWS Staging y Producción, VPN"; await wait(250);
                    document.getElementById('txt_tec').textContent = "Docker, GitHub Enterprise, Supabase Cloud"; await wait(3500);
                }
            } loop();
        </script>
        """
    },
    "intervalos": {
        "height": 230,
        "html": """
        <style>body { margin: 0; padding: 4px; box-sizing: border-box; }</style>
        <div style="display:flex; gap:15px; align-items:stretch; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="flex:1; background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:3px;">Límite Rojo (%)</div>
                <div style="border:1px solid #cbd5e1; border-radius:4px; padding:6px 8px; font-weight:bold; font-size:12.5px; margin-bottom:8px; background:#f8fafc;" id="r_val">79</div>
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:3px;">Límite Amarillo (%)</div>
                <div style="border:1px solid #cbd5e1; border-radius:4px; padding:6px 8px; font-weight:bold; font-size:12.5px; margin-bottom:8px; background:#f8fafc;">89</div>
                <div style="font-size:11px; font-weight:900; color:#002060; margin-bottom:3px;">Límite Verde (%)</div>
                <div style="border:1px solid #cbd5e1; border-radius:4px; padding:6px 8px; font-weight:bold; font-size:12.5px; background:#f8fafc;">100</div>
            </div>
            <div style="flex:1.5; display:flex; flex-direction:column; justify-content:space-between; gap:8px;">
                <div style="background:#ff0000; color:white; border-radius:6px; padding:10px 12px; font-weight:bold; font-size:12px; display:flex; justify-content:space-between; align-items:center;"><span>🔴 BAJO</span><span id="txt_r">Menor o igual a 79%</span></div>
                <div style="background:#ffff00; color:black; border-radius:6px; padding:10px 12px; font-weight:bold; font-size:12px; display:flex; justify-content:space-between; align-items:center;"><span>🟡 MEDIO</span><span id="txt_a">De 80% a 89%</span></div>
                <div style="background:#92d050; color:white; border-radius:6px; padding:10px 12px; font-weight:bold; font-size:12px; display:flex; justify-content:space-between; align-items:center;"><span>🟢 META</span><span>De 90% a 100%</span></div>
                <div style="background:#00b050; color:white; border-radius:6px; padding:10px 12px; font-weight:bold; font-size:12px; display:flex; justify-content:space-between; align-items:center;"><span>🟢 SOBRESALIENTE</span><span>Mayor a 100%</span></div>
            </div>
        </div>
        <script>
            const wait = ms => new Promise(r => setTimeout(r, ms));
            async function loop() {
                while(true) {
                    document.getElementById('r_val').innerText = "79"; document.getElementById('txt_r').innerText = "Menor o igual a 79%";
                    document.getElementById('txt_a').innerText = "De 80% a 89%"; await wait(1800);
                    document.getElementById('r_val').innerText = "69"; document.getElementById('txt_r').innerText = "Menor o igual a 69%";
                    document.getElementById('txt_a').innerText = "De 70% a 89%"; await wait(3500);
                }
            } loop();
        </script>
        """
    },
    "consolidacion": {
        "height": 255,
        "html": """
        <style>body { margin: 0; padding: 4px; box-sizing: border-box; }</style>
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:12px;">
                <div style="background:#92d050; color:white; border-radius:8px; padding:12px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"><div style="font-size:10.5px; font-weight:bold; margin-bottom:2px;">KPIs (50%)</div><div style="font-size:22px; font-weight:900;">95 %</div></div>
                <div style="background:#92d050; color:white; border-radius:8px; padding:12px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"><div style="font-size:10.5px; font-weight:bold; margin-bottom:2px;">Iniciativas (50%)</div><div style="font-size:22px; font-weight:900;">92 %</div></div>
                <div style="background:#00b050; color:white; border-radius:8px; padding:12px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"><div style="font-size:10.5px; font-weight:bold; margin-bottom:2px;">Total ONE TRACK</div><div style="font-size:22px; font-weight:900;">94 %</div></div>
            </div>
            <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <table style="width:100%; border-collapse:collapse; font-size:12px; background:white; text-align:center;">
                    <thead><tr style="background:#002060; color:white;"><th style="padding:8px;">Mes</th><th style="padding:8px;">KPIs</th><th style="padding:8px;">Iniciativas</th><th style="padding:8px;">Integrado</th><th style="padding:8px;">Q</th><th style="padding:8px;">Resultado Q</th></tr></thead>
                    <tbody>
                        <tr><td style="padding:8px; font-weight:bold; border-top:1px solid #e2e8f0;">Ene</td><td style="padding:8px; border-top:1px solid #e2e8f0;">92% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">88% 🟡</td><td style="padding:8px; border-top:1px solid #e2e8f0;">90% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">Q1</td><td style="padding:8px; border-top:1px solid #e2e8f0;">-</td></tr>
                        <tr><td style="padding:8px; font-weight:bold; border-top:1px solid #e2e8f0;">Feb</td><td style="padding:8px; border-top:1px solid #e2e8f0;">96% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">94% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">95% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">Q1</td><td style="padding:8px; border-top:1px solid #e2e8f0;">-</td></tr>
                        <tr><td style="padding:8px; font-weight:bold; border-top:1px solid #e2e8f0;">Mar</td><td style="padding:8px; border-top:1px solid #e2e8f0;">98% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">95% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">97% 🟢</td><td style="padding:8px; border-top:1px solid #e2e8f0;">Q1</td><td style="padding:8px; font-weight:bold; background:#f0fdf4; border-top:1px solid #e2e8f0;">94% 🟢</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        """
    }
}

def mostrar_animacion(clave):
    if clave in ANIMACIONES_HTML:
        components.html(ANIMACIONES_HTML[clave]["html"], height=ANIMACIONES_HTML[clave]["height"])

animacion_kpis_realista = lambda: mostrar_animacion("kpis")
animacion_iniciativa_completa_realista = lambda: mostrar_animacion("iniciativa")
animacion_gantt_tareas_realista = lambda: mostrar_animacion("gantt")
animacion_recursos_realista = lambda: mostrar_animacion("recursos")
animacion_intervalos_realista = lambda: mostrar_animacion("intervalos")
animacion_consolidacion_anual_realista = lambda: mostrar_animacion("consolidacion")

# ==============================================================================
# FASE 5: CONTROL DE SESION / ACCESO
# ==============================================================================
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
                st.session_state.perm_store = {}
                for k in list(st.session_state.keys()):
                    if k.startswith("editor_") or k.startswith("ui_") or k.startswith("live_") or k.startswith("cfg_"):
                        del st.session_state[k]
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

token = st.session_state.user_info['username']
cargar_datos()

if st.session_state.user_info['role'] == 'admin':
    st.markdown("<h2 style='color:#002060; font-weight:900;'>Panel de Administración</h2>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.user_info = None
        st.session_state.perm_store = {}
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

# --- BARRA LATERAL ---
if 'vista_actual' not in st.session_state: st.session_state.vista_actual = "Q1"

with st.sidebar:
    st.markdown("<h2 style='color:#002060; font-weight:900;'>NAVEGACIÓN</h2>", unsafe_allow_html=True)
    vistas = ["Q1", "Q2", "Q3", "Q4", "Resumen Anual", "Guía de Uso", "Configuración de ONE Track"]
    for v in vistas:
        b_type = "primary" if st.session_state.vista_actual == v else "secondary"
        if st.button(v, key=f"nav_{v}", use_container_width=True, type=b_type):
            commit_live_edits()
            st.session_state.vista_actual = v
            st.rerun()
            
    st.divider()
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.user_info = None
        st.session_state.perm_store = {}
        for k in list(st.session_state.keys()):
            if k.startswith("editor_") or k.startswith("ui_") or k.startswith("live_") or k.startswith("cfg_"):
                del st.session_state[k]
        st.rerun()

# --- HEADER PRINCIPAL ---
col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
with col2: 
    logo_c = safe_str(get_store("ui_logo_cliente", st.session_state.user_info.get("logo_url", DEFAULT_LOGO_CLIENTE)), DEFAULT_LOGO_CLIENTE)
    st.markdown(f"<div class='img-placeholder'><img src='{logo_c}' style='max-height: 90px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)
with col3: 
    st.markdown(f"<div class='img-placeholder'><img src='{DEFAULT_LOGO_ONE_TRACK}' style='max-height: 90px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)

c_inf1, c_inf2, c_inf3 = st.columns(3)
with c_inf1:
    st.markdown("<div class='custom-label'>EMPRESA</div>", unsafe_allow_html=True)
    bind_text_input("Empresa", "ui_empresa", "ONE TRACK")
with c_inf2:
    st.markdown("<div class='custom-label'>NOMBRE (DUEÑO DEL ONE TRACK)</div>", unsafe_allow_html=True)
    bind_text_input("Dueño", "ui_dueno", "")
with c_inf3:
    st.markdown("<div class='custom-label'>PUESTO</div>", unsafe_allow_html=True)
    bind_text_input("Puesto", "ui_puesto", "")

st.divider()

v_actual_title = f" {st.session_state.vista_actual}" if st.session_state.vista_actual in trimestres else ""
col_t, col_btn = st.columns([4, 1])
with col_t: st.markdown(f"<h2 style='color:#002060; font-weight:900; margin:0;'>Tablero de Control{v_actual_title}</h2>", unsafe_allow_html=True)
with col_btn:
    if st.button("Guardar Cambios", type="primary", use_container_width=True):
        with st.spinner("Guardando en la nube..."):
            guardar_en_bd()
        st.success("Guardado exitoso.")
st.write("")

# ==============================================================================
# FASE 6: RUTEO DE PESTAÑAS
# ==============================================================================
if st.session_state.vista_actual == "Guía de Uso":
    st.markdown("<div class='section-title'>📖 Guía Integral de Uso - ONE TRACK Workspace</div>", unsafe_allow_html=True)
    st.markdown("""
    Esta guía te proporciona un recorrido detallado paso a paso para configurar, operar e interpretar cada sección de tu tablero estratégico. Todas las simulaciones a continuación replican el comportamiento real de la aplicación.
    """)
    
    # 1. PONDERACIÓN
    st.markdown("<div class='sub-section-title'>1. La Doble Ponderación en ONE TRACK</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='guide-callout'>
        <strong>En ONE TRACK existen dos niveles de ponderación que debes equilibrar:</strong><br><br>
        <strong>A) Ponderación Global (Frontal):</strong> Se ubica en la parte superior del tablero. Define qué peso tiene el resultado numérico del negocio (<strong>KPIs %</strong>) frente al avance de los proyectos estratégicos (<strong>Iniciativas %</strong>). La suma recomendada es <strong>100%</strong> (por ejemplo: 50% KPIs y 50% Iniciativas).<br><br>
        <strong>B) Ponderación por Iniciativa (Trimestral):</strong> Dentro de cada trimestre (Q1, Q2, Q3, Q4), cada iniciativa cuenta con su propio campo de <strong>Ponderación (%)</strong>. La suma de las ponderaciones de todas las iniciativas de ese trimestre debe sumar exactamente <strong>100%</strong> (por ejemplo: si tienes 2 iniciativas en Q2, una puede pesar 60% y la otra 40%).
    </div>
    """, unsafe_allow_html=True)

    # 2. TABLA KPIS
    st.markdown("<div class='sub-section-title'>2. Configuración y Llenado de KPIs Mensuales</div>", unsafe_allow_html=True)
    st.write("""
    Para ingresar un indicador clave de desempeño en la tabla:
    1. **Nombre del KPI:** Escribe el nombre de la métrica (ej. *Ventas Nuevos Clientes*).
    2. **Tipo de Cálculo:** 
       - *Acumulado:* La meta anual se va alcanzando con la suma acumulativa de cada mes.
       - *Promedio:* Para porcentajes o calificaciones de servicio (ej. NPS, Margen %).
       - *Valor Final:* Solo importa el resultado puntual del último período medido.
    3. **Meta y UM (Unidad de Medida):** Define el objetivo anual y la unidad (`$`, `U`, `%`, `Tiempo`).
    4. **< Mejor (Menor es mejor):** Si marcas **SI**, la fórmula premia valores bajos (mermas, rotación, costos) invirtiendo el cálculo: $(\\text{Prog} / \\text{Real}) \\times 100$.
    5. **Tríada Mensual (Prog - Real - Semáforo):** Captura lo programado y lo ejecutado. El círculo de semáforo (`●`) se proyecta automáticamente evaluando tu desempeño frente a los intervalos configurados.
    """)
    mostrar_animacion("kpis")

    # 3. INICIATIVAS Y RESULTADOS
    st.markdown("<div class='sub-section-title'>3. Iniciativas Estratégicas y Resultados Cuantitativos</div>", unsafe_allow_html=True)
    st.write("""
    Cada iniciativa representa una apuesta táctica mayor para mover tus KPIs:
    * **Nombre y Objetivo:** Describe la iniciativa y redacta un objetivo claro con alcance y fecha.
    * **Ponderación (%):** Asigna el porcentaje que representa esta iniciativa dentro del total del trimestre.
    * **Resultados de la Iniciativa:** A diferencia de las tareas del día a día, esta tabla define los **entregables cuantitativos de impacto** (ej. *Clientes B2B activos*). Al llenar la **Meta** y lo **Realizado**, el sistema calcula el **Avance %** de cada entregable y actualiza la tarjeta superior: **CUMPLIMIENTO DE RESULTADOS**.
    """)
    mostrar_animacion("iniciativa")

    # 4. GANTT Y TAREAS
    st.markdown("<div class='sub-section-title'>4. Plan de Acción y Cronograma Gantt</div>", unsafe_allow_html=True)
    st.write("""
    El motor de seguimiento táctico de cada iniciativa:
    * **Jerarquías:** Utiliza numeración formal (`1.`, `1.1`, `1.2`) para clasificar actividades principales y secundarias.
    * **Estatus Automático:** El sistema compara la fecha de finalización (`Fin`) contra la fecha de hoy:
      - Si la casilla **Completado** está marcada: **🟢 A tiempo**.
      - Si la fecha límite ya venció y la casilla no está marcada: **🔴 Retrasado** automáticamente.
    * **Gantt Visual:** El cronograma inferior dibuja las barras de duración en tiempo real.
    """)
    mostrar_animacion("gantt")

    # 5. RECURSOS 2X2
    st.markdown("<div class='sub-section-title'>5. Recursos Requeridos para la Iniciativa (Cuadrícula 2×2)</div>", unsafe_allow_html=True)
    st.write("""
    Al pie de cada iniciativa, dispones de 4 bloques para asegurar la viabilidad del proyecto antes de arrancar:
    * **Talento:** Perfiles, roles, contrataciones clave o consultores asignados al proyecto.
    * **Presupuesto $:** Fondos específicos aprobados para licenciamiento, viáticos o pauta.
    * **Infraestructura:** Oficinas, almacenes, servidores o equipamiento físico necesario.
    * **Tecnología:** Softwares, APIs, accesos a bases de datos o plataformas requeridas.
    """)
    mostrar_animacion("recursos")

    # 6. SEMAFORIZACIÓN CONTINUA
    st.markdown("<div class='sub-section-title'>6. Parámetros de Semáforo (Intervalos Continuos)</div>", unsafe_allow_html=True)
    st.write("""
    En la pestaña **Configuración de ONE Track**, ajustas los 3 cortes porcentuales institucionales. El sistema genera rangos continuos matemáticamente consistentes sin solapamientos:
    * **🔴 Bajo (Rojo):** Rendimientos iguales o menores al primer límite (ej. $\\le 79\\%$).
    * **🟡 Medio (Amarillo):** Rendimientos en el rango de alerta (ej. $80\\%$ a $89\\%$).
    * **🟢 Meta (Verde):** Rendimientos que cumplen la meta aprobada (ej. $90\\%$ a $100\\%$).
    * **🟢 Sobresaliente (Súper Verde):** Rendimientos por encima del $100\\%$.
    """)
    mostrar_animacion("intervalos")

    # 7. TABLERO ANUAL
    st.markdown("<div class='sub-section-title'>7. Consolidación de Resultados y Tablero Anual</div>", unsafe_allow_html=True)
    st.write("""
    En la pestaña **Resumen Anual**, la plataforma consolida la totalidad del año fiscal:
    * La fórmula multiplica el avance de KPIs y de Iniciativas por sus ponderaciones globales para entregar el **Total ONE TRACK**.
    * La tabla anual despliega cada mes con su porcentaje y su círculo evaluador correspondiente.
    * El gráfico de tendencias compara mes con mes la curva de resultados de negocio frente al ritmo de avance de proyectos.
    """)
    mostrar_animacion("consolidacion")

elif st.session_state.vista_actual in trimestres.keys() or st.session_state.vista_actual == "Resumen Anual":
    
    st.markdown("""
    <div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #002060; margin-bottom: 20px;'>
        <p style='margin: 0; color: #4b5563; font-size: 15px;'>
            <strong style='color:#002060;'>Indicadores Clave de Desempeño (KPIs)</strong> &rarr; miden el resultado cuantitativo del negocio.<br>
            <strong style='color:#002060;'>Iniciativas Estratégicas</strong> &rarr; miden la ejecución de proyectos para alcanzar los resultados.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_w, col_s1, col_s2, col_s3 = st.columns([1.5, 1, 1, 1])
    with col_w:
        st.markdown("<div class='summary-card' style='padding:15px;'><p class='summary-title'>Ponderación Global</p>", unsafe_allow_html=True)
        c_kpi, c_okr = st.columns(2)
        with c_kpi:
            st.markdown("<div class='custom-label'>INDICADORES (KPIs) (%)</div>", unsafe_allow_html=True)
            bind_number_input("Ind", "ui_p_kpis", 50.0)
        with c_okr:
            st.markdown("<div class='custom-label'>INICIATIVAS (%)</div>", unsafe_allow_html=True)
            bind_number_input("Ini", "ui_p_okrs", 50.0)
        st.markdown("</div>", unsafe_allow_html=True)

    c_rojo = safe_float(get_store("cfg_corte_rojo", 79.0), 79.0)
    c_amarillo = safe_float(get_store("cfg_corte_amarillo", 89.0), 89.0)
    c_verde = safe_float(get_store("cfg_corte_verde", 100.0), 100.0)

    if st.session_state.vista_actual in trimestres.keys():
        q_name = st.session_state.vista_actual
        meses_q = trimestres[q_name]
        
        st.markdown(f"<div class='section-title'>Indicadores Clave de Desempeño (KPIs) - {q_name}</div>", unsafe_allow_html=True)
        
        df_kpi_in = get_store(f"df_kpi_{q_name}", pd.DataFrame()).reset_index(drop=True)
        df_kpi_in = calcular_sem_kpis(df_kpi_in, meses_q, c_rojo, c_amarillo, c_verde)
        
        col_cfg = {
            "Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio", "Valor Final"]), 
            "UM": st.column_config.SelectboxColumn(options=["U", "$", "%", "Tiempo"]), 
            "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])
        }
        for m in meses_q:
            col_cfg[f"{m} Semáforo"] = st.column_config.TextColumn(disabled=True, width="small")

        st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
        edited_kpi = st.data_editor(
            df_kpi_in,
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config=col_cfg,
            key=f"editor_kpi_{q_name}"
        )
        st.session_state[f"live_kpi_{q_name}"] = edited_kpi
        st.markdown("</div>", unsafe_allow_html=True)

        render_footer(edited_kpi, meses_q)

        st.markdown(f"<div class='section-title'>Iniciativas Estratégicas - {q_name}</div>", unsafe_allow_html=True)
        num_i = int(safe_float(get_store(f"num_iniciativas_{q_name}", 1), 1))
        
        for i in range(1, num_i + 1):
            init_okr_structure(q_name, i)
            st.markdown("<div class='iniciativa-box'>", unsafe_allow_html=True)
            
            df_out_in = get_store(f"df_outputs_{q_name}_{i}", pd.DataFrame()).reset_index(drop=True)
            df_tar_in = get_store(f"df_tareas_{q_name}_{i}", pd.DataFrame()).reset_index(drop=True)

            df_out_calc = update_avance_resultados(st.session_state.get(f"live_out_{q_name}_{i}", df_out_in))
            valid_o = df_out_calc[df_out_calc["Nombre"].fillna("").astype(str).str.strip() != ""] if (df_out_calc is not None and not df_out_calc.empty) else pd.DataFrame()
            avance_ini = safe_float(valid_o["Avance %"].mean(), 0.0) if not valid_o.empty else 0.0

            df_tar_calc = update_estatus_tareas(st.session_state.get(f"live_tar_{q_name}_{i}", df_tar_in))
            tot_t = len(df_tar_calc[df_tar_calc["Tarea"].fillna("").astype(str).str.strip() != ""]) if (df_tar_calc is not None and not df_tar_calc.empty) else 0
            comp = df_tar_calc["Completado"].sum() if tot_t > 0 else 0
            
            fecha_inicio, fecha_fin = None, None
            if tot_t > 0:
                df_valid_dates = df_tar_calc.copy()
                df_valid_dates['Inicio'] = pd.to_datetime(df_valid_dates['Inicio'], errors='coerce')
                df_valid_dates['Fin'] = pd.to_datetime(df_valid_dates['Fin'], errors='coerce')
                df_valid_dates = df_valid_dates.dropna(subset=['Inicio', 'Fin'])
                if not df_valid_dates.empty:
                    fecha_inicio = df_valid_dates['Inicio'].min()
                    fecha_fin = df_valid_dates['Fin'].max()

            if tot_t == 0: estatus_calc = "⚪ Sin Tareas"
            elif "🔴 Retrasado" in df_tar_calc["Estatus"].values: estatus_calc = "🔴 Retrasado"
            elif comp == tot_t and tot_t > 0: estatus_calc = "🟢 Completado"
            else: estatus_calc = "🟢 En Tiempo"
            
            col_ini = ob_color(avance_ini, c_rojo, c_amarillo, c_verde)
            txt_col = "black" if col_ini in ["#ffff00", "#92d050"] else "white"

            st.markdown(f"<div class='iniciativa-header'>Iniciativa #{i}</div>", unsafe_allow_html=True)
            
            h_col1, h_col2 = st.columns([1, 2.5])
            with h_col1: pass 
            with h_col2: 
                st.markdown(f"""
                <div style='display:flex; gap:10px; justify-content: flex-end;'>
                    <div style='background:{col_ini}; color:{txt_col}; padding: 8px 15px; border-radius:6px; font-weight:900; font-size:14px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>CUMPLIMIENTO DE RESULTADOS: {avance_ini:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            ch1, ch2, ch3 = st.columns([3, 1, 1])
            with ch1:
                st.markdown("<div class='custom-label'>NOMBRE DE LA INICIATIVA</div>", unsafe_allow_html=True)
                bind_text_input("Nombre", f"ui_nom_{q_name}_{i}")
            with ch2:
                st.markdown("<div class='custom-label'>PONDERACIÓN (%)</div>", unsafe_allow_html=True)
                bind_number_input("Peso", f"ui_peso_{q_name}_{i}", 20.0)
            with ch3:
                st.markdown("<div class='custom-label'>ESTATUS ACTUAL</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#ffffff; padding: 8px 12px; border-radius:6px; border: 1px solid #cbd5e1; font-weight: bold; color: #4b5563; font-size:14px; text-align:center;'>{estatus_calc}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='custom-label'>OBJETIVO</div>", unsafe_allow_html=True)
            bind_text_area("Obj", f"ui_obj_{q_name}_{i}")
            
            if pd.notnull(fecha_inicio) and pd.notnull(fecha_fin):
                st.markdown(f"<div style='background-color:#f8f9fa; padding:10px 15px; border-radius:6px; border:1px solid #e5e7eb; margin-bottom:15px; margin-top:15px;'><strong style='color:#002060;'>📅 Duración de la Iniciativa:</strong> &nbsp;&nbsp; {format_date_spanish(fecha_inicio)} &mdash; {format_date_spanish(fecha_fin)}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='sub-section-title'>Resultados de la Iniciativa</div>", unsafe_allow_html=True)
            edited_out = st.data_editor(
                df_out_in,
                use_container_width=True, hide_index=True, num_rows="dynamic",
                column_config={
                    "UM": st.column_config.SelectboxColumn(options=["U", "$", "%", "Tiempo"]),
                    "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"]),
                    "Avance %": st.column_config.NumberColumn(format="%.1f %%", disabled=True)
                },
                key=f"editor_out_{q_name}_{i}"
            )
            st.session_state[f"live_out_{q_name}_{i}"] = update_avance_resultados(edited_out)
            
            st.markdown("<div class='sub-section-title'>Plan de Tareas y Seguimiento</div>", unsafe_allow_html=True)
            edited_tar = st.data_editor(
                df_tar_in,
                use_container_width=True, hide_index=True, num_rows="dynamic",
                column_config={
                    "Jerarquia": st.column_config.TextColumn(width="small", help="Ej: 1, 1.1"), 
                    "Inicio": st.column_config.DateColumn(format="YYYY-MM-DD"), 
                    "Fin": st.column_config.DateColumn(format="YYYY-MM-DD"),
                    "Estatus": st.column_config.TextColumn(disabled=True)
                },
                key=f"editor_tar_{q_name}_{i}"
            )
            st.session_state[f"live_tar_{q_name}_{i}"] = update_estatus_tareas(edited_tar)
            
            st.write("")
            dibujar_gantt(st.session_state[f"live_tar_{q_name}_{i}"])
            
            # --- SECCION DE RECURSOS (CUADRÍCULA 2X2) ---
            st.markdown("<div class='sub-section-title'>Recursos Requeridos para la Iniciativa</div>", unsafe_allow_html=True)
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.markdown("<div class='custom-label'>TALENTO</div>", unsafe_allow_html=True)
                bind_text_area("Talento", f"ui_rec_talento_{q_name}_{i}", height=75)
                st.markdown("<div class='custom-label'>INFRAESTRUCTURA</div>", unsafe_allow_html=True)
                bind_text_area("Infraestructura", f"ui_rec_infra_{q_name}_{i}", height=75)
            with r_col2:
                st.markdown("<div class='custom-label'>PRESUPUESTO $</div>", unsafe_allow_html=True)
                bind_text_area("Presupuesto $", f"ui_rec_presupuesto_{q_name}_{i}", height=75)
                st.markdown("<div class='custom-label'>TECNOLOGÍA</div>", unsafe_allow_html=True)
                bind_text_area("Tecnología", f"ui_rec_tec_{q_name}_{i}", height=75)

            st.markdown("</div><hr class='iniciativa-divider'>", unsafe_allow_html=True)

        col_add, col_rem, _ = st.columns([2, 2, 6])
        with col_add:
            if st.button("➕ Añadir Iniciativa", use_container_width=True, key=f"add_{q_name}"):
                commit_live_edits()
                set_store(f"num_iniciativas_{q_name}", num_i + 1)
                st.rerun()
        with col_rem:
            if st.button("🗑️ Quitar Iniciativa", use_container_width=True, key=f"rem_{q_name}"):
                if num_i > 1:
                    commit_live_edits()
                    set_store(f"num_iniciativas_{q_name}", num_i - 1)
                    st.rerun()

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

    if st.session_state.vista_actual in trimestres.keys():
        q_sel = st.session_state.vista_actual
        df_q = df_anual[df_anual["Trimestre"] == q_sel]
        res_k_total = safe_float(df_q["Indicadores Clave de Desempeño (KPIs)"].mean() * 100, 0.0)
        res_o_total = safe_float(df_q["Iniciativas Estratégicas"].mean() * 100, 0.0)
        res_tot_final = safe_float(df_q["Integrado"].mean() * 100, 0.0)
    else:
        res_k_total = safe_float(df_anual["Indicadores Clave de Desempeño (KPIs)"].mean() * 100, 0.0)
        res_o_total = safe_float(df_anual["Iniciativas Estratégicas"].mean() * 100, 0.0)
        res_tot_final = safe_float(df_anual["Integrado"].mean() * 100, 0.0)

    c_kpi = ob_color(res_k_total, c_rojo, c_amarillo, c_verde)
    c_okr = ob_color(res_o_total, c_rojo, c_amarillo, c_verde)
    c_tot = ob_color(res_tot_final, c_rojo, c_amarillo, c_verde)
    txt_kpi = ("black" if c_kpi in ["#ffff00", "#92d050"] else "white")
    txt_okr = ("black" if c_okr in ["#ffff00", "#92d050"] else "white")
    txt_tot = ("black" if c_tot in ["#ffff00", "#92d050"] else "white")

    with col_s1: st.markdown(f"<div class='summary-card' style='background-color:{c_kpi};'><p class='summary-title' style='color:{txt_kpi};'>KPIs</p><p class='summary-value' style='color:{txt_kpi};'>{res_k_total:.0f} %</p></div>", unsafe_allow_html=True)
    with col_s2: st.markdown(f"<div class='summary-card' style='background-color:{c_okr};'><p class='summary-title' style='color:{txt_okr};'>Iniciativas</p><p class='summary-value' style='color:{txt_okr};'>{res_o_total:.0f} %</p></div>", unsafe_allow_html=True)
    with col_s3: st.markdown(f"<div class='summary-card' style='background-color:{c_tot};'><p class='summary-title' style='color:{txt_tot};'>Total ONE TRACK</p><p class='summary-value' style='color:{txt_tot};'>{res_tot_final:.0f} %</p></div>", unsafe_allow_html=True)

    if st.session_state.vista_actual == "Resumen Anual":
        st.markdown("<div class='section-title'>Resumen Anual del Desempeño</div>", unsafe_allow_html=True)
        
        df_anual_view = pd.DataFrame()
        df_anual_view["Mes"] = df_anual["Mes"]
        df_anual_view["KPIs (%)"] = df_anual["Indicadores Clave de Desempeño (KPIs)"].apply(lambda x: f"{x:.0%}")
        df_anual_view["● KPIs"] = df_anual["Indicadores Clave de Desempeño (KPIs)"].apply(lambda x: ob_circle(x*100, c_rojo, c_amarillo, c_verde))
        df_anual_view["Iniciativas (%)"] = df_anual["Iniciativas Estratégicas"].apply(lambda x: f"{x:.0%}")
        df_anual_view["● Iniciativas"] = df_anual["Iniciativas Estratégicas"].apply(lambda x: ob_circle(x*100, c_rojo, c_amarillo, c_verde))
        df_anual_view["Integrado (%)"] = df_anual["Integrado"].apply(lambda x: f"{x:.0%}")
        df_anual_view["● Integrado"] = df_anual["Integrado"].apply(lambda x: ob_circle(x*100, c_rojo, c_amarillo, c_verde))
        df_anual_view["Trimestre"] = df_anual["Trimestre"]
        df_anual_view["Resultado Q"] = df_anual["Resultado Q"].apply(lambda x: f"{x:.0%}" if pd.notnull(x) else "-")
        df_anual_view["● Trimestre"] = df_anual["Resultado Q"].apply(lambda x: ob_circle(x*100, c_rojo, c_amarillo, c_verde) if pd.notnull(x) else "-")

        col_ta, col_ch = st.columns([1.3, 1])
        with col_ta:
            st.markdown("<div class='sub-section-title'>Desempeño Mensual y Trimestral</div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
            st.dataframe(df_anual_view, use_container_width=True, hide_index=True)
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

elif st.session_state.vista_actual == "Configuración de ONE Track":
    st.markdown("<div class='section-title'>⚙️ Configuración de ONE Track</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-section-title'>🎨 Intervalos del Semáforo de Desempeño</div>", unsafe_allow_html=True)
    st.info("Configura los 3 puntos de corte. El sistema genera automáticamente intervalos continuos sin porcentajes repetidos.")
    
    c_r = safe_float(get_store("cfg_corte_rojo", 79.0), 79.0)
    c_a = safe_float(get_store("cfg_corte_amarillo", 89.0), 89.0)
    c_v = safe_float(get_store("cfg_corte_verde", 100.0), 100.0)

    col_int1, col_int2 = st.columns([1.2, 1])
    with col_int1:
        st.markdown(f"""
            <div class='interval-box' style='background-color:#ff0000; color:white;'>
                <span>🔴 BAJO (ROJO)</span>
                <span>Menor o igual a {c_r:.0f}%</span>
            </div>
            <div class='interval-box' style='background-color:#ffff00; color:black;'>
                <span>🟡 MEDIO (AMARILLO)</span>
                <span>De {c_r + 1:.0f}% a {c_a:.0f}%</span>
            </div>
            <div class='interval-box' style='background-color:#92d050; color:white;'>
                <span>🟢 META (VERDE)</span>
                <span>De {c_a + 1:.0f}% a {c_v:.0f}%</span>
            </div>
            <div class='interval-box' style='background-color:#00b050; color:white;'>
                <span>🟢 SOBRESALIENTE (SÚPER VERDE)</span>
                <span>Mayor a {c_v:.0f}%</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col_int2:
        st.markdown("<div class='custom-label'>Límite Superior Rojo (%)</div>", unsafe_allow_html=True)
        bind_number_input("Rojo", "cfg_corte_rojo", 79.0)
        st.markdown("<div class='custom-label'>Límite Superior Amarillo (%)</div>", unsafe_allow_html=True)
        bind_number_input("Amarillo", "cfg_corte_amarillo", 89.0)
        st.markdown("<div class='custom-label'>Límite Superior Verde (%)</div>", unsafe_allow_html=True)
        bind_number_input("Verde", "cfg_corte_verde", 100.0)

    # --- SECCION DESCOMENTADA: BOTON DATOS DUMMY ---
    st.markdown("<br><div class='sub-section-title'>🛠️ Generar Datos de Prueba (Dummy)</div>", unsafe_allow_html=True)
    st.info("Presiona este botón para llenar tu tablero con datos estructurados de ejemplo que reflejan todas las funciones nuevas.")
    
    if st.button("Llenar tablero con datos Dummy", type="secondary", on_click=ejecutar_dummy_callback):
        st.success("¡Datos generados y guardados con éxito!")
        
    st.markdown("<br><div class='sub-section-title'>🔒 Seguridad de la Cuenta</div>", unsafe_allow_html=True)
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
