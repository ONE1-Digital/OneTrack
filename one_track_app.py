import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="ONE Track - Workspace", layout="wide")

# --- CSS MINIMALISTA Y ELEGANTE ---
st.markdown("""
    <style>
    .img-placeholder { background-color: #e6e9f0; border: 2px dashed #a0aabf; border-radius: 10px; height: 100px; display: flex; align-items: center; justify-content: center; color: #555; font-weight: bold; margin-bottom: 20px;}
    .title-placeholder { background-color: transparent; border: none; height: 100px; color: #002060; font-size: 28px; text-transform: uppercase; letter-spacing: 2px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #f0f2f6; padding: 5px 10px; border-radius: 8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { height: 40px; background-color: transparent; border-radius: 5px; color: #555; font-weight: 600; font-size: 16px; padding: 0 20px; }
    .stTabs [aria-selected="true"] { background-color: #002060 !important; color: #ffffff !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .summary-card { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #002060; height: 100%; transition: all 0.3s; }
    .summary-title { font-size: 13px; color: #666; font-weight: bold; margin-bottom: 5px;}
    .summary-value { font-size: 24px; color: #002060; font-weight: bold; }
    .semaforo-container { font-size: 12px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden; }
    .sem-header { background-color: #002060; color: white; text-align: center; font-weight: bold; padding: 4px; }
    .sem-row { display: flex; align-items: center; }
    .sem-label { flex: 2; padding: 4px 8px; font-weight: bold; text-align: right; color: black; border-bottom: 1px solid #fff;}
    .sem-val { flex: 1; padding: 4px; text-align: center; }
    .iniciativa-header { background-color: #e6e9f0; border-left: 5px solid #002060; padding: 8px 15px; font-weight: bold; color: #002060; margin-top: 20px; margin-bottom: 10px; }
    .footer-box { border: 2px solid #000; padding: 4px 12px; font-weight: bold; border-radius: 2px; min-width: 80px; text-align: center; }
    thead tr th:first-child {display:none}
    tbody th {display:none}
    </style>
""", unsafe_allow_html=True)

# --- CONEXION A BD Y LOGIN ---
conn = st.connection("supabase", type="sql")

if 'auth_token' not in st.session_state or st.session_state.auth_token is None:
    st.title("Acceso ONE Track")
    token = st.text_input("Palabra de acceso (Token):", type="password")
    if st.button("Entrar"):
        st.session_state.auth_token = token
        st.session_state.datos_cargados = False
        st.rerun()
    st.stop()

token = st.session_state.auth_token

# --- CONSTANTES ---
trimestres = {"Q1": ["Ene", "Feb", "Mar"], "Q2": ["Abr", "May", "Jun"], "Q3": ["Jul", "Ago", "Sep"], "Q4": ["Oct", "Nov", "Dic"]}
DEFAULT_LOGO_CLIENTE = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/MARBER.png"
DEFAULT_LOGO_ONE = "https://kidjtwcttgcedcljikvy.supabase.co/storage/v1/object/public/Logos/ONE.png"

# --- FUNCIONES MATEMATICAS Y DE COLOR ---
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
    html_footer = "<div style='display:flex; justify-content:flex-start; gap:10px; margin-bottom: 15px; font-size:13px; align-items:center;'><div style='font-weight:bold; color:#002060; margin-right:10px;'>Avance Mensual:</div>"
    v_sob, v_meta, v_med = st.session_state.get("v_sob_i", 100.0), st.session_state.get("v_meta_i", 90.0), st.session_state.get("v_med_i", 89.0)
    for m in meses:
        total_peso, acumulado = 0.0, 0.0
        for i in range(len(df)):
            if str(df["KPIs-Indicadores"][i]).strip() != "":
                p, r = float(df[f"{m} Prog"][i] or 0), float(df[f"{m} Real"][i] or 0)
                peso = float(df["Peso %"][i] or 0)
                cump = calc_cump(p, r, str(df["< Mejor"][i]))
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
    if df_plot.empty:
        st.info("Agrega fechas a las tareas para visualizar el Gantt.")
        return
    df_plot['Nombre'] = df_plot['Jerarquia'] + " " + df_plot['Tarea']
    df_plot['Estado'] = df_plot['Completado'].apply(lambda x: "Realizado" if x else "Pendiente")
    chart = alt.Chart(df_plot).mark_bar(cornerRadius=3, height=15).encode(
        x=alt.X('Inicio', title='', axis=alt.Axis(format="%d %b")), x2='Fin',
        y=alt.Y('Nombre', sort=None, title=''),
        color=alt.Color('Estado', scale=alt.Scale(domain=['Realizado', 'Pendiente'], range=['#28a745', '#ffc107']))
    ).properties(height=max(120, len(df_plot)*25))
    st.altair_chart(chart, use_container_width=True)

