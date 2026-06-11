import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random

# 🎾 CONFIGURAÇÃO DA PÁGINA PREMIUM
st.set_page_config(
    page_title="ArenaMatch Pro - Painel Profissional",
    page_icon="🎾",
    layout="wide"
)

NOME_SISTEMA = "ArenaMatch Pro"
CHAVE_ADMIN = "arena123"
CATEGORIAS_OFICIAIS = ["Masculino 4ª Classe", "Feminino Iniciante", "Misto B"]

# 🎨 DESIGN ESPORTIVO PROFISSIONAL (CSS BLINDADO CONTRA BUG DE CORES)
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
    
    /* 🚨 CORREÇÃO GERAL DE BOTÕES (MÁXIMO CONTRASTE E ESTILO PREMIUM) */
    .stButton>button, div[data-testid="stForm"] button {
        background-color: #121824 !important; 
        color: #ffffff !important; 
        border: 2px solid #1f293d !important;
        font-weight: bold !important; 
        border-radius: 6px !important;
        padding: 6px 12px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover, div[data-testid="stForm"] button:hover {
        background-color: #39ff14 !important;
        color: #0b0f19 !important;
        border-color: #39ff14 !important;
        box-shadow: 0px 0px 10px rgba(57, 255, 20, 0.4) !important;
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

# Estados de edição de duplas
if "editando_idx" not in st.session_state: st.session_state.editando_idx = None
if "editando_cat" not in st.session_state: st.session_state.editando_cat = None

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
    st.markdown("### 🏆 Categoria em Edição:")
    cat_foco = st.selectbox("Escolha o Torneio:", CATEGORIAS_OFICIAIS)
    
    if is_admin and st.button("🚨 RESETAR TODO O EVENTO"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; color:#39ff14; margin-top:0;'>⚡ {NOME_SISTEMA}</h1>", unsafe_allow_html=True)

aba_controle, aba_painel_visual = st.tabs(["🎮 Mesa de Controle (Admin)", "📺 Telão da TV (Modo Rotativo Automático)"])

# ----------------------------------------------------
# ABA 1: MESA DE CONTROLE INDIVIDUAL COM EDITOR/EXCLUSOR
# ----------------------------------------------------
with aba_controle:
    t_dados = st.session_state.torneios[cat_foco]
    st.subheader(f"Gerenciando Prova: {cat_foco}")
    
    if t_dados["fase"] == "Inscrição":
        st.markdown("<div class='titulo-secao'>Inscrições da Categoria</div>", unsafe_allow_html=True)
        
        if is_admin:
            # Mecanismo Switch para alternar entre cadastro comum e edição de nomes
            if st.session_state.editando_idx is not None and st.session_state.editando_cat == cat_foco:
                idx_alvo = st.session_state.editando_idx
                dupla_atual = t_dados["duplas"][idx_alvo]
                a1_atual, a2_atual = dupla_atual.split(" / ")
                
                with st.form("edit_dupla_form"):
                    st.write("📝 **Corrigindo Registro da Dupla**")
                    c1, c2 = st.columns(2)
                    with c1: novo_j1 = st.text_input("Atleta 1:", value=a1_atual)
                    with c2: novo_j2 = st.text_input("Atleta 2:", value=a2_atual)
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.form_submit_button("💾 Salvar Alteração"):
                            if novo_j1 and novo_j2:
                                st.session_state.torneios[cat_foco]["duplas"][idx_alvo] = f"{novo_j1.strip()} / {novo_j2.strip()}"
                                st.session_state.editando_idx = None
                                st.session_state.editando_cat = None
                                st.rerun()
                    with col_b2:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state.editando_idx = None
                            st.session_state.editando_cat = None
                            st.rerun()
            else:
                with st.form(f"cad_dupla_{cat_foco}", clear_on_submit=True):
                    st.write("➕ **Nova Inscrição**")
                    c1, c2 = st.columns(2)
                    with c1: j1 = st.text_input("Atleta 1:")
                    with c2: j2 = st.text_input("Atleta 2:")
                    if st.form_submit_button("Registrar Dupla"):
                        if j1 and j2:
                            st.session_state.torneios[cat_foco]["duplas"].append(f"{j1.strip()} / {j2.strip()}")
                            st.rerun()
        else:
            st.info("🔒 Insira a senha Master na barra lateral para abrir a gestão de chaves.")
            
        st.write(f"**Lista de Atletas Confirmados ({len(t_dados['duplas'])}):**")
        
        # ✍️ CONSTRUÇÃO DA GRADE PROFISSIONAL DE GESTÃO (EDITAR/EXCLUIR)
        for idx, dp in enumerate(t_dados["duplas"]):
            col_nome, col_edit, col_excluir = st.columns([70, 15, 15])
            with col_nome:
                st.markdown(f"<p style='padding: 5px; background-color: #121824; border-radius:4px;'>🔹 {idx+1}. <b>{dp}</b></p>", unsafe_allow_html=True)
            with col_edit:
                if is_admin and st.button("✍️", key=f"btn_ed_{cat_foco}_{idx}"):
                    st.session_state.editando_idx = idx
                    st.session_state.editando_cat = cat_foco
                    st.rerun()
            with col_excluir:
                if is_admin and st.button("❌", key=f"btn_ex_{cat_foco}_{idx}"):
                    st.session_state.torneios[cat_foco]["duplas"].pop(idx)
                    st.rerun()
        
        if is_admin and len(t_dados["duplas"]) >= 3:
            st.markdown("---")
            if st.button(f"🎲 Sorteie as Chaves e Iniciar {cat_foco}"):
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
                        if st.form_submit_button("Atualizar Placar"):
                            if g1 != g2:
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["p1"] = g1
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["p2"] = g2
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["encerrado"] = True
                                atualizar_classificacao(cat_foco)
                                st.rerun()

# ----------------------------------------------------
# 📺 ABA 2: TELÃO ORQUESTRADOR MULTI-TORNEIOS
# ----------------------------------------------------
with aba_painel_visual:
    categoria_tv = CATEGORIAS_OFICIAIS[st.session_state.tv_cat_index]
    dados_tv = st.session_state.torneios[categoria_tv]
    
    st.markdown(f"""
        <h2 style='text-align:center; color:#39ff14; font-weight:900; margin-top:0; background-color:#121824; padding:10px; border-radius:8px;'>
            📺 PAINEL OFICIAL: {categoria_tv.upper()}
        </h2>
    """, unsafe_allow_html=True)
    
    if dados_tv["fase"] == "Inscrição":
        st.warning(f"Fase de montagem de chaves para a categoria: {categoria_tv}. Próxima categoria em instantes...")
        total_paginas_tv = 1
        proxima_pagina = 0
        proximo_cat_index = (st.session_state.tv_cat_index + 1) % len(CATEGORIAS_OFICIAIS)
    else:
        JOGOS_POR_PAGINA = 6
        todos_jogos_tv = dados_tv["jogos_grupos"]
        total_jogos_tv = len(todos_jogos_tv)
        total_paginas_tv = (total_jogos_tv + JOGOS_POR_PAGINA - 1) // JOGOS_POR_PAGINA
        
        if st.session_state.tv_pag_index >= total_paginas_tv:
            st.session_state.tv_pag_index = 0
            
        pag_atual_tv = st.session_state.tv_pag_index
        
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

        if (pag_atual_tv + 1) < total_paginas_tv:
            proxima_pagina = pag_atual_tv + 1
            proximo_cat_index = st.session_state.tv_cat_index
        else:
            proxima_pagina = 0
            proximo_cat_index = (st.session_state.tv_cat_index + 1) % len(CATEGORIAS_OFICIAIS)

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
