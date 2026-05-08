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
    /* Animaciones */
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
    .sticker-box { padding: 15px 5px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1em; transition: transform 0.3s; color: white; }
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
        st.error(f"🚨 Falla en la Escena del Crimen: {e}")
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
    except: pass

# Cargar la primera vez
if st.session_state.df_maestro is None:
    if not cargar_datos_desde_google(): st.stop()

df = st.session_state.df_maestro

# --- SIDEBAR & BITÁCORA ---
with st.sidebar:
    if st.button("🔄 Sincronizar Datos", use_container_width=True):
        if cargar_datos_desde_google(): st.rerun()
    
    with st.expander("📖 Glosario de Insignias"):
        st.markdown("""👑 **Big Papu** | 🚂 **Cruzazuleado** | 📦 **Clonmadre** | 🤝 **El Coyote** | 🛍️ **El Fayuquero** | 🤲 **El Hambreado** | 🎯 **El Bendecido** | 🐢 **El Funcionario** | 🧂 **El Salitre** | 🥵 **El Ya Merito**""")
    
    st.divider()
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
    if not salado: st.write("Todos traen suerte... por ahora.😶‍🌫️")

# --- MEGAZORD ---
total_total = len(df)
estampas_squad = df[nombres_papus].any(axis=1).sum()
porcentaje_megazord = (estampas_squad / total_total) * 100
total_reps_squad = sum([int(df[df[p] > 1][p].sum() - len(df[df[p] > 1])) for p in nombres_papus])

st.markdown(f"""
    <div class="megazord-card">
        <h2 style='margin:0;'>🤖 MEGAZORD (SQUAD)</h2>
        <p style='font-size:1.2em; margin:5px;'>Llevan el <b>{porcentaje_megazord:.1f}%</b> del Álbum</p>
        <p style='font-size:1em; margin:2px;'>💰 Repetidas en Bodega Squad: <b>{total_reps_squad}</b></p>
    </div>
""", unsafe_allow_html=True)
st.progress(porcentaje_megazord / 100)

# --- LÓGICA DE INSIGNIAS ---
def calcular_insignias(df_rank, df_completo, df_logs):
    insignias = {p: [] for p in nombres_papus}
    rank_positions = {row.PAPU: i+1 for i, row in enumerate(df_rank.itertuples())}
    if st.session_state.prev_rank:
        for p, pos in rank_positions.items():
            if st.session_state.prev_rank.get(p) == 1 and pos > 1:
                st.session_state.insignias_eventos[p].add("Cruzazuleado")
    st.session_state.prev_rank = rank_positions

    # 1. Big Papu
    if not df_rank.empty: insignias[df_rank.iloc[0]['PAPU']].append(("👑", "Big Papu"))
    
    for p in nombres_papus:
        if "Cruzazuleado" in st.session_state.insignias_eventos[p]: insignias[p].append(("🚂", "Cruzazuleado"))
        if df_completo[p].max() >= 5: insignias[p].append(("📦", "Clonmadre"))
        if "Fayuquero" in st.session_state.insignias_eventos[p]: insignias[p].append(("🛍️", "El Fayuquero"))
        if "Bendecido" in st.session_state.insignias_eventos[p]: insignias[p].append(("🎯", "El Bendecido"))

    # 6. El Hambreado
    deseadas_counts = {p: df_completo[f"PRIORIDAD_{p}"].sum() for p in nombres_papus}
    hambreados = [p for p in nombres_papus if df_rank[df_rank['PAPU'] == p]['REPETIDAS'].values[0] == 0 and deseadas_counts[p] > 0]
    if hambreados:
        el_h = max(hambreados, key=lambda x: deseadas_counts[x])
        insignias[el_h].append(("🤲", "El Hambreado"))

    # 8. El Funcionario
    hora_cdmx = datetime.utcnow() + timedelta(hours=-6)
    for p in nombres_papus:
        if df_logs is not None and not df_logs.empty:
            logs_p = df_logs[df_logs['ACCION'].str.contains(p, na=False)]
            if not logs_p.empty:
                try:
                    last_date = datetime.strptime(f"{logs_p.iloc[0]['FECHA']}/{hora_cdmx.year}", "%d/%m %H:%M/%Y")
                    if (hora_cdmx - last_date).days >= 3: insignias[p].append(("🐢", "El Funcionario"))
                except: pass
            else: insignias[p].append(("🐢", "El Funcionario"))

    # 9. El Salitre
    salitre_ratio = {}
    for p in nombres_papus:
        row = df_rank[df_rank['PAPU'] == p].iloc[0]
        prog = float(row['PROGRESO'].replace('%',''))
        if prog < 50: salitre_ratio[p] = row['REPETIDAS'] / row['PEGADAS'] if row['PEGADAS'] > 0 else 0
        else: salitre_ratio[p] = 0
    if salitre_ratio and any(v > 0.5 for v in salitre_ratio.values()):
        el_s = max(salitre_ratio, key=salitre_ratio.get)
        insignias[el_s].append(("🧂", "El Salitre"))

    return insignias

