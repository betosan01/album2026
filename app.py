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

# --- CONEXIÓN A DATOS Y TRADUCTOR DE ERRORES FORENSE ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos_desde_google():
    try:
        # Cargar Base de Datos Principal (SHEET1)
        temp_df = conn.read(spreadsheet=url_del_sheet, worksheet="SHEET1", ttl=0)
        temp_df.columns = [str(c).strip().upper() for c in temp_df.columns]
        st.session_state.df_maestro = temp_df
        
        # Cargar Bitácora Persistente (LOGS)
        try:
            temp_logs = conn.read(spreadsheet=url_del_sheet, worksheet="LOGS", ttl=0)
            st.session_state.df_logs = temp_logs
        except:
            st.session_state.df_logs = pd.DataFrame(columns=["FECHA", "ACCION"])
            
        return True
    except Exception as e:
        error_msg = str(e)
        st.error("🚨 ¡ALTO AHÍ! Falla en la Escena del Crimen (Error de Conexión) 🚨")
        if "APIError" in error_msg or "quota" in error_msg.lower():
            st.warning("⚠️ **Diagnóstico:** Saturaste a Google a peticiones. Espérate 30 segundos.")
        elif "insufficient authentication" in error_msg.lower() or "permission" in error_msg.lower():
            st.warning("⚠️ **Diagnóstico:** Revisa permisos del correo de servicio en el Sheet.")
        else:
            st.warning(f"⚠️ **Diagnóstico:** Error desconocido: `{error_msg}`")
        return False

def registrar_log_remoto(accion):
    # AJUSTE: Horario de la CDMX (UTC -6)
    hora_cdmx = datetime.utcnow() + timedelta(hours=-6)
    nueva_fila = pd.DataFrame([{"FECHA": hora_cdmx.strftime("%d/%m %H:%M"), "ACCION": accion}])
    
    if st.session_state.df_logs is not None:
        # Se mantienen los últimos 15 en la nube para historial, pero mostraremos solo 3
        st.session_state.df_logs = pd.concat([nueva_fila, st.session_state.df_logs]).head(15)
    else:
        st.session_state.df_logs = nueva_fila
    
    try:
        conn.update(spreadsheet=url_del_sheet, worksheet="LOGS", data=st.session_state.df_logs)
    except:
        st.error("No se pudo actualizar la bitácora en la nube.")

# Cargar la primera vez
if st.session_state.df_maestro is None:
    if not cargar_datos_desde_google():
        st.stop()

df = st.session_state.df_maestro

# Botón para forzar actualización
if st.sidebar.button("🔄 Sincronizar Datos con la Nube", use_container_width=True):
    with st.spinner("Descargando la última evidencia..."):
        if cargar_datos_desde_google():
            st.sidebar.success("¡Información al tiro!")
            st.rerun()

# --- CÁLCULO DEL MEGAZORD Y REPETIDAS TOTALES ---
total_total = len(df)
estampas_squad = df[nombres_papus].any(axis=1).sum()
porcentaje_megazord = (estampas_squad / total_total) * 100

# APARTADO NUEVO: Cálculo repetidas del Squad
total_reps_squad = 0
for p in nombres_papus:
    total_reps_squad += int(df[df[p] > 1][p].sum() - len(df[df[p] > 1]))

st.markdown(f"""
    <div class="megazord-card">
        <h2 style='margin:0;'>🤖 MEGAZORD (SQUAD)</h2>
        <p style='font-size:1.2em; margin:5px;'>Llevan el <b>{porcentaje_megazord:.1f}%</b> del Álbum Maestro</p>
        <p style='font-size:1em; margin:2px;'>💰 Repetidas en Bodega Squad: <b>{total_reps_squad}</b></p>
    </div>
""", unsafe_allow_html=True)
st.progress(porcentaje_megazord / 100)

