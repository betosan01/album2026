import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026", layout="wide")

# --- ESTILOS CSS AVANZADOS (Idea 1, 3, 6 y 7) ---
st.markdown("""
    <style>
    /* Idea 1: Efecto Brillante para Doradas */
    @keyframes shiny {
        0% { background-position: -200%; }
        100% { background-position: 200%; }
    }
    .st-gold {
        background: linear-gradient(110deg, #ffd700 45%, #fff9db 50%, #ffd700 55%);
        background-size: 200% 100%;
        animation: shiny 3s infinite linear;
        color: black !important;
        border: 2px solid #daa520 !important;
    }

    /* Idea 3: Pulso para Azules (Alguien la necesita) */
    @keyframes pulse-blue {
        0% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 123, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0); }
    }
    .st-blue {
        animation: pulse-blue 2s infinite;
        background-color: #007bff !important;
        border: 2px solid #0056b3 !important;
    }

    /* Idea 6: Línea de Escaneo de Evidencia */
    @keyframes scanline {
        0% { top: 0%; }
        100% { top: 100%; }
    }
    .scan-container { position: relative; overflow: hidden; }
    .scan-container::after {
        content: ""; position: absolute; width: 100%; height: 2px;
        background: rgba(0, 255, 255, 0.4); top: 0; left: 0;
        animation: scanline 4s linear infinite; z-index: 10; pointer-events: none;
    }

    /* Estilos Generales */
    .legend-box { padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 25px; display: flex; gap: 20px; flex-wrap: wrap; background-color: #1e1e1e; }
    .legend-item { display: flex; align-items: center; gap: 10px; font-size: 0.9em; color: #fafafa; }
    .circle { height: 15px; width: 15px; border-radius: 50%; display: inline-block; }
    .sticker-box { padding: 15px 5px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1em; transition: transform 0.3s; }
    .sticker-box:hover { transform: scale(1.05); }
    .st-gray { background-color: #2b2b2b; color: #666; border: 1px dashed #444; }
    .st-green { background-color: #28a745; color: white; border: 1px solid #1e7e34; }
    .log-entry { font-size: 0.85em; color: #888; border-bottom: 1px solid #333; padding: 5px 0; }
    .stat-card { background-color: #262730; padding: 15px; border-radius: 10px; border-top: 3px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE FUEGOS ARTIFICIALES (Idea 5) ---
def lanzar_fuegos(nombre, meta, color_hex):
    # Colores arcoíris para el 100%
    colors = "['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']" if meta == 100 else f"['{color_hex}']"
    components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
            var end = Date.now() + (3 * 1000);
            var colors = {colors};
            (function frame() {{
              confetti({{ particleCount: 5, angle: 60, spread: 55, origin: {{ x: 0 }}, colors: colors }});
              confetti({{ particleCount: 5, angle: 120, spread: 55, origin: {{ x: 1 }}, colors: colors }});
              if (Date.now() < end) {{ requestAnimationFrame(frame); }}
            }}());
        </script>
        <div style="text-align: center; font-family: sans-serif; color: white;">
            <h2 style="font-size: 40px; margin:0;">🔥 ¡{nombre} llegó al {meta}%! 🔥</h2>
        </div>
    """, height=120)

# --- CONEXIÓN A DATOS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url_del_sheet, ttl="0")
df.columns = [str(c).strip().upper() for c in df.columns]

nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]
metas_config = {10: "#cd7f32", 25: "#c0c0c0", 50: "#007bff", 75: "#9b59b6", 90: "#e74c3c", 95: "#ffd700", 100: "MULTI"}

if "log_actividad" not in st.session_state: st.session_state.log_actividad = []
if "metas_alcanzadas" not in st.session_state: st.session_state.metas_alcanzadas = {p: [] for p in nombres_papus}

def agregar_al_log(accion):
    st.session_state.log_actividad.insert(0, accion)
    if len(st.session_state.log_actividad) > 10: st.session_state.log_actividad.pop()