# --- POWER RANKING ---
rank_data = []
for p in nombres_papus:
    pegadas = len(df[df[p] > 0])
    porcentaje = (pegadas / total_total) * 100
    repetidas = df[df[p] > 1][p].sum() - len(df[df[p] > 1])
    for m, color in metas_colores.items():
        if porcentaje >= m and m not in st.session_state.metas_alcanzadas[p]:
            lanzar_fuegos(p, m, color if m < 100 else "#ffffff")
            st.session_state.metas_alcanzadas[p].append(m)
            registrar_log_remoto(f"🔥 {p} SUBIÓ NIVEL: {m}%")
    rank_data.append({"PAPU": p, "PROGRESO": f"{porcentaje:.1f}%", "PEGADAS": pegadas, "REPETIDAS": int(repetidas), "PUNTOS": (pegadas * 2) + int(repetidas)})

df_rank = pd.DataFrame(rank_data).sort_values(by="PUNTOS", ascending=False)
dict_insignias = calcular_insignias(df_rank, df, st.session_state.df_logs)

st.subheader("📊 Power Ranking")
cols_r = st.columns(4)
for i, row in enumerate(df_rank.itertuples()):
    with cols_r[i]:
        mis_i = "".join([f'<span title="{desc}" class="insignia-span">{icon}</span>' for icon, desc in dict_insignias[row.PAPU]])
        st.markdown(f"<div class='stat-card'><h3 style='margin:0; color:#007bff;'>#{i+1} {row.PAPU}</h3><div>{mis_i}</div><p style='font-size:1.2em;'><b>{row.PROGRESO}</b></p><p style='font-size:0.8em; color:#888;'>P: {row.PEGADAS} | R: {row.REPETIDAS}</p></div>", unsafe_allow_html=True)

# --- REGISTRO DE SOBRES ---
st.divider()
st.subheader("📖 Registro de Sobres")
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
filtro_texto = st.text_input("🔍 Busca por código...").upper()

if "estampas_a_registrar" not in st.session_state: st.session_state.estampas_a_registrar = {}

if filtro_texto:
    opciones_f = [est for est in df['ESTAMPA'].tolist() if filtro_texto in est]
    if opciones_f:
        cols_b = st.columns(6)
        for i, est in enumerate(opciones_f[:18]):
            idx = df[df['ESTAMPA'] == est].index[0]
            ya = df.at[idx, usuario] > 0
            with cols_b[i % 6]:
                if st.toggle(f"{'⚠️' if ya else '✅'} {est}", key=f"tg_{est}"):
                    st.session_state.estampas_a_registrar[est] = 1
                elif est in st.session_state.estampas_a_registrar:
                    del st.session_state.estampas_a_registrar[est]

if st.session_state.estampas_a_registrar:
    st.write("### 📋 Panel de Control")
    cambios = {}
    cols_c = st.columns(4)
    for i, (est, cant) in enumerate(st.session_state.estampas_a_registrar.items()):
        with cols_c[i % 4]:
            cambios[df[df['ESTAMPA']==est].index[0]] = st.number_input(f"Cant {est}", 1, 10, cant, key=f"num_{est}")
    
    if st.button("💾 Guardar al toque", type="primary", use_container_width=True):
        nuevas = 0
        for idx, suma in cambios.items():
            if df.at[idx, usuario] == 0: nuevas += 1
            df.at[idx, usuario] += suma
        if sum(cambios.values()) > 15: st.session_state.insignias_eventos[usuario].add("Fayuquero")
        if nuevas >= 4: st.session_state.insignias_eventos[usuario].add("Bendecido")
        st.session_state.racha_salada[usuario] = 0 if nuevas > 0 else st.session_state.racha_salada[usuario] + 1
        conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
        registrar_log_remoto(f"{usuario} registró {len(cambios)} estampas")
        st.session_state.estampas_a_registrar = {}
        st.rerun()

# --- INVENTARIO DE REPETIDAS ---
st.divider()
st.subheader(f"📋 Repetidas ({usuario})")
df_reps = df[df[usuario] > 1][['ESTAMPA', usuario]].copy()
if not df_reps.empty:
    df_reps_ed = st.data_editor(df_reps, hide_index=True, use_container_width=True, key=f"ed_{usuario}")
    if st.button("🔄 Actualizar Cantidades"):
        for _, row in df_reps_ed.iterrows():
            df.at[df[df['ESTAMPA'] == row['ESTAMPA']].index[0], usuario] = row[usuario]
        conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
        st.rerun()