# --- LÓGICA DE LAS 10 INSIGNIAS OFICIALES ---
def calcular_insignias(df_rank, df_completo, df_logs):
    insignias = {p: [] for p in nombres_papus}
    
    # Rastrear posiciones para el Cruzazuleado
    rank_positions = {row.PAPU: i+1 for i, row in enumerate(df_rank.itertuples())}
    if not st.session_state.prev_rank:
        st.session_state.prev_rank = rank_positions
    else:
        for p, pos in rank_positions.items():
            if st.session_state.prev_rank.get(p) == 1 and pos > 1:
                st.session_state.insignias_eventos[p].add("Cruzazuleado")
        st.session_state.prev_rank = rank_positions

    # 1. 👑 Big Papu
    el_patron = df_rank.iloc[0]['PAPU']
    insignias[el_patron].append(("👑", "Big Papu: Líder actual del Power Ranking."))
    
    # 2. 🚂 Cruzazuleado
    for p in nombres_papus:
        if "Cruzazuleado" in st.session_state.insignias_eventos[p]:
            insignias[p].append(("🚂", "Cruzazuleado: Era el #1 y la pecheó."))

    # 3. 📦 Clonmadre
    for p in nombres_papus:
        if df_completo[p].max() >= 5: # 1 pegada + 4 o más repetidas
            insignias[p].append(("📦", "Clonmadre: Tiene 4 o más repetidas de una misma estampa."))
            
    # 4. 🤝 El Coyote
    tratos_count = {p: 0 for p in nombres_papus}
    for p in nombres_papus:
        for o in nombres_papus:
            if p != o:
                yo = df_completo[(df_completo[p] > 1) & (df_completo[o] == 0)].shape[0]
                el = df_completo[(df_completo[o] > 1) & (df_completo[p] == 0)].shape[0]
                tratos_count[p] += min(yo, el)
    el_coyote = max(tratos_count, key=tratos_count.get)
    if tratos_count[el_coyote] > 0:
        insignias[el_coyote].append(("🤝", "El Coyote: El rey del trueque. Más tratos 1 a 1 activos."))
        
    # 5. 🛍️ El Fayuquero y 7. 🎯 El Bendecido (Por eventos)
    for p in nombres_papus:
        if "Fayuquero" in st.session_state.insignias_eventos[p]:
            insignias[p].append(("🛍️", "El Fayuquero: Registró más de 15 estampas de un jalón."))
        if "Bendecido" in st.session_state.insignias_eventos[p]:
            insignias[p].append(("🎯", "El Bendecido: Puntería fina, le salieron 4 o más nuevas en un sobre."))

    # 6. 🤲 El Hambreado
    deseadas_counts = {p: df_completo[f"PRIORIDAD_{p}"].sum() for p in nombres_papus}
    hambreados = [p for p in nombres_papus if df_rank[df_rank['PAPU'] == p]['REPETIDAS'].values[0] == 0 and deseadas_counts[p] > 0]
    if hambreados:
        el_hambreado = max(hambreados, key=lambda x: deseadas_counts[x])
        insignias[el_hambreado].append(("🤲", "El Hambreado: Cero repetidas, pero pide y pide doradas de a grapa."))
        
    # 8. 🐢 El Funcionario
    hora_cdmx = datetime.utcnow() + timedelta(hours=-6)
    if df_logs is not None and not df_logs.empty:
        for p in nombres_papus:
            logs_p = df_logs[df_logs['ACCION'].str.contains(p, na=False)]
            if not logs_p.empty:
                last_date_str = logs_p.iloc[0]['FECHA']
                try:
                    last_date = datetime.strptime(f"{last_date_str}/{hora_cdmx.year}", "%d/%m %H:%M/%Y")
                    if (hora_cdmx - last_date).days >= 3:
                        insignias[p].append(("🐢", "El Funcionario: Lleva más de 3 días sin chambear (registrar)."))
                except: pass
            else:
                insignias[p].append(("🐢", "El Funcionario: Lleva más de 3 días sin chambear (registrar)."))
    else:
        for p in nombres_papus:
            insignias[p].append(("🐢", "El Funcionario: Lleva más de 3 días sin chambear (registrar)."))

    # 9. 🧂 El Salitre
    salitre_ratio = {}
    for p in nombres_papus:
        pegadas = df_rank[df_rank['PAPU'] == p]['PEGADAS'].values[0]
        reps = df_rank[df_rank['PAPU'] == p]['REPETIDAS'].values[0]
        prog = float(df_rank[df_rank['PAPU'] == p]['PROGRESO'].values[0].replace('%',''))
        if prog < 50: # Solo aplica si vas a menos de la mitad
            salitre_ratio[p] = reps / pegadas if pegadas > 0 else 0
        else:
            salitre_ratio[p] = 0
    el_salitre = max(salitre_ratio, key=salitre_ratio.get)
    if salitre_ratio[el_salitre] > 0.5: # Si su basura es más del 50% de sus pegadas
        insignias[el_salitre].append(("🧂", "El Salitre: Saladísimo. Pésimo ratio, pura repetida y poco avance."))

    # 10. 🥵 El Ya Merito
    for p in nombres_papus:
        prog = float(df_rank[df_rank['PAPU'] == p]['PROGRESO'].values[0].replace('%',''))
        if 90 <= prog < 100:
            insignias[p].append(("🥵", "El Ya Merito: Sudando frío, ya superó el 90% del álbum."))

    return insignias