# --- 6. RANKING Y METAS ---
st.title("🏆 Control Albúm Papus")
total_total = len(df)

st.subheader("📊 Power Ranking del Squad")
cols_rank = st.columns(len(nombres_papus))
for i, p in enumerate(nombres_papus):
    pegadas = len(df[df[p] > 0])
    porcentaje = round((pegadas / total_total) * 100, 1)
    
    # Detección de Metas (Idea 5)
    for m, col in metas_config.items():
        if porcentaje >= m and m not in st.session_state.metas_alcanzadas[p]:
            lanzar_fuegos(p, m, col if m < 100 else "#ffffff")
            st.session_state.metas_alcanzadas[p].append(m)
            agregar_al_log(f"🚀 {p} ALCANZÓ EL {m}%")

    with cols_rank[i]:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style='margin:0; color:#007bff;'>{p}</h3>
            <p style='margin:0; font-size:1.3em;'><b>{porcentaje}%</b></p>
            <p style='margin:0; font-size:0.8em; color:#888;'>Pegadas: {pegadas}</p>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR: CHISMÓGRAFO Y TRISTE REALIDAD ---
with st.sidebar:
    st.header("🕵️ Bitácora de Evidencias")
    for log in st.session_state.log_actividad:
        color = "#ffd700" if "ALCANZÓ" in log else "#888"
        st.markdown(f"<div class='log-entry' style='color:{color};'>• {log}</div>", unsafe_allow_html=True)
    
    st.divider()
    st.header("📉 La Triste Realidad")
    usuario_stats = st.selectbox("Analizar a:", nombres_papus, key="stats_user")
    faltantes = total_total - len(df[df[usuario_stats] > 0])
    prob_nueva = 1 - (((total_total - faltantes) / total_total) ** 7)
    sobres_faltantes = max(0, ((total_total * np.log(total_total) + 0.577 * total_total) / 7) - ((total_total - faltantes) / 7))
    
    st.write(f"**Te faltan:** {faltantes} estampas.")
    st.write(f"**Chanza de nueva en sig. sobre:** {round(prob_nueva*100, 1)}%")
    st.write(f"**Sobres pa' terminar (promedio):** {int(sobres_faltantes)}")

# --- REGISTRO DE SOBRES ---
st.divider()
st.subheader("📖 Registro de Sobres")
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
col_prioridad_mia = f"PRIORIDAD_{usuario}"

opciones = df['ESTAMPA'].tolist()
seleccionadas = st.multiselect("¿Cuáles te salieron perro?😯", opciones)

if seleccionadas:
    st.write("### 📋 Panel de Control")
    cols = st.columns(4)
    cambios_pendientes = {}
    for i, est in enumerate(seleccionadas):
        idx = df[df['ESTAMPA'] == est].index[0]
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align:center;'>{est}</h4>", unsafe_allow_html=True)
                cambios_pendientes[idx] = st.number_input("Cantidad", min_value=0, value=1, key=f"n_{est}")

    if st.button("💾 Al toque pa, ya los puedes guardar", type="primary", use_container_width=True):
        for idx, suma in cambios_pendientes.items():
            if suma > 0: df.at[idx, usuario] += suma
        conn.update(spreadsheet=url_del_sheet, data=df)
        agregar_al_log(f"{usuario} registró {len(cambios_pendientes)} estampas")
        st.success("¡Ya quedó papu!🔥")
        st.rerun()

# --- 3. MERCADO NIGGER & CAZA-TRATOS ---
st.divider()
st.subheader("💱 Mercado Nigger")
t_mercado, t_caza = st.tabs(["Repetidas Disponibles", "🤝 Tratos Ideales"])

with t_mercado:
    me_faltan = df[df[usuario] == 0]
    hay_inter = False
    c1, c2 = st.columns(2)
    for i, (_, row) in enumerate(me_faltan.iterrows()):
        for otro in nombres_papus:
            if otro != usuario and row[otro] > 1:
                hay_inter = True
                with (c1 if i % 2 == 0 else c2):
                    st.markdown(f"<div style='padding:10px; border-left:5px solid #007bff; background:#262730; margin-bottom:5px;'><b>{row['ESTAMPA']}</b> ➔ {otro}</div>", unsafe_allow_html=True)

