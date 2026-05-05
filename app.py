import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026", layout="wide")

# --- ESTILOS CSS (ANIMACIONES + TU ESTILO BASE) ---
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
    .scan-container { position: relative; overflow: hidden; }
    .scan-container::after {
        content: ""; position: absolute; width: 100%; height: 2px;
        background: rgba(0, 255, 255, 0.4); top: 0; left: 0;
        animation: scanline 5s linear infinite; z-index: 10; pointer-events: none;
    }

    /* Estilos de tus cajas y leyendas */
    .legend-box { padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 25px; display: flex; gap: 25px; flex-wrap: wrap; background-color: #1e1e1e; }
    .legend-item { display: flex; align-items: center; gap: 10px; font-size: 0.95em; color: #fafafa; }
    .circle { height: 18px; width: 18px; border-radius: 50%; display: inline-block; border: 1px solid #777; }
    .sticker-box { padding: 15px 5px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1em; transition: transform 0.3s; }
    .sticker-box:hover { transform: scale(1.1); }
    .st-gray { background-color: #2b2b2b; color: #666; border: 1px dashed #444; }
    .st-green { background-color: #28a745; color: white; border: 1px solid #1e7e34; }
    .log-entry { font-size: 0.85em; color: #888; border-bottom: 1px solid #333; padding: 5px 0; }
    .stat-card { background-color: #262730; padding: 15px; border-radius: 10px; border-top: 3px solid #007bff; }
    .shame-card { background-color: #4a1a1a; padding: 10px; border-radius: 5px; border: 1px solid #ff4b4b; color: #ff9b9b; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE FUEGOS ARTIFICIALES ---
def lanzar_fuegos(nombre, meta, color_hex):
    is_rainbow = (meta == 100)
    colors = "['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']" if is_rainbow else f"['{color_hex}']"
    components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
            var end = Date.now() + (4 * 1000);
            var colors = {colors};
            (function frame() {{
              confetti({{ particleCount: 7, angle: 60, spread: 55, origin: {{ x: 0 }}, colors: colors }});
              confetti({{ particleCount: 7, angle: 120, spread: 55, origin: {{ x: 1 }}, colors: colors }});
              if (Date.now() < end) {{ requestAnimationFrame(frame); }}
            }}());
        </script>
        <div style="text-align: center; font-family: sans-serif; color: {'white' if is_rainbow else color_hex};">
            <h2 style="font-size: 40px; margin: 0;">🎉 ¡{nombre} LLEGÓ AL {meta}%! 🎉</h2>
        </div>
    """, height=120)

# --- CONEXIÓN A DATOS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url_del_sheet, ttl="0")
df.columns = [str(c).strip().upper() for c in df.columns]

nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]
metas_colores = {10: "#cd7f32", 25: "#c0c0c0", 50: "#007bff", 75: "#9b59b6", 90: "#e74c3c", 95: "#ffd700", 100: "RAINBOW"}

# --- INICIALIZACIÓN DE ESTADOS ---
if "log_actividad" not in st.session_state: st.session_state.log_actividad = []
if "metas_alcanzadas" not in st.session_state: st.session_state.metas_alcanzadas = {p: [] for p in nombres_papus}
if "racha_salada" not in st.session_state: st.session_state.racha_salada = {p: 0 for p in nombres_papus}

def agregar_al_log(accion):
    st.session_state.log_actividad.insert(0, accion)
    if len(st.session_state.log_actividad) > 10: st.session_state.log_actividad.pop()

# --- RANKING DE COLECCIONISTAS ---
st.title("🏆 Control Albúm Papus")
st.subheader("📊 Power Ranking del Squad")
rank_data = []
total_total = len(df)

for p in nombres_papus:
    pegadas = len(df[df[p] > 0])
    porcentaje = (pegadas / total_total) * 100
    repetidas = df[df[p] > 1][p].sum() - len(df[df[p] > 1])
    
    for m, color in metas_colores.items():
        if porcentaje >= m and m not in st.session_state.metas_alcanzadas[p]:
            lanzar_fuegos(p, m, color if m < 100 else "#ffffff")
            st.session_state.metas_alcanzadas[p].append(m)
            agregar_al_log(f"🔥 {p} SUBIÓ DE NIVEL: {m}% ALCANZADO")

    rank_data.append({"PAPU": p, "PROGRESO": f"{porcentaje:.1f}%", "PEGADAS": pegadas, "REPETIDAS": int(repetidas), "PUNTOS": (pegadas * 2) + int(repetidas)})

df_rank = pd.DataFrame(rank_data).sort_values(by="PUNTOS", ascending=False)
cols_rank = st.columns(len(nombres_papus))
for i, row in enumerate(df_rank.itertuples()):
    with cols_rank[i]:
        st.markdown(f"""<div class="stat-card"><h3 style='margin:0; color:#007bff;'>#{i+1} {row.PAPU}</h3><p style='margin:0; font-size:1.2em;'><b>{row.PROGRESO}</b></p><p style='margin:0; font-size:0.8em; color:#888;'>Pegadas: {row.PEGADAS} | Reps: {row.REPETIDAS}</p></div>""", unsafe_allow_html=True)

# --- SIDEBAR: CHISMÓGRAFO, TRISTE REALIDAD Y MURO DE LA VERGÜENZA ---
with st.sidebar:
    st.header("🕵️ Bitácora de Evidencias")
    if not st.session_state.log_actividad:
        st.write("Nadie le ha movido pa🕴🏼")
    for log in st.session_state.log_actividad:
        color = "#ffd700" if "NIVEL" in log else "#888"
        st.markdown(f"<div class='log-entry' style='color:{color};'>• {log}</div>", unsafe_allow_html=True)
    
    st.divider()
    st.header("💀 Muro de la Vergüenza")
    alguien_salado = False
    for p, racha in st.session_state.racha_salada.items():
        if racha >= 2:
            alguien_salado = True
            st.markdown(f"""<div class='shame-card'>⚠️ <b>{p}</b> lleva {racha} registros de puras repetidas. ¡Ta´ saladísimo! 🤡</div>""", unsafe_allow_html=True)
    if not alguien_salado:
        st.write("Todos traen suerte... por ahora.😶‍🌫️")

    st.divider()
    st.header("Triste Realidad🤡")
    usuario_stats = st.selectbox("Analizar a:", nombres_papus, key="stats_user")
    faltantes = total_total - len(df[df[usuario_stats] > 0])
    prob_nueva = 1 - (((total_total - faltantes) / total_total) ** 7)
    sobres_estimados = (total_total * np.log(total_total) + 0.577 * total_total) / 7
    sobres_faltantes = max(0, sobres_estimados - ((total_total - faltantes) / 7))
    
    st.write(f"**Te faltan:** {faltantes} estampas.🫡")
    st.write(f"**Chances de nueva en sig. sobre🥸:** {prob_nueva*100:.1f}%")
    st.write(f"**Sobres pa' terminar💦** {int(sobres_faltantes)}")

# --- SIMBOLOGÍA ---
st.markdown("""<div class="legend-box"><div class="legend-item"><span class="circle" style="background-color: #f0f2f6;"></span> <b>Gris:</b> No la tienes🤣🫵</div><div class="legend-item"><span class="circle" style="background-color: #28a745;"></span> <b>Verde:</b> Ya la tienes😎</div><div class="legend-item"><span class="circle" style="background-color: #007bff;"></span> <b>Azul:</b> Alguien la necesita🤑</div><div class="legend-item"><span class="circle" style="background-color: #ffd700;"></span> <b>Dorado:</b> Tus deseadas ⭐</div></div>""", unsafe_allow_html=True)

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
    for i, estampa in enumerate(seleccionadas):
        idx = df[df['ESTAMPA'] == estampa].index[0]
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align:center; margin-bottom: 0px;'>{estampa}</h4>", unsafe_allow_html=True)
                cambios_pendientes[idx] = st.number_input("Cantidad", min_value=0, value=1, key=f"num_{estampa}")

    if st.button("💾 Al toque pa, ya los puedes guardar", type="primary", use_container_width=True):
        nuevas_detectadas = 0
        for idx_cambio, suma in cambios_pendientes.items():
            if suma > 0:
                if df.at[idx_cambio, usuario] == 0: nuevas_detectadas += 1
                df.at[idx_cambio, usuario] += suma
        
        if nuevas_detectadas == 0:
            st.session_state.racha_salada[usuario] += 1
            if st.session_state.racha_salada[usuario] >= 2:
                agregar_al_log(f"🤡 {usuario} registró puras repetidas (Racha: {st.session_state.racha_salada[usuario]})")
        else:
            st.session_state.racha_salada[usuario] = 0

        conn.update(spreadsheet=url_del_sheet, data=df)
        agregar_al_log(f"{usuario} registró {len(cambios_pendientes)} estampas")
        st.success("¡Sincronizado!🔥")
        st.rerun()

# --- NUEVO: INVENTARIO DE REPETIDAS EDITABLE ---
st.divider()
st.subheader(f"📋 Mi Inventario de Repetidas ({usuario})")
st.write("Aquí solo salen las que tienes de más. Edítalas si registraste mal.")

df_reps = df[df[usuario] > 1][['ESTAMPA', usuario]].copy()

if not df_reps.empty:
    # Usamos st.data_editor para que sea una tabla interactiva y rápida
    # Solo permitimos editar la columna del usuario
    df_reps_edited = st.data_editor(
        df_reps,
        column_config={
            usuario: st.column_config.NumberColumn(
                f"Cantidad Total ({usuario})",
                help="1 es pegada, 2+ son repetidas",
                min_value=1, # No dejamos bajar de 1 para no borrar la que ya pegó
                step=1,
            ),
            "ESTAMPA": st.column_config.Column(disabled=True)
        },
        hide_index=True,
        use_container_width=True,
        key=f"editor_{usuario}"
    )

    if st.button("🔄 Actualizar Cantidades 🛠️"):
        # Detectar qué filas cambiaron
        for i, row in df_reps_edited.iterrows():
            orig_val = df_reps.iloc[i][usuario]
            new_val = row[usuario]
            if orig_val != new_val:
                idx = df[df['ESTAMPA'] == row['ESTAMPA']].index[0]
                df.at[idx, usuario] = new_val
        
        conn.update(spreadsheet=url_del_sheet, data=df)
        agregar_al_log(f"🕵️ {usuario} ajustó su inventario de repetidas")
        st.success("¡Cantidades corregidas! 🔎")
        st.rerun()
else:
    st.info("No tienes repetidas registradas todavía. ¡Suerte con los sobres! 🍀")


# --- BAJAS DEL INVENTARIO ---
with st.expander("🗑️ Bajas del Inventario (Regaladas fuera)"):
    mis_reps_list = df[df[usuario] > 1]['ESTAMPA'].tolist()
    if mis_reps_list:
        reps_baja = st.multiselect("¿Cuáles se fueron?💸", mis_reps_list)
        if reps_baja:
            bajas_pendientes = {}
            for r in reps_baja:
                bajas_pendientes[r] = st.number_input(f"Cuántas de {r}", min_value=1, max_value=int(df[df['ESTAMPA']==r][usuario].values[0]-1), key=f"del_{r}")
            if st.button("Adios popó 💩"):
                for est, cant in bajas_pendientes.items():
                    df.at[df[df['ESTAMPA'] == est].index[0], usuario] -= cant
                conn.update(spreadsheet=url_del_sheet, data=df)
                agregar_al_log(f"⚠️ {usuario} eliminó {sum(bajas_pendientes.values())} repetidas del sistema")
                st.rerun()
    else:
        st.write("No se da lo que no se tiene papu.🤨")

# --- MERCADO NIGGER ---
st.divider()
st.subheader("💱 Mercado Nigger & Tratos Mega Pro🤯")
tab1, tab2, tab3 = st.tabs(["Repetidas Disponibles", "🤝 Un precio justo🦑", "🔄 Triangulaciones"])

with tab1:
    me_faltan = df[df[usuario] == 0]
    hay_inter = False
    c_m1, c_m2 = st.columns(2)
    for i, (_, row) in enumerate(me_faltan.iterrows()):
        for otro in nombres_papus:
            if otro != usuario and row[otro] > 1:
                hay_inter = True
                with (c_m1 if i % 2 == 0 else c_m2):
                    st.markdown(f"<div style='padding:10px; border-left:5px solid #28a745; background:#262730; margin-bottom:5px;'><b>{row['ESTAMPA']}</b> ➔ Ruégale a <b>{otro}</b></div>", unsafe_allow_html=True)
    if not hay_inter: st.info("Ni modo pa, nadie la trae🫥")

with tab2:
    trato = False
    for otro in nombres_papus:
        if otro != usuario:
            yo_doy = df[(df[usuario] > 1) & (df[otro] == 0)]['ESTAMPA'].tolist()
            el_da = df[(df[otro] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if yo_doy and el_da:
                trato = True
                st.success(f"🔥 **¡TRATO IDEAL CON {otro}!**")
                st.write(f"Tú le das: `{', '.join(yo_doy[:3])}` | Él te da: `{', '.join(el_da[:3])}`")

with tab3:
    triangulos = []
    otros = [p for p in nombres_papus if p != usuario]
    for b in otros:
        for c in [p for p in otros if p != b]:
            yo_a_b = df[(df[usuario] > 1) & (df[b] == 0)]['ESTAMPA'].tolist()
            b_a_c = df[(df[b] > 1) & (df[c] == 0)]['ESTAMPA'].tolist()
            c_a_yo = df[(df[c] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if yo_a_b and b_a_c and c_a_yo:
                triangulos.append(f"🔄 **¡TENEMOS TRÍOO!🥵** Tú le das a **{b}**, {b} le da a **{c}**, y **{c}** te da a ti.")
    if triangulos:
        for t in triangulos: st.info(t)
    else:
        st.write("No hay tríos disponibles por ahora.😢")

# --- ÁLBUM VIRTUAL PAGINADO ---
st.divider()
st.subheader(f"📔 Álbum Virtual ({usuario})")
f1, f2, f3 = st.columns(3)
with f1: f_faltantes = st.checkbox("Las que me faltan🙁")
with f2: f_deseadas = st.checkbox("Las deseadas🤩")
with f3: f_nadie = st.checkbox("Ningún papu las tiene🙁")

df_d = df.copy()
if f_faltantes: df_d = df_d[df_d[usuario] == 0]
if f_deseadas: df_d = df_d[df_d[col_prioridad_mia] > 0]
if f_nadie: df_d = df_d[(df_d[nombres_papus] == 0).all(axis=1)]

st.markdown("<div class='scan-container'>", unsafe_allow_html=True)
ITEMS_PAG = 30
total_p = (len(df_d) - 1) // ITEMS_PAG + 1
if "album_page" not in st.session_state: st.session_state.album_page = 0
cp1, cp2, cp3 = st.columns([1,2,1])
with cp1: 
    if st.button("⬅️ Va pa´tras") and st.session_state.album_page > 0:
        st.session_state.album_page -= 1
        st.rerun()
with cp2: st.markdown(f"<p style='text-align:center;'>Página {st.session_state.album_page + 1} de {max(1, total_p)}</p>", unsafe_allow_html=True)
with cp3:
    if st.button("Va pa´lante ➡️") and st.session_state.album_page < total_p - 1:
        st.session_state.album_page += 1
        st.rerun()

chunk = df_d.iloc[st.session_state.album_page*ITEMS_PAG : (st.session_state.album_page+1)*ITEMS_PAG]
cols_alb = st.columns(6)
for i, (_, row) in enumerate(chunk.iterrows()):
    est, act, prio = row['ESTAMPA'], row[usuario], row[col_prioridad_mia]
    otros_f = [p for p in nombres_papus if p != usuario if row[p] == 0]
    if act > 1 and otros_f: css = "st-blue"
    elif act >= 1: css = "st-green"
    elif prio > 0: css = "st-gold"
    else: css = "st-gray"
    with cols_alb[i % 6]: st.markdown(f"<div class='sticker-box {css}'>{est}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# GESTIÓN DE DORADAS
st.divider()
st.subheader(f"⭐ TUS MÁS DESEADAS ({usuario})")
cg1, cg2 = st.columns(2)
with cg1:
    no_p = df[(df[col_prioridad_mia] == 0) & (df[usuario] == 0)]['ESTAMPA'].tolist()
    if no_p:
        p_add = st.selectbox("Marcar como Dorada:", no_p, key="add_g")
        if st.button("✨ LA NECESITOOOOOOO🧽"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], col_prioridad_mia] = 1
            conn.update(spreadsheet=url_del_sheet, data=df)
            agregar_al_log(f"{usuario} marcó {p_add} como dorada")
            st.rerun()
with cg2:
    si_p = df[df[col_prioridad_mia] > 0]['ESTAMPA'].tolist()
    if si_p:
        p_rem = st.selectbox("Quitar de Doradas:", si_p, key="rem_g")
        if st.button("❌ Ya no va"):
            df.at[df[df['ESTAMPA'] == p_rem].index[0], col_prioridad_mia] = 0
            conn.update(spreadsheet=url_del_sheet, data=df)
            st.rerun()
