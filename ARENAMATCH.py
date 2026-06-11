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

# 🎨 DESIGN ESPORTIVO PREMIUM (TOTALMENTE OTIMIZADO PARA TV)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; } 
    section[data-testid="stSidebar"] { background-color: #060911; border-right: 2px solid #1f293d; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #39ff14; }
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { color: #ffffff !important; }
    
    .titulo-secao {
        color: #39ff14 !important; font-size: 1.3rem !important; font-weight: bold !important;
        border-left: 5px solid #39ff14; padding-left: 10px; margin-top: 15px; margin-bottom: 10px; text-transform: uppercase;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: #ffffff !important; background-color: #121824 !important; border: 2px solid #1f293d !important; border-radius: 8px !important;
    }
    
    /* Estilo customizado para tabelas de grupos */
    div[data-testid="stTable"] table { border: 2px solid #1f293d !important; background-color: #121824 !important; width: 100%; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; font-size: 0.85rem; padding: 4px !important; }
    div[data-testid="stTable"] td { color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; font-weight: bold; font-size: 0.85rem; padding: 4px !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if "duplas" not in st.session_state:
    st.session_state.duplas = []
if "categoria_selecionada" not in st.session_state:
    st.session_state.categoria_selecionada = "4ª Categoria"
if "torneio_fase" not in st.session_state:
    st.session_state.torneio_fase = "Inscrição"  
if "grupos" not in st.session_state:
    st.session_state.grupos = {}      
if "jogos_grupos" not in st.session_state:
    st.session_state.jogos_grupos = [] 
if "tabelas_grupos" not in st.session_state:
    st.session_state.tabelas_grupos = {} 

# --- RECALCULADOR DA MATRIZ DOS GRUPOS ---
def atualizar_classificacao_grupos():
    tabelas_novas = {}
    
    for nome_g, lista_duplas in st.session_state.grupos.items():
        tabelas_novas[nome_g] = pd.DataFrame({
            'Dupla': lista_duplas,
            'Pts': 0, 'Vit': 0, 'GP': 0, 'GC': 0, 'Saldo': 0
        }).set_index('Dupla')
    
    for jogo in st.session_state.jogos_grupos:
        if jogo["encerrado"]:
            g = jogo["grupo"]
            d1, d2 = jogo["d1"], jogo["d2"]
            p1, p2 = int(jogo["p1"]), int(jogo["p2"])
            
            tabelas_novas[g].loc[d1, 'GP'] += p1
            tabelas_novas[g].loc[d1, 'GC'] += p2
            tabelas_novas[g].loc[d2, 'GP'] += p2
            tabelas_novas[g].loc[d2, 'GC'] += p1
            
            if p1 > p2:
                tabelas_novas[g].loc[d1, 'Pts'] += 1
                tabelas_novas[g].loc[d1, 'Vit'] += 1
            else:
                tabelas_novas[g].loc[d2, 'Pts'] += 1
                tabelas_novas[g].loc[d2, 'Vit'] += 1

    for g in tabelas_novas:
        df = tabelas_novas[g]
        df['Saldo'] = df['GP'] - df['GC']
        tabelas_novas[g] = df.sort_values(by=['Pts', 'Saldo', 'GP'], ascending=False)
        
    st.session_state.tabelas_grupos = tabelas_novas

# --- VISUAL COMPACTO DA QUADRA VIRTUAL (FEITO PARA GRIDES) ---
def desenhar_quadra_virtual(dupla1, dupla2, num_jogo, p1, p2, encerrado, nome_grupo):
    bg_cor = "#112415" if encerrado else "#121824"
    borda_cor = "#39ff14" if encerrado else "#1f293d"
    status_texto = "FIM" if encerrado else "JOGANDO"
    status_cor = "#39ff14" if encerrado else "#ffb703"
    
    html_quadra = f"""
    <div style="background-color: {bg_cor}; border: 2px solid {borda_cor}; border-radius: 8px; padding: 8px; font-family: sans-serif; color: #ffffff; margin-bottom: 8px; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 0.7rem; font-weight: bold;">
            <span style="color: #8fa0bc;">JOGO {num_jogo} ({nome_grupo.upper()})</span>
            <span style="color: {status_cor}; letter-spacing: 0.5px;">● {status_texto}</span>
        </div>
        <div style="background-color: rgba(0,0,0,0.2); border-radius: 4px; padding: 6px; display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.85rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%; color: #ffffff;">{dupla1}</span>
                <span style="font-size: 1.1rem; font-weight: 900; color: #39ff14;">{p1 if p1 != "" else "-"}</span>
            </div>
            <div style="border-top: 1px dashed rgba(255,255,255,0.1); margin: 1px 0;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.85rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%; color: #ffffff;">{dupla2}</span>
                <span style="font-size: 1.1rem; font-weight: 900; color: #ffffff;">{p2 if p2 != "" else "-"}</span>
            </div>
        </div>
    </div>
    """
    components.html(html_quadra, height=95, scrolling=False)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.markdown("## ⚙️ Gestão de Arbitragem")
    senha = st.text_input("Senha Master Arena:", type="password")
    is_admin = (senha == CHAVE_ADMIN)
    st.markdown("---")
    if is_admin and st.button("🚨 RESETAR TODO O TORNEIO"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h2 style='text-align:center; color:#39ff14; margin-bottom: 0; padding-top:0;'>⚡ {NOME_SISTEMA}</h2>", unsafe_allow_html=True)

aba_controle, aba_painel_visual = st.tabs(["... Controles de Arbitragem", "📺 Telão da Lanchonete (Público)"])

with aba_controle:
    # FASE 1: INSCRIÇÕES
    if st.session_state.torneio_fase == "Inscrição":
        st.markdown("<div class='titulo-secao'>Painel de Inscrições</div>", unsafe_allow_html=True)
        st.session_state.categoria_selecionada = st.selectbox(
            "Selecione a Categoria do Torneio:",
            ["Masculino 4ª Classe", "Masculino 5ª Classe", "Feminino Iniciante", "Misto B"]
        )
        
        if is_admin:
            with st.form("cad_dupla", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1: j1 = st.text_input("Atleta 1:")
                with c2: j2 = st.text_input("Atleta 2:")
                if st.form_submit_button("➕ Registrar Dupla"):
                    if j1 and j2:
                        st.session_state.duplas.append(f"{j1.strip()} / {j2.strip()}")
                        st.rerun()
        else:
            st.warning("🔒 Digite a Senha Master na barra lateral para liberar as inscrições.")

        st.write(f"**Duplas Confirmadas ({len(st.session_state.duplas)}):**")
        for idx, dp in enumerate(st.session_state.duplas):
            st.write(f"🔹 {idx+1}. {dp}")
            
        if is_admin and len(st.session_state.duplas) >= 3:
            st.markdown("---")
            if st.button("🎲 GERAR CHAVES E JOGOS AUTOMATICAMENTE"):
                lista_sorteio = list(st.session_state.duplas)
                random.shuffle(lista_sorteio)
                
                tam = 3 if len(lista_sorteio) <= 7 else 4
                letra = 'A'
                st.session_state.grupos = {}
                st.session_state.jogos_grupos = []
                
                for i in range(0, len(lista_sorteio), tam):
                    fatia = lista_sorteio[i:i+tam]
                    nome_g = f"Grupo {letra}"
                    st.session_state.grupos[nome_g] = fatia
                    
                    for g_i in range(len(fatia)):
                        for g_j in range(g_i + 1, len(fatia)):
                            st.session_state.jogos_grupos.append({
                                "grupo": nome_g, "d1": fatia[g_i], "d2": fatia[g_j],
                                "p1": 0, "p2": 0, "encerrado": False
                            })
                    letra = chr(ord(letra) + 1)
                
                atualizar_classificacao_grupos()
                st.session_state.torneio_fase = "Grupos"
                st.rerun()

    # FASE 2: ENTRADA DE RESULTADOS
    elif st.session_state.torneio_fase == "Grupos":
        st.markdown(f"<div class='titulo-secao'>Lançamento de Resultados - {st.session_state.categoria_selecionada}</div>", unsafe_allow_html=True)
        
        if not is_admin:
            st.info("🔒 Use a senha de Administrador na barra lateral para computar os resultados.")
            
        for idx, jogo in enumerate(st.session_state.jogos_grupos):
            status_txt = "🟢 CONCLUÍDO" if jogo["encerrado"] else "⏳ EM ABERTO"
            
            with st.expander(f"➔ [{jogo['grupo']}] {jogo['d1']} VS {jogo['d2']} | {status_txt}"):
                if is_admin:
                    with st.form(key=f"form_jogo_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1:
                            g1 = st.number_input(f"Games {jogo['d1'][:12]}", 0, 7, value=int(jogo["p1"]), key=f"p1_val_{idx}")
                        with col_g2:
                            g2 = st.number_input(f"Games {jogo['d2'][:12]}", 0, 7, value=int(jogo["p2"]), key=f"p2_val_{idx}")
                        
                        if st.form_submit_button("💾 Salvar Placar"):
                            if g1 != g2:
                                st.session_state.jogos_grupos[idx]["p1"] = g1
                                st.session_state.jogos_grupos[idx]["p2"] = g2
                                st.session_state.jogos_grupos[idx]["encerrado"] = True
                                atualizar_classificacao_grupos()
                                st.rerun()
                            else:
                                st.error("Erro: Um jogo de padel não termina empatado em games.")
                else:
                    st.write(f"Placar oficial: **{jogo['p1']} x {jogo['p2']}**")

# --- 📺 TELÃO DA ARENA TOTALMENTE OTIMIZADO EM SUPORTE HORIZONTAL ---
with aba_painel_visual:
    st.markdown(f"<h3 style='text-align:center; color:#39ff14; font-weight:900; margin-top:0; margin-bottom:5px;'>📺 CIRCUITO ARENA - {st.session_state.categoria_selecionada.upper()}</h3>", unsafe_allow_html=True)
    
    if st.session_state.torneio_fase == "Inscrição":
        st.info("Aguardando definição e chaveamento das chaves pelo administrador.")
    else:
        # PARTE SUPERIOR: TABELAS DE CLASSIFICAÇÃO LADO A LADO
        st.markdown("<div class='titulo-secao'>📊 Classificação dos Grupos</div>", unsafe_allow_html=True)
        lista_grupos = list(st.session_state.tabelas_grupos.items())
        num_grupos = len(lista_grupos)
        
        if num_grupos > 0:
            col_g_tv = st.columns(min(num_grupos, 4)) # Até 4 grupos na horizontal perfeitamente
            for i, (nome_g, df_classif) in enumerate(lista_grupos):
                col_alvo = col_g_tv[i % 4]
                with col_alvo:
                    st.markdown(f"<span style='color:#39ff14; font-weight:bold; font-size:0.95rem;'>⚔️ {nome_g}</span>", unsafe_allow_html=True)
                    st.table(df_classif)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # PARTE INFERIOR: QUADRO GERAL DE CONFRONTOS (TODOS APARECEM EM GRADE COMPACTA)
        st.markdown("<div class='titulo-secao'>🎾 Painel Geral de Confrontos (Rodada Completa)</div>", unsafe_allow_html=True)
        
        todos_jogos = st.session_state.jogos_grupos
        
        if todos_jogos:
            # Organiza os blocos em uma grade limpa de 4 colunas horizontais
            col_q_tv = st.columns(4)
            for idx_j, jogo in enumerate(todos_jogos):
                col_alvo_q = col_q_tv[idx_j % 4]
                
                p1_vis = jogo["p1"] if jogo["encerrado"] else ""
                p2_vis = jogo["p2"] if jogo["encerrado"] else ""
                
                with col_alvo_q:
                    desenhar_quadra_virtual(
                        jogo['d1'], jogo['d2'], idx_j + 1, 
                        p1_vis, p2_vis, jogo["encerrado"], jogo["grupo"]
                    )
