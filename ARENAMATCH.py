import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random

# 🎾 CONFIGURAÇÃO DA PÁGINA PREMIUM ULTRA WIDE
st.set_page_config(
    page_title="ArenaMatch Pro - Multi-Torneios",
    page_icon="🎾",
    layout="wide"
)

NOME_SISTEMA = "ArenaMatch Pro"
CHAVE_ADMIN = "arena123"
CATEGORIAS_OFICIAIS = ["Masculino 4ª Classe", "Feminino Iniciante", "Misto B"]

# 🎨 DESIGN ESPORTIVO COM REGRAS DE CONTRASTE FIXAS
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19 !important; } 
    section[data-testid="stSidebar"] { background-color: #060911 !important; border-right: 2px solid #1f293d; }
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { color: #ffffff !important; margin: 2px 0 !important; }
    
    .titulo-secao {
        color: #39ff14 !important; font-size: 1.2rem !important; font-weight: bold !important;
        border-left: 5px solid #39ff14; padding-left: 10px; margin-top: 15px; margin-bottom: 12px; text-transform: uppercase;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: #ffffff !important; background-color: #121824 !important; border: 2px solid #1f293d !important; border-radius: 8px !important;
    }
    
    /* Tabelas Anti-Fundo Branco */
    div[data-testid="stTable"] { background-color: #121824 !important; border-radius: 8px; overflow: hidden; border: 2px solid #1f293d !important; }
    div[data-testid="stTable"] table { background-color: #121824 !important; width: 100% !important; margin: 0 !important; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; font-size: 0.85rem !important; padding: 6px !important; }
    div[data-testid="stTable"] td { background-color: #121824 !important; color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; font-weight: bold !important; font-size: 0.85rem !important; padding: 6px !important; }
    
    button[data-baseweb="tab"] { color: #8fa0bc !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #39ff14 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE BANCO DE DADOS MULTI-CATEGORIA ---
if "torneios" not in st.session_state:
    st.session_state.torneios = {}
    for cat in CATEGORIAS_OFICIAIS:
        st.session_state.torneios[cat] = {
            "duplas": [],
            "fase": "Inscrição",
            "grupos": {},
            "jogos_grupos": [],
            "tabelas_grupos": {}
        }

# Controles globais do motor de rotação da TV
if "tv_cat_index" not in st.session_state: st.session_state.tv_cat_index = 0
if "tv_pag_index" not in st.session_state: st.session_state.tv_pag_index = 0

# --- RECALCULADOR MATEMÁTICO MULTI-CATEGORIA ---
def atualizar_classificacao(cat):
    dados = st.session_state.torneios[cat]
    tabelas_novas = {}
    
    for nome_g, lista_duplas in dados["grupos"].items():
        tabelas_novas[nome_g] = pd.DataFrame({
            'Dupla Atleta': lista_duplas, 'Pontos': 0, 'Vitórias': 0, 'GP': 0, 'GC': 0, 'Saldo': 0
        }).set_index('Dupla Atleta')
    
    for jogo in dados["jogos_grupos"]:
        if jogo["encerrado"]:
            g, d1, d2 = jogo["grupo"], jogo["d1"], jogo["d2"]
            p1, p2 = int(jogo["p1"]), int(jogo["p2"])
            tabelas_novas[g].loc[d1, 'GP'] += p1
            tabelas_novas[g].loc[d1, 'GC'] += p2
            tabelas_novas[g].loc[d2, 'GP'] += p2
            tabelas_novas[g].loc[d2, 'GC'] += p1
            if p1 > p2:
                tabelas_novas[g].loc[d1, ['Pontos', 'Vitórias']] += [1, 1]
            else:
                tabelas_novas[g].loc[d2, ['Pontos', 'Vitórias']] += [1, 1]

    for g in tabelas_novas:
        df = tabelas_novas[g]
        df['Saldo'] = df['GP'] - df['GC']
        tabelas_novas[g] = df.sort_values(by=['Pontos', 'Saldo', 'GP'], ascending=False)
        
    st.session_state.torneios[cat]["tabelas_grupos"] = tabelas_novas

# --- DESIGN DO CARD DA QUADRA VIRTUAL ---
def desenhar_quadra_virtual(dupla1, dupla2, num_jogo, p1, p2, encerrado, nome_grupo):
    bg_cor = "#112415" if encerrado else "#1a2333"
    borda_cor = "#39ff14" if encerrado else "#1f293d"
    status_texto = "FINAL" if encerrado else "JOGANDO"
    status_cor = "#39ff14" if encerrado else "#ffb703"
    
    html_quadra = f"""
    <div style="background-color: #121824; border: 2px solid {borda_cor}; border-radius: 8px; padding: 10px; font-family: sans-serif; color: #ffffff; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 0.7rem; font-weight: bold;">
            <span style="background-color: #1f293d; color: #39ff14; padding: 1px 5px; border-radius: 3px;">JOGO {num_jogo} ({nome_grupo.upper()})</span>
            <span style="color: {status_cor};">● {status_texto}</span>
        </div>
        <div style="background-color: {bg_cor}; border-radius: 5px; padding: 6px; display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%; color: #ffffff;">{dupla1}</span>
                <span style="font-size: 1.2rem; font-weight: 900; color: #39ff14;">{p1 if p1 != "" else "-"}</span>
            </div>
            <div style="border-top: 1px dashed #2c3a54; margin: 1px 0;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%; color: #ffffff;">{dupla2}</span>
                <span style="font-size: 1.2rem; font-weight: 900; color: #ffffff;">{p2 if p2 != "" else "-"}</span>
            </div>
        </div>
    </div>
    """
    components.html(html_quadra, height=115, scrolling=False)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.markdown("## ⚙️ Central de Arbitragem")
    senha = st.text_input("Senha Master Arena:", type="password")
    is_admin = (senha == CHAVE_ADMIN)
    
    st.markdown("---")
    st.markdown("### 🏆 Selecione a Categoria para Gerenciar:")
    cat_foco = st.selectbox("Categoria Atual:", CATEGORIAS_OFICIAIS)
    
    if is_admin and st.button("🚨 RESETAR TODO O EVENTO"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; color:#39ff14; margin-top:0;'>⚡ {NOME_SISTEMA}</h1>", unsafe_allow_html=True)

aba_controle, aba_painel_visual = st.tabs(["🎮 Mesa de Controle (Admin)", "📺 Telão da TV (Modo Rotativo Automático)"])

# ----------------------------------------------------
# ABA 1: MESA DE CONTROLE INDIVIDUAL POR CATEGORIA
# ----------------------------------------------------
with aba_controle:
    t_dados = st.session_state.torneios[cat_foco]
    st.subheader(f"Gerenciando Prova: {cat_foco}")
    
    if t_dados["fase"] == "Inscrição":
        st.markdown("<div class='titulo-secao'>Inscrições da Categoria</div>", unsafe_allow_html=True)
        if is_admin:
            with st.form(f"cad_dupla_{cat_foco}", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1: j1 = st.text_input("Atleta 1:")
                with c2: j2 = st.text_input("Atleta 2:")
                if st.form_submit_button("➕ Inscrever Dupla"):
                    if j1 and j2:
                        st.session_state.torneios[cat_foco]["duplas"].append(f"{j1.strip()} / {j2.strip()}")
                        st.rerun()
        else:
            st.info("Digite a Senha Master na barra lateral para abrir os formulários.")
            
        st.write(f"**Duplas inscritas nesta categoria ({len(t_dados['duplas'])}):**")
        for idx, dp in enumerate(t_dados["duplas"]): st.write(f"🔹 {idx+1}. {dp}")
        
        if is_admin and len(t_dados["duplas"]) >= 3:
            if st.button(f"🎲 Sorteie e Iniciar {cat_foco}"):
                lista_sorteio = list(t_dados["duplas"]); random.shuffle(lista_sorteio)
                tam = 3 if len(lista_sorteio) <= 7 else 4
                letra = 'A'
                st.session_state.torneios[cat_foco]["grupos"] = {}
                st.session_state.torneios[cat_foco]["jogos_grupos"] = []
                
                for i in range(0, len(lista_sorteio), tam):
                    fatia = lista_sorteio[i:i+tam]
                    nome_g = f"Grupo {letra}"
                    st.session_state.torneios[cat_foco]["grupos"][nome_g] = fatia
                    for g_i in range(len(fatia)):
                        for g_j in range(g_i + 1, len(fatia)):
                            st.session_state.torneios[cat_foco]["jogos_grupos"].append({
                                "grupo": nome_g, "d1": fatia[g_i], "d2": fatia[g_j], "p1": 0, "p2": 0, "encerrado": False
                            })
                    letra = chr(ord(letra) + 1)
                
                st.session_state.torneios[cat_foco]["fase"] = "Grupos"
                atualizar_classificacao(cat_foco)
                st.rerun()

    elif t_dados["fase"] == "Grupos":
        st.markdown("<div class='titulo-secao'>Resultados da Categoria</div>", unsafe_allow_html=True)
        for idx, juego in enumerate(t_dados["jogos_grupos"]):
            status_txt = "🟢 CONCLUÍDO" if juego["encerrado"] else "⏳ EM ABERTO"
            with st.expander(f"➔ [{juego['grupo']}] {juego['d1']} VS {juego['d2']} | {status_txt}"):
                if is_admin:
                    with st.form(key=f"form_jogo_{cat_foco}_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1: g1 = st.number_input("Games D1", 0, 7, value=int(juego["p1"]), key=f"p1_{cat_foco}_{idx}")
                        with col_g2: g2 = st.number_input("Games D2", 0, 7, value=int(juego["p2"]), key=f"p2_{cat_foco}_{idx}")
                        if st.form_submit_button("💾 Atualizar Placar"):
                            if g1 != g2:
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["p1"] = g1
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["p2"] = g2
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["encerrado"] = True
                                atualizar_classificacao(cat_foco)
                                st.rerun()

# ----------------------------------------------------
# 📺 ABA 2: TELÃO ORQUESTRADOR MULTI-TORNEIOS INTELIGENTE
# ----------------------------------------------------
with aba_painel_visual:
    # Captura qual categoria a TV deve renderizar neste exato segundo
    categoria_tv = CATEGORIAS_OFICIAIS[st.session_state.tv_cat_index]
    dados_tv = st.session_state.torneios[categoria_tv]
    
    st.markdown(f"""
        <h2 style='text-align:center; color:#39ff14; font-weight:900; margin-top:0; background-color:#121824; padding:10px; border-radius:8px;'>
            📺 PAINEL OFICIAL: {categoria_tv.upper()}
        </h2>
    """, unsafe_allow_html=True)
    
    if dados_tv["fase"] == "Inscrição":
        st.warning(f"Fase de montagem de chaves para a categoria: {categoria_tv}. Próxima categoria em instantes...")
        # Configurações de salto simples se não houver jogos ainda nesta chave
        total_paginas_tv = 1
        proxima_pagina = 0
        proximo_cat_index = (st.session_state.tv_cat_index + 1) % len(CATEGORIAS_OFICIAIS)
    else:
        # paginação interna dos confrontos da categoria ativa
        JOGOS_POR_PAGINA = 6
        todos_jogos_tv = dados_tv["jogos_grupos"]
        total_jogos_tv = len(todos_jogos_tv)
        total_paginas_tv = (total_jogos_tv + JOGOS_POR_PAGINA - 1) // JOGOS_POR_PAGINA
        
        if st.session_state.tv_pag_index >= total_paginas_tv:
            st.session_state.tv_pag_index = 0
            
        pag_atual_tv = st.session_state.tv_pag_index
        
        # Desenha o Layout Dividido
        col_esq, col_dir = st.columns([45, 55])
        
        with col_esq:
            st.markdown("<div class='titulo-secao'>📊 Classificação de Grupos</div>", unsafe_allow_html=True)
            for nome_g, df_classif in dados_tv["tabelas_grupos"].items():
                st.markdown(f"<p style='color:#39ff14; font-weight:bold; margin-top:5px;'>⚔️ {nome_g}</p>", unsafe_allow_html=True)
                st.table(df_classif)
                
        with col_dir:
            st.markdown(f"<div class='titulo-secao'>🎾 Tabela de Jogos (Painel {pag_atual_tv + 1}/{total_paginas_tv})</div>", unsafe_allow_html=True)
            inicio_idx = pag_atual_tv * JOGOS_POR_PAGINA
            fim_idx = inicio_idx + JOGOS_POR_PAGINA
            lote_jogos_tv = todos_jogos_tv[inicio_idx:fim_idx]
            
            if lote_jogos_tv:
                grid_quadras_tv = st.columns(2)
                for i_lote, jogo in enumerate(lote_jogos_tv):
                    idx_real = inicio_idx + i_lote
                    col_alvo = grid_quadras_tv[i_lote % 2]
                    p1_v = jogo["p1"] if jogo["encerrado"] else ""
                    p2_v = jogo["p2"] if jogo["encerrado"] else ""
                    with col_alvo:
                        desenhar_quadra_virtual(jogo['d1'], jogo['d2'], idx_real + 1, p1_v, p2_v, jogo["encerrado"], jogo["grupo"])

        # Cálculo do próximo passo do loop
        if (pag_atual_tv + 1) < total_paginas_tv:
            # Se a categoria ainda tem mais jogos para mostrar, vai para a próxima página dela
            proxima_pagina = pag_atual_tv + 1
            proximo_cat_index = st.session_state.tv_cat_index
        else:
            # Se os jogos daquela categoria terminaram, zera a página e pula para a PRÓXIMA CATEGORIA
            proxima_pagina = 0
            proximo_cat_index = (st.session_state.tv_cat_index + 1) % len(CATEGORIAS_OFICIAIS)

    # 🔄 ATUALIZADOR AUTOMÁTICO VIA JAVASCRIPT (Loop de 10 segundos)
    st.session_state.tv_pag_index = proxima_pagina
    st.session_state.tv_cat_index = proximo_cat_index
    
    componente_js_multicat = """
        <script>
        setTimeout(function() {
            window.parent.document.querySelector('iframe').contentWindow.location.reload();
        }, 10000);
        </script>
    """
    components.html(componente_js_multicat, height=0, width=0)
