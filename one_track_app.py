import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from sqlalchemy import text

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE TRACK - Workspace", layout="wide", initial_sidebar_state="expanded")

# --- CSS MINIMALISTA, ELEGANTE Y AZUL/BLANCO/GRIS ---
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
    .sub-section-title { font-size: 15px; font-weight: 900; color: #4b5563; margin-top: 15px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;}
    .custom-label { font-size: 13px; font-weight: 900; color: #002060; text-transform: uppercase; margin-bottom: 2px; margin-top: 10px; letter-spacing: 0.5px; }
    
    .title-placeholder { display: flex; align-items: center; justify-content: center; height: 160px; background-color: transparent; border: none; box-shadow: none; }
    .img-placeholder { background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; height: 160px; display: flex; align-items: center; justify-content: center; color: #6b7280; font-weight: bold; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);}
    
    /* Tarjetas Blancas (Cards) */
    .summary-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #002060; height: 100%; }
    .summary-title { font-size: 14px; color: #4b5563; font-weight: 900; margin-bottom: 5px; text-transform: uppercase;}
    .summary-value { font-size: 28px; color: #002060; font-weight: 900; }
    .iniciativa-box { background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
    .iniciativa-header { font-size: 20px; font-weight: 900; color: #ffffff; background-color: #002060; padding: 10px 20px; border-radius: 8px; display: inline-block;}
    
    /* Ajustes Estéticos para las Tablas (Anti-plano) */
    div[data-testid="stDataFrame"] > div { border: none; border-radius: 12px; overflow: hidden; box-shadow: 0 6px 12px rgba(0,0,0,0.08); background-color: #ffffff; padding: 4px; border: 1px solid #e2e8f0; }
    div[data-testid="stDataFrame"] table th { background-color: #002060 !important; color: #ffffff !important; font-size: 15px !important; font-weight: 900 !important; text-transform: uppercase; text-align: center !important;}
    
    .footer-box { border: 1px solid #d1d5db; padding: 6px 15px; font-weight: 900; border-radius: 6px; min-width: 90px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
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

# --- FUNCION DUMMY DE EJECUCION MANUAL ---
def generar_dummy_onetest():
    mult_q = {"Q1": 0.85, "Q2": 0.90, "Q3": 0.98, "Q4": 1.05}
    for q_name, meses in trimestres.items():
        df_k = st.session_state.get(f"df_kpi_{q_name}", pd.DataFrame(columns=["KPIs Indicadores", "Tipo", "Meta", "UM", "< Mejor", "Peso %"] + [f"{m} Prog" for m in meses] + [f"{m} Real" for m in meses]))
        df_k.loc[0] = ["Ventas Mensuales", "Promedio", 500000.0, "$", "NO", 50.0] + [100000.0, 100000.0 * mult_q[q_name]] * 3
        df_k.loc[1] = ["Satisfacción de Clientes", "Promedio", 95.0, "%", "NO", 50.0] + [95.0, 95.0 * mult_q[q_name]] * 3
        st.session_state[f"df_kpi_{q_name}"] = df_k
        
        st.session_state[f"okr_{q_name}_1_nom"] = "Expansión de Mercado Norte"
        st.session_state[f"okr_{q_name}_1_obj"] = "Conquistar 3 nuevos estados mediante campañas digitales."
        st.session_state[f"okr_{q_name}_1_peso"] = 100.0
        st.session_state[f"okr_{q_name}_1_salud"] = "🟢 En Tiempo"
        
        df_c = st.session_state.get(f"df_crit_{q_name}_1", pd.DataFrame())
        if df_c.empty:
            cols_c = ["Criterio", "Tipo", "Meta", "UM", "< Mejor", "%"]
            for m in meses: cols_c.extend([f"{m} Prog", f"{m} Real"])
            df_c = pd.DataFrame(columns=cols_c)
        df_c.loc[0] = ["Nuevas Cuentas (B2B)", "Acumulado", 50.0, "U", "NO", 100.0] + [10.0, 10.0 * mult_q[q_name]] * 3
        st.session_state[f"df_crit_{q_name}_1"] = df_c
        
        df_t = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"])
        mes_num = list(trimestres.keys()).index(q_name) * 3 + 1
        end_mes = mes_num + 1 if mes_num + 1 <= 12 else 12
        df_t.loc[0] = ["1.", "Diseño de Estrategia", "Ana", date(2026, mes_num, 5), date(2026, mes_num, 20), True]
        df_t.loc[1] = ["1.1", "Ejecución de Campaña", "Luis", date(2026, mes_num, 22), date(2026, end_mes, 15), False]
        st.session_state[f"df_tareas_{q_name}_1"] = df_t

if 'user_info' not in st.session_state or st.session_state.user_info is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"<div style='text-align:center; margin-bottom:40px;'><img src='{DEFAULT_LOGO_ONE_TRACK}' style='max-height: 240px; object-fit: contain;'></div>", unsafe_allow_html=True)
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
    v_sob, v_meta, v_med = float(st.session_state.get("_v_sob", 100.0)), float(st.session_state.get("_v_meta", 90.0)), float(st.session_state.get("_v_med", 89.0))
    for m in meses:
        total_peso, acumulado = 0.0, 0.0
        for i in range(len(df)):
            if str(df["KPIs Indicadores"].iloc[i]).strip() != "":
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
    chart = alt.Chart(df_plot).mark_bar(cornerRadius=4, height=18).encode(
        x=alt.X('Inicio', title='', axis=alt.Axis(format="%d %b", grid=True, gridColor="#f0f2f6")), x2='Fin',
        y=alt.Y('Nombre', sort=None, title='', axis=alt.Axis(labelFontWeight="bold")),
        color=alt.Color('Estado', scale=alt.Scale(domain=['Realizado', 'Pendiente'], range=['#002060', '#a0aabf']), legend=alt.Legend(title="Estado", orient="bottom"))
    ).properties(height=max(150, len(df_plot)*35))
    st.altair_chart(chart, use_container_width=True)

# --- CARGA DE DATOS ---
def init_okr_structure(q_name, i, meses):
    if f"okr_{q_name}_{i}_nom" not in st.session_state:
        st.session_state[f"okr_{q_name}_{i}_nom"] = ""
        st.session_state[f"okr_{q_name}_{i}_obj"] = ""
        st.session_state[f"okr_{q_name}_{i}_peso"] = 20.0
        st.session_state[f"okr_{q_name}_{i}_salud"] = "🟢 En Tiempo"
        cols_c = ["Criterio", "Tipo", "Meta", "UM", "< Mejor", "%"]
        for m in meses: cols_c.extend([f"{m} Prog", f"{m} Real"])
        df_c = pd.DataFrame(columns=cols_c)
        for _ in range(3): df_c.loc[len(df_c)] = ["", "Promedio", 0.0, "U", "NO", 33.3] + [0.0]*(len(meses)*2)
        st.session_state[f"df_crit_{q_name}_{i}"] = df_c
        st.session_state[f"df_tareas_{q_name}_{i}"] = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"])

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
    st.session_state["_p_kpis"] = float(df_kpis.iloc[0].get("Peso_Global_KPI", 50.0)) if not es_nuevo else 50.0
    st.session_state["_p_okrs"] = float(df_kpis.iloc[0].get("Peso_Global_OKR", 50.0)) if not es_nuevo else 50.0
    st.session_state["_v_sob"] = float(df_kpis.iloc[0].get("U_SVerde", 100.0)) if not es_nuevo else 100.0
    st.session_state["_v_meta"] = float(df_kpis.iloc[0].get("U_Verde", 90.0)) if not es_nuevo else 90.0
    st.session_state["_v_med"] = float(df_kpis.iloc[0].get("U_Amarillo", 80.0)) if not es_nuevo else 80.0
    
    st.session_state["empresa_input"] = str(df_kpis.iloc[0].get("Empresa", "")) if not es_nuevo else st.session_state.user_info.get("empresa", "")
    st.session_state["dueno_input"] = str(df_kpis.iloc[0].get("Dueno", "")) if not es_nuevo else st.session_state.user_info.get("nombre", "")
    st.session_state["puesto_input"] = str(df_kpis.iloc[0].get("Puesto", "")) if not es_nuevo else st.session_state.user_info.get("puesto", "")
    st.session_state["logo_input"] = str(df_kpis.iloc[0].get("Logo_Cliente", "")) if not es_nuevo else st.session_state.user_info.get("logo_url", "")

    for q_name, meses in trimestres.items():
        cols_kpi = ["KPIs Indicadores", "Tipo", "Meta", "UM", "< Mejor", "Peso %"]
        for m in meses: cols_kpi.extend([f"{m} Prog", f"{m} Real"])
        df_k = pd.DataFrame(columns=cols_kpi)

        if not es_nuevo:
            for i in range(len(df_kpis)):
                row = df_kpis.iloc[i]
                new_row = [str(row.get("KPI_Nombre", "")), str(row.get("Tipo", "Promedio")), float(row.get("Meta", 0.0)), str(row.get("UM", "U")), str(row.get("< Mejor", "NO")), float(row.get("Peso_%", 20.0))]
                for m in meses: new_row.extend([float(row.get(f"{m}_P", 0.0)), float(row.get(f"{m}_R", 0.0))])
                df_k.loc[len(df_k)] = new_row
        else:
            df_k.loc[0] = ["", "Promedio", 0.0, "U", "NO", 0.0] + [0.0]*(len(meses)*2)
        
        st.session_state[f"df_kpi_{q_name}"] = df_k

        for i in range(1, 6):
            init_okr_structure(q_name, i, meses)
            if not es_nuevo and (i-1) < len(df_okrs):
                row_o = df_okrs.iloc[i-1]
                st.session_state[f"okr_{q_name}_{i}_nom"] = str(row_o.get("OKR_Nombre", ""))
                st.session_state[f"okr_{q_name}_{i}_obj"] = str(row_o.get("Objetivo", ""))
                st.session_state[f"okr_{q_name}_{i}_peso"] = float(row_o.get("Peso_%", 20.0))
                st.session_state[f"okr_{q_name}_{i}_salud"] = str(row_o.get("Estatus_Salud", "🟢 En Tiempo"))
            
            if not df_crit.empty:
                crit_okr = df_crit[(df_crit['OKR_ID'] == i)].reset_index(drop=True)
                if len(crit_okr) > 0:
                    df_c_temp = st.session_state[f"df_crit_{q_name}_{i}"]
                    for c_idx in range(len(crit_okr)):
                        if c_idx >= len(df_c_temp): df_c_temp.loc[len(df_c_temp)] = ["", "Promedio", 0.0, "U", "NO", 0.0] + [0.0]*(len(meses)*2)
                        r_c = crit_okr.iloc[c_idx]
                        df_c_temp.at[c_idx, "Criterio"] = str(r_c.get("Criterio_Nombre", ""))
                        df_c_temp.at[c_idx, "Meta"] = float(r_c.get("Meta", 0.0))
                        df_c_temp.at[c_idx, "< Mejor"] = str(r_c.get("< Mejor", "NO"))
                        df_c_temp.at[c_idx, "%"] = float(r_c.get("Peso_%", 33.3))
                        for m in meses:
                            df_c_temp.at[c_idx, f"{m} Prog"] = float(r_c.get(f"{m}_P", 0.0))
                            df_c_temp.at[c_idx, f"{m} Real"] = float(r_c.get(f"{m}_R", 0.0))
                    st.session_state[f"df_crit_{q_name}_{i}"] = df_c_temp

            if not df_tareas.empty:
                tar_okr = df_tareas[(df_tareas['Iniciativa_ID'] == i) & (df_tareas['Trimestre'] == q_name)]
                if not tar_okr.empty:
                    df_t = tar_okr[["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]].reset_index(drop=True)
                    df_t["Completado"] = df_t["Completado"].astype(bool)
                    df_t["Inicio"] = pd.to_datetime(df_t["Inicio"]).dt.date
                    df_t["Fin"] = pd.to_datetime(df_t["Fin"]).dt.date
                    st.session_state[f"df_tareas_{q_name}_{i}"] = df_t

    st.session_state.datos_cargados = True

cargar_datos()

# --- OPTIMIZACION DE GUARDADO RÁPIDO CON ESQUEMA FUERTE ---
def guardar_en_bd():
    kpis_data, okrs_data, crit_data, tareas_data = [], [], [], []
    peso_k, peso_o = float(st.session_state.get("_p_kpis", 50.0)), float(st.session_state.get("_p_okrs", 50.0))
    v_sob, v_meta, v_med = float(st.session_state.get("_v_sob", 100.0)), float(st.session_state.get("_v_meta", 90.0)), float(st.session_state.get("_v_med", 89.0))
    emp, due, pue = st.session_state.get("empresa_input", ""), st.session_state.get("dueno_input", ""), st.session_state.get("puesto_input", "")
    logo_c = st.session_state.get("logo_input", "")

    cols_kpi = ["onetrack_id", "Empresa", "Puesto", "Dueno", "Logo_Cliente", "KPI_Nombre", "Tipo", "Meta", "UM", "< Mejor", "Peso_%", "Peso_Global_KPI", "Peso_Global_OKR", "U_SVerde", "U_Verde", "U_Amarillo"]
    for q_n, meses in trimestres.items():
        for m in meses: cols_kpi.extend([f"{m}_P", f"{m}_R"])
        
    cols_okr = ["onetrack_id", "OKR_ID", "OKR_Nombre", "Objetivo", "Peso_%", "Estatus_Salud"]
    
    cols_crit = ["onetrack_id", "OKR_ID", "Criterio_Nombre", "Tipo", "Meta", "UM", "< Mejor", "Peso_%"]
    for q_n, meses in trimestres.items():
        for m in meses: cols_crit.extend([f"{m}_P", f"{m}_R"])
        
    cols_tareas = ["onetrack_id", "Iniciativa_ID", "Trimestre", "Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]

    df_kpi_master = st.session_state.get("df_kpi_Q1", pd.DataFrame())
    if not df_kpi_master.empty:
        for idx, r in df_kpi_master.iterrows():
            k_nom = str(r.get("KPIs Indicadores", "")).strip()
            if k_nom:
                row = {
                    "onetrack_id": token, "Empresa": emp, "Puesto": pue, "Dueno": due, "Logo_Cliente": logo_c,
                    "KPI_Nombre": k_nom, "Tipo": r["Tipo"], "Meta": r["Meta"],
                    "UM": r["UM"], "< Mejor": r["< Mejor"], "Peso_%": r["Peso %"],
                    "Peso_Global_KPI": peso_k, "Peso_Global_OKR": peso_o, "U_SVerde": v_sob, "U_Verde": v_meta, "U_Amarillo": v_med
                }
                for q_n, meses in trimestres.items():
                    df_q = st.session_state[f"df_kpi_{q_n}"]
                    if idx < len(df_q) and str(df_q["KPIs Indicadores"].iloc[idx]).strip() == k_nom:
                        for m in meses:
                            row[f"{m}_P"] = df_q[f"{m} Prog"].iloc[idx]
                            row[f"{m}_R"] = df_q[f"{m} Real"].iloc[idx]
                    else:
                        matches = df_q[df_q["KPIs Indicadores"] == k_nom]
                        if not matches.empty:
                            for m in meses:
                                row[f"{m}_P"] = matches[f"{m} Prog"].iloc[0]
                                row[f"{m}_R"] = matches[f"{m} Real"].iloc[0]
                        else:
                            for m in meses:
                                row[f"{m}_P"], row[f"{m}_R"] = 0.0, 0.0
                kpis_data.append(row)

    for i in range(1, 6):
        o_nom = st.session_state.get(f"okr_Q1_{i}_nom", "")
        if o_nom:
            okrs_data.append({"onetrack_id": token, "OKR_ID": i, "OKR_Nombre": o_nom, "Objetivo": st.session_state.get(f"okr_Q1_{i}_obj", ""), "Peso_%": float(st.session_state.get(f"okr_Q1_{i}_peso", 20.0)), "Estatus_Salud": st.session_state.get(f"okr_Q1_{i}_salud", "🟢 En Tiempo")})
            
            df_c = st.session_state.get(f"df_crit_Q1_{i}", pd.DataFrame())
            if not df_c.empty:
                for c_idx in range(len(df_c)):
                    c_nom = df_c["Criterio"].iloc[c_idx]
                    if str(c_nom).strip() != "":
                        c_row = {"onetrack_id": token, "OKR_ID": i, "Criterio_Nombre": c_nom, "Tipo": df_c["Tipo"].iloc[c_idx], "Meta": df_c["Meta"].iloc[c_idx], "UM": df_c["UM"].iloc[c_idx], "< Mejor": df_c["< Mejor"].iloc[c_idx], "Peso_%": df_c["%"].iloc[c_idx]}
                        for q_n, meses in trimestres.items():
                            df_cq = st.session_state[f"df_crit_{q_n}_{i}"]
                            if c_idx < len(df_cq):
                                for m in meses:
                                    c_row[f"{m}_P"] = df_cq[f"{m} Prog"].iloc[c_idx]
                                    c_row[f"{m}_R"] = df_cq[f"{m} Real"].iloc[c_idx]
                        crit_data.append(c_row)
                    
            for q_n in trimestres.keys():
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
    st.markdown(f"<div class='img-placeholder'><img src='{DEFAULT_LOGO_ONE}' style='max-height: 80px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)
with c_img2: 
    st.markdown(f"<div class='title-placeholder'><img src='{DEFAULT_LOGO_ONE_TRACK}' style='max-height: 160px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)
with c_img3: 
    logo_c = st.session_state.get("logo_input", "")
    if not logo_c: logo_c = DEFAULT_LOGO_CLIENTE
    st.markdown(f"<div class='img-placeholder'><img src='{logo_c}' style='max-height: 80px; max-width: 100%; object-fit: contain;'></div>", unsafe_allow_html=True)

c_inf1, c_inf2, c_inf3 = st.columns(3)
with c_inf1:
    st.markdown("<div class='custom-label'>EMPRESA</div>", unsafe_allow_html=True)
    v_emp = st.session_state.get("empresa_input", "")
    st.session_state.empresa_input = st.text_input("Empresa", value=v_emp, key="ui_empresa", label_visibility="collapsed")
with c_inf2:
    st.markdown("<div class='custom-label'>NOMBRE (DUEÑO DEL ONE TRACK)</div>", unsafe_allow_html=True)
    v_due = st.session_state.get("dueno_input", "")
    st.session_state.dueno_input = st.text_input("Dueño", value=v_due, key="ui_dueno", label_visibility="collapsed")
with c_inf3:
    st.markdown("<div class='custom-label'>PUESTO</div>", unsafe_allow_html=True)
    v_pue = st.session_state.get("puesto_input", "")
    st.session_state.puesto_input = st.text_input("Puesto", value=v_pue, key="ui_puesto", label_visibility="collapsed")

st.divider()

col_t, col_btn = st.columns([4, 1])
with col_t: st.markdown("<h2 style='color:#002060; font-weight:900; margin:0;'>Tablero de Control</h2>", unsafe_allow_html=True)
with col_btn:
    if st.button("Guardar Cambios", type="primary", use_container_width=True):
        with st.spinner("Sincronizando de forma rápida..."):
            guardar_en_bd()
            st.session_state.datos_cargados = False
        st.success("Guardado exitoso en 1s.")
st.write("")

# TARJETAS FRONTALES PONDERACION Y RESULTADOS
col_w, col_s1, col_s2, col_s3 = st.columns([1.5, 1, 1, 1])
with col_w:
    st.markdown("<div class='summary-card' style='padding:15px;'><p class='summary-title'>Ponderación Global</p>", unsafe_allow_html=True)
    c_kpi, c_okr = st.columns(2)
    with c_kpi:
        st.markdown("<div class='custom-label'>INDICADORES (%)</div>", unsafe_allow_html=True)
        v_pk = float(st.session_state.get("_p_kpis", 50.0))
        st.session_state._p_kpis = st.number_input("Ind", value=v_pk, key="ui_p_kpis", label_visibility="collapsed")
    with c_okr:
        st.markdown("<div class='custom-label'>INICIATIVAS (%)</div>", unsafe_allow_html=True)
        v_po = float(st.session_state.get("_p_okrs", 50.0))
        st.session_state._p_okrs = st.number_input("Ini", value=v_po, key="ui_p_okrs", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
with col_s1: ph_kpi = st.empty()
with col_s2: ph_okr = st.empty()
with col_s3: ph_tot = st.empty()
st.write("")

# --- VISTAS NAVEGABLES ---
if st.session_state.vista_actual in trimestres.keys():
    q_name = st.session_state.vista_actual
    meses_q = trimestres[q_name]
    
    st.markdown(f"<div class='section-title'>KPIs Indicadores - {q_name}</div>", unsafe_allow_html=True)
    render_footer(st.session_state.get(f"df_kpi_{q_name}", pd.DataFrame()), meses_q)
    
    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
    st.session_state[f"df_kpi_{q_name}"] = st.data_editor(
        st.session_state.get(f"df_kpi_{q_name}", pd.DataFrame()),
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
    for i in range(1, 6):
        st.markdown("<div class='iniciativa-box'>", unsafe_allow_html=True)
        
        h_col1, h_col2 = st.columns([1, 3])
        with h_col1: st.markdown(f"<div class='iniciativa-header'>Iniciativa #{i}</div>", unsafe_allow_html=True)
        with h_col2: ph_avance_ini = st.empty()
        
        ch1, ch2, ch3 = st.columns([3, 1, 1])
        with ch1:
            st.markdown("<div class='custom-label'>NOMBRE DE LA INICIATIVA</div>", unsafe_allow_html=True)
            v_nom = st.session_state.get(f"okr_{q_name}_{i}_nom", "")
            n_nom = st.text_input("Nombre", value=v_nom, key=f"ui_nom_{q_name}_{i}", label_visibility="collapsed")
            st.session_state[f"okr_{q_name}_{i}_nom"] = n_nom
        
        with ch2:
            st.markdown("<div class='custom-label'>PONDERACIÓN (%)</div>", unsafe_allow_html=True)
            v_peso = float(st.session_state.get(f"okr_{q_name}_{i}_peso", 20.0))
            n_peso = st.number_input("Peso", value=v_peso, key=f"ui_peso_{q_name}_{i}", label_visibility="collapsed")
            st.session_state[f"okr_{q_name}_{i}_peso"] = n_peso
        
        with ch3:
            opciones_salud = ["🟢 En Tiempo", "🟡 En Riesgo", "🔴 Retrasado"]
            salud_act = st.session_state.get(f"okr_{q_name}_{i}_salud", "🟢 En Tiempo")
            if salud_act not in opciones_salud: salud_act = "🟢 En Tiempo"
            st.markdown("<div class='custom-label'>ESTATUS ACTUAL</div>", unsafe_allow_html=True)
            n_salud = st.selectbox("Salud", options=opciones_salud, index=opciones_salud.index(salud_act), key=f"ui_salud_{q_name}_{i}", label_visibility="collapsed")
            st.session_state[f"okr_{q_name}_{i}_salud"] = n_salud
        
        st.markdown("<div class='custom-label'>OBJETIVO</div>", unsafe_allow_html=True)
        v_obj = st.session_state.get(f"okr_{q_name}_{i}_obj", "")
        n_obj = st.text_area("Obj", value=v_obj, key=f"ui_obj_{q_name}_{i}", height=80, label_visibility="collapsed")
        st.session_state[f"okr_{q_name}_{i}_obj"] = n_obj
        
        st.markdown("<div class='sub-section-title'>Criterios de Éxito (Medición)</div>", unsafe_allow_html=True)
        st.session_state[f"df_crit_{q_name}_{i}"] = st.data_editor(
            st.session_state.get(f"df_crit_{q_name}_{i}", pd.DataFrame()),
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio"]), "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])},
            key=f"ed_crit_{q_name}_{i}"
        )
        
        df_c_prog = st.session_state.get(f"df_crit_{q_name}_{i}", pd.DataFrame())
        acum_ini, tot_peso_ini = 0.0, 0.0
        if not df_c_prog.empty:
            for c_idx in range(len(df_c_prog)):
                if str(df_c_prog["Criterio"].iloc[c_idx]).strip() != "":
                    peso_c = float(df_c_prog["%"].iloc[c_idx] or 0)
                    p_c = sum([float(df_c_prog[f"{m} Prog"].iloc[c_idx] or 0) for m in meses_q])
                    r_c = sum([float(df_c_prog[f"{m} Real"].iloc[c_idx] or 0) for m in meses_q])
                    cump_c = calc_cump(p_c, r_c, str(df_c_prog["< Mejor"].iloc[c_idx]))
                    acum_ini += cump_c * (peso_c / 100.0)
                    tot_peso_ini += peso_c
        avance_ini = (acum_ini / (tot_peso_ini / 100.0)) if tot_peso_ini > 0 else 0.0
        col_ini = ob_color(avance_ini, float(st.session_state.get("_v_sob", 100.0)), float(st.session_state.get("_v_meta", 90.0)), float(st.session_state.get("_v_med", 80.0)))
        txt_col = "black" if col_ini in ["#ffff00", "#92d050"] else "white"
        
        ph_avance_ini.markdown(f"<div style='background-color:{col_ini}; color:{txt_col}; padding: 8px 15px; border-radius: 6px; font-weight: 900; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top:2px;'>AVANCE INTEGRADO: {avance_ini:.1f}%</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='sub-section-title'>Plan de Tareas y Seguimiento</div>", unsafe_allow_html=True)
        st.session_state[f"df_tareas_{q_name}_{i}"] = st.data_editor(
            st.session_state.get(f"df_tareas_{q_name}_{i}", pd.DataFrame()),
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"Jerarquia": st.column_config.TextColumn(width="small", help="Ej: 1, 1.1"), "Inicio": st.column_config.DateColumn(format="YYYY-MM-DD"), "Fin": st.column_config.DateColumn(format="YYYY-MM-DD")},
            key=f"ed_tar_{q_name}_{i}"
        )
        
        df_t_prog = st.session_state.get(f"df_tareas_{q_name}_{i}", pd.DataFrame())
        if not df_t_prog.empty:
            t_validas = df_t_prog[df_t_prog["Tarea"].str.strip() != ""]
            tot_t = len(t_validas)
            comp = t_validas["Completado"].sum() if tot_t > 0 else 0
            pct = int((comp / tot_t) * 100) if tot_t > 0 else 0
            st.markdown(f"<div style='font-size:14px; font-weight:900; color:#002060; margin-bottom:8px;'>Avance de Tareas Operativas: {comp}/{tot_t} ({pct}%)</div>", unsafe_allow_html=True)
            st.progress(pct / 100.0)
            st.write("")
            dibujar_gantt(df_t_prog)
            
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.vista_actual == "Configuración de Cuenta":
    st.markdown("<div class='section-title'>Configuración de Cuenta</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-section-title'>Generar Datos de Prueba (Dummy)</div>", unsafe_allow_html=True)
    st.info("Presiona este botón para llenar tu tablero actual con datos de ejemplo matemáticamente perfectos. Luego ve a cualquier pestaña y presiona 'Guardar Cambios' para enviarlos a tu base de datos.")
    if st.button("Llenar tablero con datos Dummy", type="secondary"):
        generar_dummy_onetest()
        st.success("¡Datos generados localmente! Ve a Q1 o Resumen Anual y presiona 'Guardar Cambios'.")
        
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
            if str(df_kpi["KPIs Indicadores"].iloc[i]).strip():
                p = float(df_kpi[f"{m} Prog"].iloc[i] or 0)
                r = float(df_kpi[f"{m} Real"].iloc[i] or 0)
                peso = float(df_kpi["Peso %"].iloc[i] or 0)
                cump = calc_cump(p, r, str(df_kpi["< Mejor"].iloc[i]))
                acum_k += cump * (peso / 100.0); t_peso_k += peso
    res_k = (acum_k / (t_peso_k / 100.0)) if t_peso_k > 0 else 0.0

    t_peso_o, acum_o = 0.0, 0.0
    for i in range(1, 6):
        if str(st.session_state.get(f"okr_{q_name}_{i}_nom", "")).strip():
            peso_o = float(st.session_state.get(f"okr_{q_name}_{i}_peso", 0.0))
            df_c = st.session_state.get(f"df_crit_{q_name}_{i}", pd.DataFrame())
            p_t, r_t = 0.0, 0.0
            if not df_c.empty:
                for c_i in range(len(df_c)):
                    if str(df_c["Criterio"].iloc[c_i]).strip():
                        p_t += float(df_c[f"{m} Prog"].iloc[c_i] or 0)
                        r_t += float(df_c[f"{m} Real"].iloc[c_i] or 0)
            cump_o = calc_cump(p_t, r_t, "NO")
            acum_o += cump_o * (peso_o / 100.0); t_peso_o += peso_o
    res_o = (acum_o / (t_peso_o / 100.0)) if t_peso_o > 0 else 0.0

    t_peso_tot = float(st.session_state.get("_p_kpis", 50.0)) + float(st.session_state.get("_p_okrs", 50.0))
    res_tot = ((res_k * (float(st.session_state.get("_p_kpis", 50.0)) / 100.0)) + (res_o * (float(st.session_state.get("_p_okrs", 50.0)) / 100.0))) / (t_peso_tot / 100.0) if t_peso_tot > 0 else 0.0
    return res_k, res_o, res_tot

anual_data, line_mensual = [], []
for q, meses in trimestres.items():
    acum_k_q, acum_o_q, acum_tot_q = 0.0, 0.0, 0.0
    for m in meses:
        rk, ro, rtot = get_mes_cump(m, q)
        anual_data.append({"Mes": m, "KPIs": rk/100.0, "Iniciativas": ro/100.0, "Integrado": rtot/100.0, "Trimestre": q, "Resultado Q": None})
        line_mensual.extend([{"Mes": m, "Tipo": "KPIs Operativos", "Valor": rk}, {"Mes": m, "Tipo": "Iniciativas Estratégicas", "Valor": ro}, {"Mes": m, "Tipo": "Desempeño Integrado", "Valor": rtot}])
        acum_k_q += rk; acum_o_q += ro; acum_tot_q += rtot
    anual_data[-1]["Resultado Q"] = (acum_tot_q / 3.0) / 100.0

df_anual = pd.DataFrame(anual_data)

if st.session_state.vista_actual == "Resumen Anual":
    st.markdown("<div class='section-title'>Resumen Anual del Desempeño</div>", unsafe_allow_html=True)
    
    with st.expander("⚙️ Configuración de Semáforos (Criterios de Éxito)", expanded=False):
        st.info("Estos rangos definen qué colores se mostrarán automáticamente en tus recuadros de avance de todo el año.")
        col_sem, col_space = st.columns([2, 3])
        with col_sem:
            st.markdown("""<div class='semaforo-container'><div class='sem-header'>Criterios de Éxito</div>""", unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            c1.markdown("<div class='sem-label' style='background-color:#00b050; color:white;'>Sobresaliente</div>", unsafe_allow_html=True)
            st.session_state._v_sob = c2.number_input("sob", value=float(st.session_state.get("_v_sob", 100.0)), label_visibility="collapsed", key="cfg_sob")
            c3, c4 = st.columns([2, 1])
            c3.markdown("<div class='sem-label' style='background-color:#92d050; color:white;'>Meta</div>", unsafe_allow_html=True)
            st.session_state._v_meta = c4.number_input("meta", value=float(st.session_state.get("_v_meta", 90.0)), label_visibility="collapsed", key="cfg_meta")
            c5, c6 = st.columns([2, 1])
            c5.markdown("<div class='sem-label' style='background-color:#ffff00;'>Medio</div>", unsafe_allow_html=True)
            st.session_state._v_med = c6.number_input("med", value=float(st.session_state.get("_v_med", 80.0)), label_visibility="collapsed", key="cfg_med")
            c7, c8 = st.columns([2, 1])
            c7.markdown("<div class='sem-label' style='background-color:#ff0000; color:white; border:none;'>Bajo</div>", unsafe_allow_html=True)
            c8.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:800; font-size:16px;'>{st.session_state.get('_v_med', 80.0)}%</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    col_ta, col_ch = st.columns([1.2, 1])
    with col_ta:
        st.markdown("<div class='sub-section-title'>Desempeño Mensual y Trimestral</div>", unsafe_allow_html=True)
        st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
        st.dataframe(df_anual.style.format({"KPIs": "{:.0%}", "Iniciativas": "{:.0%}", "Integrado": "{:.0%}", "Resultado Q": "{:.0%}"}), use_container_width=True, hide_index=True)
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
        color=alt.Color('Tipo', scale=alt.Scale(domain=['KPIs Operativos', 'Iniciativas Estratégicas', 'Desempeño Integrado'], range=['#002060', '#4B8BBE', '#808080']), legend=alt.Legend(title="", orient='bottom', labelFontWeight="bold")),
        tooltip=['Mes', 'Tipo', 'Valor']
    ).properties(height=350)
    st.altair_chart(ch_m, use_container_width=True)

# --- CALCULO REACTIVO TARJETAS FRONTALES ---
res_k_total, res_o_total = df_anual["KPIs"].mean() * 100, df_anual["Iniciativas"].mean() * 100
res_tot_final = df_anual["Integrado"].mean() * 100
v_sob, v_meta, v_med = float(st.session_state.get("_v_sob", 100.0)), float(st.session_state.get("_v_meta", 90.0)), float(st.session_state.get("_v_med", 89.0))

c_kpi, c_okr, c_tot = ob_color(res_k_total, v_sob, v_meta, v_med), ob_color(res_o_total, v_sob, v_meta, v_med), ob_color(res_tot_final, v_sob, v_meta, v_med)
txt_kpi, txt_okr, txt_tot = ("black" if c_kpi in ["#ffff00", "#92d050"] else "white"), ("black" if c_okr in ["#ffff00", "#92d050"] else "white"), ("black" if c_tot in ["#ffff00", "#92d050"] else "white")

ph_kpi.markdown(f"<div class='summary-card' style='background-color:{c_kpi};'><p class='summary-title' style='color:{txt_kpi};'>Indicadores (Acumulado)</p><p class='summary-value' style='color:{txt_kpi};'>{res_k_total:.0f} %</p></div>", unsafe_allow_html=True)
ph_okr.markdown(f"<div class='summary-card' style='background-color:{c_okr};'><p class='summary-title' style='color:{txt_okr};'>Iniciativas (Acumulado)</p><p class='summary-value' style='color:{txt_okr};'>{res_o_total:.0f} %</p></div>", unsafe_allow_html=True)
ph_tot.markdown(f"<div class='summary-card' style='background-color:{c_tot};'><p class='summary-title' style='color:{txt_tot};'>Total ONE TRACK</p><p class='summary-value' style='color:{txt_tot};'>{res_tot_final:.0f} %</p></div>", unsafe_allow_html=True)
