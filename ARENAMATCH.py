import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random

# 🎾 CONFIGURAÇÃO DA PÁGINA PREMIUM ULTRA WIDE
st.set_page_config(
    page_title="ArenaMatch Pro - Padrão GRIPO",
    page_icon="🎾",
    layout="wide"
)

NOME_SISTEMA = "ArenaMatch Pro"
CHAVE_ADMIN = "arena123"
CATEGORIAS_OFICIAIS = ["Masculino 4ª Classe", "Feminino Iniciante", "Misto B"]
TOTAL_QUADRAS_CLUBE = 4 

# 🎨 DESIGN ESPORTIVO PROFISSIONAL PREMIUM (CONTRASTE CONFIGURADO)
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
    
    .stButton>button, div[data-testid="stForm"] button {
        background-color: #121824 !important; color: #ffffff !important; border: 2px solid #1f293d !important;
        font-weight: bold !important; border-radius: 6px !important; padding: 6px 12px !important; transition: all 0.2s ease !important;
    }
    .stButton>button:hover, div[data-testid="stForm"] button:hover {
        background-color: #39ff14 !important; color: #0b0f19 !important; border-color: #39ff14 !important;
    }
    
    div[data-testid="stTable"] { background-color: #121824 !important; border-radius: 8px; overflow: hidden; border: 2px solid #1f293d !important; }
    div[data-testid="stTable"] table { background-color: #121824 !important; width: 100% !important; margin: 0 !important; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; font-size: 0.85rem !important; padding: 6px !important; }
    div[data-testid="stTable"] td { background-color: #121824 !important; color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; font-weight: bold !important; font-size: 0.85rem !important; padding: 6px !important; }
    
    button[data-baseweb="tab"] { color: #8fa0bc !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #39ff14 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE BANCO DE DADOS SEGURO ---
if "torneios" not in st.session_state:
    st.session_state.torneios = {}
    for cat in CATEGORIAS_OFICIAIS:
        st.session_state.torneios[cat] = {
            "duplas": [],
            "fase": "Inscrição", 
            "grupos": {},
            "jogos_grupos": [],
            "tabelas_grupos": {},
            "jogos_eliminatoria": [] 
        }

# Controle de edição de registros
if "editando_idx" not in st.session_state: st.session_state.editando_idx = None
if "editando_cat" not in st.session_state: st.session_state.editando_cat = None

# 🚨 SISTEMA DE ROTAÇÃO INDEPENDENTE PARA A TV (SEM CONFLITO COM SIDEBAR)
if "tv_cat_ativa" not in st.session_state: st.session_state.tv_cat_ativa = CATEGORIAS_OFICIAIS[0]
if "tv_pag_ativa" not in st.session_state: st.session_state.tv_pag_ativa = 0

# --- PROCESSADOR MATEMÁTICO DE JOGOS ---
def atualizar_classificacao(cat):
    dados = st.session_state.torneios[cat]
    tabelas_novas = {}
    
    for nome_g, lista_duplas in dados["grupos"].items():
        tabelas_novas[nome_g] = pd.DataFrame({
            'Dupla Atleta': lista_duplas, 'Pontos': 0, 'Vitórias': 0, 'GP': 0, 'GC': 0, 'Saldo': 0
        }).set_index('Dupla Atleta')
    
    for jogo in dados["jogos_grupos"]:
        if juego["encerrado"]:
            g = juego["grupo"]
            d1, d2 = juego["d1"], juego["d2"]
            p1, p2 = int(juego["p1"]), int(juego["p2"])
            
            if d1 in tabelas_novas[g].index and d2 in tabelas_novas[g].index:
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
        tabelas_novas[g] = df.sort_values(by=['Pontos', 'Vitórias', 'Saldo', 'GP'], ascending=False)
        
    st.session_state.torneios[cat]["tabelas_grupos"] = tabelas_novas

# --- CARD VISUAL DE CONFRONTO DA TV ---
def desenhar_quadra_virtual(dupla1, dupla2, num_jogo, p1, p2, encerrado, f_nome, quadra):
    if encerrado:
        bg_cor, borda_cor, status_txt, status_cor = "#112415", "#39ff14", "FINALIZADO", "#39ff14"
    elif quadra != "Chamando...":
        bg_cor, borda_cor, status_txt, status_cor = "#2a210f", "#ffb703", f"QUADRA {quadra}", "#ffb703"
    else:
        bg_cor, borda_cor, status_txt, status_cor = "#1a2333", "#1f293d", "AGUARDANDO", "#8fa0bc"
        
    html_quadra = f"""
    <div style="background-color: #121824; border: 2px solid {borda_cor}; border-radius: 8px; padding: 10px; font-family: sans-serif; color: #ffffff; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 0.7rem; font-weight: bold;">
            <span style="background-color: #1f293d; color: #39ff14; padding: 1px 5px; border-radius: 3px;">J JOGO {num_jogo} ({f_nome.upper()})</span>
            <span style="color: {status_cor}; font-weight: 900; letter-spacing: 1px;">● {status_txt}</span>
        </div>
        <div style="background-color: {bg_cor}; border-radius: 5px; padding: 6px; display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.85rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%; color: #ffffff;">{dupla1}</span>
                <span style="font-size: 1.1rem; font-weight: 900; color: #39ff14;">{p1 if encerrado else "-"}</span>
            </div>
            <div style="border-top: 1px dashed #2c3a54; margin: 1px 0;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.85rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%; color: #ffffff;">{dupla2}</span>
                <span style="font-size: 1.1rem; font-weight: 900; color: #ffffff;">{p2 if encerrado else "-"}</span>
            </div>
        </div>
    </div>
    """
    components.html(html_quadra, height=115, scrolling=False)

# --- SIDEBAR DE SELEÇÃO DE ARBITRAGEM ---
with st.sidebar:
    st.markdown("## ⚙️ Central de Arbitragem")
    senha = st.text_input("Senha Master Arena:", type="password")
    is_admin = (senha == CHAVE_ADMIN)
    st.markdown("---")
    cat_foco = st.selectbox("🏆 Escolha o Torneio para Controlar:", CATEGORIAS_OFICIAIS)
    if is_admin and st.button("🚨 RESETAR TODO O EVENTO"):
        st.session_state.clear(); st.rerun()

# --- ABAS PRINCIPAIS ---
st.markdown(f"<h1 style='text-align:center; color:#39ff14; margin-top:0;'>⚡ {NOME_SISTEMA}</h1>", unsafe_allow_html=True)
aba_controle, aba_painel_visual = st.tabs(["🎮 Mesa de Controle (Admin)", "📺 Telão da TV (Modo Rotativo Padrão GRIPO)"])

# ----------------------------------------------------
# ABA 1: MESA DE CONTROLE
# ----------------------------------------------------
with aba_controle:
    t_dados = st.session_state.torneios[cat_foco]
    st.subheader(f"Mesa Operacional: {cat_foco}")
    
    # 1. INSCRIÇÕES
    if t_dados["fase"] == "Inscrição":
        st.markdown("<div class='titulo-secao'>Inscrições da Categoria</div>", unsafe_allow_html=True)
        if is_admin:
            if st.session_state.editando_idx is not None and st.session_state.editando_cat == cat_foco:
                idx_alvo = st.session_state.editando_idx
                a1, a2 = t_dados["duplas"][idx_alvo].split(" / ")
                with st.form("edit_dupla_form"):
                    novo_j1 = st.text_input("Atleta 1:", value=a1)
                    novo_j2 = st.text_input("Atleta 2:", value=a2)
                    if st.form_submit_button("💾 Salvar Modificação"):
                        st.session_state.torneios[cat_foco]["duplas"][idx_alvo] = f"{novo_j1.strip()} / {novo_j2.strip()}"
                        st.session_state.editando_idx, st.session_state.editando_cat = None, None
                        st.rerun()
            else:
                with st.form(f"cad_dupla_{cat_foco}", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1: j1 = st.text_input("Atleta 1:")
                    with c2: j2 = st.text_input("Atleta 2:")
                    if st.form_submit_button("Registrar Nova Dupla"):
                        if j1 and j2: t_dados["duplas"].append(f"{j1.strip()} / {j2.strip()}"); st.rerun()
        
        for idx, dp in enumerate(t_dados["duplas"]):
            col_nome, col_ed, col_ex = st.columns([70, 15, 15])
            with col_nome: st.markdown(f"<p style='padding:5px; background-color:#121824; border-radius:4px;'>🔹 {idx+1}. {dp}</p>", unsafe_allow_html=True)
            if is_admin:
                with col_ed: 
                    if st.button("✍️", key=f"ed_{cat_foco}_{idx}"): st.session_state.editando_idx, st.session_state.editando_cat = idx, cat_foco; st.rerun()
                with col_ex: 
                    if st.button("❌", key=f"ex_{cat_foco}_{idx}"): t_dados["duplas"].pop(idx); st.rerun()
                    
        if is_admin and len(t_dados["duplas"]) >= 4:
            st.markdown("---")
            if st.button(f"🎲 Gerar Chaves Automáticas"):
                lista = list(t_dados["duplas"]); random.shuffle(lista)
                metade = len(lista) // 2
                st.session_state.torneios[cat_foco]["grupos"] = {"Grupo A": lista[:metade], "Grupo B": lista[metade:]}
                st.session_state.torneios[cat_foco]["jogos_grupos"] = []
                
                for g_nome, f_duplas in st.session_state.torneios[cat_foco]["grupos"].items():
                    for i in range(len(f_duplas)):
                        for j in range(i+1, len(f_duplas)):
                            st.session_state.torneios[cat_foco]["jogos_grupos"].append({
                                "grupo": g_nome, "d1": f_duplas[i], "d2": f_duplas[j], "p1": 0, "p2": 0, "encerrado": False, "quadra": "Chamando..."
                            })
                st.session_state.torneios[cat_foco]["fase"] = "Grupos"
                atualizar_classificacao(cat_foco); st.rerun()

    # 2. FASE DE GRUPOS
    elif t_dados["fase"] == "Grupos":
        st.markdown("<div class='titulo-secao'>Painel de Lançamento e Chamada de Quadras</div>", unsafe_allow_html=True)
        
        todos_encerrados = all(j["encerrado"] for j in t_dados["jogos_grupos"])
        if todos_encerrados and is_admin:
            if st.button("🏆 FINALIZAR GRUPOS E GERAR MATA-MATA"):
                df_a = t_dados["tabelas_grupos"]["Grupo A"]
                df_b = t_dados["tabelas_grupos"]["Grupo B"]
                
                st.session_state.torneios[cat_foco]["jogos_eliminatoria"] = [
                    {"fase": "Semifinal 1", "d1": df_a.index[0], "d2": df_b.index[1], "p1": 0, "p2": 0, "encerrado": False, "quadra": "Chamando..."},
                    {"fase": "Semifinal 2", "d1": df_b.index[0], "d2": df_a.index[1], "p1": 0, "p2": 0, "encerrado": False, "quadra": "Chamando..."},
                    {"fase": "Grande Final", "d1": "Vencedor Semi 1", "d2": "Vencedor Semi 2", "p1": 0, "p2": 0, "encerrado": False, "quadra": "Chamando..."}
                ]
                st.session_state.torneios[cat_foco]["fase"] = "Eliminatoria"
                st.rerun()

        for idx, juego in enumerate(t_dados["jogos_grupos"]):
            status_txt = "🟢 CONCLUÍDO" if juego["encerrado"] else "⏳ EM ABERTO"
            with st.expander(f"➔ [{juego['grupo']}] {juego['d1']} VS {juego['d2']} | {status_txt}"):
                if is_admin:
                    nova_q = st.selectbox("Escalar Quadra:", [f"{i+1}" for i in range(TOTAL_QUADRAS_CLUBE)], key=f"q_grp_{cat_foco}_{idx}")
                    if st.button("Confirmar Quadra", key=f"b_q_{cat_foco}_{idx}"):
                        st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["quadra"] = nova_q; st.rerun()
                        
                    with st.form(key=f"f_j_g_{cat_foco}_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1: g1 = st.number_input("Games D1", 0, 7, value=int(juego["p1"]))
                        with col_g2: g2 = st.number_input("Games D2", 0, 7, value=int(juego["p2"]))
                        if st.form_submit_button("Lançar Placar"):
                            if g1 != g2:
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["p1"] = int(g1)
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["p2"] = int(g2)
                                st.session_state.torneios[cat_foco]["jogos_grupos"][idx]["encerrado"] = True
                                atualizar_classificacao(cat_foco); st.rerun()

    # 3. FASE DE PLAYOFFS
    elif t_dados["fase"] == "Eliminatoria":
        st.markdown("<div class='titulo-secao'>Chaves de Playoffs (Mata-Mata)</div>", unsafe_allow_html=True)
        for idx, juego in enumerate(t_dados["jogos_eliminatoria"]):
            status_txt = "🟢 CONCLUÍDO" if juego["encerrado"] else "⏳ EM ABERTO"
            with st.expander(f"➔ [{juego['fase']}] {juego['d1']} VS {juego['d2']} | {status_txt}"):
                if is_admin:
                    nova_q = st.selectbox("Escalar Quadra:", [f"{i+1}" for i in range(TOTAL_QUADRAS_CLUBE)], key=f"q_elim_{cat_foco}_{idx}")
                    if st.button("Confirmar Quadra", key=f"b_qe_{cat_foco}_{idx}"):
                        st.session_state.torneios[cat_foco]["jogos_eliminatoria"][idx]["quadra"] = nova_q; st.rerun()
                        
                    with st.form(key=f"f_j_e_{cat_foco}_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1: g1 = st.number_input("Games D1", 0, 7, value=int(juego["p1"]))
                        with col_g2: g2 = st.number_input("Games D2", 0, 7, value=int(juego["p2"]))
                        if st.form_submit_button("Salvar Placar Mata-Mata"):
                            if g1 != g2:
                                st.session_state.torneios[cat_foco]["jogos_eliminatoria"][idx]["p1"] = int(g1)
                                st.session_state.torneios[cat_foco]["jogos_eliminatoria"][idx]["p2"] = int(g2)
                                st.session_state.torneios[cat_foco]["jogos_eliminatoria"][idx]["encerrado"] = True
                                
                                vencedor = juego['d1'] if g1 > g2 else juego['d2']
                                if idx == 0: st.session_state.torneios[cat_foco]["jogos_eliminatoria"][2]["d1"] = vencedor
                                if idx == 1: st.session_state.torneios[cat_foco]["jogos_eliminatoria"][2]["d2"] = vencedor
                                st.rerun()

# ----------------------------------------------------
# 📺 ABA 2: TELÃO ORQUESTRADOR BLINDADO CONTRA BUGS
# ----------------------------------------------------
with aba_painel_visual:
    # Captura a categoria correta da rotação independente
    cat_tv_render = st.session_state.tv_cat_ativa
    dados_tv = st.session_state.torneios[cat_tv_render]
    
    st.markdown(f"""
        <h2 style='text-align:center; color:#39ff14; font-weight:900; margin-top:0; background-color:#121824; padding:10px; border-radius:8px;'>
            📺 CIRCUITO ARENA - {cat_tv_render.upper()}
        </h2>
    """, unsafe_allow_html=True)
    
    if dados_tv["fase"] == "Inscrição":
        st.warning(f"Fase de captação de atletas. Sorteio de chaves pendente para: {cat_tv_render}.")
        total_paginas_tv, proxima_pagina = 1, 0
        
        # Avança para a próxima categoria no próximo ciclo de 10s
        idx_atual = CATEGORIAS_OFICIAIS.index(cat_tv_render)
        proxima_categoria = CATEGORIAS_OFICIAIS[(idx_atual + 1) % len(CATEGORIAS_OFICIAIS)]
    else:
        jogos_alvo_tv = dados_tv["jogos_eliminatoria"] if dados_tv["fase"] == "Eliminatoria" else dados_tv["jogos_grupos"]
        
        JOGOS_POR_PAGINA = 6
        total_jogos_tv = len(jogos_alvo_tv)
        total_paginas_tv = (total_jogos_tv + JOGOS_POR_PAGINA - 1) // JOGOS_POR_PAGINA
        
        pag_atual_tv = st.session_state.tv_pag_ativa
        if pag_atual_tv >= total_paginas_tv: pag_atual_tv = 0
        
        col_esq, col_dir = st.columns([45, 55])
        
        with col_esq:
            if dados_tv["fase"] == "Eliminatoria":
                st.markdown("<div class='titulo-secao'>🏆 Fase Final (Mata-Mata)</div>", unsafe_allow_html=True)
                st.info("Chaves de Playoffs ativas! Acompanhe as semifinais e finais ao lado.")
            else:
                st.markdown("<div class='titulo-secao'>📊 Classificação de Grupos</div>", unsafe_allow_html=True)
                for nome_g, df_classif in dados_tv["tabelas_grupos"].items():
                    st.markdown(f"<p style='color:#39ff14; font-weight:bold; margin-top:5px;'>⚔️ {nome_g}</p>", unsafe_allow_html=True)
                    st.table(df_classif)
                
        with col_dir:
            st.markdown(f"<div class='titulo-secao'>🎾 Painel de Quadras (Grade {pag_atual_tv + 1}/{total_paginas_tv})</div>", unsafe_allow_html=True)
            inicio_idx = pag_atual_tv * JOGOS_POR_PAGINA
            fim_idx = inicio_idx + JOGOS_POR_PAGINA
            lote_jogos_tv = jogos_alvo_tv[inicio_idx:fim_idx]
            
            if lote_jogos_tv:
                grid_quadras_tv = st.columns(2)
                for i_lote, jogo in enumerate(lote_jogos_tv):
                    idx_real = inicio_idx + i_lote
                    col_alvo = grid_quadras_tv[i_lote % 2]
                    f_tag = jogo["fase"] if "fase" in jogo else jogo["grupo"]
                    
                    with col_alvo:
                        desenhar_quadra_virtual(jogo['d1'], jogo['d2'], idx_real + 1, jogo["p1"], jogo["p2"], jogo["encerrado"], f_tag, jogo["quadra"])

        # Cálculo de Próximo Passo Sem Interrupção
        if (pag_atual_tv + 1) < total_paginas_tv:
            proxima_pagina = pag_atual_tv + 1
            proxima_categoria = cat_tv_render
        else:
            proxima_pagina = 0
            idx_atual = CATEGORIAS_OFICIAIS.index(cat_tv_render)
            proxima_categoria = CATEGORIAS_OFICIAIS[(idx_atual + 1) % len(CATEGORIAS_OFICIAIS)]

    # Salva os próximos passos sem cruzar com a Sidebar
    st.session_state.tv_pag_ativa = proxima_pagina
    st.session_state.tv_cat_ativa = proxima_categoria
    
    # 🔄 ATUALIZADOR JAVASCRIPT EM SEGUNDO PLANO (10 SEGUNDOS)
    componente_js_multicat = """
        <script>
        setTimeout(function() {
            window.parent.document.querySelector('iframe').contentWindow.location.reload();
        }, 10000);
        </script>
    """
    components.html(componente_js_multicat, height=0, width=0)
