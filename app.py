import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026", layout="wide")

# --- ANIMACIONES Y ESTILOS CSS AVANZADOS ---
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

    /* Idea 3: Pulso Radar para Azules (Match) */
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
    .scan-container {
        position: relative;
        overflow: hidden;
    }
    .scan-container::after {
        content: "";
        position: absolute;
        width: 100%;
        height: 2px;
        background: rgba(0, 255, 255, 0.5);
        top: 0;
        left: 0;
        animation: scanline 4s linear infinite;
        z-index: 10;
        pointer-events: none;
    }

    /* Estilos Base */
    .legend-box { padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 25px; display: flex; gap: 20px; flex-wrap: wrap; background-color: #1e1e1e; }
    .legend-item { display: flex; align-items: center; gap: 10px; font-size: 0.9em; color: #fafafa; }
    .circle { height: 15px; width: 15px; border-radius: 50%; display: inline-block; }
    .sticker-box { padding: 15px 5px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1em; transition: transform 0.3s; }
    .sticker-box:hover { transform: translateY(-5px) scale(1.05); }
    .st-gray { background-color: #2b2b2b; color: #666; border: 1px dashed #444; }
    .st-green { background-color: #28a745; color: white; border: 1px solid #1e7e34; }
    .log-entry { font-size: 0.85em; color: #888; border-bottom: 1px solid #333; padding: 5px 0; }
    .stat-card { background-color: #262730; padding: 15px; border-radius: 10px; border-top: 3px solid #007bff; transition: 0.3s; }
    .stat-card:hover { border-top: 3px solid #ffd700; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PARA FUEGOS ARTIFICIALES (Idea 5) ---
def lanzar_fuegos(nombre, meta, color_hex):
    # Colores para 100% (Rainbow)
    colors = "['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']" if meta == 100 else f"['{color_hex}']"
    
    components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
            var end = floatDate + (3 * 1000);
            var colors = {colors};

            (function frame() {{
              confetti({{
                particleCount: 5,
                angle: 60,
                spread: 55,
                origin: {{ x: 0 }},
                colors: colors
              }});
              confetti({{
                particleCount: 5,
                angle: 120,
                spread: 55,
                origin: {{ x: 1 }},
                colors: colors
              }});

              if (Date.now() < end) {{
                requestAnimationFrame(frame);
              }}
            }}());
        </script>
        <div style="text-align: center; font-family: sans-serif; color: {color_hex if meta < 100 else 'white'};">
            <h1 style="font-size: 50px;">🔥 ¡{nombre} llegó al {meta}%! 🔥</h1>
        </div>
    """, height=150)

# --- CONEXIÓN A DATOS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url_del_sheet, ttl="0")
df.columns = [str(c).strip().upper() for c in df.columns]

nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]
metas = {10: "#cd7f32", 25: "#c0c0c0", 50: "#007bff", 75: "#9b59b6", 90: "#e74c3c", 95: "#ffd700", 100: "MULTI"}

# Inicializar historial de metas para evitar spam de fuegos artificiales
if "metas_log" not in st.session_state:
    st.session_state.metas_log = {p: [] for p in nombres_papus}
if "log_actividad" not in st.session_state:
    st.session_state.log_actividad = []

def agregar_al_log(accion):
    st.session_state.log_actividad.insert(0, accion)
    if len(st.session_state.log_actividad) > 10: st.session_state.log_actividad.pop()

# --- 6. RANKING Y DETECCIÓN DE METAS ---
st.title("🏆 Control Albúm Papus")
total_total = len(df)

cols_rank = st.columns(len(nombres_papus))
for i, p in enumerate(nombres_papus):
    pegadas = len(df[df[p] > 0])
    porcentaje = round((pegadas / total_total) * 100, 1)
    
    # Lógica de Metas (Idea 5)
    for m, color in metas.items():
        if porcentaje >= m and m not in st.session_state.metas_log[p]:
            lanzar_fuegos(p, m, color if m < 100 else "#ffffff")
            st.session_state.metas_log[p].append(m)
            agregar_al_log(f"🚀 {p} ALCANZÓ EL {m}%")

    with cols_rank[i]:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style='margin:0; color:#007bff;'>{p}</h3>
            <p style='margin:0; font-size:1.5em;'><b>{porcentaje}%</b></p>
            <div style='background:#444; border-radius:5px; height:8px;'>
                <div style='background:#28a745; width:{porcentaje}%; height:8px; border-radius:5px; transition: width 1s ease-in-out;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR: CHISMÓGRAFO Y TRISTE REALIDAD ---
with st.sidebar:
    st.header("🕵️ Bitácora")
    for log in st.session_state.log_actividad:
        # Idea 7: Resaltar logs importantes
        color = "#ffd700" if "ALCANZÓ" in log else "#888"
        st.markdown(f"<div class='log-entry' style='color:{color};'>• {log}</div>", unsafe_allow_html=True)
    
    st.divider()
    st.header("📉 La Triste Realidad")
    usuario_stats = st.selectbox("Analizar a:", nombres_papus)
    faltantes = total_total - len(df[df[usuario_stats] > 0])
    prob_nueva = 1 - (((total_total - faltantes) / total_total) ** 7)
    sobres_faltantes = max(0, ((total_total * np.log(total_total) + 0.577 * total_total) / 7) - ((total_total - faltantes) / 7))
    
    st.write(f"**Faltantes:** {faltantes}")
    st.write(f"**Chanza en sig. sobre:** {round(prob_nueva*100, 1)}%")
    st.write(f"**Sobres promedio:** {int(sobres_faltantes)}")

# --- REGISTRO DE SOBRES ---
st.divider()
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
col_prio_mia = f"PRIORIDAD_{usuario}"

opciones = df['ESTAMPA'].tolist()
seleccionadas = st.multiselect("¿Cuáles te salieron perro?😯", opciones)

if seleccionadas:
    st.write("### 📋 Registro")
    cols = st.columns(4)
    cambios = {}
    for i, est in enumerate(seleccionadas):
        idx = df[df['ESTAMPA'] == est].index[0]
        with cols[i % 4]:
            with st.container(border=True):
                # Idea 4: Animación de entrada suave (implícita por el container)
                st.markdown(f"<h4 style='text-align:center;'>{est}</h4>", unsafe_allow_html=True)
                cambios[idx] = st.number_input("Cantidad", min_value=0, value=1, key=f"n_{est}")

    if st.button("💾 GUARDAR EVIDENCIA", type="primary", use_container_width=True):
        for idx, suma in cambios.items():
            if suma > 0: df.at[idx, usuario] += suma
        conn.update(spreadsheet=url_del_sheet, data=df)
        agregar_al_log(f"{usuario} registró {len(cambios)} estampas")
        st.success("¡Evidencia guardada, criminólogo! 🔎")
        st.rerun()

# --- MERCADO NEGRO Y CAZA-TRATOS ---
st.divider()
st.subheader("💱 Mercado Nigger")
t_mercado, t_caza = st.tabs(["Disponibles", "🤝 Tratos Ideales"])

with t_mercado:
    me_faltan = df[df[usuario] == 0]
    c1, c2 = st.columns(2)
    for i, (_, row) in enumerate(me_faltan.iterrows()):
        for otro in nombres_papus:
            if otro != usuario and row[otro] > 1:
                with (c1 if i % 2 == 0 else c2):
                    st.markdown(f"<div style='padding:10px; border-left:5px solid #007bff; background:#262730; margin-bottom:5px;'><b>{row['ESTAMPA']}</b> ➔ {otro}</div>", unsafe_allow_html=True)

with t_caza:
    trato = False
    for otro in nombres_papus:
        if otro != usuario:
            yo_le_doy = df[(df[usuario] > 1) & (df[otro] == 0)]['ESTAMPA'].tolist()
            el_me_da = df[(df[otro] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if yo_le_doy and el_me_da:
                trato = True
                st.success(f"🤝 **¡TRATO IDEAL CON {otro}!**")
                st.write(f"Tú le das: `{', '.join(yo_le_doy[:2])}...` | Él te da: `{', '.join(el_me_da[:2])}...`")

# --- ÁLBUM VIRTUAL PAGINADO ---
st.divider()
st.subheader(f"📔 Álbum Virtual ({usuario})")

# Filtros
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: f_falt = st.checkbox("Faltantes")
with col_f2: f_des = st.checkbox("Deseadas ⭐")
with col_f3: f_nadi = st.checkbox("Nadie las tiene")

df_d = df.copy()
if f_falt: df_d = df_d[df_d[usuario] == 0]
if f_des: df_d = df_d[df_d[col_prio_mia] > 0]
if f_nadi: df_d = df_d[(df_d[nombres_papus] == 0).all(axis=1)]

# Idea 6: El contenedor con línea de escaneo
st.markdown("<div class='scan-container'>", unsafe_allow_html=True)
items_p = 30
total_p = (len(df_d) - 1) // items_p + 1
if "p_alb" not in st.session_state: st.session_state.p_alb = 0

cp1, cp2, cp3 = st.columns([1,2,1])
with cp1: 
    if st.button("⬅️ Atrás") and st.session_state.p_alb > 0:
        st.session_state.p_alb -= 1
        st.rerun()
with cp2: st.markdown(f"<p style='text-align:center;'>Página {st.session_state.p_alb + 1} de {max(1, total_p)}</p>", unsafe_allow_html=True)
with cp3:
    if st.button("Siguiente ➡️") and st.session_state.p_alb < total_p - 1:
        st.session_state.p_alb += 1
        st.rerun()

chunk = df_d.iloc[st.session_state.p_alb*items_p : (st.session_state.album_page+1)*items_p] # Nota: se usó session_state.album_page por consistencia con el código anterior guardado
cols_alb = st.columns(6)

for i, (_, row) in enumerate(chunk.iterrows()):
    est, act, prio = row['ESTAMPA'], row[usuario], row[col_prio_mia]
    otros_f = [p for p in nombres_papus if p != usuario if row[p] == 0]
    
    if act > 1 and otros_f: css = "st-blue"
    elif act >= 1: css = "st-green"
    elif prio > 0: css = "st-gold"
    else: css = "st-gray"
    
    with cols_alb[i % 6]:
        st.markdown(f"<div class='sticker-box {css}'>{est}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# GESTIÓN DE DORADAS
st.divider()
st.subheader("⭐ MIS DESEADAS")
cg1, cg2 = st.columns(2)
with cg1:
    no_p = df[(df[col_prio_mia] == 0) & (df[usuario] == 0)]['ESTAMPA'].tolist()
    if no_p:
        p_add = st.selectbox("Agregar:", no_p, key="add")
        if st.button("✨ LA NECESITO"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], col_prio_mia] = 1
            conn.update(spreadsheet=url_del_sheet, data=df)
            st.rerun()