# --- POWER RANKING ---
st.subheader("📊 Power Ranking del Squad")
rank_data = []
for p in nombres_papus:
    pegadas = len(df[df[p] > 0])
    porcentaje = (pegadas / total_total) * 100
    # APARTADO NUEVO: Conteo individual de repetidas
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
                <p style='margin:0; font-size:0.8em; color:#888;'>Pegadas: {row.PEGADAS} | Repetidas: {row.REPETIDAS}</p>
            </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR & BITÁCORA GLOBAL ---
with st.sidebar:
    with st.expander("📖 Glosario de Insignias Oficiales"):
        st.markdown("""
        👑 **Big Papu:** Líder del Ranking.  
        🚂 **Cruzazuleado:** Era el #1 y la pecheó.  
        📦 **Clonmadre:** Tiene 4 o más repetidas de una misma.  
        🤝 **El Coyote:** El rey del trueque, más tratos activos.  
        🛍️ **El Fayuquero:** Registró más de 15 estampas de jalón.  
        🤲 **El Hambreado:** Cero repetidas, pero exige doradas.  
        🎯 **El Bendecido:** Le salieron 4 o más nuevas en un registro.  
        🐢 **El Funcionario:** Lleva más de 3 días sin registrar nada.  
        🧂 **El Salitre:** Saladísimo. Pura repetida y poco avance.  
        🥵 **El Ya Merito:** Sudando frío, superó el 90%.  
        """)
    
    st.divider()
    st.header("🕵️ Bitácora")
    # AJUSTE: Solo muestra los últimos 3 movimientos (.head(3))
    if st.session_state.df_logs is not None and not st.session_state.df_logs.empty:
        for _, log in st.session_state.df_logs.head(3).iterrows():
            st.markdown(f"<div class='log-entry'><b>[{log['FECHA']}]</b> {log['ACCION']}</div>", unsafe_allow_html=True)
    else:
        st.write("Sin registros previos.")
    
    st.divider()
    st.header("💀 Muro de la Vergüenza")
    salado = False
    for p, racha in st.session_state.racha_salada.items():
        if racha >= 2:
            salado = True
            st.markdown(f"<div class='shame-card'>⚠️ <b>{p}</b> lleva {racha} registros de puras repetidas. 🤡</div>", unsafe_allow_html=True)
    if not salado: st.write("Todos traen suerte... por ahora.😶‍🌫️")

# --- REGISTRO & INVENTARIO (VERSIÓN CUADRÍCULA OPTIMIZADA) ---
st.divider()
st.subheader("📖 Registro de Sobres")
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
col_prio = f"PRIORIDAD_{usuario}"

opciones = df['ESTAMPA'].tolist()

# Buscador de texto libre en lugar del multiselect
filtro_texto = st.text_input("🔍 Busca por código (Ej. MEX, ARG, FWC)...").upper()

if "estampas_a_registrar" not in st.session_state: 
    st.session_state.estampas_a_registrar = {}