# --- CARGA Y DATOS DUMMY ---
def init_okr_structure(q_name, i, meses):
    if f"okr_{q_name}_{i}_nom" not in st.session_state:
        st.session_state[f"okr_{q_name}_{i}_nom"] = ""
        st.session_state[f"okr_{q_name}_{i}_obj"] = ""
        st.session_state[f"okr_{q_name}_{i}_peso"] = 20.0
        
        cols_c = ["Criterio", "Tipo", "Meta", "UM", "< Mejor", "%"]
        for m in meses: cols_c.extend([f"{m} Prog", f"{m} Real"])
        df_c = pd.DataFrame(columns=cols_c)
        for _ in range(3): df_c.loc[len(df_c)] = ["", "Promedio", 0.0, "U", "NO", 33.3] + [0.0]*(len(meses)*2)
        st.session_state[f"df_crit_{q_name}_{i}"] = df_c
        
        df_t = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"])
        st.session_state[f"df_tareas_{q_name}_{i}"] = df_t

def cargar_datos():
    if st.session_state.get('datos_cargados', False): return
    try:
        df_kpis = conn.query(f"SELECT * FROM kpis WHERE onetrack_id = '{token}'")
        df_okrs = conn.query(f"SELECT * FROM okrs_general WHERE onetrack_id = '{token}'")
        df_crit = conn.query(f"SELECT * FROM okr_criterios WHERE onetrack_id = '{token}'")
        df_tareas = conn.query(f"SELECT * FROM iniciativas_tareas WHERE onetrack_id = '{token}'")
    except Exception:
        df_kpis, df_okrs, df_crit, df_tareas = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    es_nuevo = df_kpis.empty

    st.session_state["p_kpis"] = float(df_kpis.iloc[0].get("Peso_Global_KPI", 50.0)) if not es_nuevo else 50.0
    st.session_state["p_okrs"] = float(df_kpis.iloc[0].get("Peso_Global_OKR", 50.0)) if not es_nuevo else 50.0
    st.session_state["v_sob_i"] = float(df_kpis.iloc[0].get("U_SVerde", 100.0)) if not es_nuevo else 100.0
    st.session_state["v_meta_i"] = float(df_kpis.iloc[0].get("U_Verde", 90.0)) if not es_nuevo else 90.0
    st.session_state["v_med_i"] = float(df_kpis.iloc[0].get("U_Amarillo", 80.0)) if not es_nuevo else 80.0
    st.session_state["empresa_input"] = str(df_kpis.iloc[0].get("Empresa", "")) if not es_nuevo else "Tech Solutions LATAM"
    st.session_state["puesto_input"] = str(df_kpis.iloc[0].get("Puesto", "")) if not es_nuevo else "Director de Operaciones"
    st.session_state["dueno_input"] = str(df_kpis.iloc[0].get("Dueno", "")) if not es_nuevo else "Carlos Rivera"

    for q_name, meses in trimestres.items():
        data_kpi = {"No.": ["#1", "#2", "#3", "#4", "#5"], "KPIs-Indicadores": [""]*5, "Tipo": ["Promedio"]*5, "Meta": [0.0]*5, "UM": ["U"]*5, "< Mejor": ["NO"]*5, "Peso %": [20.0]*5}
        for m in meses:
            data_kpi[f"{m} Prog"] = [0.0]*5
            data_kpi[f"{m} Real"] = [0.0]*5
            
        if not es_nuevo:
            for i in range(min(5, len(df_kpis))):
                row = df_kpis.iloc[i]
                data_kpi["KPIs-Indicadores"][i] = str(row.get("KPI_Nombre", ""))
                data_kpi["Meta"][i] = float(row.get("Meta", 0.0))
                data_kpi["UM"][i] = str(row.get("UM", "U"))
                data_kpi["< Mejor"][i] = str(row.get("< Mejor", "NO"))
                data_kpi["Peso %"][i] = float(row.get("Peso_%", 20.0))
                for m in meses:
                    data_kpi[f"{m} Prog"][i] = float(row.get(f"{m}_P", 0.0))
                    data_kpi[f"{m} Real"][i] = float(row.get(f"{m}_R", 0.0))
        elif q_name == "Q1":
            data_kpi["KPIs-Indicadores"][0] = "Ventas Mensuales"
            data_kpi["Meta"][0], data_kpi["UM"][0], data_kpi["Peso %"][0] = 500000, "$", 50.0
            data_kpi["Ene Prog"][0], data_kpi["Ene Real"][0] = 150000, 160000
            data_kpi["Feb Prog"][0], data_kpi["Feb Real"][0] = 160000, 145000
            data_kpi["KPIs-Indicadores"][1] = "Rotacion de Personal"
            data_kpi["Meta"][1], data_kpi["UM"][1], data_kpi["< Mejor"][1], data_kpi["Peso %"][1] = 5, "%", "SI", 50.0
            data_kpi["Ene Prog"][1], data_kpi["Ene Real"][1] = 5, 4
            data_kpi["Feb Prog"][1], data_kpi["Feb Real"][1] = 5, 8

        st.session_state[f"df_kpi_{q_name}"] = pd.DataFrame(data_kpi)

        for i in range(1, 6):
            init_okr_structure(q_name, i, meses)
            if not es_nuevo and (i-1) < len(df_okrs):
                row_o = df_okrs.iloc[i-1]
                st.session_state[f"okr_{q_name}_{i}_nom"] = str(row_o.get("OKR_Nombre", ""))
                st.session_state[f"okr_{q_name}_{i}_obj"] = str(row_o.get("Objetivo", ""))
                st.session_state[f"okr_{q_name}_{i}_peso"] = float(row_o.get("Peso_%", 20.0))
            elif es_nuevo and q_name == "Q1" and i == 1:
                st.session_state[f"okr_{q_name}_{i}_nom"] = "Expansion Comercial 2026"
                st.session_state[f"okr_{q_name}_{i}_obj"] = "Abrir mercado en la region norte mejorando la infraestructura logistica."
                st.session_state[f"okr_{q_name}_{i}_peso"] = 100.0
            
            if not df_crit.empty:
                crit_okr = df_crit[df_crit['OKR_ID'] == i].reset_index(drop=True)
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
            elif es_nuevo and q_name == "Q1" and i == 1:
                st.session_state[f"df_crit_{q_name}_{i}"].at[0, "Criterio"] = "Nuevos Clientes"
                st.session_state[f"df_crit_{q_name}_{i}"].at[0, "Meta"] = 50
                st.session_state[f"df_crit_{q_name}_{i}"].at[0, "Ene Prog"] = 10
                st.session_state[f"df_crit_{q_name}_{i}"].at[0, "Ene Real"] = 12

            if not df_tareas.empty:
                tar_okr = df_tareas[(df_tareas['Iniciativa_ID'] == i) & (df_tareas['Trimestre'] == q_name)]
                if not tar_okr.empty:
                    df_t = tar_okr[["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"]].reset_index(drop=True)
                    df_t["Completado"] = df_t["Completado"].astype(bool)
                    df_t["Inicio"] = pd.to_datetime(df_t["Inicio"]).dt.date
                    df_t["Fin"] = pd.to_datetime(df_t["Fin"]).dt.date
                    st.session_state[f"df_tareas_{q_name}_{i}"] = df_t
            elif es_nuevo and q_name == "Q1" and i == 1:
                df_t = pd.DataFrame(columns=["Jerarquia", "Tarea", "Responsable", "Inicio", "Fin", "Completado"])
                df_t.loc[0] = ["1.", "Estudio de Mercado", "Ana", date(2026, 1, 5), date(2026, 1, 20), True]
                df_t.loc[1] = ["1.1", "Analisis de Competencia", "Luis", date(2026, 1, 22), date(2026, 2, 15), False]
                st.session_state[f"df_tareas_{q_name}_{i}"] = df_t

    st.session_state.datos_cargados = True

