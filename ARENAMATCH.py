import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random

# 🎾 CONFIGURAÇÃO DA PÁGINA ULTRA WIDE (TELA CHEIA)
st.set_page_config(
    page_title="ArenaMatch Pro - Telão Fixo",
    page_icon="🎾",
    layout="wide"
)

NOME_SISTEMA = "ArenaMatch Pro"
CHAVE_ADMIN = "arena123"

# 🎨 CSS CIRÚRGICO PARA BANIR A BARRA DE ROLAGEM GERAL
st.markdown("""
    <style>
    /* Força o app a ocupar exatamente a altura do monitor e esconde barras de rolagem globais */
    .stApp { 
        background-color: #0b0f19; 
        max-height: 100vh; 
        overflow: hidden !important; 
    } 
    
    /* Remove padding padrão do streamlit para ganhar espaço precioso */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    
    section[data-testid="stSidebar"] { background-color: #060911; border-right: 2px solid #1f293d; }
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { color: #ffffff !important; margin: 2px 0 !important; }
    
    .titulo-secao {
        color: #39ff14 !important; font-size: 1.1rem !important; font-weight: bold !important;
        border-left: 4px solid #39ff14; padding-left: 8px; margin-top: 5px !important; margin-bottom: 8px !important; text-transform: uppercase;
    }
    
    /* Tabelas Ultra Compactas para a TV */
    div[data-testid="stTable"] table { border: 1px solid #1f293d !important; background-color: #121824 !important; width: 100%; margin-bottom: 5px !important; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; font-size: 0.75rem; padding: 2px !important; }
    div[data-testid="stTable"] td { color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; font-weight: bold; font-size: 0.75rem; padding: 2px !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if "duplas" not in st.session_state: st.session_state.duplas = []
if "categoria_selecionada" not in st.session_state: st.session_state.categoria_selecionada = "4ª Categoria"
if "torneio_fase" not in st.session_state: st.session_state.torneio_fase = "Inscrição"  
if "grupos" not in st.session_state: st.session_state.grupos = {}      
if "jogos_grupos" not in st.session_state: st.session_state.jogos_grupos = [] 
if "tabelas_grupos" not in st.session_state: st.session_state.tabelas_grupos = {} 

# --- RECALCULADOR DA MATRIZ DOS GRUPOS ---
def atualizar_classificacao_grupos():
    tabelas_novas = {}
    for nome_g, lista_duplas in st.session_state.grupos.items():
        tabelas_novas[nome_g] = pd.DataFrame({
            'Dupla': lista_duplas, 'Pts': 0, 'Vit': 0, 'GP': 0, 'GC': 0, 'Saldo': 0
        }).set_index('Dupla')
    
    for jogo in st.session_state.jogos_grupos:
        if jogo["encerrado"]:
            g, d1, d2 = jogo["grupo"], jogo["d1"], jogo["d2"]
            p1, p2 = int(jogo["p1"]), int(jogo["p2"])
            tabelas_novas[g].loc[d1, 'GP'] += p1
            tabelas_novas[g].loc[d1, 'GC'] += p2
            tabelas_novas[g].loc[d2, 'GP'] += p2
            tabelas_novas[g].loc[d2, 'GC'] += p1
            if p1 > p2:
                tabelas_novas[g].loc[d1, ['Pts', 'Vit']] += [1, 1]
            else:
                tabelas_novas[g].loc[d2, ['Pts', 'Vit']] += [1, 1]

    for g in tabelas_novas:
        df = tabelas_novas[g]
        df['Saldo'] = df['GP'] - df['GC']
        tabelas_novas[g] = df.sort_values(by=['Pts', 'Saldo', 'GP'], ascending=False)
    st.session_state.tabelas_grupos = tabelas_novas

# --- VISUAL MINI-QUADRA (MÁXIMA ECONOMIA DE ESPAÇO) ---
def desenhar_quadra_virtual(dupla1, dupla2, num_jogo, p1, p2, encerrado, nome_grupo):
    bg_cor = "#112415" if encerrado else "#121824"
    borda_cor = "#39ff14" if encerrado else "#1f293d"
    status_texto = "FIM" if encerrado else "PLAY"
    status_cor = "#39ff14" if encerrado else "#ffb703"
    
    html_quadra = f"""
    <div style="background-color: {bg_cor}; border: 1px solid {borda_cor}; border-radius: 6px; padding: 4px; font-family: sans-serif; color: #ffffff; box-sizing: border-box; margin-bottom: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; font-size: 0.6rem; font-weight: bold;">
            <span style="color: #8fa0bc;">J{num_jogo} ({nome_grupo.replace("Grupo ", "")})</span>
            <span style="color: {status_cor};">● {status_texto}</span>
        </div>
        <div style="background-color: rgba(0,0,0,0.15); border-radius: 3px; padding: 4px; display: flex; flex-direction: column; gap: 2px;">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%;">{dupla1.split(' / ')[0]}</span>
                <span style="font-weight: 900; color: #39ff14;">{p1 if p1 != "" else "-"}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%;">{dupla2.split(' / ')[0]}</span>
                <span style="font-weight: 900; color: #ffffff;">{p2 if p2 != "" else "-"}</span>
            </div>
        </div>
    </div>
    """
    components.html(html_quadra, height=62, scrolling=False)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.markdown("## ⚙️ Arbitragem")
    senha = st.text_input("Senha Master:", type="password")
    is_admin = (senha == CHAVE_ADMIN)
    if is_admin and st.button("🚨 RESETAR TORNEIO"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
aba_controle, aba_painel_visual = st.tabs(["🎮 Arbitragem", "📺 Telão Fixo da TV (Sem Rolagem)"])

with aba_controle:
    # (O painel de arbitragem continua igual para o seu controle)
    if st.session_state.torneio_fase == "Inscrição":
        st.markdown("<div class='titulo-secao'>Painel de Inscrições</div>", unsafe_allow_html=True)
        st.session_state.categoria_selecionada = st.selectbox("Categoria:", ["4ª Classe", "5ª Classe", "Iniciante"])
        if is_admin:
            with st.form("cad_dupla", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1: j1 = st.text_input("Atleta 1:")
                with c2: j2 = st.text_input("Atleta 2:")
                if st.form_submit_button("➕ Registrar"):
                    if j1 and j2: st.session_state.duplas.append(f"{j1.strip()} / {j2.strip()}"); st.rerun()
        if is_admin and len(st.session_state.duplas) >= 3:
            if st.button("🎲 GERAR CHAVES AUTOMATICAMENTE"):
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
        for idx, dp in enumerate(st.session_state.duplas): st.write(f"🔹 {idx+1}. {dp}")

    elif st.session_state.torneio_fase == "Grupos":
        st.markdown(f"<div class='titulo-secao'>Lançamento de Resultados</div>", unsafe_allow_html=True)
        for idx, jogo in enumerate(st.session_state.jogos_grupos):
            status_txt = "🟢 CONCLUÍDO" if jogo["encerrado"] else "⏳ EM ABERTO"
            with st.expander(f"➔ [{jogo['grupo']}] {jogo['d1']} VS {jogo['d2']} | {status_txt}"):
                if is_admin:
                    with st.form(key=f"form_jogo_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1: g1 = st.number_input(f"Games D1", 0, 7, value=int(jogo["p1"]), key=f"p1_val_{idx}")
                        with col_g2: g2 = st.number_input(f"Games D2", 0, 7, value=int(jogo["p2"]), key=f"p2_val_{idx}")
                        if st.form_submit_button("💾 Salvar"):
                            if g1 != g2:
                                st.session_state.jogos_grupos[idx]["p1"], st.session_state.jogos_grupos[idx]["p2"], st.session_state.jogos_grupos[idx]["encerrado"] = g1, g2, True
                                atualizar_classificacao_grupos(); st.rerun()

# --- 📺 O SEGREDO DO TELÃO FIXO INTEGRAÇÃO LADO A LADO ---
with aba_painel_visual:
    if st.session_state.torneio_fase == "Inscrição":
        st.info("Aguardando sorteio das chaves.")
    else:
        # Dividimos a tela da TV em duas metades horizontais perfeitas
        # Coluna 1 (Esquerda - 35% de largura): Tabelas de Classificação dos Grupos
        # Coluna 2 (Direita - 65% de largura): Grade Geral com TODOS os jogos
        col_esquerda, col_direita = st.columns([35, 65])
        
        with col_esquerda:
            st.markdown("<div class='titulo-secao'>📊 Classificação Geral</div>", unsafe_allow_html=True)
            # Mostra as tabelas empilhadas de forma bem fina e compacta
            for nome_g, df_classif in st.session_state.tabelas_grupos.items():
                st.markdown(f"<span style='color:#39ff14; font-weight:bold; font-size:0.8rem;'>⚔️ {nome_g}</span>", unsafe_allow_html=True)
                st.table(df_classif)
                
        with col_direita:
            st.markdown("<div class='titulo-secao'>🎾 Painel Geral de Jogos (Resultados e Andamento)</div>", unsafe_allow_html=True)
            
            todos_jogos = st.session_state.jogos_grupos
            if todos_jogos:
                # Distribuímos todos os jogos em uma grade super larga de 5 colunas horizontais.
                # Se houver 15 jogos, eles ocuparão apenas 3 linhas de altura, cabendo 100% na tela!
                col_grid_jogos = st.columns(5)
                for idx_j, jogo in enumerate(todos_jogos):
                    col_alvo_q = col_grid_jogos[idx_j % 5]
                    
                    p1_vis = jogo["p1"] if jogo["encerrado"] else ""
                    p2_vis = jogo["p2"] if jogo["encerrado"] else ""
                    
                    with col_alvo_q:
                        desenhar_quadra_virtual(
                            jogo['d1'], jogo['d2'], idx_j + 1, 
                            p1_vis, p2_vis, jogo["encerrado"], jogo["grupo"]
                        )