# Mostrar botones solo si hay texto en el buscador
if filtro_texto:
    opciones_filtradas = [est for est in opciones if filtro_texto in est]
    
    if opciones_filtradas:
        st.write("👇 Selecciona las que te salieron pa:")
        cols_botones = st.columns(6)
        
        for i, est in enumerate(opciones_filtradas):
            idx = df[df['ESTAMPA'] == est].index[0]
            ya_la_tengo = df.at[idx, usuario] > 0
            
            with cols_botones[i % 6]:
                is_checked = st.session_state.estampas_a_registrar.get(est, 0) > 0
                
                if ya_la_tengo:
                    label = f"⚠️ {est}"
                else:
                    label = f"✅ {est}"
                
                seleccion = st.toggle(label, value=is_checked, key=f"tg_{est}")
                
                if seleccion:
                    st.session_state.estampas_a_registrar[est] = 1
                elif est in st.session_state.estampas_a_registrar:
                    del st.session_state.estampas_a_registrar[est]
    else:
        st.warning("No se encontró esa estampa. Revisa bien el código, pai.🤨")

# Mostrar panel de control solo si ya se seleccionó al menos una estampa
if st.session_state.estampas_a_registrar:
    st.write("### 📋 Panel de Control (Tu Lote Actual)")
    cols_control = st.columns(4)
    cambios = {}
    
    for i, (est, cantidad) in enumerate(st.session_state.estampas_a_registrar.items()):
        idx = df[df['ESTAMPA'] == est].index[0]
        with cols_control[i % 4]:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align:center;'>{est}</h4>", unsafe_allow_html=True)
                cambios[idx] = st.number_input("Cantidad", min_value=1, value=cantidad, key=f"num_{est}")

    if st.button("💾 Al toque pa, ya los puedes guardar", type="primary", use_container_width=True):
        # 🕵️‍♂️ BLOQUEO ANTI-DOBLE CLIC (RESTAURADO)
        transaccion_actual = {"user": usuario, "cambios": cambios.copy()}
        
        if st.session_state.ultima_transaccion == transaccion_actual:
            st.warning("¡Tranquilo papu! 🛑 Detectamos un doble clic.")
        else:
            with st.spinner("Subiendo datos a la nube..."):
                nuevas = 0
                total_registradas = sum(cambios.values())
                
                for idx, suma in cambios.items():
                    if suma > 0:
                        if df.at[idx, usuario] == 0: nuevas += 1
                        df.at[idx, usuario] += suma
                
                # Asignación de insignias por eventos
                if total_registradas > 15: st.session_state.insignias_eventos[usuario].add("Fayuquero")
                if nuevas >= 4: st.session_state.insignias_eventos[usuario].add("Bendecido")
                
                st.session_state.racha_salada[usuario] = 0 if nuevas > 0 else st.session_state.racha_salada[usuario] + 1
                
                try:
                    conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                    st.session_state.df_maestro = df
                    registrar_log_remoto(f"{usuario} registró {len(cambios)} estampas")
                    st.session_state.ultima_transaccion = transaccion_actual
                    st.session_state.estampas_a_registrar = {}
                    st.rerun()
                except Exception as e:
                    st.error("🚨 Ocurrió un problema al guardar.")

# --- INVENTARIO DE REPETIDAS ---
st.divider()
st.subheader(f"📋 Repetidas ({usuario})")
df_reps = df[df[usuario] > 1][['ESTAMPA', usuario]].copy()
if not df_reps.empty:
    df_reps_edited = st.data_editor(df_reps, column_config={usuario: st.column_config.NumberColumn("Total", min_value=1), "ESTAMPA": st.column_config.Column(disabled=True)}, hide_index=True, use_container_width=True, key=f"ed_{usuario}")
    if st.button("🔄 Actualizar Cantidades 🛠️"):
        with st.spinner("Ajustando inventario..."):
            for _, row in df_reps_edited.iterrows():
                idx_real = df[df['ESTAMPA'] == row['ESTAMPA']].index[0]
                df.at[idx_real, usuario] = row[usuario]
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                registrar_log_remoto(f"🕵️ {usuario} ajustó su inventario")
                st.rerun()
            except:
                st.error("🚨 API saturada.")