cargar_datos()

def guardar_en_bd():
    kpis_data, okrs_data, crit_data, tareas_data = [], [], [], []
    peso_k, peso_o = st.session_state.get("p_kpis", 50.0), st.session_state.get("p_okrs", 50.0)
    v_sob, v_meta, v_med = st.session_state.get("v_sob_i", 100.0), st.session_state.get("v_meta_i", 90.0), st.session_state.get("v_med_i", 89.0)
    
    emp = st.session_state.get("empresa_input", "")
    pue = st.session_state.get("puesto_input", "")
    due = st.session_state.get("dueno_input", "")
    logo_c = DEFAULT_LOGO_CLIENTE # Mantenemos el logo por defecto en la BD por coherencia de columnas

    for i in range(5):
        k_nom = st.session_state["df_kpi_Q1"]["KPIs-Indicadores"][i]
        if k_nom:
            row = {
                "onetrack_id": token, "Empresa": emp, "Puesto": pue, "Dueno": due, "Logo_Cliente": logo_c,
                "KPI_Nombre": k_nom, "Tipo": st.session_state["df_kpi_Q1"]["Tipo"][i], "Meta": st.session_state["df_kpi_Q1"]["Meta"][i],
                "UM": st.session_state["df_kpi_Q1"]["UM"][i], "< Mejor": st.session_state["df_kpi_Q1"]["< Mejor"][i], "Peso_%": st.session_state["df_kpi_Q1"]["Peso %"][i],
                "Peso_Global_KPI": peso_k, "Peso_Global_OKR": peso_o, "U_SVerde": v_sob, "U_Verde": v_meta, "U_Amarillo": v_med
            }
            for q_n, meses in trimestres.items():
                for m in meses:
                    row[f"{m}_P"] = st.session_state[f"df_kpi_{q_n}"][f"{m} Prog"][i]
                    row[f"{m}_R"] = st.session_state[f"df_kpi_{q_n}"][f"{m} Real"][i]
            kpis_data.append(row)

    for i in range(1, 6):
        o_nom = st.session_state.get(f"okr_Q1_{i}_nom", "")
        if o_nom:
            okrs_data.append({"onetrack_id": token, "OKR_ID": i, "OKR_Nombre": o_nom, "Objetivo": st.session_state.get(f"okr_Q1_{i}_obj", ""), "Peso_%": st.session_state.get(f"okr_Q1_{i}_peso", 20.0)})
            
            df_c = st.session_state[f"df_crit_Q1_{i}"]
            for c_idx in range(len(df_c)):
                c_nom = df_c["Criterio"][c_idx]
                if str(c_nom).strip() != "":
                    c_row = {"onetrack_id": token, "OKR_ID": i, "Criterio_Nombre": c_nom, "Tipo": df_c["Tipo"][c_idx], "Meta": df_c["Meta"][c_idx], "UM": df_c["UM"][c_idx], "< Mejor": df_c["< Mejor"][c_idx], "Peso_%": df_c["%"][c_idx]}
                    for q_n, meses in trimestres.items():
                        df_cq = st.session_state[f"df_crit_{q_n}_{i}"]
                        if c_idx < len(df_cq):
                            for m in meses:
                                c_row[f"{m}_P"] = df_cq[f"{m} Prog"][c_idx]
                                c_row[f"{m}_R"] = df_cq[f"{m} Real"][c_idx]
                    crit_data.append(c_row)
                    
            for q_n in trimestres.keys():
                df_t = st.session_state[f"df_tareas_{q_n}_{i}"]
                for t_idx, t_row in df_t.iterrows():
                    if str(t_row.get("Tarea", "")).strip() != "":
                        tareas_data.append({"onetrack_id": token, "Iniciativa_ID": i, "Trimestre": q_n, "Jerarquia": t_row.get("Jerarquia", ""), "Tarea": t_row.get("Tarea", ""), "Responsable": t_row.get("Responsable", ""), "Inicio": t_row.get("Inicio"), "Fin": t_row.get("Fin"), "Completado": bool(t_row.get("Completado", False))})

    def sync_tabla(df_nuevo, table_name):
        if df_nuevo.empty: return
        try:
            df_total = conn.query(f"SELECT * FROM {table_name}")
            df_otros = df_total[df_total['onetrack_id'] != token]
            df_final = pd.concat([df_otros, df_nuevo], ignore_index=True)
        except Exception: df_final = df_nuevo
        df_final.to_sql(table_name, con=conn.engine, if_exists='replace', index=False)

    sync_tabla(pd.DataFrame(kpis_data), "kpis")
    sync_tabla(pd.DataFrame(okrs_data), "okrs_general")
    sync_tabla(pd.DataFrame(crit_data), "okr_criterios")
    sync_tabla(pd.DataFrame(tareas_data), "iniciativas_tareas")

