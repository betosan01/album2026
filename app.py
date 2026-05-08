import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026 - Megazord Edition", layout="wide")

# --- ESTILOS CSS (ANIMACIONES + ESTILO BASE) ---
st.markdown("""
    <style>
    /* Animaciones de siempre */
    @keyframes shiny { 0% { background-position: -200%; } 100% { background-position: 200%; } }
    .st-gold { background: linear-gradient(110deg, #ffd700 45%, #fff9db 50%, #ffd700 55%); background-size: 200% 100%; animation: shiny 3s infinite linear; color: black !important; border: 2px solid #daa520 !important; }
    
    @keyframes pulse-blue { 0% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(0, 123, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0); } }
    .st-blue { animation: pulse-blue 2s infinite; background-color: #007bff !important; border: 2px solid #0056b3 !important; }

    @keyframes scanline { 0% { top: 0%; } 100% { top: 100%; } }
    .scan-container { position: relative; overflow: hidden; }
    .scan-container::after { content: ""; position: absolute; width: 100%; height: 2px; background: rgba(0, 255, 255, 0.4); top: 0; left: 0; animation: scanline 5s linear infinite; z-index: 10; pointer-events: none; }

    /* Estilos de tarjetas y Megazord */
    .megazord-card { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 20px; border-radius: 15px; border: 2px solid #60a5fa; margin-bottom: 25px; text-align: center; color: white; }
    .stat-card { background-color: #262730; padding: 15px; border-radius: 10px; border-top: 3px solid #007bff; text-align: center; }
    .insignia-span { font-size: 1.5em; cursor: help; margin-left: 5px; }
    .legend-box { padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 25px; display: flex; gap: 25px; flex-wrap: wrap; background-color: #1e1e1e; }
    .sticker-box { padding: 15px 5px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1em; transition: transform 0.3s; }
    .sticker-box:hover { transform: scale(1.1); }
    .st-gray { background-color: #2b2b2b; color: #666; border: 1px dashed #444; }
    .st-green { background-color: #28a745; color: white; border: 1px solid #1e7e34; }
    .shame-card { background-color: #4a1a1a; padding: 10px; border-radius: 5px; border: 1px solid #ff4b4b; color: #ff9b9b; font-size: 0.9em; }
    .log-entry { font-size: 0.85em; color: #bbb; border-bottom: 1px solid #333; padding: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- FUEGOS ARTIFICIALES ---
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
            <h2 style="font-size: 40px; margin: 0;">🎉 ¡{nombre} LLEVA EL {meta}%! 🤯</h2>
        </div>
    """, height=120)

# --- INICIALIZACIÓN DE ESTADOS DE SESIÓN ---
nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]
metas_colores = {10: "#cd7f32", 25: "#c0c0c0", 50: "#007bff", 75: "#9b59b6", 90: "#e74c3c", 95: "#ffd700", 100: "RAINBOW"}

if "metas_alcanzadas" not in st.session_state: st.session_state.metas_alcanzadas = {p: [] for p in nombres_papus}
if "racha_salada" not in st.session_state: st.session_state.racha_salada = {p: 0 for p in nombres_papus}
if "ultima_transaccion" not in st.session_state: st.session_state.ultima_transaccion = None
if "df_maestro" not in st.session_state: st.session_state.df_maestro = None
if "df_logs" not in st.session_state: st.session_state.df_logs = None

# Variables para las nuevas insignias que dependen de eventos o memoria
if "prev_rank" not in st.session_state: st.session_state.prev_rank = {}
if "insignias_eventos" not in st.session_state: st.session_state.insignias_eventos = {p: set() for p in nombres_papus}

# --- CONEXIÓN A DATOS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos_desde_google():
    try:
        temp_df = conn.read(spreadsheet=url_del_sheet, worksheet="SHEET1", ttl=0)
        temp_df.columns = [str(c).strip().upper() for c in temp_df.columns]
        st.session_state.df_maestro = temp_df
        try:
            temp_logs = conn.read(spreadsheet=url_del_sheet, worksheet="LOGS", ttl=0)
            st.session_state.df_logs = temp_logs
        except:
            st.session_state.df_logs = pd.DataFrame(columns=["FECHA", "ACCION"])
        return True
    except Exception as e:
        st.error(f"🚨 ¡Falla en la conexión! `{e}`")
        return False

