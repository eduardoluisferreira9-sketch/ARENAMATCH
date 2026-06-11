import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import json
import os
from datetime import datetime

# 🎾 CONFIGURAÇÃO DA PÁGINA COM ESTILO PREMIUM/ARENA
st.set_page_config(
    page_title="ArenaMatch - Gestão de Padel & Beach Tennis",
    page_icon="🎾",
    layout="wide"
)

NOME_SISTEMA = "ArenaMatch Pro"
ARQUIVO_ARENA = "torneio_arena_padel.json"

# 🎨 CSS CUSTOMIZADO: Identidade Visual Esportiva Moderna (Cinza Escuro + Verde Neon)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; } 
    
    section[data-testid="stSidebar"] {
        background-color: #060911;
        border-right: 2px solid #1f293d;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #39ff14; }
    
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { 
        color: #ffffff !important; 
    }
    
    .titulo-secao {
        color: #39ff14 !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
        border-left: 5px solid #39ff14;
        padding-left: 10px;
        margin-top: 25px;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: #ffffff !important;
        background-color: #121824 !important;
        border: 2px solid #1f293d !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #39ff14 !important;
    }
    
    button[data-baseweb="tab"] { color: #8fa0bc !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #39ff14 !important; font-weight: bold; }
    
    .stButton>button {
        background-color: #39ff14 !important; color: #0b0f19 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
        border: none !important; font-size: 1.1rem !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2ecc11 !important;
        box-shadow: 0px 0px 15px rgba(57, 255, 20, 0.4);
    }
    
    /* Tabela Estilo Arena */
    div[data-testid="stTable"] table { border: 2px solid #1f293d !important; background-color: #121824 !important; }
    div[data-testid="stTable"] th { background-color: #060911 !important; color: #39ff14 !important; border: 1px solid #1f293d !important; text-align: center !important; }
    div[data-testid="stTable"] td { color: #ffffff !important; border: 1px solid #1f293d !important; text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE VARIÁVEIS ---
if "duplas" not in st.session_state:
    st.session_state.duplas = []
    st.session_state.categoria_selecionada = "4ª Categoria (Masculina)"
    st.session_state.torneio_fase = "Inscrição" # Inscrição, Grupos, MataMata, Fim
    st.session_state.grupos = {}
    st.session_state.jogos_grupos = []
    st.session_state.resultados_jogos = {}

# --- QUADRA HTML VISUAL (O SEU PRODUTO DE TELA/PROJETOR) ---
def desenhar_quadra_virtual(dupla1, dupla2, num_quadra, placar_d1="", placar_d2=""):
    html_quadra = f"""
    <div style="background-color: #1e4620; border: 4px solid #ffffff; border-radius: 8px; padding: 15px; position: relative; box-shadow: 0px 10px 20px rgba(0,0,0,0.5); height: 260px; box-sizing: border-box; color: #ffffff; font-family: sans-serif; margin-bottom: 15px;">
        <div style="position: absolute; top: 0; bottom: 0; left: 50%; border-left: 2px dashed rgba(255,255,255,0.6); margin-left: -1px;"></div>
        <div style="position: absolute; left: 0; right: 0; top: 50%; border-top: 4px solid #ffffff; margin-top: -2px;"></div>
        
        <div style="position: absolute; top: 8px; left: 12px; background-color: #39ff14; color: #0b0f19; padding: 3px 10px; font-weight: bold; border-radius: 4px; font-size: 0.8rem;">
            🎾 QUADRA {num_quadra}
        </div>
        
        <div style="position: absolute; top: 40px; left: 0; right: 0; text-align: center; padding: 0 10px;">
            <div style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{dupla1}</div>
            <div style="font-size: 1.8rem; font-weight: 900; color: #39ff14; margin-top: 5px;">{placar_d1 if placar_d1 != "" else "-"}</div>
        </div>
        
        <div style="position: absolute; top: 50%; left: 0; right: 0; text-align: center; transform: translateY(-50%);">
            <span style="background-color: #ffffff; color: #1e4620; font-size: 0.75rem; font-weight: bold; padding: 1px 8px; border-radius: 10px; letter-spacing: 1px;">REDE</span>
        </div>
        
        <div style="position: absolute; bottom: 25px; left: 0; right: 0; text-align: center; padding: 0 10px;">
            <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff; margin-bottom: 5px;">{placar_d2 if placar_d2 != "" else "-"}</div>
            <div style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{dupla2}</div>
        </div>
    </div>
    """
    components.html(html_quadra, height=275, scrolling=False)

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; color:#39ff14;'>⚡ {NOME_SISTEMA}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8fa0bc !important;'>Gestão Inteligente de Torneios de Padel & Beach Tennis</p>", unsafe_allow_html=True)

aba_controle, aba_painel_visual = st.tabs(["🎮 Painel de Controle (Admin)", "📺 Telão da Arena (Público)"])

with aba_controle:
    # ----------------------------------------------------
    # FASE 1: INSCRIÇÕES E SELEÇÃO DE CATEGORIAS
    # ----------------------------------------------------
    if st.session_state.torneio_fase == "Inscrição":
        st.markdown("<div class='titulo-secao'>Abertura do Torneio & Categorias</div>", unsafe_allow_html=True)
        col_cat, col_vazia = st.columns([2, 2])
        with col_cat:
            st.session_state.categoria_selecionada = st.selectbox(
                "Selecione a Categoria Atual para Gerenciamento:",
                ["Iniciante (Masculino)", "5ª Categoria (Masculino)", "4ª Categoria (Masculino)", "Open (Livre)", "Feminino B", "Misto C"]
            )
            
        st.markdown("<div class='titulo-secao'>Inscrição de Duplas Atletas</div>", unsafe_allow_html=True)
        with st.form("cad_dupla", clear_on_submit=True):
            c_j1, c_j2 = st.columns(2)
            with c_j1: nome_j1 = st.text_input("Nome do Atleta 1:")
            with c_j2: nome_j2 = st.text_input("Nome do Atleta 2 (Parceiro):")
            
            if st.form_submit_button("🔒 Confirmar Inscrição da Dupla"):
                if nome_j1 and nome_j2:
                    nome_dupla = f"{nome_j1.strip()} / {nome_j2.strip()}"
                    st.session_state.duplas.append(nome_dupla)
                    st.rerun()
                    
        st.write(f"**Duplas Confirmadas na {st.session_state.categoria_selecionada} ({len(st.session_state.duplas)}):**")
        if st.session_state.duplas:
            for idx, dp in enumerate(st.session_state.duplas):
                st.markdown(f"🎾 {idx+1}. **{dp}**")
        else:
            st.info("Aguardando inscrições de atletas para esta categoria.")
            
        if len(st.session_state.duplas) >= 3:
            st.markdown("---")
            if st.button("🚀 SORTEAR GRUPOS E GERAR JOGOS (Fase de Grupos)"):
                # Lógica de divisão automática (Ex: grupos de 3 ou 4 duplas)
                lista_sorteio = list(st.session_state.duplas)
                random.shuffle(lista_sorteio)
                
                # Divisão simples em Grupo A, Grupo B...
                tamanho_grupo = 3 if len(lista_sorteio) <= 7 else 4
                st.session_state.grupos = {}
                st.session_state.jogos_grupos = []
                
                letra_grupo = 'A'
                for i in range(0, len(lista_sorteio), tamanho_grupo):
                    fatia = lista_sorteio[i:i+tamanho_grupo]
                    nome_g = f"Grupo {letra_grupo}"
                    st.session_state.grupos[nome_g] = fatia
                    
                    # Gerar jogos do tipo "Todos contra todos" dentro do grupo
                    for g_i in range(len(fatia)):
                        for g_j in range(g_i + 1, len(fatia)):
                            st.session_state.jogos_grupos.append({
                                "grupo": nome_g,
                                "d1": fatia[g_i],
                                "d2": fatia[g_j],
                                "status": "A jogar"
                            })
                    letra_grupo = chr(ord(letra_grupo) + 1)
                
                st.session_state.torneio_fase = "Grupos"
                st.rerun()

    # ----------------------------------------------------
    # FASE 2: GESTÃO DA FASE DE GRUPOS (LANÇAMENTO DE PLACARES)
    # ----------------------------------------------------
    elif st.session_state.torneio_fase == "Grupos":
        st.markdown(f"<div class='titulo-secao'>Fase de Grupos: {st.session_state.categoria_selecionada}</div>", unsafe_allow_html=True)
        
        # Exibir os jogos para o Admin lançar o resultado
        st.write("### 📝 Lançamento de Resultados (Súmulas)")
        for idx, jogo in enumerate(st.session_state.jogos_grupos):
            id_jogo_str = f"j_g_{idx}"
            st.markdown(f"**[{jogo['grupo']}]** {jogo['d1']} **VS** {jogo['d2']}")
            
            c_p1, c_p2, c_btn = st.columns([1, 1, 2])
            with c_p1: 
                p1 = st.number_input(f"Games {jogo['d1'][:15]}", 0, 9, key=f"p1_{id_jogo_str}")
            with c_p2: 
                p2 = st.number_input(f"Games {jogo['d2'][:15]}", 0, 9, key=f"p2_{id_jogo_str}")
            with c_btn:
                st.write("") # Espaçador alinhamento
                st.write("") 
                if st.button(f"💾 Confirmar Jogo {idx+1}", key=f"btn_{id_jogo_str}"):
                    st.session_state.resultados_jogos[id_jogo_str] = {"p1": p1, "p2": p2}
                    jogo["status"] = "Encerrado"
                    st.success("Resultado computado com sucesso!")
            st.markdown("---")
            
        if st.button("🏆 Finalizar Fase de Grupos e Ir para o Mata-Mata"):
            # Aqui no futuro você adiciona a tabela matemática de classificação
            st.session_state.torneio_fase = "MataMata"
            st.rerun()

    # ----------------------------------------------------
    # FASE 3: MATA-MATAS ELIMINATÓRIOS
    # ----------------------------------------------------
    elif st.session_state.torneio_fase == "MataMata":
        st.markdown("<div class='titulo-secao'>Chaves Eliminatórias (Mata-Mata)</div>", unsafe_allow_html=True)
        st.info("Aqui entram as semifinais e finais geradas automaticamente com os melhores de cada grupo.")
        if st.button("🔄 Resetar e Voltar para Inscrições"):
            st.session_state.clear()
            st.rerun()

# ----------------------------------------------------
# 📺 TAB 2: O TELÃO VISUAL DA ARENA (PROJETAR NA TV DA LANCHONETE)
# ----------------------------------------------------
with aba_painel_visual:
    st.markdown(f"<h2 style='text-align:center; color:#39ff14;'>📺 PAINEL DE CONFRONTOS - {st.session_state.categoria_selecionada}</h2>", unsafe_allow_html=True)
    
    if st.session_state.torneio_fase == "Inscrição":
        st.warning("Aguardando o sorteio das chaves pelo organizador da Arena.")
    
    elif st.session_state.torneio_fase == "Grupos":
        # Renderiza as quadras virtuais baseadas nos jogos ativos
        st.markdown("<div class='titulo-secao'>Jogos em Andamento / Próximas Chamadas</div>", unsafe_allow_html=True)
        
        col_q1, col_q2 = st.columns(2)
        
        contador_quadra = 1
        for idx, jogo in enumerate(st.session_state.jogos_grupos):
            id_jogo_str = f"j_g_{idx}"
            res = st.session_state.resultados_jogos.get(id_jogo_str, {"p1": "", "p2": ""})
            
            # Divide a exibição visual entre as duas colunas
            if contador_quadra % 2 != 0:
                with col_q1:
                    desenhar_quadra_virtual(jogo['d1'], jogo['d2'], contador_quadra, res['p1'], res['p2'])
            else:
                with col_q2:
                    desenhar_quadra_virtual(jogo['d1'], jogo['d2'], contador_quadra, res['p1'], res['p2'])
            
            contador_quadra += 1