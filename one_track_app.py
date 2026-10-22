import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from sqlalchemy import text

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE TRACK - Workspace", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎥 CONFIGURACION DE ENLACES PARA GIFS 
# Pega la URL directa de tu .gif entre las comillas.
# Ejemplo: GIF_KPIS = "https://tu-servidor.com/demo_kpi.gif"
# ==========================================
GIF_KPIS = "" 
GIF_RESULTADOS = "" 
GIF_GANTT = "" 
GIF_RECURSOS = ""
GIF_BOTONES = "" 
GIF_SEMAFOROS = ""
# ==========================================

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
    .sub-section-title { font-size: 15px; font-weight: 900; color: #4b5563; margin-top: 25px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;}
    .custom-label { font-size: 14px; font-weight: 900; color: #002060; text-transform: uppercase; margin-bottom: 5px; margin-top: 10px; letter-spacing: 0.5px; }
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

# --- BÓVEDA PERMANENTE DE ESTADO (PERSISTENCIA INVIOLABLE) ---
if "perm_store" not in st.session_state:
    st.session_state.perm_store = {}

def get_store(key, default=None):
    return st.session_state.perm_store.get(key, default)

def set_store(key, val):
    st.session_state.perm_store[key] = val

def bind_text_input(label, key, default=""):
    if key not in st.session_state:
        st.session_state[key] = get_store(key, default)
    st.text_input(label, key=key, label_visibility="collapsed")
    set_store(key, st.session_state[key])

def bind_text_area(label, key, default="", height=70):
    if key not in st.session_state:
        st.session_state[key] = get_store(key, default)
    st.text_area(label, key=key, height=height, label_visibility="collapsed")
    set_store(key, st.session_state[key])

def bind_number_input(label, key, default=0.0):
    if key not in st.session_state:
        st.session_state[key] = float(get_store(key, default))
    st.number_input(label, key=key, label_visibility="collapsed")
    set_store(key, st.session_state[key])

# --- FUNCIONES MATEMATICAS, INTERVALOS Y COLORES ---
def calc_cump(prog, real, menor_mejor="NO"):
    if prog == 0 and real == 0: return 0.0
    if menor_mejor == "SI": return (prog / real * 100) if real > 0 else 100.0
    else: return (real / prog * 100) if prog > 0 else (100.0 if real > 0 else 0.0)

def ob_color(val, c_rojo=79.0, c_amarillo=89.0, c_verde=100.0):
    if val > c_verde: return "#00b050"       # Súper Verde (> corte verde)
    elif val > c_amarillo: return "#92d050"   # Verde (Meta: > amarillo y <= verde)
    elif val > c_rojo: return "#ffff00"       # Amarillo (Medio: > rojo y <= amarillo)
    else: return "#ff0000"                    # Rojo (Bajo: <= rojo)

def ob_circle(val, c_rojo=79.0, c_amarillo=89.0, c_verde=100.0):
    if val > c_verde: return "🟢"
    elif val > c_amarillo: return "🟢"
    elif val > c_rojo: return "🟡"
    else: return "🔴"

def format_date_spanish(d):
    meses_abrev = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    return f"{d.day} de {meses_abrev[d.month-1]}"

def update_estatus_tareas(df):
    if df.empty: return df
    df_res = df.copy()
    hoy = date.today()
    if "Estatus" not in df_res.columns: df_res["Estatus"] = "⚪ Pendiente"
    for idx, row in df_res.iterrows():
        if row.get("Completado", False):
            df_res.at[idx, "Estatus"] = "🟢 A tiempo"
        else:
            if pd.notnull(row.get("Fin")):
                try:
                    fin = pd.to_datetime(row["Fin"]).date()
                    if fin < hoy: df_res.at[idx, "Estatus"] = "🔴 Retrasado"
                    else: df_res.at[idx, "Estatus"] = "🟢 A tiempo"
                except Exception:
                    df_res.at[idx, "Estatus"] = "🟢 A tiempo"
            else:
                df_res.at[idx, "Estatus"] = "⚪ Pendiente"
    return df_res

def update_avance_resultados(df):
    if df.empty: return df
    df_res = df.copy()
    if "Avance %" not in df_res.columns: df_res["Avance %"] = 0.0
    for idx, row in df_res.iterrows():
        if str(row.get("Nombre", "")).strip() != "":
            try:
                meta = float(row.get("Meta", 0.0) or 0.0)
                real = float(row.get("Real", 0.0) or 0.0)
                menor = str(row.get("< Mejor", "NO"))
                df_res.at[idx, "Avance %"] = calc_cump(meta, real, menor)
            except Exception:
                df_res.at[idx, "Avance %"] = 0.0
        else:
            df_res.at[idx, "Avance %"] = 0.0
    return df_res

def calcular_sem_kpis(df, meses, c_rojo, c_amarillo, c_verde):
    if df.empty: return df
    df_res = df.copy()
    for idx, row in df_res.iterrows():
        menor = str(row.get("< Mejor", "NO"))
        for m in meses:
            p = float(row.get(f"{m} Prog", 0.0) or 0.0)
            r = float(row.get(f"{m} Real", 0.0) or 0.0)
            if p == 0.0 and r == 0.0:
                df_res.at[idx, f"{m} Semáforo"] = "⚪"
            else:
                cump = calc_cump(p, r, menor)
                df_res.at[idx, f"{m} Semáforo"] = ob_circle(cump, c_rojo, c_amarillo, c_verde)
    return df_res

def render_footer(df, meses):
    html_footer = "<div style='display:flex; justify-content:flex-start; gap:12px; margin-bottom: 20px; align-items:center;'><div style='font-weight:900; color:#002060; font-size:15px; text-transform:uppercase;'>Avance Mensual:</div>"
    c_rojo = float(get_store("cfg_corte_rojo", 79.0))
    c_amarillo = float(get_store("cfg_corte_amarillo", 89.0))
    c_verde = float(get_store("cfg_corte_verde", 100.0))
    for m in meses:
        total_peso, acumulado = 0.0, 0.0
        for i in range(len(df)):
            if str(df["Indicadores Clave de Desempeño (KPIs)"].iloc[i]).strip() != "":
                p = float(df[f"{m} Prog"].iloc[i] or 0.0)
                r = float(df[f"{m} Real"].iloc[i] or 0.0)
                peso = float(df["Peso %"].iloc[i] or 0.0)
                cump = calc_cump(p, r, str(df["< Mejor"].iloc[i]))
                acumulado += cump * (peso / 100.0)
                total_peso += peso
        avance = (acumulado / (total_peso / 100.0)) if total_peso > 0 else 0.0
        col = ob_color(avance, c_rojo, c_amarillo, c_verde)
        txt = "black" if col in ["#ffff00", "#92d050"] else "white"
        html_footer += f"<div class='footer-box' style='background-color:{col}; color:{txt};'>{m}: {avance:.1f}%</div>"
    st.markdown(html_footer + "</div>", unsafe_allow_html=True)

def dibujar_gantt(df_tareas):
    if df_tareas.empty: return
    df_plot = df_tareas.copy()
    df_plot = df_plot[df_plot["Tarea"].str.strip() != ""]
    df_plot["Inicio"] = pd.to_datetime(df_plot["Inicio"], errors='coerce')
    df_plot["Fin"] = pd.to_datetime(df_plot["Fin"], errors='coerce')
    df_plot = df_plot.dropna(subset=["Inicio", "Fin"])
    if df_plot.empty: return
    df_plot = df_plot.sort_values(by="Jerarquia")
    df_plot['Nombre'] = df_plot['Jerarquia'] + " " + df_plot['Tarea']
    df_plot['Estado_Visual'] = df_plot['Completado'].apply(lambda x: "Realizado" if x else "Pendiente")
    chart = alt.Chart(df_plot).mark_bar(cornerRadius=4, size=20).encode(
        x=alt.X('Inicio', title='', axis=alt.Axis(format="%d %b", grid=True, gridColor="#f0f2f6")), x2='Fin',
        y=alt.Y('Nombre', sort=df_plot['Nombre'].tolist(), title='', axis=alt.Axis(labelFontWeight="bold", labelLimit=300)),
        color=alt.Color('Estado_Visual', scale=alt.Scale(domain=['Realizado', 'Pendiente'], range=['#002060', '#a0aabf']), legend=alt.Legend(title="Estado", orient="bottom"))
    ).properties(height=alt.Step(40))
    st.altair_chart(chart, use_container_width=True)

def render_gif_placeholder(url, placeholder_text):
    if url and str(url).strip() != "":
        st.markdown(f"""
            <div style='text-align: center; margin: 15px 0;'>
                <img src='{url.strip()}' style='max-width: 100%; border-radius: 10px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='img-placeholder' style='height: 180px; color: #94a3b8; border: 2px dashed #cbd5e1; background: #ffffff; font-weight: 600;'>{placeholder_text}</div>", unsafe_allow_html=True)

# --- SINCRONIZADOR DE EDICIONES ACTIVAS ---
def commit_live_edits():
    for q in trimestres.keys():
        if f"live_kpi_{q}" in st.session_state:
            set_store(f"df_kpi_{q}", st.session_state[f"live_kpi_{q}"])
        num_i = int(get_store(f"num_iniciativas_{q}", 1))
        for i in range(1, num_i + 1):
            if f"live_out_{q}_{i}" in st.session_state:
                set_store(f"df_outputs_{q}_{i}", st.session_state[f"live_out_{q}_{i}"])
            if f"live_tar_{q}_{i}" in st.session_state:
                set_store(f"df_tareas_{q}_{i}", st.session_state[f"live_tar_{q}_{i}"])

# --- GENERADOR DUMMY (ACTUALIZADO A NUEVA ARQUITECTURA) ---
def generar_dummy_onetest():
    mult_q = {"Q1": 0.85, "Q2": 0.90, "Q3": 0.98, "Q4": 1.05}
    cols_t = ["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado", "Estatus"]
    cols_out = ["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance %"]

    set_store("ui_p_kpis", 50.0)
    set_store("ui_p_okrs", 50.0)
    set_store("cfg_corte_rojo", 79.0)
    set_store("cfg_corte_amarillo", 89.0)
    set_store("cfg_corte_verde", 100.0)

    for q_name, meses in trimestres.items():
        cols_kpi = ["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"]
        for m in meses: cols_kpi.extend([f"{m} Prog", f"{m} Real", f"{m} Semáforo"])
        df_k = pd.DataFrame(columns=cols_kpi)
        
        row1 = ["Ventas Mensuales", "Acumulado", 500000.0, "$", "NO", 50.0]
        for _ in meses: row1.extend([166666.0, 166666.0 * mult_q[q_name], "⚪"])
        df_k.loc[1] = row1

        row2 = ["Satisfacción de Clientes", "Promedio", 95.0, "%", "NO", 50.0]
        for _ in meses: row2.extend([95.0, 95.0 * mult_q[q_name], "⚪"])
        df_k.loc[2] = row2

        df_k = calcular_sem_kpis(df_k, meses, 79.0, 89.0, 100.0)
        set_store(f"df_kpi_{q_name}", df_k)

    # Q1
    q_n = "Q1"; set_store(f"num_iniciativas_{q_n}", 1)
    set_store(f"ui_nom_{q_n}_1", "Expansión de Mercado Norte")
    set_store(f"ui_peso_{q_n}_1", 100.0)
    set_store(f"ui_obj_{q_n}_1", "Conquistar 3 nuevos estados mediante campañas digitales y alianzas locales.")
    set_store(f"ui_rec_talento_{q_n}_1", "1 Director Comercial, 2 Ejecutivos Regionales, 1 Especialista en Performance Marketing")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$250,000 MXN para pauta digital y prospección en campo")
    set_store(f"ui_rec_infra_{q_n}_1", "Oficina satélite compartida en Monterrey, líneas IP móviles")
    set_store(f"ui_rec_tec_{q_n}_1", "HubSpot CRM Pro, Zoom Phone, Plataforma Meta Ads")
    df_o1 = pd.DataFrame(columns=cols_out)
    df_o1.loc[1] = ["Abrir sucursales", "U", "NO", 3.0, 2.0, 0.0]
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o1))
    df_t1 = pd.DataFrame(columns=cols_t)
    df_t1.loc[1] = ["1.", "Investigación", "Ana", date(2026, 1, 5), date(2026, 1, 15), True, ""]
    df_t1.loc[2] = ["1.1", "Contratación", "Luis", date(2026, 1, 16), date(2026, 2, 10), True, ""]
    df_t1.loc[3] = ["1.2", "Lanzamiento", "Carlos", date(2026, 2, 15), date(2026, 3, 20), False, ""]
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t1))

    # Q2
    q_n = "Q2"; set_store(f"num_iniciativas_{q_n}", 2)
    set_store(f"ui_nom_{q_n}_1", "Nuevo Producto Alpha")
    set_store(f"ui_peso_{q_n}_1", 60.0)
    set_store(f"ui_obj_{q_n}_1", "Lanzar producto Alpha antes del cierre de semestre.")
    set_store(f"ui_rec_talento_{q_n}_1", "1 Product Manager, 2 Ingenieros de Software, 1 Diseñador UX/UI")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$180,000 MXN para desarrollo y pruebas de usabilidad")
    set_store(f"ui_rec_infra_{q_n}_1", "Servidores cloud AWS dedicados para pruebas de carga")
    set_store(f"ui_rec_tec_{q_n}_1", "Figma, GitHub Enterprise, Docker, Sentry")
    df_o2_1 = pd.DataFrame(columns=cols_out)
    df_o2_1.loc[1] = ["Prototipos", "U", "NO", 5.0, 5.0, 0.0]
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o2_1))
    df_t2_1 = pd.DataFrame(columns=cols_t)
    df_t2_1.loc[1] = ["1.", "Diseño", "Ana", date(2026, 4, 1), date(2026, 4, 20), True, ""]
    df_t2_1.loc[2] = ["2.", "Pruebas", "Luis", date(2026, 5, 1), date(2026, 5, 15), True, ""]
    df_t2_1.loc[3] = ["3.", "Preventa", "Carlos", date(2026, 6, 1), date(2026, 6, 25), False, ""]
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t2_1))

    set_store(f"ui_nom_{q_n}_2", "Optimización Costos Operativos")
    set_store(f"ui_peso_{q_n}_2", 40.0)
    set_store(f"ui_obj_{q_n}_2", "Reducir costos operativos en logística y distribución.")
    set_store(f"ui_rec_talento_{q_n}_2", "1 Coordinador de Logística, 1 Auditor Financiero Externo")
    set_store(f"ui_rec_presupuesto_{q_n}_2", "$50,000 MXN en honorarios de consultoría")
    set_store(f"ui_rec_infra_{q_n}_2", "Revisión física de bodegas y contratos de flota")
    set_store(f"ui_rec_tec_{q_n}_2", "Sistema TMS de optimización de rutas, Excel Avanzado")
    df_o2_2 = pd.DataFrame(columns=cols_out)
    df_o2_2.loc[1] = ["Ahorro en logística", "%", "SI", 15.0, 12.0, 0.0]
    set_store(f"df_outputs_{q_n}_2", update_avance_resultados(df_o2_2))
    df_t2_2 = pd.DataFrame(columns=cols_t)
    df_t2_2.loc[1] = ["1.", "Auditoría", "Sofia", date(2026, 4, 5), date(2026, 4, 25), True, ""]
    df_t2_2.loc[2] = ["2.", "Renegociación", "Luis", date(2026, 5, 5), date(2026, 5, 20), False, ""]
    df_t2_2.loc[3] = ["3.", "Rutas", "Sofia", date(2026, 6, 1), date(2026, 6, 28), False, ""]
    set_store(f"df_tareas_{q_n}_2", update_estatus_tareas(df_t2_2))

    # Q3
    q_n = "Q3"; set_store(f"num_iniciativas_{q_n}", 1)
    set_store(f"ui_nom_{q_n}_1", "Certificación ISO 9001")
    set_store(f"ui_peso_{q_n}_1", 100.0)
    set_store(f"ui_obj_{q_n}_1", "Obtener certificación en procesos de calidad clave.")
    set_store(f"ui_rec_talento_{q_n}_1", "1 Oficial de Cumplimiento, Comité Interno de Calidad (5 líderes)")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$120,000 MXN para auditoría certificadora y talleres")
    set_store(f"ui_rec_infra_{q_n}_1", "Salas de capacitación y señalética institucional de procesos")
    set_store(f"ui_rec_tec_{q_n}_1", "Gestor documental Confluence, Software de Auditoría ISO")
    df_o3 = pd.DataFrame(columns=cols_out)
    df_o3.loc[1] = ["Fases", "U", "NO", 3.0, 2.0, 0.0]
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o3))
    df_t3 = pd.DataFrame(columns=cols_t)
    df_t3.loc[1] = ["1.", "Diagnóstico", "Juan", date(2026, 7, 1), date(2026, 7, 15), True, ""]
    df_t3.loc[2] = ["2.", "Capacitación", "Ana", date(2026, 8, 1), date(2026, 8, 20), False, ""]
    df_t3.loc[3] = ["3.", "Auditoría Final", "Luis", date(2026, 9, 10), date(2026, 9, 25), False, ""]
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t3))

    # Q4
    q_n = "Q4"; set_store(f"num_iniciativas_{q_n}", 1)
    set_store(f"ui_nom_{q_n}_1", "Planificación Estratégica 2027")
    set_store(f"ui_peso_{q_n}_1", 100.0)
    set_store(f"ui_obj_{q_n}_1", "Cerrar métricas anuales y consolidar presupuestos de 2027.")
    set_store(f"ui_rec_talento_{q_n}_1", "Equipo Directivo Completo, 1 Consultor de Estrategia")
    set_store(f"ui_rec_presupuesto_{q_n}_1", "$90,000 MXN para offsite estratégico y estudios de mercado")
    set_store(f"ui_rec_infra_{q_n}_1", "Sede externa para retiro de planeación anual")
    set_store(f"ui_rec_tec_{q_n}_1", "Tableros ONE TRACK, Miro, Power BI")
    df_o4 = pd.DataFrame(columns=cols_out)
    df_o4.loc[1] = ["Presupuestos", "U", "NO", 4.0, 4.0, 0.0]
    set_store(f"df_outputs_{q_n}_1", update_avance_resultados(df_o4))
    df_t4 = pd.DataFrame(columns=cols_t)
    df_t4.loc[1] = ["1.", "Revisión", "Carlos", date(2026, 10, 5), date(2026, 10, 25), True, ""]
    df_t4.loc[2] = ["2.", "Metas", "Ana", date(2026, 11, 1), date(2026, 11, 20), False, ""]
    df_t4.loc[3] = ["3.", "Presentación", "Juan", date(2026, 12, 1), date(2026, 12, 15), False, ""]
    set_store(f"df_tareas_{q_n}_1", update_estatus_tareas(df_t4))

def ejecutar_dummy_callback():
    for key in list(st.session_state.keys()):
        if key.startswith("editor_") or key.startswith("ui_") or key.startswith("live_") or key.startswith("cfg_"):
            del st.session_state[key]
    generar_dummy_onetest()
    guardar_en_bd()
    set_store("datos_cargados", False)

# --- CARGA INICIAL DESDE SUPABASE ---
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
        df_o.index = df_o.index + 1
        set_store(f"df_outputs_{q_name}_{i}", df_o)
        
    if f"df_tareas_{q_name}_{i}" not in st.session_state.perm_store:
        df_t = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado", "Estatus"])
        df_t.index = df_t.index + 1
        set_store(f"df_tareas_{q_name}_{i}", df_t)

def cargar_datos():
    if get_store("datos_cargados", False): return
    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{token}'", ttl=0)
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{token}'", ttl=0)
        df_outputs_db = conn.query(f"SELECT * FROM iniciativas_outputs WHERE onetrack_id = '{token}'", ttl=0)
        df_tareas = conn.query(f"SELECT * FROM iniciativas_tareas WHERE onetrack_id = '{token}'", ttl=0)
    except Exception:
        df_kpis, df_okrs, df_outputs_db, df_tareas = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    es_nuevo = df_kpis.empty

    for q_name in trimestres.keys():
        if not df_okrs.empty and 'OKR_ID' in df_okrs.columns:
            q_okrs = df_okrs[df_okrs['Trimestre_ID'] == q_name]
            max_id = q_okrs["OKR_ID"].max() if not q_okrs.empty else 1
            set_store(f"num_iniciativas_{q_name}", int(max_id) if pd.notna(max_id) else 1)
        else:
            set_store(f"num_iniciativas_{q_name}", 1)

    set_store("ui_p_kpis", float(df_kpis.iloc[0].get("Peso_Global_KPI", 50.0)) if not es_nuevo else 50.0)
    set_store("ui_p_okrs", float(df_kpis.iloc[0].get("Peso_Global_OKR", 50.0)) if not es_nuevo else 50.0)
    set_store("cfg_corte_rojo", float(df_kpis.iloc[0].get("U_Amarillo", 79.0)) if not es_nuevo else 79.0)
    set_store("cfg_corte_amarillo", float(df_kpis.iloc[0].get("U_Verde", 89.0)) if not es_nuevo else 89.0)
    set_store("cfg_corte_verde", float(df_kpis.iloc[0].get("U_SVerde", 100.0)) if not es_nuevo else 100.0)
    
    set_store("ui_empresa", str(df_kpis.iloc[0].get("Empresa", "")) if not es_nuevo else st.session_state.user_info.get("empresa", ""))
    set_store("ui_dueno", str(df_kpis.iloc[0].get("Dueno", "")) if not es_nuevo else st.session_state.user_info.get("nombre", ""))
    set_store("ui_puesto", str(df_kpis.iloc[0].get("Puesto", "")) if not es_nuevo else st.session_state.user_info.get("puesto", ""))

    cols_out = ["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance %"]
    cols_t = ["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado", "Estatus"]

    c_r = float(get_store("cfg_corte_rojo", 79.0))
    c_a = float(get_store("cfg_corte_amarillo", 89.0))
    c_v = float(get_store("cfg_corte_verde", 100.0))

    for q_name, meses in trimestres.items():
        cols_kpi = ["Indicadores Clave de Desempeño (KPIs)", "Tipo", "Meta", "UM", "< Mejor", "Peso %"]
        for m in meses: cols_kpi.extend([f"{m} Prog", f"{m} Real", f"{m} Semáforo"])
        df_k = pd.DataFrame(columns=cols_kpi)

        if not es_nuevo:
            unique_kpis = df_kpis.drop_duplicates(subset=["KPI_Nombre"])
            for _, row in unique_kpis.iterrows():
                new_row = [str(row.get("KPI_Nombre", "")), str(row.get("Tipo", "Promedio")), float(row.get("Meta", 0.0) or 0.0), str(row.get("UM", "U")), str(row.get("< Mejor", "NO")), float(row.get("Peso_%", 20.0) or 0.0)]
                for m in meses:
                    new_row.extend([float(row.get(f"{m}_P", 0.0) or 0.0), float(row.get(f"{m}_R", 0.0) or 0.0), "⚪"])
                df_k.loc[len(df_k) + 1] = new_row
            df_k = calcular_sem_kpis(df_k, meses, c_r, c_a, c_v)
        else:
            row_empty = ["", "Promedio", 0.0, "U", "NO", 0.0]
            for _ in meses: row_empty.extend([0.0, 0.0, "⚪"])
            df_k.loc[1] = row_empty
        
        set_store(f"df_kpi_{q_name}", df_k)

        num_i = int(get_store(f"num_iniciativas_{q_name}", 1))
        for i in range(1, num_i + 1):
            init_okr_structure(q_name, i)

            if not df_okrs.empty and 'OKR_ID' in df_okrs.columns:
                match_okr = df_okrs[(df_okrs['Trimestre_ID'] == q_name) & (pd.to_numeric(df_okrs['OKR_ID']) == i)]
                if not match_okr.empty:
                    row_o = match_okr.iloc[0]
                    set_store(f"ui_nom_{q_name}_{i}", str(row_o.get("OKR_Nombre", "")))
                    set_store(f"ui_obj_{q_name}_{i}", str(row_o.get("Objetivo", "")))
                    set_store(f"ui_peso_{q_name}_{i}", float(row_o.get("Peso_%", 20.0) or 20.0))
                    set_store(f"ui_rec_talento_{q_name}_{i}", str(row_o.get("Recurso_Talento", "") if 'Recurso_Talento' in row_o else ""))
                    set_store(f"ui_rec_presupuesto_{q_name}_{i}", str(row_o.get("Recurso_Presupuesto", "") if 'Recurso_Presupuesto' in row_o else ""))
                    set_store(f"ui_rec_infra_{q_name}_{i}", str(row_o.get("Recurso_Infraestructura", "") if 'Recurso_Infraestructura' in row_o else ""))
                    set_store(f"ui_rec_tec_{q_name}_{i}", str(row_o.get("Recurso_Tecnologia", "") if 'Recurso_Tecnologia' in row_o else ""))

            if not df_outputs_db.empty and 'Iniciativa_ID' in df_outputs_db.columns:
                out_okr = df_outputs_db[(pd.to_numeric(df_outputs_db['Iniciativa_ID']) == i) & (df_outputs_db['Trimestre'] == q_name)]
                if not out_okr.empty:
                    df_o = out_okr[["Nombre", "UM", "< Mejor", "Meta", "Real", "Avance"]].rename(columns={"Avance": "Avance %"}).reset_index(drop=True)
                    df_o.index = df_o.index + 1
                    set_store(f"df_outputs_{q_name}_{i}", update_avance_resultados(df_o))

            if not df_tareas.empty and 'Iniciativa_ID' in df_tareas.columns and 'Trimestre' in df_tareas.columns:
                tar_okr = df_tareas[(pd.to_numeric(df_tareas['Iniciativa_ID']) == i) & (df_tareas['Trimestre'] == q_name)]
                if not tar_okr.empty:
                    df_t = tar_okr[["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]].reset_index(drop=True)
                    df_t["Completado"] = df_t["Completado"].astype(bool)
                    df_t["Inicio"] = pd.to_datetime(df_t["Inicio"]).dt.date
                    df_t["Fin"] = pd.to_datetime(df_t["Fin"]).dt.date
                    df_t.index = df_t.index + 1
                    set_store(f"df_tareas_{q_name}_{i}", update_estatus_tareas(df_t))

    set_store("datos_cargados", True)

# --- GUARDADO EN SUPABASE ---
def guardar_en_bd():
    commit_live_edits()
    kpis_data, okrs_data, tareas_data, outputs_data = [], [], [], []
    
    peso_k = float(get_store("ui_p_kpis", 50.0))
    peso_o = float(get_store("ui_p_okrs", 50.0))
    c_rojo = float(get_store("cfg_corte_rojo", 79.0))
    c_amarillo = float(get_store("cfg_corte_amarillo", 89.0))
    c_verde = float(get_store("cfg_corte_verde", 100.0))
    emp = str(get_store("ui_empresa", ""))
    due = str(get_store("ui_dueno", ""))
    pue = str(get_store("ui_puesto", ""))
    logo_c = st.session_state.user_info.get("logo_url", DEFAULT_LOGO_CLIENTE)
    if not logo_c: logo_c = DEFAULT_LOGO_CLIENTE

    df_kpi_master = get_store("df_kpi_Q1", pd.DataFrame())
    if not df_kpi_master.empty:
        for _, r in df_kpi_master.iterrows():
            k_nom = str(r.get("Indicadores Clave de Desempeño (KPIs)", "")).strip()
            if k_nom:
                row = {
                    "onetrack_id": token, "Empresa": emp, "Puesto": pue, "Dueno": due, "Logo_Cliente": logo_c,
                    "KPI_Nombre": k_nom, "Tipo": r.get("Tipo", "Promedio"), "Meta": float(r.get("Meta", 0.0) or 0.0),
                    "UM": str(r.get("UM", "U")), "< Mejor": str(r.get("< Mejor", "NO")), "Peso_%": float(r.get("Peso %", 0.0) or 0.0),
                    "Peso_Global_KPI": peso_k, "Peso_Global_OKR": peso_o, "U_SVerde": c_verde, "U_Verde": c_amarillo, "U_Amarillo": c_rojo
                }
                for q_n, meses in trimestres.items():
                    df_q = get_store(f"df_kpi_{q_n}", pd.DataFrame())
                    match = df_q[df_q["Indicadores Clave de Desempeño (KPIs)"] == k_nom]
                    if not match.empty:
                        for m in meses:
                            row[f"{m}_P"] = float(match.iloc[0].get(f"{m} Prog", 0.0) or 0.0)
                            row[f"{m}_R"] = float(match.iloc[0].get(f"{m} Real", 0.0) or 0.0)
                    else:
                        for m in meses: row[f"{m}_P"], row[f"{m}_R"] = 0.0, 0.0
                kpis_data.append(row)

    for q_n in trimestres.keys():
        num_i = int(get_store(f"num_iniciativas_{q_n}", 1))
        for i in range(1, num_i + 1):
            o_nom = str(get_store(f"ui_nom_{q_n}_{i}", "")).strip()
            if o_nom:
                df_t_prog = update_estatus_tareas(get_store(f"df_tareas_{q_n}_{i}", pd.DataFrame()))
                tot_t = len(df_t_prog[df_t_prog["Tarea"].str.strip() != ""]) if not df_t_prog.empty else 0
                comp = df_t_prog["Completado"].sum() if tot_t > 0 else 0
                if tot_t == 0: e_calc = "⚪ Sin Tareas"
                elif "🔴 Retrasado" in df_t_prog["Estatus"].values: e_calc = "🔴 Retrasado"
                elif comp == tot_t and tot_t > 0: e_calc = "🟢 Completado"
                else: e_calc = "🟢 En Tiempo"

                okrs_data.append({
                    "onetrack_id": token, "Trimestre_ID": q_n, "OKR_ID": i, "OKR_Nombre": o_nom,
                    "Objetivo": str(get_store(f"ui_obj_{q_n}_{i}", "")), "Peso_%": float(get_store(f"ui_peso_{q_n}_{i}", 20.0) or 20.0),
                    "Estatus_Salud": e_calc,
                    "Recurso_Talento": str(get_store(f"ui_rec_talento_{q_n}_{i}", "")),
                    "Recurso_Presupuesto": str(get_store(f"ui_rec_presupuesto_{q_n}_{i}", "")),
                    "Recurso_Infraestructura": str(get_store(f"ui_rec_infra_{q_n}_{i}", "")),
                    "Recurso_Tecnologia": str(get_store(f"ui_rec_tec_{q_n}_{i}", ""))
                })

                df_o = update_avance_resultados(get_store(f"df_outputs_{q_n}_{i}", pd.DataFrame()))
                if not df_o.empty:
                    for _, o_row in df_o.iterrows():
                        if str(o_row.get("Nombre", "")).strip() != "":
                            outputs_data.append({
                                "onetrack_id": token, "Iniciativa_ID": i, "Trimestre": q_n,
                                "Nombre": str(o_row.get("Nombre", "")), "UM": str(o_row.get("UM", "U")),
                                "< Mejor": str(o_row.get("< Mejor", "NO")), "Meta": float(o_row.get("Meta", 0.0) or 0.0),
                                "Real": float(o_row.get("Real", 0.0) or 0.0), "Avance": float(o_row.get("Avance %", 0.0) or 0.0)
                            })

                if not df_t_prog.empty:
                    for _, t_row in df_t_prog.iterrows():
                        if str(t_row.get("Tarea", "")).strip() != "":
                            tareas_data.append({
                                "onetrack_id": token, "Iniciativa_ID": i, "Trimestre": q_n,
                                "Jerarquia": str(t_row.get("Jerarquia", "")), "Tarea": str(t_row.get("Tarea", "")),
                                "Responsable": str(t_row.get("Responsable", "")), "Inicio": t_row.get("Inicio"),
                                "Fin": t_row.get("Fin"), "Completado": bool(t_row.get("Completado", False))
                            })

    try:
        with conn.engine.begin() as transaction:
            transaction.execute(text("DELETE FROM kpis WHERE onetrack_id = :token"), {"token": token})
            transaction.execute(text("DELETE FROM okrs_general WHERE onetrack_id = :token"), {"token": token})
            transaction.execute(text("DELETE FROM iniciativas_outputs WHERE onetrack_id = :token"), {"token": token})
            transaction.execute(text("DELETE FROM iniciativas_tareas WHERE onetrack_id = :token"), {"token": token})
    except Exception: pass

    cols_k_all = ["onetrack_id", "Empresa", "Puesto", "Dueno", "Logo_Cliente", "KPI_Nombre", "Tipo", "Meta", "UM", "< Mejor", "Peso_%", "Peso_Global_KPI", "Peso_Global_OKR", "U_SVerde", "U_Verde", "U_Amarillo"]
    for q_n, meses in trimestres.items():
        for m in meses: cols_k_all.extend([f"{m}_P", f"{m}_R"])

    pd.DataFrame(kpis_data, columns=cols_k_all).to_sql("kpis", con=conn.engine, if_exists='append', index=False)
    pd.DataFrame(okrs_data, columns=["onetrack_id", "Trimestre_ID", "OKR_ID", "OKR_Nombre", "Objetivo", "Peso_%", "Estatus_Salud", "Recurso_Talento", "Recurso_Presupuesto", "Recurso_Infraestructura", "Recurso_Tecnologia"]).to_sql("okrs_general", con=conn.engine, if_exists='append', index=False)
    pd.DataFrame(outputs_data, columns=["onetrack_id", "Iniciativa_ID", "Trimestre", "Nombre", "UM", "< Mejor", "Meta", "Real", "Avance"]).to_sql("iniciativas_outputs", con=conn.engine, if_exists='append', index=False)
    pd.DataFrame(tareas_data, columns=["onetrack_id", "Iniciativa_ID", "Trimestre", "Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]).to_sql("iniciativas_tareas", con=conn.engine, if_exists='append', index=False)

# --- INICIO DE SESIÓN ---
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
        st.rerun()

# --- HEADER PRINCIPAL ---
col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
with col2: 
    logo_c = st.session_state.user_info.get("logo_url", "")
    if not logo_c or str(logo_c).strip() == "": logo_c = DEFAULT_LOGO_CLIENTE
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

# --- RUTEO DE VISTAS ---
if st.session_state.vista_actual == "Guía de Uso":
    st.markdown("<div class='section-title'>📖 Guía de Uso Integral - ONE TRACK</div>", unsafe_allow_html=True)
    st.markdown("""
    Bienvenido al manual operativo de **ONE TRACK**. Esta herramienta estratégica está diseñada para cerrar la brecha entre la formulación de objetivos ejecutivos y su ejecución táctica en el día a día.
    """)
    
    st.markdown("<div class='sub-section-title'>1. Filosofía ONE TRACK y Estructura Global</div>", unsafe_allow_html=True)
    st.write("""
    ONE TRACK divide la gestión estratégica en dos grandes ejes balanceados:
    * **Indicadores Clave de Desempeño (KPIs):** Miden el resultado final o desempeño cuantitativo del negocio (ventas, satisfacción, rentabilidad).
    * **Iniciativas Estratégicas:** Miden la ejecución estructurada y los proyectos clave que mueven la aguja de dichos resultados.
    * **Ponderación Global:** Permite asignar qué porcentaje del éxito general corresponde a los resultados numéricos de negocio y qué porcentaje a la ejecución disciplinada de proyectos.
    """)
    
    st.markdown("<div class='sub-section-title'>2. Indicadores Clave de Desempeño (KPIs)</div>", unsafe_allow_html=True)
    st.write("""
    En cada trimestre (Q1 a Q4) podrás planificar y registrar el avance de tus métricas:
    * **Programado - Real - Semáforo:** Cada mes presenta una tríada de columnas. Al ingresar tus valores, la columna semáforo proyecta automáticamente un círculo de color (🔴, 🟡, 🟢) evaluando el nivel de cumplimiento del mes según tus intervalos configurados.
    * **Tipo de Cálculo:** 
        - *Acumulado:* Para métricas que suman mes a mes (e.g. Ventas, Nuevos Clientes).
        - *Promedio:* Para porcentajes o calificaciones de servicio (e.g. CSAT, Margen %).
        - *Valor Final:* Para metas puntuales de fin de ciclo.
    * **< Mejor (Menor es Mejor):** Si seleccionas **SI**, la fórmula premia valores bajos (útil para rotación de personal, mermas o costos).
    """)
    render_gif_placeholder(GIF_KPIS, "[ 🎥 ESPACIO PARA GIF: Carga y semaforización de KPIs mensuales ]")
    
    st.markdown("<div class='sub-section-title'>3. Iniciativas Estratégicas y Resultados</div>", unsafe_allow_html=True)
    st.write("""
    Las iniciativas agrupan las grandes apuestas trimestrales:
    * **Ponderación (%):** Define el peso de cada iniciativa sobre el total de iniciativas del trimestre.
    * **Resultados de la Iniciativa:** Matriz donde desglosas los entregables cuantitativos de la iniciativa (Nombre, Unidad de Medida, Sentido menor mejor, Meta y Real). El sistema calcula en vivo el **Avance %** exacto de cada resultado y promedia el cumplimiento global.
    * **Estatus Actual:** El semáforo general de la iniciativa evalúa automáticamente el estatus del cronograma de tareas (detectando si existen actividades en riesgo o retraso).
    """)
    render_gif_placeholder(GIF_RESULTADOS, "[ 🎥 ESPACIO PARA GIF: Creación de resultados y cálculo de avance ]")
    
    st.markdown("<div class='sub-section-title'>4. Plan de Acción y Cronograma Gantt</div>", unsafe_allow_html=True)
    st.write("""
    El motor de ejecución táctica:
    * **Jerarquía Numérica:** Asigna numeraciones (e.g. `1.`, `1.1`, `1.2`) para que el cronograma ordene y agrupe las fases visualmente de forma automática.
    * **Estatus Automático de Tarea:** Compara en tiempo real la fecha límite (`Fin`) contra la fecha del día de hoy. Si la actividad no está completada y ya venció, se marca como 🔴 Retrasado de forma inmediata.
    * **Duración de la Iniciativa:** El sistema detecta la fecha de inicio más temprana y la fecha fin más tardía del plan para mostrar el rango total de ejecución.
    """)
    render_gif_placeholder(GIF_GANTT, "[ 🎥 ESPACIO PARA GIF: Diagrama Gantt y estatus automático de tareas ]")
    
    st.markdown("<div class='sub-section-title'>5. Asignación y Control de Recursos</div>", unsafe_allow_html=True)
    st.write("""
    Cada iniciativa cuenta con una cuadrícula 2×2 para delimitar los recursos requeridos:
    * **Talento:** Líderes de proyecto, personal interno y contrataciones clave requeridas.
    * **Presupuesto $:** Fondos financieros específicos aprobados para licencias, consultorías o pauta.
    * **Infraestructura:** Espacios físicos, bodegas, líneas telefónicas o ambientes de servidores.
    * **Tecnología:** Herramientas de software, licencias, sistemas CRM o APIs indispensables.
    """)
    render_gif_placeholder(GIF_RECURSOS, "[ 🎥 ESPACIO PARA GIF: Panel 2x2 de Recursos por iniciativa ]")
    
    st.markdown("<div class='sub-section-title'>6. Configuración de Semáforos e Intervalos</div>", unsafe_allow_html=True)
    st.write("""
    Personaliza la escala de exigencia institucional sin solapamiento de porcentajes:
    * **Rojo (Bajo):** Del 0% al corte inferior establecido.
    * **Amarillo (Medio):** Intervalo de alerta intermedia.
    * **Verde (Meta):** Intervalo de meta aprobada institucional.
    * **Súper Verde (Sobresaliente):** Rendimientos superiores a la meta fijada.
    """)
    render_gif_placeholder(GIF_SEMAFOROS, "[ 🎥 ESPACIO PARA GIF: Configuración de intervalos de semáforo ]")
    
    st.markdown("<div class='sub-section-title'>7. Resumen Anual y Análisis de Tendencias</div>", unsafe_allow_html=True)
    st.write("""
    Vista gerencial consolidada:
    * Muestra la tabla anual con el porcentaje y el círculo de desempeño de cada métrica a lo largo de los 12 meses.
    * Gráfico de líneas mensual para contrastar el comportamiento de los KPIs de negocio contra el ritmo de ejecución de las iniciativas.
    """)

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

    c_rojo = float(get_store("cfg_corte_rojo", 79.0))
    c_amarillo = float(get_store("cfg_corte_amarillo", 89.0))
    c_verde = float(get_store("cfg_corte_verde", 100.0))

    if st.session_state.vista_actual in trimestres.keys():
        q_name = st.session_state.vista_actual
        meses_q = trimestres[q_name]
        
        st.markdown(f"<div class='section-title'>Indicadores Clave de Desempeño (KPIs) - {q_name}</div>", unsafe_allow_html=True)
        
        df_kpi_in = get_store(f"df_kpi_{q_name}", pd.DataFrame())
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
        num_i = int(get_store(f"num_iniciativas_{q_name}", 1))
        
        for i in range(1, num_i + 1):
            st.markdown("<div class='iniciativa-box'>", unsafe_allow_html=True)
            
            df_out_in = get_store(f"df_outputs_{q_name}_{i}", pd.DataFrame())
            df_tar_in = get_store(f"df_tareas_{q_name}_{i}", pd.DataFrame())

            df_out_calc = update_avance_resultados(st.session_state.get(f"live_out_{q_name}_{i}", df_out_in))
            valid_o = df_out_calc[df_out_calc["Nombre"].str.strip() != ""] if not df_out_calc.empty else pd.DataFrame()
            avance_ini = valid_o["Avance %"].mean() if not valid_o.empty else 0.0

            df_tar_calc = update_estatus_tareas(st.session_state.get(f"live_tar_{q_name}_{i}", df_tar_in))
            tot_t = len(df_tar_calc[df_tar_calc["Tarea"].str.strip() != ""]) if not df_tar_calc.empty else 0
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

    # --- CÁLCULOS ANUALES Y TARJETAS FRONTALES ---
    def get_mes_cump(m, q_name):
        t_peso_k, acum_k = 0.0, 0.0
        df_kpi = st.session_state.get(f"live_kpi_{q_name}", get_store(f"df_kpi_{q_name}", pd.DataFrame()))
        if not df_kpi.empty:
            for i in range(len(df_kpi)):
                if str(df_kpi["Indicadores Clave de Desempeño (KPIs)"].iloc[i]).strip():
                    p = float(df_kpi[f"{m} Prog"].iloc[i] or 0.0)
                    r = float(df_kpi[f"{m} Real"].iloc[i] or 0.0)
                    peso = float(df_kpi["Peso %"].iloc[i] or 0.0)
                    cump = calc_cump(p, r, str(df_kpi["< Mejor"].iloc[i]))
                    acum_k += cump * (peso / 100.0); t_peso_k += peso
        res_k = (acum_k / (t_peso_k / 100.0)) if t_peso_k > 0 else 0.0

        t_peso_o, acum_o = 0.0, 0.0
        num_i = int(get_store(f"num_iniciativas_{q_name}", 1))
        for i in range(1, num_i + 1):
            if str(get_store(f"ui_nom_{q_name}_{i}", "")).strip():
                peso_o = float(get_store(f"ui_peso_{q_name}_{i}", 0.0))
                df_o = st.session_state.get(f"live_out_{q_name}_{i}", get_store(f"df_outputs_{q_name}_{i}", pd.DataFrame()))
                df_o = update_avance_resultados(df_o)
                cump_resultados = 0.0
                if not df_o.empty:
                    valid_o = df_o[df_o["Nombre"].str.strip() != ""]
                    if not valid_o.empty: cump_resultados = valid_o["Avance %"].mean()
                acum_o += cump_resultados * (peso_o / 100.0); t_peso_o += peso_o
        res_o = (acum_o / (t_peso_o / 100.0)) if t_peso_o > 0 else 0.0

        t_peso_tot = float(get_store("ui_p_kpis", 50.0)) + float(get_store("ui_p_okrs", 50.0))
        res_tot = ((res_k * (float(get_store("ui_p_kpis", 50.0)) / 100.0)) + (res_o * (float(get_store("ui_p_okrs", 50.0)) / 100.0))) / (t_peso_tot / 100.0) if t_peso_tot > 0 else 0.0
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

    if st.session_state.vista_actual in trimestres.keys():
        q_sel = st.session_state.vista_actual
        df_q = df_anual[df_anual["Trimestre"] == q_sel]
        res_k_total = df_q["Indicadores Clave de Desempeño (KPIs)"].mean() * 100
        res_o_total = df_q["Iniciativas Estratégicas"].mean() * 100
        res_tot_final = df_q["Integrado"].mean() * 100
    else:
        res_k_total = df_anual["Indicadores Clave de Desempeño (KPIs)"].mean() * 100
        res_o_total = df_anual["Iniciativas Estratégicas"].mean() * 100
        res_tot_final = df_anual["Integrado"].mean() * 100

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
        
        # Generar tabla anual con círculos después de cada métrica
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
    
    c_r = float(get_store("cfg_corte_rojo", 79.0))
    c_a = float(get_store("cfg_corte_amarillo", 89.0))
    c_v = float(get_store("cfg_corte_verde", 100.0))

    col_int1, col_int2 = st.columns([1.2, 1])
    with col_int1:
        # Visualización de Intervalos Continuos
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