# --- UI PRINCIPAL ---
c_img1, c_img2, c_img3 = st.columns([1, 2, 1])

with c_img1: 
    try:
        st.image(DEFAULT_LOGO_ONE, use_container_width=True)
    except:
        st.markdown("<div class='img-placeholder'>Logo ONE</div>", unsafe_allow_html=True)

with c_img2: 
    st.markdown("<div class='img-placeholder title-placeholder' style='border:none;'>ONE TRACK </div>", unsafe_allow_html=True)

with c_img3: 
    try:
        st.image(DEFAULT_LOGO_CLIENTE, use_container_width=True)
    except:
        st.markdown("<div class='img-placeholder'>Logo Cliente</div>", unsafe_allow_html=True)

c_inf1, c_inf2, c_inf3 = st.columns(3)
st.session_state.empresa_input = c_inf1.text_input("Empresa", value=st.session_state.get("empresa_input", ""))
st.session_state.puesto_input = c_inf2.text_input("Puesto", value=st.session_state.get("puesto_input", ""))
st.session_state.dueno_input = c_inf3.text_input("Dueno del One Track", value=st.session_state.get("dueno_input", ""))

st.divider()

col_t, col_btn = st.columns([4, 1])
with col_t: st.markdown("<h3 style='color:#002060; margin:0;'>Tablero de Control</h3>", unsafe_allow_html=True)
with col_btn:
    if st.button("Guardar Cambios", type="primary", use_container_width=True):
        with st.spinner("Sincronizando con base de datos..."):
            guardar_en_bd()
            st.session_state.datos_cargados = False
        st.success("Guardado exitoso.")