def registrar_log_remoto(accion):
    hora_cdmx = datetime.utcnow() + timedelta(hours=-6)
    nueva_fila = pd.DataFrame([{"FECHA": hora_cdmx.strftime("%d/%m %H:%M"), "ACCION": accion}])
    if st.session_state.df_logs is not None:
        st.session_state.df_logs = pd.concat([nueva_fila, st.session_state.df_logs]).head(15)
    else:
        st.session_state.df_logs = nueva_fila
    try:
        conn.update(spreadsheet=url_del_sheet, worksheet="LOGS", data=st.session_state.df_logs)
    except:
        pass

if st.session_state.df_maestro is None:
    if not cargar_datos_desde_google():
        st.stop()

df = st.session_state.df_maestro

if st.sidebar.button("🔄 Sincronizar Datos", use_container_width=True):
    with st.spinner("Actualizando..."):
        if cargar_datos_desde_google():
            st.rerun()

# --- CÁLCULO DEL MEGAZORD ---
total_total = len(df)
estampas_squad = df[nombres_papus].any(axis=1).sum()
porcentaje_megazord = (estampas_squad / total_total) * 100
total_reps_squad = 0
for p in nombres_papus:
    total_reps_squad += int(df[df[p] > 1][p].sum() - len(df[df[p] > 1]))

st.markdown(f"""
    <div class="megazord-card">
        <h2 style='margin:0;'>🤖 MEGAZORD (SQUAD)</h2>
        <p style='font-size:1.2em; margin:5px;'>Llevan el <b>{porcentaje_megazord:.1f}%</b></p>
        <p style='font-size:1em; margin:2px;'>💰 Repetidas Squad: <b>{total_reps_squad}</b></p>
    </div>
""", unsafe_allow_html=True)
st.progress(porcentaje_megazord / 100)

# --- INSIGNIAS ---
def calcular_insignias(df_rank, df_completo, df_logs):
    insignias = {p: [] for p in nombres_papus}
    rank_positions = {row.PAPU: i+1 for i, row in enumerate(df_rank.itertuples())}
    if not st.session_state.prev_rank:
        st.session_state.prev_rank = rank_positions
    else:
        for p, pos in rank_positions.items():
            if st.session_state.prev_rank.get(p) == 1 and pos > 1:
                st.session_state.insignias_eventos[p].add("Cruzazuleado")
        st.session_state.prev_rank = rank_positions

    # 1. Big Papu
    el_patron = df_rank.iloc[0]['PAPU']
    insignias[el_patron].append(("👑", "Big Papu: Líder actual."))
    # 2. Cruzazuleado
    for p in nombres_papus:
        if "Cruzazuleado" in st.session_state.insignias_eventos[p]:
            insignias[p].append(("🚂", "Cruzazuleado: Pecheó el liderato."))
    # 3. Clonmadre
    for p in nombres_papus:
        if df_completo[p].max() >= 5:
            insignias[p].append(("📦", "Clonmadre: 3+ repetidas de una."))
    # 4. El Coyote
    tratos_count = {p: 0 for p in nombres_papus}
    for p in nombres_papus:
        for o in nombres_papus:
            if p != o:
                yo = df_completo[(df_completo[p] > 1) & (df_completo[o] == 0)].shape[0]
                el = df_completo[(df_completo[o] > 1) & (df_completo[p] == 0)].shape[0]
                tratos_count[p] += min(yo, el)
    el_coyote = max(tratos_count, key=tratos_count.get)
    if tratos_count[el_coyote] > 0:
        insignias[el_coyote].append(("🤝", "El Coyote: Rey del trueque."))
    # 8. El Funcionario
    hora_cdmx = datetime.utcnow() + timedelta(hours=-6)
    if df_logs is not None and not df_logs.empty:
        for p in nombres_papus:
            logs_p = df_logs[df_logs['ACCION'].str.contains(p, na=False)]
            if not logs_p.empty:
                last_date_str = logs_p.iloc[0]['FECHA']
                try:
                    last_date = datetime.strptime(f"{last_date_str}/{hora_cdmx.year}", "%d/%m %H:%M/%Y")
                    if (hora_cdmx - last_date).days >= 3:
                        insignias[p].append(("🐢", "El Funcionario: 3 días sin chambear."))
                except: pass
            else:
                insignias[p].append(("🐢", "El Funcionario: 3 días sin chambear."))
    else:
        for p in nombres_papus:
            insignias[p].append(("🐢", "El Funcionario: 3 días sin chambear."))

    return insignias

