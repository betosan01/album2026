import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026 - Megazord Edition", layout="wide")

# --- ESTILOS CSS (ANIMACIONES + ESTILO BASE) ---
st.markdown("""
    <style>
    /* Animaciones y estilos base mantenidos de v5.0 */
    @keyframes shiny { 0% { background-position: -200%; } 100% { background-position: 200%; } }
    .st-gold { background: linear-gradient(110deg, #ffd700 45%, #fff9db 50%, #ffd700 55%); background-size: 200% 100%; animation: shiny 3s infinite linear; color: black !important; border: 2px solid #daa520 !important; }
    
    @keyframes pulse-blue { 0% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(0, 123, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0); } }
    .st-blue { animation: pulse-blue 2s infinite; background-color: #007bff !important; border: 2px solid #0056b3 !important; }

    @keyframes scanline { 0% { top: 0%; } 100% { top: 100%; } }
    .scan-container { position: relative; overflow: hidden; }
    .scan-container::after { content: ""; position: absolute; width: 100%; height: 2px; background: rgba(0, 255, 255, 0.4); top: 0; left: 0; animation: scanline 5s linear infinite; z-index: 10; pointer-events: none; }

    .megazord-card { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 20px; border-radius: 15px; border: 2px solid #60a5fa; margin-bottom: 25px; text-align: center; color: white; }
    .stat-card { background-color: #262730; padding: 15px; border-radius: 10px; border-top: 3px solid #007bff; text-align: center; }
    .insignia-span { font-size: 1.5em; cursor: help; margin-left: 5px; }
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

# --- INICIALIZACIÓN DE ESTADOS ---
nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]
metas_colores = {10: "#cd7f32", 25: "#c0c0c0", 50: "#007bff", 75: "#9b59b6", 90: "#e74c3c", 95: "#ffd700", 100: "RAINBOW"}

if "metas_alcanzadas" not in st.session_state: st.session_state.metas_alcanzadas = {p: [] for p in nombres_papus}
if "racha_salada" not in st.session_state: st.session_state.racha_salada = {p: 0 for p in nombres_papus}
if "ultima_transaccion" not in st.session_state: st.session_state.ultima_transaccion = None
if "df_maestro" not in st.session_state: st.session_state.df_maestro = None
if "df_logs" not in st.session_state: st.session_state.df_logs = None

# --- CONEXIÓN Y CARGA DE DATOS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos_desde_google():
    try:
        # Cargar Base de Datos
        temp_df = conn.read(spreadsheet=url_del_sheet, worksheet="SHEET1", ttl=0)
        temp_df.columns = [str(c).strip().upper() for c in temp_df.columns]
        st.session_state.df_maestro = temp_df
        
        # Cargar Bitácora Persistente
        try:
            temp_logs = conn.read(spreadsheet=url_del_sheet, worksheet="LOGS", ttl=0)
            st.session_state.df_logs = temp_logs
        except:
            st.session_state.df_logs = pd.DataFrame(columns=["FECHA", "ACCION"])
            
        return True
    except Exception as e:
        error_msg = str(e)
        st.error("🚨 Falla en la Escena del Crimen (Error de Conexión) 🚨")
        if "APIError" in error_msg or "quota" in error_msg.lower():
            st.warning("⚠️ **Diagnóstico:** Cuota excedida. Espera 30 segundos.")
        elif "permission" in error_msg.lower():
            st.warning("⚠️ **Diagnóstico:** Falta permiso en el Sheet para el correo de servicio.")
        return False

def registrar_log_remoto(accion):
    nueva_fila = pd.DataFrame([{"FECHA": datetime.now().strftime("%d/%m %H:%M"), "ACCION": accion}])
    if st.session_state.df_logs is not None:
        st.session_state.df_logs = pd.concat([nueva_fila, st.session_state.df_logs]).head(15)
    else:
        st.session_state.df_logs = nueva_fila
    
    try:
        conn.update(spreadsheet=url_del_sheet, worksheet="LOGS", data=st.session_state.df_logs)
    except:
        st.error("No se pudo actualizar la bitácora en la nube, pero se guardó localmente.")

# Carga inicial
if st.session_state.df_maestro is None:
    if not cargar_datos_desde_google(): st.stop()

df = st.session_state.df_maestro

if st.sidebar.button("🔄 Sincronizar Operativo", use_container_width=True):
    with st.spinner("Sincronizando evidencia..."):
        if cargar_datos_desde_google():
            st.sidebar.success("¡Datos frescos!")
            st.rerun()

# --- CÁLCULO DEL MEGAZORD ---
total_total = len(df)
estampas_squad = df[nombres_papus].any(axis=1).sum()
porcentaje_megazord = (estampas_squad / total_total) * 100

st.markdown(f"""
    <div class="megazord-card">
        <h2 style='margin:0;'>🤖 MEGAZORD (SQUAD)</h2>
        <p style='font-size:1.2em; margin:5px;'>Avance del Cártel: <b>{porcentaje_megazord:.1f}%</b></p>
    </div>
""", unsafe_allow_html=True)
st.progress(porcentaje_megazord / 100)

# --- LÓGICA DE INSIGNIAS ---
def calcular_insignias(df_rank, df_completo):
    insignias = {p: [] for p in nombres_papus}
    el_patron = df_rank.iloc[0]['PAPU']
    insignias[el_patron].append(("👑", "Big Papu: Líder actual."))
    
    el_monopolio = df_rank.sort_values(by="REPETIDAS", ascending=False).iloc[0]['PAPU']
    insignias[el_monopolio].append(("🎩", "El Monopolio: Más repetidas."))
    
    ayuda_p = {}
    for p in nombres_papus:
        otros = [o for o in nombres_papus if o != p]
        sirven = df_completo[(df_completo[p] > 1) & (df_completo[otros].eq(0).any(axis=1))].shape[0]
        ayuda_p[p] = sirven
    el_donante = max(ayuda_p, key=ayuda_p.get)
    if ayuda_p[el_donante] > 0: insignias[el_donante].append(("🩸", "Donante Universal: Gran ayuda al squad."))
    
    for p in nombres_papus:
        reps = df_rank[df_rank['PAPU'] == p]['REPETIDAS'].values[0]
        prog = float(df_rank[df_rank['PAPU'] == p]['PROGRESO'].values[0].replace('%',''))
        if prog > 20 and reps < 3: insignias[p].append(("💪🏼", "El Codo: Poco aporte al mercado."))
            
    deseadas_c = {p: df_completo[f"PRIORIDAD_{p}"].sum() for p in nombres_papus}
    el_aferrado = max(deseadas_c, key=deseadas_c.get)
    if deseadas_c[el_aferrado] > 0: insignias[el_aferrado].append(("🧽", "El Aferrado: Muchas deseadas marcadas."))

    el_fantasma = df_rank.iloc[-1]['PAPU']
    insignias[el_fantasma].append(("👻", "Fantasmón: Último lugar."))

    for p, racha in st.session_state.racha_salada.items():
        if racha >= 2: insignias[p].append(("🤡", "Cliente Frecuente: Atrapado en el Muro."))
    return insignias

# --- POWER RANKING ---
st.subheader("📊 Power Ranking del Squad")
rank_data = []
for p in nombres_papus:
    pegadas = len(df[df[p] > 0])
    porcentaje = (pegadas / total_total) * 100
    repetidas = df[df[p] > 1][p].sum() - len(df[df[p] > 1])
    
    for m, color in metas_colores.items():
        if porcentaje >= m and m not in st.session_state.metas_alcanzadas[p]:
            lanzar_fuegos(p, m, color if m < 100 else "#ffffff")
            st.session_state.metas_alcanzadas[p].append(m)
            # Log de nivel persistente
            registrar_log_remoto(f"🔥 {p} SUBIÓ AL {m}%")

    rank_data.append({"PAPU": p, "PROGRESO": f"{porcentaje:.1f}%", "PEGADAS": pegadas, "REPETIDAS": int(repetidas), "PUNTOS": (pegadas * 2) + int(repetidas)})

df_rank = pd.DataFrame(rank_data).sort_values(by="PUNTOS", ascending=False)
dict_insignias = calcular_insignias(df_rank, df)

cols_rank = st.columns(len(nombres_papus))
for i, row in enumerate(df_rank.itertuples()):
    with cols_rank[i]:
        mis_insig = "".join([f'<span title="{desc}" class="insignia-span">{icon}</span>' for icon, desc in dict_insignias[row.PAPU]])
        st.markdown(f"""<div class="stat-card"><h3 style='margin:0; color:#007bff;'>#{i+1} {row.PAPU}</h3><div style='margin:10px 0;'>{mis_insig}</div><p style='margin:0; font-size:1.2em;'><b>{row.PROGRESO}</b></p><p style='margin:0; font-size:0.8em; color:#888;'>Pegadas: {row.PEGADAS} | Reps: {row.REPETIDAS}</p></div>""", unsafe_allow_html=True)

# --- SIDEBAR PERSISTENTE ---
with st.sidebar:
    with st.expander("📖 Glosario de Insignias"):
        st.markdown("👑 **Big Papu** | 🎩 **El Monopolio** | 🩸 **Donante** | 💪🏼 **El Codo** | 🧽 **El Aferrado** | 👻 **Fantasmón** | 🤡 **Cliente Frecuente**")
    
    st.divider()
    st.header("🕵️ Bitácora Global")
    if st.session_state.df_logs is not None and not st.session_state.df_logs.empty:
        for _, log in st.session_state.df_logs.iterrows():
            st.markdown(f"<div class='log-entry'><b>[{log['FECHA']}]</b> {log['ACCION']}</div>", unsafe_allow_html=True)
    else:
        st.write("Sin registros previos.")
    
    st.divider()
    st.header("💀 Muro de la Vergüenza")
    salado = False
    for p, racha in st.session_state.racha_salada.items():
        if racha >= 2:
            salado = True
            st.markdown(f"<div class='shame-card'>⚠️ <b>{p}</b> lleva {racha} repetidas seguidas. 🤡</div>", unsafe_allow_html=True)
    if not salado: st.write("Suerte por ahora.😶‍🌫️")

# --- REGISTRO Y GESTIÓN ---
st.divider()
st.subheader("📖 Registro de Sobres")
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
opciones = df['ESTAMPA'].tolist()

if "multi_registro" not in st.session_state: st.session_state.multi_registro = []
seleccionadas = st.multiselect("¿Cuáles salieron?😯", opciones, key="multi_registro")

if seleccionadas:
    cambios = {}
    cols = st.columns(4)
    for i, est in enumerate(seleccionadas):
        idx = df[df['ESTAMPA'] == est].index[0]
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"**{est}**")
                cambios[idx] = st.number_input("Cant", min_value=0, value=1, key=f"n_{est}")
                
    if st.button("💾 Guardar Evidencia", type="primary", use_container_width=True):
        trans_act = {"u": usuario, "c": cambios.copy()}
        if st.session_state.ultima_transaccion == trans_act:
            st.warning("Doble clic bloqueado. 🛑")
        else:
            nuevas = 0
            for idx, suma in cambios.items():
                if suma > 0:
                    if df.at[idx, usuario] == 0: nuevas += 1
                    df.at[idx, usuario] += suma
            
            st.session_state.racha_salada[usuario] = 0 if nuevas > 0 else st.session_state.racha_salada[usuario] + 1
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                # Log persistente
                registrar_log_remoto(f"{usuario} registró {len(cambios)} estampas")
                st.session_state.ultima_transaccion = trans_act
                del st.session_state["multi_registro"]
                st.rerun()
            except:
                st.error("Error al guardar. API saturada.")

