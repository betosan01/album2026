import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026", layout="wide")

# --- ESTILOS CSS (DARK MODE + ESTILO CRIMI/ALBUM) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .legend-box { 
        padding: 15px; border-radius: 8px; border: 1px solid #444; 
        margin-bottom: 25px; display: flex; gap: 20px; flex-wrap: wrap; 
        background-color: #1e1e1e; 
    }
    .legend-item { display: flex; align-items: center; gap: 10px; font-size: 0.9em; color: #fafafa; }
    .circle { height: 15px; width: 15px; border-radius: 50%; display: inline-block; }
    .priority-badge { 
        background-color: #ffd700; color: black; padding: 2px 10px; 
        border-radius: 10px; font-weight: bold; font-size: 0.7em; 
    }
    .sticker-box {
        padding: 15px 5px; border-radius: 8px; text-align: center; 
        font-weight: bold; margin-bottom: 10px; font-size: 1em;
        transition: transform 0.2s;
    }
    .st-gray { background-color: #2b2b2b; color: #666; border: 1px dashed #444; }
    .st-green { background-color: #28a745; color: white; border: 1px solid #1e7e34; }
    .st-blue { background-color: #007bff; color: white; border: 1px solid #0056b3; }
    .st-gold { background-color: #ffd700; color: black; border: 1px solid #daa520; }
    .log-entry { font-size: 0.85em; color: #888; border-bottom: 1px solid #333; padding: 5px 0; }
    .stat-card { background-color: #262730; padding: 15px; border-radius: 10px; border-top: 3px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE SESIÓN (Para la Bitácora de Actividad - Opción 1) ---
if "log_actividad" not in st.session_state:
    st.session_state.log_actividad = []

def agregar_al_log(accion):
    st.session_state.log_actividad.insert(0, accion)
    if len(st.session_state.log_actividad) > 10:
        st.session_state.log_actividad.pop()

# --- CONEXIÓN A DATOS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url_del_sheet, ttl="0")
df.columns = [str(c).strip().upper() for c in df.columns]

nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]

# --- 6. RANKING DE COLECCIONISTAS (POWER RANKING) ---
st.title("🏆 Control Albúm Papus")

st.subheader("📊 Power Ranking del Squad")
rank_data = []
total_total = len(df)

for p in nombres_papus:
    pegadas = len(df[df[p] > 0])
    repetidas = df[df[p] > 1][p].sum() - len(df[df[p] > 1])
    deseadas_pendientes = len(df[(df[f"PRIORIDAD_{p}"] > 0) & (df[p] == 0)])
    rank_data.append({
        "PAPU": p,
        "PROGRESO": f"{(pegadas/total_total)*100:.1f}%",
        "PEGADAS": pegadas,
        "REPETIDAS": int(repetidas),
        "DESEADAS": deseadas_pendientes,
        "PUNTOS": (pegadas * 2) + int(repetidas) # Sistema de puntos simple
    })

df_rank = pd.DataFrame(rank_data).sort_values(by="PUNTOS", ascending=False)
cols_rank = st.columns(len(nombres_papus))
for i, row in enumerate(df_rank.itertuples()):
    with cols_rank[i]:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style='margin:0; color:#007bff;'>#{i+1} {row.PAPU}</h3>
            <p style='margin:0; font-size:1.2em;'><b>{row.PROGRESO}</b></p>
            <p style='margin:0; font-size:0.8em; color:#888;'>Puntos: {row.PUNTOS}</p>
        </div>
        """, unsafe_allow_html=True)

# --- 1. BITÁCORA DE ACTIVIDAD (CHISMÓGRAFO) ---
with st.sidebar:
    st.header("🕵️ Bitácora de Evidencias")
    if not st.session_state.log_actividad:
        st.write("Sin movimientos recientes, carnal.")
    for log in st.session_state.log_actividad:
        st.markdown(f"<div class='log-entry'>• {log}</div>", unsafe_allow_html=True)
    
    st.divider()
    # --- 4. LA TRISTE REALIDAD (CALCULADORA DE STATS) ---
    st.header("📉 La Triste Realidad")
    usuario_stats = st.selectbox("Analizar a:", nombres_papus, key="stats_user")
    faltantes = total_total - len(df[df[usuario_stats] > 0])
    # Probabilidad de estampa nueva en el siguiente sobre (asumiendo 5 por sobre)
    prob_nueva = 1 - ( ( (total_total - faltantes) / total_total ) ** 5 )
    # Estimación de sobres restantes (Cupón del coleccionista)
    # Fórmula: N * Hn donde Hn es el n-ésimo número armónico
    sobres_estimados = (total_total * np.log(total_total) + 0.577 * total_total) / 5
    
    st.write(f"**Te faltan:** {faltantes} estampas.")
    st.write(f"**Chanza de nueva en sig. sobre:** {prob_nueva*100:.1f}%")
    st.write(f"**Sobres pa' terminar (aprox):** {int(sobres_estimados - (total_total-faltantes)/5)}")

# --- IDENTIFICACIÓN Y REGISTRO ---
st.divider()
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
col_prioridad_mia = f"PRIORIDAD_{usuario}"

opciones = df['ESTAMPA'].tolist()
seleccionadas = st.multiselect("¿Cuáles te salieron perro?😯", opciones)

if seleccionadas:
    st.write("### 📋 Panel de Control")
    cols = st.columns(4)
    cambios_pendientes = {}
    for i, estampa in enumerate(seleccionadas):
        idx = df[df['ESTAMPA'] == estampa].index[0]
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align:center; margin-bottom: 0px;'>{estampa}</h4>", unsafe_allow_html=True)
                cantidad_nueva = st.number_input("Cantidad", min_value=0, value=1, key=f"num_{estampa}")
                cambios_pendientes[idx] = cantidad_nueva

    if st.button("💾 Al toque pa, ya los puedes guardar", type="primary", use_container_width=True):
        for idx_cambio, suma in cambios_pendientes.items():
            if suma > 0:
                df.at[idx_cambio, usuario] += suma
        conn.update(spreadsheet=url_del_sheet, data=df)
        agregar_al_log(f"{usuario} registró {len(cambios_pendientes)} estampas")
        st.success("¡Sincronizado!🔥")
        st.rerun()

# --- 3. CAZA-TRATOS (MERCADO NEGRO OPTIMIZADO) ---
st.divider()
st.subheader("💱 Mercado Nigger & Caza-Tratos")
tab_mercado, tab_caza = st.tabs(["Repetidas Disponibles", "🤝 Tratos Ideales"])

with tab_mercado:
    me_faltan = df[df[usuario] == 0]
    hay_inter = False
    col_m1, col_m2 = st.columns(2)
    for i, (_, row) in enumerate(me_faltan.iterrows()):
        for otro in nombres_papus:
            if otro != usuario and row[otro] > 1:
                hay_inter = True
                with (col_m1 if i % 2 == 0 else col_m2):
                    st.markdown(f"<div class='swap-card' style='padding:10px; border-left:5px solid #28a745; background:#262730; margin-bottom:5px;'><b>{row['ESTAMPA']}</b> ➔ Pídesela a <b>{otro}</b></div>", unsafe_allow_html=True)
    if not hay_inter: st.info("Nadie tiene lo que te falta, carnal.")

with tab_caza:
    tratos_encontrados = False
    for otro in nombres_papus:
        if otro != usuario:
            # Yo tengo lo que él quiere (repetidas mías > 1 y él tiene 0)
            yo_le_doy = df[(df[usuario] > 1) & (df[otro] == 0)]['ESTAMPA'].tolist()
            # Él tiene lo que yo quiero (repetidas de él > 1 y yo tengo 0)
            el_me_da = df[(df[otro] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            
            if yo_le_doy and el_me_da:
                tratos_encontrados = True
                st.success(f"🔥 **¡TRATO IDEAL CON {otro}!**")
                st.write(f"Tú le das: `{', '.join(yo_le_doy[:3])}`... | Él te da: `{', '.join(el_me_da[:3])}`...")

# --- 5. ÁLBUM VIRTUAL CON FILTROS INTELIGENTES ---
st.divider()
st.subheader(f"📔 Álbum Virtual ({usuario})")

# Filtros
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: f_faltantes = st.checkbox("Solo mis faltantes")
with col_f2: f_deseadas = st.checkbox("Solo mis deseadas ⭐")
with col_f3: f_nadie = st.checkbox("Nadie del squad las tiene")

df_display = df.copy()
if f_faltantes: df_display = df_display[df_display[usuario] == 0]
if f_deseadas: df_display = df_display[df_display[col_prioridad_mia] > 0]
if f_nadie:
    mask = (df_display[nombres_papus] == 0).all(axis=1)
    df_display = df_display[mask]

# Paginación
ITEMS_PAG = 30
total_p = (len(df_display) - 1) // ITEMS_PAG + 1
page = st.number_input("Página", min_value=1, max_value=max(1, total_p), step=1) - 1

st.write(f"Mostrando {len(df_display)} estampas")
chunk = df_display.iloc[page*ITEMS_PAG : (page+1)*ITEMS_PAG]
cols_alb = st.columns(6)

for i, (_, row) in enumerate(chunk.iterrows()):
    est = row['ESTAMPA']
    act = row[usuario]
    prio = row[col_prioridad_mia]
    otros_faltan = [p for p in nombres_papus if p != usuario if row[p] == 0]
    
    if act > 1 and otros_faltan: css = "st-blue"
    elif act >= 1: css = "st-green"
    elif prio > 0: css = "st-gold"
    else: css = "st-gray"
    
    with cols_alb[i % 6]:
        st.markdown(f"<div class='sticker-box {css}'>{est}</div>", unsafe_allow_html=True)