# --- POWER RANKING ---
st.subheader("📊 Power Ranking")
rank_data = []
for p in nombres_papus:
    pegadas = len(df[df[p] > 0])
    porcentaje = (pegadas / total_total) * 100
    repetidas = df[df[p] > 1][p].sum() - len(df[df[p] > 1])
    for m, color in metas_colores.items():
        if porcentaje >= m and m not in st.session_state.metas_alcanzadas[p]:
            lanzar_fuegos(p, m, color if m < 100 else "#ffffff")
            st.session_state.metas_alcanzadas[p].append(m)
            registrar_log_remoto(f"🔥 {p} SUBIÓ DE NIVEL: {m}%")
    rank_data.append({"PAPU": p, "PROGRESO": f"{porcentaje:.1f}%", "PEGADAS": pegadas, "REPETIDAS": int(repetidas), "PUNTOS": (pegadas * 2) + int(repetidas)})

df_rank = pd.DataFrame(rank_data).sort_values(by="PUNTOS", ascending=False)
dict_insignias = calcular_insignias(df_rank, df, st.session_state.df_logs)

cols_rank = st.columns(len(nombres_papus))
for i, row in enumerate(df_rank.itertuples()):
    with cols_rank[i]:
        mis_insig = "".join([f'<span title="{desc}" class="insignia-span">{icon}</span>' for icon, desc in dict_insignias[row.PAPU]])
        st.markdown(f"""
            <div class="stat-card">
                <h3 style='margin:0; color:#007bff;'>#{i+1} {row.PAPU}</h3>
                <div style='margin:10px 0;'>{mis_insig}</div>
                <p style='margin:0; font-size:1.2em;'><b>{row.PROGRESO}</b></p>
                <p style='margin:0; font-size:0.8em; color:#888;'>P: {row.PEGADAS} | R: {row.REPETIDAS}</p>
            </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🕵️ Bitácora")
    if st.session_state.df_logs is not None and not st.session_state.df_logs.empty:
        for _, log in st.session_state.df_logs.head(3).iterrows():
            st.markdown(f"<div class='log-entry'><b>[{log['FECHA']}]</b> {log['ACCION']}</div>", unsafe_allow_html=True)
    st.divider()
    st.header("💀 Muro de la Vergüenza")
    salado = False
    for p, racha in st.session_state.racha_salada.items():
        if racha >= 2:
            salado = True
            st.markdown(f"<div class='shame-card'>⚠️ <b>{p}</b> lleva {racha} registros de puras repetidas. 🤡</div>", unsafe_allow_html=True)
    if not salado: st.write("Suerte por ahora.😶‍🌫️")

# --- REGISTRO ---
st.divider()
st.subheader("📖 Registro de Sobres")
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
opciones = df['ESTAMPA'].tolist()
filtro_texto = st.text_input("🔍 Busca por código...", key="search_input").upper()

if "estampas_a_registrar" not in st.session_state: 
    st.session_state.estampas_a_registrar = {}

if filtro_texto:
    opciones_filtradas = [est for est in opciones if filtro_texto in est]
    if opciones_filtradas:
        st.write("👇 Selecciona las que te salieron:")
        cols_botones = st.columns(6)
        for i, est in enumerate(opciones_filtradas):
            idx = df[df['ESTAMPA'] == est].index[0]
            ya_la_tengo = df.at[idx, usuario] > 0
            with cols_botones[i % 6]:
                is_checked = est in st.session_state.estampas_a_registrar
                label = f"⚠️ {est}" if ya_la_tengo else f"✅ {est}"
                seleccion = st.toggle(label, value=is_checked, key=f"tg_{est}")
                if seleccion: st.session_state.estampas_a_registrar[est] = 1
                elif est in st.session_state.estampas_a_registrar: del st.session_state.estampas_a_registrar[est]
    else: st.warning("No se encontró, pai.🤨")

if st.session_state.estampas_a_registrar:
    st.write("### 📋 Lote Actual")
    cols_control = st.columns(4)
    cambios = {}
    for i, (est, cantidad) in enumerate(st.session_state.estampas_a_registrar.items()):
        idx = df[df['ESTAMPA'] == est].index[0]
        with cols_control[i % 4]:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align:center;'>{est}</h4>", unsafe_allow_html=True)
                cambios[idx] = st.number_input("Cantidad", min_value=1, value=cantidad, key=f"num_{est}")

    if st.button("💾 Guardar al toque pa", type="primary", use_container_width=True):
        transaccion_actual = {"user": usuario, "cambios": cambios.copy()}
        if st.session_state.ultima_transaccion == transaccion_actual:
            st.warning("¡Doble clic evitado! 🛑")
        else:
            with st.spinner("Subiendo..."):
                nuevas = 0
                for idx, suma in cambios.items():
                    if suma > 0:
                        if df.at[idx, usuario] == 0: nuevas += 1
                        df.at[idx, usuario] += suma
                st.session_state.racha_salada[usuario] = 0 if nuevas > 0 else st.session_state.racha_salada[usuario] + 1
                try:
                    conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                    st.session_state.df_maestro = df
                    st.session_state.ultima_transaccion = transaccion_actual
                    try: registrar_log_remoto(f"{usuario} registró {len(cambios)} estampas")
                    except: pass
                    # --- LIMPIEZA TOTAL ---
                    st.session_state["search_input"] = ""
                    for est_key in list(st.session_state.estampas_a_registrar.keys()):
                        if f"tg_{est_key}" in st.session_state: del st.session_state[f"tg_{est_key}"]
                        if f"num_{est_key}" in st.session_state: del st.session_state[f"num_{est_key}"]
                    st.session_state.estampas_a_registrar = {}
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Error al conectar: {e}")

# --- INVENTARIO REPETIDAS ---
st.divider()
st.subheader(f"📋 Repetidas ({usuario})")
df_reps = df[df[usuario] > 1][['ESTAMPA', usuario]].copy()
if not df_reps.empty:
    df_reps_edited = st.data_editor(df_reps, column_config={usuario: st.column_config.NumberColumn("Total", min_value=1), "ESTAMPA": st.column_config.Column(disabled=True)}, hide_index=True, use_container_width=True, key=f"ed_{usuario}")
    if st.button("🔄 Actualizar Cantidades"):
        with st.spinner("Ajustando..."):
            for _, row in df_reps_edited.iterrows():
                idx_real = df[df['ESTAMPA'] == row['ESTAMPA']].index[0]
                df.at[idx_real, usuario] = row[usuario]
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                registrar_log_remoto(f"🕵️ {usuario} ajustó inventario")
                st.rerun()
            except: st.error("🚨 API saturada.")
else: st.info("Sin repetidas. 🍀")

# --- TRATOS ---
st.divider()
st.subheader("💱 Tratos Pro🤯")
t1, t2 = st.tabs(["Disponibles🔁", "Ideal Squid🦑"])
with t1:
    me_faltan = df[df[usuario] == 0]
    for _, row in me_faltan.iterrows():
        for o in nombres_papus:
            if o != usuario and row[o] > 1: st.markdown(f"**{row['ESTAMPA']}** ➔ Ruégale a **{o}**")
with t2:
    for o in nombres_papus:
        if o != usuario:
            yo = df[(df[usuario] > 1) & (df[o] == 0)]['ESTAMPA'].tolist()
            el = df[(df[o] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if yo and el: st.success(f"🔥 **TRATO IDEAL CON {o}!** Tú: {yo[:2]} | Él: {el[:2]}")

# --- ÁLBUM VIRTUAL ---
st.divider()
st.subheader(f"📔 Álbum Virtual ({usuario})")
df_v = df.copy()
chunk = df_v.head(30)
cols_a = st.columns(6)
for i, (_, r) in enumerate(chunk.iterrows()):
    act = r[usuario]
    css = "st-blue" if act > 1 else "st-green" if act >= 1 else "st-gray"
    with cols_a[i % 6]: st.markdown(f"<div class='sticker-box {css}'>{r['ESTAMPA']}</div>", unsafe_allow_html=True)
