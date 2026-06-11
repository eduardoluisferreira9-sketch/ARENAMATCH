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

# 🎨 DESIGN ESPORTIVO PREMIUM (DARK MODE + VERDE NEON)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; } 
    section[data-testid="stSidebar"] { background-color: #060911; border-right: 2px solid #1f293d; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #39ff14; }
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { color: #ffffff !important; }
    
    .titulo-secao {
        color: #39ff14 !important; font-size: 1.5rem !important; font-weight: bold !important;
        border-left: 5px solid #39ff14; padding-left: 10px; margin-top: 25px; margin-bottom: 15px; text-transform: uppercase;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: #ffffff !important; background-color: #121824 !important; border: 2px solid #1f293d !important; border-radius: 8px !important;
    }
    
    /* Estilo customizado para tabelas de grupos */
    div[data-testid="stTable"] table { border: 2px solid #1f293d !important; background-color: #121824 !important; width: 100%; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; font-size: 1rem; }
    div[data-testid="stTable"] td { color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; font-weight: bold; }
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

# --- RECALCULADOR DA MATRIZ DOS GRUPOS (CORRIGIDO) ---
def atualizar_classificacao_grupos():
    tabelas_novas = {}
    # Criar estrutura limpa para cada grupo baseado nas duplas sorteadas
    for nome_g, lista_duplas in st.session_state.grupos.items():
        tabelas_novas[nome_g] = pd.DataFrame({
            'Dupla Atleta': lista_duplas,
            'Pontos': 0, 'Vitórias': 0, 'Games Pró': 0, 'Games Contra': 0, 'Saldo Games': 0
        }).set_index('Dupla Atleta')
    
    # Computar os dados dos jogos salvos
    for jogo in st.session_state.jogos_grupos:
        if jogo["encerrado"]:
            g = jogo["grupo"]
            d1, d2 = jogo["d1"], job["d2"]
            p1, p2 = int(jogo["p1"]), int(jogo["p2"])
            
            # Acumular saldo de games
            tabelas_novas[g].loc[d1, 'Games Pró'] += p1
            tabelas_novas[g].loc[d1, 'Games Contra'] += p2
            tabelas_novas[g].loc[d2, 'Games Pró'] += p2
            tabelas_novas[g].loc[d2, 'Games Contra'] += p1
            
            # Computar pontos e vitórias
            if p1 > p2:
                tabelas_novas[g].loc[d1, 'Pontos'] += 1
                tabelas_novas[g].loc[d1, 'Vitórias'] += 1
            elif p2 > p1:
                tabelas_novas[g].loc[d2, 'Pontos'] += 1
                tabelas_novas[g].loc[d2, 'Vitórias'] += 1

    # Recalcular saldos de ordenação final
    for g in tabelas_novas:
        df = tabelas_novas[g]
        df['Saldo Games'] = df['Games Pró'] - df['Games Contra']
        tabelas_novas[g] = df.sort_values(by=['Pontos', 'Saldo Games', 'Games Pró'], ascending=False)
        
    st.session_state.tabelas_grupos = tabelas_novas

# --- VISUAL DA QUADRA REESTRUTURADO PARA TV ---
def desenhar_quadra_virtual(dupla1, dupla2, num_quadra, p1, p2, encerrado):
    status_cor = "#39ff14" if encerrado else "#ffb703"
    status_texto = "PLACAR FINAL" if encerrado else "EM ANDAMENTO"
    
    html_quadra = f"""
    <div style="background-color: #121824; border: 3px solid #1f293d; border-radius: 12px; padding: 15px; box-shadow: 0px 8px 16px rgba(0,0,0,0.4); font-family: sans-serif; color: #ffffff; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="background-color: #1f293d; color: #39ff14; padding: 4px 10px; font-weight: bold; border-radius: 6px; font-size: 0.8rem;">🎾 QUADRA {num_quadra}</span>
            <span style="color: {status_cor}; font-size: 0.75rem; font-weight: bold; letter-spacing: 1px;">● {status_texto}</span>
        </div>
        <div style="background-color: #1a2333; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.05rem; font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%;">{dupla1}</span>
                <span style="font-size: 1.6rem; font-weight: 900; color: #39ff14;">{p1 if p1 != "" else "-"}</span>
            </div>
            <div style="border-top: 1px dashed #2c3a54; margin: 2px 0;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.05rem; font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%;">{dupla2}</span>
                <span style="font-size: 1.6rem; font-weight: 900; color: #ffffff;">{p2 if p2 != "" else "-"}</span>
            </div>
        </div>
    </div>
    """
    components.html(html_quadra, height=165, scrolling=False)

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
st.markdown(f"<h1 style='text-align:center; color:#39ff14;'>⚡ {NOME_SISTEMA}</h1>", unsafe_allow_html=True)

aba_controle, aba_painel_visual = st.tabs(["🎮 Painel de Arbitragem (Admin)", "📺 Telão da Lanchonete (Público)"])

with aba_controle:
    # FASE 1: INSCRIÇÕES
    if st.session_state.torneio_fase == "Inscrição":
        st.markdown("<div class='titulo-secao'>Painel de Inscrições</div>", unsafe_allow_html=True)
        st.session_state.categoria_selecionada = st.selectbox(
            "Selecione a Categoria do Torneio:",
            ["Masculino Open", "Masculino 4ª Classe", "Masculino 5ª Classe", "Feminino Iniciante"]
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

    # FASE 2: ENTRADA DE RESULTADOS (BLINDADA CONTRA TRAVAMENTOS)
    elif st.session_state.torneio_fase == "Grupos":
        st.markdown(f"<div class='titulo-secao'>Lançamento de Resultados - {st.session_state.categoria_selecionada}</div>", unsafe_allow_html=True)
        
        if not is_admin:
            st.info("🔒 Use a senha de Administrador na barra lateral para computar os resultados.")
            
        for idx, jogo in enumerate(st.session_state.jogos_grupos):
            status_txt = "🟢 CONCLUÍDO" if jogo["encerrado"] else "⏳ EM ABERTO"
            
            # Usando uma chave totalmente única por expander e formulário
            with st.expander(f"➔ [{jogo['grupo']}] {jogo['d1']} VS {jogo['d2']} | {status_txt}"):
                if is_admin:
                    # Cada jogo agora ganha um formulário próprio isolado
                    with st.form(key=f"form_jogo_{idx}"):
                        col_g1, col_g2 = st.columns(2)
                        with col_g1:
                            g1 = st.number_input(f"Games {jogo['d1'][:12]}", 0, 7, value=int(jogo["p1"]), key=f"p1_val_{idx}")
                        with col_g2:
                            g2 = st.number_input(f"Games {jogo['d2'][:12]}", 0, 7, value=int(jogo["p2"]), key=f"p2_val_{idx}")
                        
                        if st.form_submit_button("💾 Salvar Placar"):
                            if g1 != g2: # Validação simples: não aceita empate em set de tênis/padel
                                st.session_state.jogos_grupos[idx]["p1"] = g1
                                st.session_state.jogos_grupos[idx]["p2"] = g2
                                st.session_state.jogos_grupos[idx]["encerrado"] = True
                                atualizar_classificacao_grupos()
                                st.rerun()
                            else:
                                st.error("Erro: Um set de padel/beach não pode terminar empatado em games.")
                else:
                    st.write(f"Placar atualizado pelos árbitros: **{jogo['p1']} x {jogo['p2']}**")

# --- 📺 TELÃO AUTOMÁTICO DA ARENA (PARA MOSTRAR NA TV) ---
with aba_painel_visual:
    st.markdown(f"<h2 style='text-align:center; color:#39ff14; font-weight:900;'>📺 COPA ARENA - {st.session_state.categoria_selecionada.upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.torneio_fase == "Inscrição":
        st.info("Visualização das Chaves será liberada assim que o sorteio for realizado.")
    else:
        col_telas_1, col_telas_2 = st.columns([5, 4])
        
        with col_telas_1:
            st.markdown("<div class='titulo-secao'>📊 Classificação de Grupos ao Vivo</div>", unsafe_allow_html=True)
            for nome_g, df_classif in st.session_state.tabelas_grupos.items():
                st.write(f"### ⚔️ {nome_g}")
                st.table(df_classif)
                
        with col_telas_2:
            st.markdown("<div class='titulo-secao'>🎾 Status das Quadras</div>", unsafe_allow_html=True)
            for idx, jogo in enumerate(st.session_state.jogos_grupos):
                p1_vis = jogo["p1"] if jogo["encerrado"] else ""
                p2_vis = jogo["p2"] if jogo["encerrado"] else ""
                desenhar_quadra_virtual(jogo['d1'], jogo['d2'], idx+1, p1_vis, p2_vis, jogo["encerrado"])