col_w, col_s1, col_s2, col_s3 = st.columns([1.5, 1, 1, 1])
with col_w:
    st.markdown("<div class='summary-card' style='padding:10px;'><p class='summary-title'>Ponderacion Global</p>", unsafe_allow_html=True)
    c_kpi, c_okr = st.columns(2)
    peso_k = c_kpi.number_input("Indicadores (%)", value=st.session_state["p_kpis"], key="p_kpis")
    peso_o = c_okr.number_input("Iniciativas (%)", value=st.session_state["p_okrs"], key="p_okrs")
    st.markdown("</div>", unsafe_allow_html=True)
with col_s1: ph_kpi = st.empty()
with col_s2: ph_okr = st.empty()
with col_s3: ph_tot = st.empty()

col_sem, col_space = st.columns([2, 3])
with col_sem:
    st.markdown("""<div class='semaforo-container'><div class='sem-header'>Criterios de Exito</div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    c1.markdown("<div class='sem-label' style='background-color:#00b050;'>Sobresaliente </div>", unsafe_allow_html=True)
    v_sob = c2.number_input("sob", value=st.session_state["v_sob_i"], label_visibility="collapsed", key="v_sob_i")
    c3, c4 = st.columns([2, 1])
    c3.markdown("<div class='sem-label' style='background-color:#92d050;'>Meta </div>", unsafe_allow_html=True)
    v_meta = c4.number_input("meta", value=st.session_state["v_meta_i"], label_visibility="collapsed", key="v_meta_i")
    c5, c6 = st.columns([2, 1])
    c5.markdown("<div class='sem-label' style='background-color:#ffff00;'>Medio </div>", unsafe_allow_html=True)
    v_med = c6.number_input("med", value=st.session_state["v_med_i"], label_visibility="collapsed", key="v_med_i")
    c7, c8 = st.columns([2, 1])
    c7.markdown("<div class='sem-label' style='background-color:#ff0000; color:white; border:none;'>Bajo </div>", unsafe_allow_html=True)
    c8.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:bold; font-size:14px;'>{st.session_state['v_med_i']}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

tabs_main = st.tabs(["Q1", "Q2", "Q3", "Q4", "Resumen Anual"])

for q_idx, q_name in enumerate(["Q1", "Q2", "Q3", "Q4"]):
    with tabs_main[q_idx]:
        meses_q = trimestres[q_name]
        
        st.markdown(f"<h3 style='color:#002060;'>KPIs-Indicadores - {q_name}</h3>", unsafe_allow_html=True)
        render_footer(st.session_state[f"df_kpi_{q_name}"], meses_q)
        
        st.session_state[f"df_kpi_{q_name}"] = st.data_editor(
            st.session_state[f"df_kpi_{q_name}"],
            use_container_width=True, hide_index=True, num_rows="fixed",
            column_config={"No.": st.column_config.TextColumn(disabled=True, width="small"), "Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio", "Valor Final"]), "UM": st.column_config.SelectboxColumn(options=["U", "$", "%", "Horas"]), "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])},
            key=f"ed_kpi_{q_name}"
        )

        st.write("")
        st.markdown(f"<h3 style='color:#002060;'>Iniciativas Estrategicas - {q_name}</h3>", unsafe_allow_html=True)
        
        for i in range(1, 6):
            st.markdown(f"<div class='iniciativa-header'>Iniciativa #{i}</div>", unsafe_allow_html=True)
            ch1, ch2 = st.columns([4, 1])
            ch1.text_input("Nombre de la Iniciativa", value=st.session_state[f"okr_{q_name}_{i}_nom"], key=f"okr_{q_name}_{i}_nom", label_visibility="collapsed", placeholder="Nombre de la Iniciativa")
            ch2.number_input("Peso %", value=st.session_state[f"okr_{q_name}_{i}_peso"], key=f"okr_{q_name}_{i}_peso", label_visibility="collapsed")
            
            co1, co2 = st.columns([1, 3])
            with co1: st.text_area("Objetivo:", value=st.session_state[f"okr_{q_name}_{i}_obj"], key=f"okr_{q_name}_{i}_obj", height=150)
            with co2:
                st.caption("Criterios de Exito")
                st.session_state[f"df_crit_{q_name}_{i}"] = st.data_editor(
                    st.session_state[f"df_crit_{q_name}_{i}"],
                    use_container_width=True, hide_index=True, num_rows="dynamic",
                    column_config={"Tipo": st.column_config.SelectboxColumn(options=["Acumulado", "Promedio"]), "< Mejor": st.column_config.SelectboxColumn(options=["NO", "SI"])},
                    key=f"ed_crit_{q_name}_{i}"
                )
            
            st.caption("Plan de Tareas y Diagrama de Gantt")
            cg1, cg2 = st.columns([1, 1])
            with cg1:
                st.session_state[f"df_tareas_{q_name}_{i}"] = st.data_editor(
                    st.session_state[f"df_tareas_{q_name}_{i}"],
                    use_container_width=True, hide_index=True, num_rows="dynamic",
                    column_config={"Jerarquia": st.column_config.TextColumn(width="small", help="Ej: 1, 1.1"), "Inicio": st.column_config.DateColumn(format="YYYY-MM-DD"), "Fin": st.column_config.DateColumn(format="YYYY-MM-DD")},
                    key=f"ed_tar_{q_name}_{i}"
                )
            with cg2:
                dibujar_gantt(st.session_state[f"df_tareas_{q_name}_{i}"])
            st.write("")

with tabs_main[4]:
    st.title("Resumen Anual: ONE Track")
    st.info("Vista consolidada lista para programar graficas anuales y reportes de impresion.")

# --- CALCULO REACTIVO TARJETAS ---
av_kpis, t_kpis = 0.0, 0.0
for i in range(5):
    if str(st.session_state["df_kpi_Q1"]["KPIs-Indicadores"][i]).strip():
        peso = float(st.session_state["df_kpi_Q1"]["Peso %"][i] or 0)
        p_t, r_t = 0.0, 0.0
        for q, ms in trimestres.items():
            for m in ms:
                p_t += float(st.session_state[f"df_kpi_{q}"][f"{m} Prog"][i] or 0)
                r_t += float(st.session_state[f"df_kpi_{q}"][f"{m} Real"][i] or 0)
        cump = calc_cump(p_t, r_t, str(st.session_state["df_kpi_Q1"]["< Mejor"][i]))
        av_kpis += cump * (peso / 100.0); t_kpis += peso
if t_kpis > 0: av_kpis = av_kpis / (t_kpis / 100.0)

av_okrs, t_okrs = 0.0, 0.0
for i in range(1, 6):
    if str(st.session_state.get(f"okr_Q1_{i}_nom", "")).strip():
        p_okr = float(st.session_state.get(f"okr_Q1_{i}_peso", 0.0))
        p_t, r_t = 0.0, 0.0
        for q, ms in trimestres.items():
            df_c = st.session_state[f"df_crit_{q}_{i}"]
            for c_i in range(len(df_c)):
                if str(df_c["Criterio"][c_i]).strip():
                    for m in ms:
                        p_t += float(df_c[f"{m} Prog"][c_i] or 0); r_t += float(df_c[f"{m} Real"][c_i] or 0)
        c_okr = calc_cump(p_t, r_t, "NO")
        av_okrs += c_okr * (p_okr / 100.0); t_okrs += p_okr
if t_okrs > 0: av_okrs = av_okrs / (t_okrs / 100.0)

t_peso = peso_k + peso_o
av_tot = ((av_kpis * (peso_k / 100.0)) + (av_okrs * (peso_o / 100.0))) / (t_peso / 100.0) if t_peso > 0 else 0.0

c_kpi, c_okr, c_tot = ob_color(av_kpis, v_sob, v_meta, v_med), ob_color(av_okrs, v_sob, v_meta, v_med), ob_color(av_tot, v_sob, v_meta, v_med)
txt_kpi, txt_okr, txt_tot = ("black" if c_kpi in ["#ffff00", "#92d050"] else "white"), ("black" if c_okr in ["#ffff00", "#92d050"] else "white"), ("black" if c_tot in ["#ffff00", "#92d050"] else "white")

ph_kpi.markdown(f"<div class='summary-card' style='background-color:{c_kpi};'><p class='summary-title' style='color:{txt_kpi};'>Indicadores (Acumulado)</p><p class='summary-value' style='color:{txt_kpi};'>{av_kpis:.1f} %</p></div>", unsafe_allow_html=True)
ph_okr.markdown(f"<div class='summary-card' style='background-color:{c_okr};'><p class='summary-title' style='color:{txt_okr};'>Iniciativas (Acumulado)</p><p class='summary-value' style='color:{txt_okr};'>{av_okrs:.1f} %</p></div>", unsafe_allow_html=True)
ph_tot.markdown(f"<div class='summary-card' style='background-color:{c_tot};'><p class='summary-title' style='color:{txt_tot};'>Total ONE Track</p><p class='summary-value' style='color:{txt_tot};'>{av_tot:.1f} %</p></div>", unsafe_allow_html=True)