# --- INVENTARIO ---
st.divider()
st.subheader(f"📋 Repetidas ({usuario})")
df_reps = df[df[usuario] > 1][['ESTAMPA', usuario]].copy()
if not df_reps.empty:
    df_reps_ed = st.data_editor(df_reps, hide_index=True, use_container_width=True, key=f"ed_{usuario}")
    if st.button("🔄 Actualizar Inventario"):
        for _, row in df_reps_ed.iterrows():
            idx_real = df[df['ESTAMPA'] == row['ESTAMPA']].index[0]
            df.at[idx_real, usuario] = row[usuario]
        try:
            conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
            st.session_state.df_maestro = df
            registrar_log_remoto(f"🕵️ {usuario} ajustó inventario")
            st.rerun()
        except: st.error("API saturada.")

# --- ADIOS POPÓ ---
st.divider()
with st.expander("🗑️ Adios popó 💩 (Bajas)"):
    mis_reps = df[df[usuario] > 1]['ESTAMPA'].tolist()
    if mis_reps:
        bajas_sel = st.multiselect("Bajas💸", mis_reps, key="multi_bajas")
        if bajas_sel:
            b_pend = {r: st.number_input(f"Cant {r}", min_value=1, key=f"d_{r}") for r in bajas_sel}
            if st.button("Confirmar Baja"):
                for e, c in b_pend.items(): df.at[df[df['ESTAMPA'] == e].index[0], usuario] -= c
                try:
                    conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                    st.session_state.df_maestro = df
                    registrar_log_remoto(f"⚠️ {usuario} dio bajas")
                    st.rerun()
                except: st.error("API saturada.")