else: st.info("Sin repetidas registradas. 🍀")

# --- ADIOS POPÓ ---
st.divider()
with st.expander("🗑️ Adios popó 💩 (Bajas externas)"):
    mis_reps = df[df[usuario] > 1]['ESTAMPA'].tolist()
    if mis_reps:
        if "multi_bajas" not in st.session_state: st.session_state.multi_bajas = []
        baja = st.multiselect("¿Cuáles se fueron?💸", mis_reps, key="multi_bajas")
        if baja:
            b_pend = {r: st.number_input(f"Cant {r}", min_value=1, max_value=int(df[df['ESTAMPA']==r][usuario].values[0]-1), key=f"d_{r}") for r in baja}
            if st.button("Confirmar baja"):
                transaccion_baja = {"tipo": "baja", "user": usuario, "cambios": b_pend.copy()}
                if st.session_state.ultima_transaccion == transaccion_baja:
                    st.warning("Doble clic evitado. 🛑")
                else:
                    with st.spinner("Ejecutando bajas..."):
                        for e, c in b_pend.items(): df.at[df[df['ESTAMPA'] == e].index[0], usuario] -= c
                        try:
                            conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                            st.session_state.df_maestro = df
                            registrar_log_remoto(f"⚠️ {usuario} dio bajas")
                            st.session_state.ultima_transaccion = transaccion_baja
                            del st.session_state["multi_bajas"]
                            st.rerun()
                        except:
                            st.error("🚨 Error al conectar.")

# --- TRATOS Y MERCADO ---
st.divider()
st.subheader("💱 Mercado Nigger & Tratos Pro🤯")
t1, t2, t3 = st.tabs(["Disponibles🔁", "Un precio justo🦑", "Tríos🥵"])
with t1:
    me_faltan = df[df[usuario] == 0]
    for i, (_, row) in enumerate(me_faltan.iterrows()):
        for o in nombres_papus:
            if o != usuario and row[o] > 1: st.markdown(f"**{row['ESTAMPA']}** ➔ Ruégale a **{o}**")
with t2:
    for o in nombres_papus:
        if o != usuario:
            yo = df[(df[usuario] > 1) & (df[o] == 0)]['ESTAMPA'].tolist()
            el = df[(df[o] > 1) & (df[usuario] == 0)]['ESTAMPA'].tolist()
            if yo and el: st.success(f"🔥 **TRATO IDEAL CON {o}!** Tú: {yo[:2]} | Él: {el[:2]}")
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
    if st.button("⬅️ Va pa´trás") and st.session_state.p_a > 0: st.session_state.p_a -= 1; st.rerun()
with cp3: 
    if st.button("Va pa´lante ➡️") and st.session_state.p_a < (len(df_v)-1)//30: st.session_state.p_a += 1; st.rerun()

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
        p_add = st.selectbox("Marcar como Dorada:", no_p, key="add_g")
        if st.button("✨ LA NECESITOOOOOOO🧽"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], f"PRIORIDAD_{usuario}"] = 1
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                registrar_log_remoto(f"🤩 {usuario} marcó dorada: {p_add}")
                st.rerun()
            except: st.error("🚨 Falló al guardar.")
with cg2:
    si_p = df[df[f"PRIORIDAD_{usuario}"] > 0]['ESTAMPA'].tolist()
    if si_p:
        p_rem = st.selectbox("Quitar de Doradas:", si_p, key="rem_g")
        if st.button("❌ Ya no va"):
            df.at[df[df['ESTAMPA'] == p_rem].index[0], f"PRIORIDAD_{usuario}"] = 0
            try:
                conn.update(spreadsheet=url_del_sheet, worksheet="SHEET1", data=df)
                st.session_state.df_maestro = df
                registrar_log_remoto(f"🗑️ {usuario} quitó dorada: {p_rem}")
                st.rerun()
            except: st.error("🚨 Falló al guardar.")