with t_caza:
    trato = False
    for otro in nombres_papus:
        if otro != usuario:
            le_doy = df[(df[usuario] > 1) & (df[otro] == 0)]['ESTAMPA'].tolist()
            me_da = df[(df[otro] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if le_doy and me_da:
                trato = True
                st.success(f"🤝 **¡TRATO IDEAL CON {otro}!**")
                st.write(f"Tú le das: `{', '.join(le_doy[:2])}...` | Él te da: `{', '.join(me_da[:2])}...`")

# --- ÁLBUM VIRTUAL (Idea 6) ---
st.divider()
st.subheader(f"📔 Álbum Virtual ({usuario})")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: f_falt = st.checkbox("Solo mis faltantes")
with col_f2: f_des = st.checkbox("Solo mis deseadas ⭐")
with col_f3: f_nadie = st.checkbox("Nadie del squad las tiene")

df_v = df.copy()
if f_falt: df_v = df_v[df_v[usuario] == 0]
if f_des: df_v = df_v[df_v[col_prioridad_mia] > 0]
if f_nadie: df_v = df_v[(df_v[nombres_papus] == 0).all(axis=1)]

# Paginación
ITEMS = 30
total_p = (len(df_v) - 1) // ITEMS + 1
if "album_p" not in st.session_state: st.session_state.album_p = 0

st.markdown("<div class='scan-container'>", unsafe_allow_html=True)
cp1, cp2, cp3 = st.columns([1,2,1])
with cp1: 
    if st.button("⬅️ Va pa´tras") and st.session_state.album_p > 0:
        st.session_state.album_p -= 1
        st.rerun()
with cp2: st.markdown(f"<p style='text-align:center;'>Página {st.session_state.album_p + 1} de {max(1, total_p)}</p>", unsafe_allow_html=True)
with cp3:
    if st.button("Va pa´lante ➡️") and st.session_state.album_p < total_p - 1:
        st.session_state.album_p += 1
        st.rerun()

chunk = df_v.iloc[st.session_state.album_p*ITEMS : (st.session_state.album_p+1)*ITEMS]
cols_v = st.columns(6)
for i, (_, row) in enumerate(chunk.iterrows()):
    est, act, prio = row['ESTAMPA'], row[usuario], row[col_prioridad_mia]
    otros_f = [p for p in nombres_papus if p != usuario if row[p] == 0]
    
    if act > 1 and otros_f: css = "st-blue"
    elif act >= 1: css = "st-green"
    elif prio > 0: css = "st-gold"
    else: css = "st-gray"
    
    with cols_v[i % 6]:
        st.markdown(f"<div class='sticker-box {css}'>{est}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# GESTIÓN DE DORADAS
st.divider()
st.subheader(f"⭐ TUS MÁS DESEADAS ({usuario})")
cg1, cg2 = st.columns(2)
with cg1:
    no_p = df[(df[col_prioridad_mia] == 0) & (df[usuario] == 0)]['ESTAMPA'].tolist()
    if no_p:
        p_add = st.selectbox("Marcar como Dorada:", no_p, key="add")
        if st.button("✨ LA NECESITOOOOOOO🧽"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], col_prioridad_mia] = 1
            conn.update(spreadsheet=url_del_sheet, data=df)
            agregar_al_log(f"{usuario} marcó {p_add} como dorada")
            st.rerun()
with cg2:
    si_p = df[df[col_prioridad_mia] > 0]['ESTAMPA'].tolist()
    if si_p:
        p_rem = st.selectbox("Quitar de Doradas:", si_p, key="rem")
        if st.button("❌ Ya no va"):
            df.at[df[df['ESTAMPA'] == p_rem].index[0], col_prioridad_mia] = 0
            conn.update(spreadsheet=url_del_sheet, data=df)
            st.rerun()