# --- MERCADO ---
st.divider()
st.subheader("💱 Mercado & Tratos")
t1, t2, t3 = st.tabs(["Disponibles", "Trato Justo", "Tríos🥵"])
with t1:
    faltan = df[df[usuario] == 0]
    for _, row in faltan.iterrows():
        for o in nombres_papus:
            if o != usuario and row[o] > 1: st.markdown(f"**{row['ESTAMPA']}** ➔ **{o}**")
with t2:
    for o in nombres_papus:
        if o != usuario:
            yo = df[(df[usuario] > 1) & (df[o] == 0)]['ESTAMPA'].tolist()
            el = df[(df[o] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if yo and el: st.success(f"🔥 **TRATO CON {o}!** Tú: {yo[:2]} | Él: {el[:2]}")
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
cp1, cp2, cp3 = st.columns([1,2,1])
with cp1: 
    if st.button("⬅️ Atrás") and st.session_state.p_a > 0: st.session_state.p_a -= 1; st.rerun()
with cp3: 
    if st.button("Sig. ➡️") and st.session_state.p_a < (len(df_v)-1)//30: st.session_state.p_a += 1; st.rerun()

st.markdown("<div class='scan-container'>", unsafe_allow_html=True)
chunk = df_v.iloc[st.session_state.p_a*30 : (st.session_state.p_a+1)*30]
cols_a = st.columns(6)
for i, (_, r) in enumerate(chunk.iterrows()):
    act, prio = r[usuario], r[f"PRIORIDAD_{usuario}"]
    otros_f = [p for p in nombres_papus if p != usuario if r[p] == 0]
    css = "st-blue" if act > 1 and otros_f else "st-green" if act >= 1 else "st-gold" if prio > 0 else "st-gray"
    with cols_a[i % 6]: st.markdown(f"<div class='sticker-box {css}'>{r['ESTAMPA']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- DORADAS ---
st.divider()
st.subheader("⭐ TUS MÁS DESEADAS")
cg1, cg2 = st.columns(2)
with cg1:
    no_p = df[(df[f"PRIORIDAD_{usuario}"] == 0) & (df[usuario] == 0)]['ESTAMPA'].tolist()
    if no_p:
        p_add = st.selectbox("Marcar Dorada:", no_p, key="add_g")
        if st.button("✨ LA NECESITOOOOOOO🧽"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], f"PRIORIDAD_{usuario}"] = 1
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                st.rerun()
            except: st.error("Error al guardar.")
with cg2:
    si_p = df[df[f"PRIORIDAD_{usuario}"] > 0]['ESTAMPA'].tolist()
    if si_p:
        p_rem = st.selectbox("Quitar Dorada:", si_p, key="rem_g")
        if st.button("❌ Ya no va"):
            df.at[df[df['ESTAMPA'] == p_rem].index[0], f"PRIORIDAD_{usuario}"] = 0
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                st.rerun()
            except: st.error("Error al guardar.")
