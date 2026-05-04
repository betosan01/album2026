import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de pantalla ancha
st.set_page_config(page_title="Dashboard Mundial 2026", layout="wide")

# --- ESTILOS CSS (DARK MODE FRIENDLY + ÁLBUM FÍSICO) ---
st.markdown("""
    <style>
    .legend-box { 
        padding: 15px; border-radius: 8px; border: 1px solid #444; 
        margin-bottom: 25px; display: flex; gap: 25px; flex-wrap: wrap; 
        background-color: #1e1e1e; 
    }
    .legend-item { display: flex; align-items: center; gap: 10px; font-size: 0.95em; color: #fafafa; }
    .circle { height: 18px; width: 18px; border-radius: 50%; display: inline-block; border: 1px solid #777; }
    .match-alert { 
        padding: 8px; border-radius: 5px; background-color: #007bff; 
        color: white; font-weight: bold; margin-top: 8px; text-align: center; font-size: 0.85em; 
    }
    .priority-badge { 
        background-color: #ffd700; color: black; padding: 4px 12px; 
        border-radius: 15px; font-weight: bold; font-size: 0.8em; 
        display: inline-block; margin-bottom: 5px; border: 1px solid #daa520; 
    }
    .swap-card {
        padding: 10px; border-left: 5px solid #28a745; background-color: #262730; 
        border-radius: 5px; margin-bottom: 10px;
    }
    /* NUEVOS ESTILOS PARA EL ÁLBUM VIRTUAL */
    .sticker-box {
        padding: 20px 5px; border-radius: 8px; text-align: center; 
        font-weight: bold; margin-bottom: 15px; font-size: 1.1em;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3); transition: transform 0.2s;
    }
    .sticker-box:hover { transform: scale(1.05); cursor: default; }
    .st-gray { background-color: #2b2b2b; color: #777; border: 2px dashed #555; }
    .st-green { background-color: #28a745; color: white; border: 2px solid #1e7e34; }
    .st-blue { background-color: #007bff; color: white; border: 2px solid #0056b3; }
    .st-gold { background-color: #ffd700; color: black; border: 2px solid #daa520; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Control Dashboard Papus")

# --- 1. SIMBOLOGÍA DE COLORES ---
st.markdown("""
    <div class="legend-box">
        <div class="legend-item"><span class="circle" style="background-color: #f0f2f6;"></span> <b>Gris:</b> No la tienes🤣🫵</div>
        <div class="legend-item"><span class="circle" style="background-color: #28a745;"></span> <b>Verde:</b> Ya la tienes😎</div>
        <div class="legend-item"><span class="circle" style="background-color: #007bff;"></span> <b>Azul:</b> Alguien la necesita🤑</div>
        <div class="legend-item"><span class="circle" style="background-color: #ffd700;"></span> <b>Dorado:</b> Tus deseadas ⭐</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN A DATOS Y AUTO-CREACIÓN DE COLUMNAS ---
url_del_sheet = "https://docs.google.com/spreadsheets/d/10sQ2DRiylPSinFnOlbThhz2Wz6H24eXvyoKn31hqWKY/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url_del_sheet, ttl="0")
df.columns = [str(c).strip().upper() for c in df.columns]

nombres_papus = ["BETOSAN", "LUISE", "OSCARINHO", "ROYS"]

cambios_estructura = False
for p in nombres_papus:
    col_prio = f"PRIORIDAD_{p}"
    if col_prio not in df.columns:
        df[col_prio] = 0
        cambios_estructura = True
if cambios_estructura:
    conn.update(spreadsheet=url_del_sheet, data=df)

# --- 3. PROGRESO DEL ESCUADRÓN ---
st.subheader("📊 Progreo General del Escuadrón")
cols_progreso = st.columns(len(nombres_papus))
total_estampas = len(df)

for i, p in enumerate(nombres_papus):
    tenidas = len(df[df[p] > 0])
    porcentaje = (tenidas / total_estampas) * 100
    with cols_progreso[i]:
        st.metric(label=f"Progreso {p}", value=f"{round(porcentaje, 1)}%", delta=f"{tenidas}/{total_estampas}")
        st.progress(porcentaje / 100)

# --- 4. IDENTIFICACIÓN Y REGISTRO ---
st.divider()
st.subheader("📖 Registro de Sobres")
usuario = st.selectbox("¿Quién eres papu?🧐", nombres_papus)
col_prioridad_mia = f"PRIORIDAD_{usuario}"

opciones = df['ESTAMPA'].tolist()
seleccionadas = st.multiselect("Cuáles te salieron perro?😯", opciones)

if seleccionadas:
    st.write("### 📋 Panel de Control")
    cols = st.columns(4)
    cambios_pendientes = {}

    for i, estampa in enumerate(seleccionadas):
        idx = df[df['ESTAMPA'] == estampa].index[0]
        actual = df.at[idx, usuario]
        prioridad_mia = df.at[idx, col_prioridad_mia]
        
        with cols[i % 4]:
            with st.container(border=True):
                if prioridad_mia > 0:
                    st.markdown(f"<div style='text-align: center;'><span class='priority-badge'>⭐ DORADA</span></div>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align:center; margin-bottom: 0px;'>{estampa}</h4>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; color: #aaa; margin-bottom: 10px;'>Ya tienes: {actual}</div>", unsafe_allow_html=True)
                
                cantidad_nueva = st.number_input("¿Cuántas te salieron?", min_value=0, value=1, step=1, key=f"num_{estampa}")
                cambios_pendientes[idx] = cantidad_nueva

                otros = [p for p in nombres_papus if p != usuario]
                buscan = [p for p in otros if p in df.columns and df.at[idx, p] == 0]
                
                if buscan and (actual >= 1 or cantidad_nueva >= 1):
                    for p in buscan:
                        es_su_dorada = " (¡ES SU DORADA!⭐)" if df.at[idx, f"PRIORIDAD_{p}"] > 0 else ""
                        st.markdown(f"<div class='match-alert'>🤝 LA NECESITAAA {p}{es_su_dorada}</div>", unsafe_allow_html=True)

    if st.button("💾 GUARDAR CAMBIOS EN LA NUBE", type="primary", use_container_width=True):
        for idx_cambio, suma in cambios_pendientes.items():
            if suma > 0:
                df.at[idx_cambio, usuario] += suma
        conn.update(spreadsheet=url_del_sheet, data=df)
        st.success("¡Ya quedó papu!🔥 Dale a la 'X' para limpiar.")
        st.balloons()

# --- 5. MERCADO NEGRO ---
st.divider()
st.subheader("💱 Mercado Negro (Intercambios)")
me_faltan = df[df[usuario] == 0]
hay_intercambios = False
cols_mercado = st.columns(2)
col_idx = 0

for _, row in me_faltan.iterrows():
    estampa = row['ESTAMPA']
    for otro in nombres_papus:
        if otro != usuario and row[otro] > 1:
            hay_intercambios = True
            repetidas_disp = row[otro] - 1
            es_mi_dorada = "⭐" if row[col_prioridad_mia] > 0 else ""
            with cols_mercado[col_idx % 2]:
                st.markdown(f"<div class='swap-card'><b>{estampa}</b> {es_mi_dorada} ➔ Pídesela a <b>{otro}</b> ({repetidas_disp} repetidas)</div>", unsafe_allow_html=True)
            col_idx += 1

if not hay_intercambios:
    st.info("Ni modo papu, nadie tiene las que te faltan ahorita. 😔")

# --- 6. MI ÁLBUM VIRTUAL PAGINADO (LA NUEVA MAGIA) ---
st.divider()
st.subheader(f"📔 Mi Álbum Virtual ({usuario})")

# Variables para la paginación (30 estampas por página = 6 columnas x 5 filas)
if "album_page" not in st.session_state:
    st.session_state.album_page = 0

ITEMS_POR_PAGINA = 30
total_paginas = (total_estampas - 1) // ITEMS_POR_PAGINA + 1

# Controles de navegación de páginas
col_prev, col_info, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("⬅️ Página Anterior") and st.session_state.album_page > 0:
        st.session_state.album_page -= 1
        st.rerun()
with col_info:
    st.markdown(f"<h4 style='text-align: center; color:#fafafa;'>📖 Página {st.session_state.album_page + 1} de {total_paginas}</h4>", unsafe_allow_html=True)
with col_next:
    if st.button("Página Siguiente ➡️") and st.session_state.album_page < total_paginas - 1:
        st.session_state.album_page += 1
        st.rerun()

st.write("") # Espacio en blanco

# Recortar el dataframe solo a las estampas de esta página
start_idx = st.session_state.album_page * ITEMS_POR_PAGINA
end_idx = start_idx + ITEMS_POR_PAGINA
chunk_album = df.iloc[start_idx:end_idx]

cols_album = st.columns(6)
for i, (_, row) in enumerate(chunk_album.iterrows()):
    estampa = row['ESTAMPA']
    actual = row[usuario]
    prioridad_mia = row[col_prioridad_mia]
    
    otros = [p for p in nombres_papus if p != usuario]
    buscan = [p for p in otros if p in df.columns and row[p] == 0]
    
    # Lógica de Color según leyenda
    if actual > 1 and buscan:
        css_class = "st-blue"
    elif actual >= 1:
        css_class = "st-green"
    elif prioridad_mia > 0:
        css_class = "st-gold"
    else:
        css_class = "st-gray" # Hueco vacío punteado
        
    with cols_album[i % 6]:
        st.markdown(f"<div class='sticker-box {css_class}'>{estampa}</div>", unsafe_allow_html=True)

# --- 7. GESTIÓN DE DORADAS ---
st.divider()
st.subheader(f"⭐ TUS MÁS DESEADAS ({usuario})")
col_p1, col_p2 = st.columns(2)

with col_p1:
    no_doradas = df[(df[col_prioridad_mia] == 0) & (df[usuario] == 0)]['ESTAMPA'].tolist()
    if no_doradas:
        p_add = st.selectbox("Marcar como Dorada:", no_doradas, key="add_g")
        if st.button("✨ LA NECESITOOOOOOO🧽"):
            df.at[df[df['ESTAMPA'] == p_add].index[0], col_prioridad_mia] = 1
            conn.update(spreadsheet=url_del_sheet, data=df)
            st.rerun()

with col_p2:
    si_doradas = df[df[col_prioridad_mia] > 0]['ESTAMPA'].tolist()
    if si_doradas:
        p_rem = st.selectbox("Quitar de Doradas:", si_doradas, key="rem_g")
        if st.button("❌ Quitar prioridad"):
            df.at[df[df['ESTAMPA'] == p_rem].index[0], col_prioridad_mia] = 0
            conn.update(spreadsheet=url_del_sheet, data=df)
            st.rerun()