# --- ADIOS POPÓ (BAJAS) ---
st.divider()
with st.expander("🗑️ Adios popó 💩 (Bajas externas)"):
    mis_reps = df[df[usuario] > 1]['ESTAMPA'].tolist()
    if mis_reps:
        bajas = st.multiselect("¿Cuáles se fueron?💸", mis_reps)
        if bajas:
            b_pend = {r: st.number_input(f"Cant {r}", 1, int(df[df['ESTAMPA']==r][usuario].values[0]-1), key=f"d_{r}") for r in bajas}
            if st.button("Confirmar baja"):
                for e, c in b_pend.items(): df.at[df[df['ESTAMPA'] == e].index[0], usuario] -= c
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                registrar_log_remoto(f"⚠️ {usuario} dio bajas")
                st.rerun()

# --- TRATOS Y MERCADO ---
st.divider()
st.subheader("💱 Mercado & Tratos Pro")
t1, t2, t3 = st.tabs(["Disponibles🔁", "Un precio justo🦑", "Tríos🥵"])
with t1:
    me_f = df[df[usuario] == 0]
    for _, row in me_f.iterrows():
        for o in nombres_papus:
            if o != usuario and row[o] > 1: st.markdown(f"**{row['ESTAMPA']}** ➔ Ruégale a **{o}**")
with t2:
    for o in [p for p in nombres_papus if p != usuario]:
        yo = df[(df[usuario] > 1) & (df[o] == 0)]['ESTAMPA'].tolist()
        el = df[(df[o] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
        if yo and el: st.success(f"🔥 **TRUEQUE CON {o}!** Tú das {yo[0]} | Él da {el[0]}")
with t3:
    otros = [p for p in nombres_papus if p != usuario]
    for b in otros:
        for c in [p for p in otros if p != b]:
            if not df[(df[usuario]>1)&(df[b]==0)].empty and not df[(df[b]>1)&(df[c]==0)].empty and not df[(df[c]>1)&(df[usuario]==0)].empty:
                st.info(f"🔄 **TRÍO!** Tú ➔ {b} ➔ {c} ➔ Tú")

# --- ÁLBUM VIRTUAL ---
st.divider()
st.subheader(f"📔 Álbum Virtual ({usuario})")
f1, f2, f3 = st.columns(3)
with f1: f_f = st.checkbox("Faltantes🙁")
with f2: f_d = st.checkbox("Deseadas🤩")
with f3: f_n = st.checkbox("Nadie las tiene🙁")
df_v = df.copy()
if f_f: df_v = df_v[df_v[usuario] == 0]
if f_d: df_v = df_v[df_v[f"PRIORIDAD_{usuario}"] > 0]
if f_n: df_v = df_v[(df_v[nombres_papus] == 0).all(axis=1)]

if "p_a" not in st.session_state: st.session_state.p_a = 0
chunk = df_v.iloc[st.session_state.p_a*30 : (st.session_state.p_a+1)*30]
st.markdown("<div class='scan-container'>", unsafe_allow_html=True)
cols_a = st.columns(6)
for i, (_, r) in enumerate(chunk.iterrows()):
    act = r[usuario]
    css = "st-blue" if act > 1 else "st-green" if act == 1 else "st-gold" if r[f"PRIORIDAD_{usuario}"] > 0 else "st-gray"
    with cols_a[i % 6]: st.markdown(f"<div class='sticker-box {css}'>{r['ESTAMPA']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

cp1, cp2, cp3 = st.columns([1,2,1])
with cp1: 
    if st.button("⬅️ Atrás") and st.session_state.p_a > 0: st.session_state.p_a -= 1; st.rerun()
with cp3: 
    if st.button("Adelante ➡️") and (st.session_state.p_a+1)*30 < len(df_v): st.session_state.p_a += 1; st.rerun()

# --- DORADAS ---
st.divider()
st.subheader("⭐ TUS MÁS DESEADAS")
cg1, cg2 = st.columns(2)
with cg1:
    no_p = df[(df[f"PRIORIDAD_{usuario}"] == 0) & (df[usuario] == 0)]['ESTAMPA'].tolist()
    if no_p:
        p_add = st.selectbox("Marcar como Dorada:", no_p)
        if st.button("✨ LA NECESITOOOOOOO🧽"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], f"PRIORIDAD_{usuario}"] = 1
            conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
            registrar_log_remoto(f"🤩 {usuario} marcó dorada: {p_add}")
            st.rerun()
with cg2:
    si_p = df[df[f"PRIORIDAD_{usuario}"] > 0]['ESTAMPA'].tolist()
    if si_p:
        p_rem = st.selectbox("Quitar de Doradas:", si_p)
        if st.button("❌ Ya no va"):
            df.at[df[df['ESTAMPA'] == p_rem].index[0], f"PRIORIDAD_{usuario}"] = 0
            conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
            st.rerun()
