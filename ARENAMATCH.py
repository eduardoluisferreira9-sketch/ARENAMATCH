import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random

# 🎾 CONFIGURAÇÃO DA PÁGINA PREMIUM
st.set_page_config(
    page_title="ArenaMatch Pro - Padel & Beach Tennis",
    page_icon="🎾",
    layout="wide"
)

NOME_SISTEMA = "ArenaMatch Pro"
CHAVE_ADMIN = "arena123"

# 🎨 DIRETRIZES VISUAIS PREMIUM (DARK MODE COMPLETO)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19 !important; } 
    section[data-testid="stSidebar"] { background-color: #060911 !important; border-right: 2px solid #1f293d; }
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { color: #ffffff !important; margin: 2px 0 !important; }
    
    .titulo-secao {
        color: #39ff14 !important; font-size: 1.3rem !important; font-weight: bold !important;
        border-left: 5px solid #39ff14; padding-left: 10px; margin-top: 15px; margin-bottom: 12px; text-transform: uppercase;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: #ffffff !important; background-color: #121824 !important; border: 2px solid #1f293d !important; border-radius: 8px !important;
    }
    
    /* Tabelas Estilo Arena */
    div[data-testid="stTable"] { background-color: #121824 !important; border-radius: 8px; overflow: hidden; border: 2px solid #1f293d !important; }
    div[data-testid="stTable"] table { background-color: #121824 !important; width: 100% !important; margin: 0 !important; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; font-size: 0.9rem !important; padding: 6px !important; }
    div[data-testid="stTable"] td { background-color: #121824 !important; color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; font-weight: bold !important; font-size: 0.9rem !important; padding: 6px !important; }
    
    button[data-baseweb="tab"] { color: #8fa0bc !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #39ff14 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if "duplas" not in st.session_state: st.session_state.duplas = []
if "categoria_selecionada" not in st.session_state: st.session_state.categoria_selecionada = "4ª Categoria"
if "torneio_fase" not in st.session_state: st.session_state.torneio_fase = "Inscrição"  
if "grupos" not in st.session_state: st.session_state.grupos = {}      
if "jogos_grupos" not in st.session_state: st.session_state.jogos_grupos = [] 
if "tabelas_grupos" not in st.session_state: st.session_state.tabelas_grupos = {} 
# Inicializador da página da TV
if "tv_pagina_atual" not in st.session_state: st.session_state.tv_pagina_atual = 0

# --- RECALCULADOR MATEMÁTICO ---
def atualizar_classificacao_grupos():
    tabelas_novas = {}
    for nome_g, lista_duplas in st.session_state.grupos.items():
        tabelas_novas[nome_g] = pd.DataFrame({
            'Dupla Atleta': lista_duplas, 'Pontos': 0, 'Vitórias': 0, 'Games Pró': 0, 'Games Contra': 0, 'Saldo Games': 0
        }).set_index('Dupla Atleta')
    
    for jogo in st.session_state.jogos_grupos:
        if jogo["encerrado"]:
            g, d1, d2 = jogo["grupo"], jogo["d1"], jogo["d2"]
            p1, p2 = int(jogo["p1"]), int(jogo["p2"])
            tabelas_novas[g].loc[d1, 'Games Pró'] += p1
            tabelas_novas[g].loc[d1, 'Games Contra'] += p2
            tabelas_novas[g].loc[d2, 'Games Pró'] += p2
            tabelas_novas[g].loc[d2, 'Games Contra'] += p1
            if p1 > p2:
                tabelas_novas[g].loc[d1, ['Pontos', 'Vitórias']] += [1, 1]
            else:
                tabelas_novas[g].loc[d2, ['Pontos', 'Vitórias']] += [1, 1]

    for g in tabelas_novas:
        df = tabelas_novas[g]
        df['Saldo Games'] = df['Games Pró'] - df['Games Contra']
        tabelas_novas[g] = df.sort_values(by=['Pontos', 'Saldo Games', 'Games Pró'], ascending=False)
    st.session_state.tabelas_grupos = tabelas_novas

# --- CARD DA QUADRA VIRTUAL ---
def desenhar_quadra_virtual(dupla1, dupla2, num_jogo, p1, p2, encerrado, nome_grupo):
    bg_cor = "#112415" if encerrado else "#1a2333"
    borda_cor = "#39ff14" if encerrado else "#1f293d"
    status_texto = "ENCERRADO" if encerrado else "EM ANDAMENTO"
    status_cor = "#39ff14" if encerrado else "#ffb703"
    
    html_quadra = f"""
    <div style="background-color: #121824; border: 2px solid {borda_cor}; border-radius: 10px; padding: 12px; font-family: sans-serif; color: #ffffff; margin-bottom: 10px; box-shadow: 0px 6px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 0.75rem; font-weight: bold;">
            <span style="background-color: #1f293d; color: #39ff14; padding: 2px 6px; border-radius: 4px;">JOGO {num_jogo} ({nome_grupo.upper()})</span>
            <span style="color: {status_cor};">● {status_texto}</span>
        </div>
        <div style="background-color: {bg_cor}; border-radius: 6px; padding: 8px; display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.95rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%; color: #ffffff;">{dupla1}</span>
                <span style="font-size: 1.3rem; font-weight: 900; color: #39ff14;">{p1 if p1 != "" else "-"}</span>
            </div>
            <div style="border-top: 1px dashed #2c3a54; margin: 2px 0;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.95rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%; color: #ffffff;">{dupla2}</span>
                <span style="font-size: 1.3rem; font-weight: 900; color: #ffffff;">{p2 if p2 != "" else "-"}</span>
            </div>
        </div>
    </div>
    """
    components.html(html_quadra, height=130, scrolling=False)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ Painel de Controle")
    senha = st.text_input("Senha Master Arena:", type="password")
    is_admin = (senha == CHAVE_ADMIN)
    if is_admin and st.button("🚨 RESETAR TORNEIO"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; color:#39ff14; margin-top:0;'>⚡ {NOME_SISTEMA}</h1>", unsafe_allow_html=True)

aba_controle, aba_painel_visual = st.tabs(["🎮 Painel de Arbitragem (Admin)", "📺 Telão da Lanchonete (Público)"])

# ----------------------------------------------------
# ABA 1: CONTROLES INTERNOS DE ARBITRAGEM
# ----------------------------------------------------
with aba_controle:
    if st.session_state.torneio_fase == "Inscrição":
        st.markdown("<div class='titulo-secao'>Painel de Inscrições</div>", unsafe_allow_html=True)
        st.session_state.categoria_selecionada = st.selectbox("Selecione a Categoria do Torneio:", ["Masculino 4ª Classe", "Masculino 5ª Classe", "Feminino Iniciante", "Misto B"])
        
        if is_admin:
            with st.form("cad_dupla", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1: j1 = st.text_input("Atleta 1:")
                with c2: j2 = st.text_input("Atleta 2:")
                if st.form_submit_button("➕ Registrar Dupla"):
                    if j1 and j2: st.session_state.duplas.append(f"{j1.strip()} / {j2.strip()}"); st.rerun()
        
        st.write(f"**Duplas Confirmadas ({len(st.session_state.duplas)}):**")
        for idx, dp in enumerate(st.session_state.duplas): st.write(f"🔹 {idx+1}. {dp}")
            
        if is_admin and len(st.session_state.duplas) >= 3:
            if st.button("🎲 GERAR CHAVES E JOGOS AUTOMATICAMENTE"):
                lista_sorteio = list(st.session_state.duplas); random.shuffle(lista_sorteio)
                tam = 3 if len(lista_sorteio) <= 7 else 4
                letra = 'A'; st.session_state.grupos = {}; st.session_state.jogos_grupos = []
                for i in range(0, len(lista_sorteio), tam):
                    fatia = lista_sorteio[i:i+tam]; nome_g = f"Grupo {letra}"; st.session_state.grupos[nome_g] = fatia
                    for g_i in range(len(fatia)):
                        for g_j in range(g_i + 1, len(fatia)):
                            st.session_state.jogos_grupos.append({"grupo": nome_g, "d1": fatia[g_i], "d2": fatia[g_j], "p1": 0, "p2": 0, "encerrado": False})
                    letra = chr(ord(letra) + 1)
                atualizar_classificacao_grupos(); st.session_state.torneio_fase = "Grupos"; st.rerun()

    elif st.session_state.torneio_fase == "Grupos":
        st.markdown(f"<div class='titulo-secao'>Lançamento de Resultados - {st.session_state.categoria_selecionada}</div>", unsafe_allow_html=True)
        for idx, juego in enumerate(st.session_state.jogos_grupos):
            status_txt = "🟢 CONCLUÍDO" if juego["encerrado"] else "⏳ EM ABERTO"
            with st.expander(f"➔ [{juego['grupo']}] {juego['d1']} VS {juego['d2']} | {status_txt}"):
                if is_admin:
                    with st.form(key=f"form_jogo_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1: g1 = st.number_input(f"Games D1", 0, 7, value=int(juego["p1"]), key=f"p1_val_{idx}")
                        with col_g2: g2 = st.number_input(f"Games D2", 0, 7, value=int(juego["p2"]), key=f"p2_val_{idx}")
                        if st.form_submit_button("💾 Salvar Placar"):
                            if g1 != g2:
                                st.session_state.jogos_grupos[idx]["p1"], st.session_state.jogos_grupos[idx]["p2"], st.session_state.jogos_grupos[idx]["encerrado"] = g1, g2, True
                                atualizar_classificacao_grupos(); st.rerun()

# ----------------------------------------------------
# 📺 ABA 2: TELÃO DA TV COM CARROSSEL JAVASCRIPT INFINITO
# ----------------------------------------------------
with aba_painel_visual:
    if st.session_state.torneio_fase == "Inscrição":
        st.info("Aguardando sorteio das chaves.")
    else:
        JOGOS_POR_PAGINA = 6
        todos_jogos = st.session_state.jogos_grupos
        total_jogos = len(todos_jogos)
        
        total_paginas = (total_jogos + JOGOS_POR_PAGINA - 1) // JOGOS_POR_PAGINA
        
        # Garante que a página atual está dentro do limite real
        if st.session_state.tv_pagina_atual >= total_paginas:
            st.session_state.tv_pagina_atual = 0
            
        pag_atual = st.session_state.tv_pagina_atual
        
        # Cabeçalho com o indicador da página
        st.markdown(f"""
            <h3 style='text-align:center; color:#39ff14; font-weight:900; margin-top:0;'>
                📺 CIRCUITO ARENA - {st.session_state.categoria_selecionada.upper()} 
                <span style='font-size:1rem; color:#8fa0bc; margin-left:15px;'>(Painel de Jogos: {pag_atual + 1}/{total_paginas})</span>
            </h3>
        """, unsafe_allow_html=True)
        
        col_tabelas, col_quadras = st.columns([45, 55])
        
        with col_tabelas:
            st.markdown("<div class='titulo-secao'>📊 Classificação dos Grupos</div>", unsafe_allow_html=True)
            for nome_g, df_classif in st.session_state.tabelas_grupos.items():
                st.markdown(f"<p style='color:#39ff14 !important; font-weight:bold; margin-top:8px !important;'>⚔️ {nome_g}</p>", unsafe_allow_html=True)
                st.table(df_classif)
                
        with col_quadras:
            st.markdown("<div class='titulo-secao'>🎾 Confrontos da Rodada</div>", unsafe_allow_html=True)
            
            inicio_idx = pag_atual * JOGOS_POR_PAGINA
            fim_idx = inicio_idx + JOGOS_POR_PAGINA
            lote_jogos = todos_jogos[inicio_idx:fim_idx]
            
            if lote_jogos:
                col_sub_grid = st.columns(2)
                for i_lote, jogo in enumerate(lote_jogos):
                    idx_real_do_jogo = inicio_idx + i_lote
                    col_alvo_q = col_sub_grid[i_lote % 2]
                    
                    p1_vis = jogo["p1"] if jogo["encerrado"] else ""
                    p2_vis = jogo["p2"] if jogo["encerrado"] else ""
                    
                    with col_alvo_q:
                        desenhar_quadra_virtual(
                            jogo['d1'], jogo['d2'], idx_real_do_jogo + 1, 
                            p1_vis, p2_vis, jogo["encerrado"], jogo["grupo"]
                        )

        # 🔄 INJETOR DE JAVASCRIPT: MOTOR DE LOOP INFINITO (CORRIGIDO)
        if total_paginas > 1:
            # Calcula o próximo passo matemático de forma circular
            proxima_pag = (pag_atual + 1) % total_paginas
            
            # Atualiza o estado via clique simulado oculto no Streamlit usando Javascript limpo
            # Esse código espera 10000ms (10 segundos) e força a atualização do estado
            st.session_state.tv_pagina_atual = proxima_pag
            
            componente_js_loop = f"""
                <script>
                setTimeout(function() {{
                    window.parent.document.querySelector('iframe').contentWindow.location.reload();
                }}, 10000);
                </script>
            """
            # Injeta o timer silencioso diretamente no corpo HTML do navegador
            components.html(componente_js_loop, height=0, width=0)
