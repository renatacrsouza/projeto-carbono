#!/usr/bin/env python3
"""Interface web premium do diagnóstico de carbono - Estilo Minimalista Apple."""

import time
from datetime import datetime
from typing import Optional
import streamlit as st
from fpdf import FPDF
from google import genai
from google.genai import types

from diagnostico import (
    avaliar_maturidade,
    gerar_proximos_passos,
    gerar_relatorio_pdf,
    gerar_resumo_executivo,
    obter,
)


def gerar_template_pdf() -> bytes:
    """Gera o modelo de relatório completo em branco com 2 linhas simétricas por item."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    # Cabeçalho Slim Corporativo
    pdf.set_fill_color(27, 67, 50)
    pdf.rect(0, 0, 210, 28, "F")
    
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(6)
    pdf.cell(0, 8, "TEMPLATE OFICIAL DE SUPORTE - MERCADO DE CARBONO", ln=True, align="C")
    pdf.set_font("Arial", "I", 8.5)
    pdf.cell(0, 4, "Formulario de Due Diligence e Coleta de Dados Primarios", ln=True, align="C")
    
    pdf.set_y(34)
    
    # Dados Gerais do Cliente/Propriedade
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(190, 5, "DADOS GERAIS DA PROPRIEDADE", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("Arial", "", 9.5)
    pdf.set_text_color(60, 60, 60)
    
    # Bloco de dados iniciais com alinhamento padronizado
    linhas_topo = [
        "Nome da Propriedade / Empresa",
        "Proprietario / Responsavel Tecnico",
        "Localizacao / Coordenadas / Bioma",
        "Contato (E-mail / Telefone)"
    ]
    for campo in linhas_topo:
        pdf.cell(60, 6, f"{campo}:")
        pdf.cell(130, 6, "_____________________________________________________________", ln=True)
    
    conteudo_template = [
        ("FRENTE 1: ESTRUTURACAO TECNICA BASE", [
            "Item 1. Tipo principal do projeto",
            "Item 2. Bioma / regiao de localizacao",
            "Item 3. Area total envolvida (ha)",
            "Item 4. Estagio atual do projeto",
            "Item 5. Documentacao fundiaria regularizada",
            "Item 6. Dados historicos de uso do solo (anos)",
            "Item 7. Certificacao ambiental ou social existente",
            "Item 8. Atividade principal geradora de creditos",
            "Item 9. Estimativa de toneladas de CO2e/ano",
            "Item 10. Beneficios socioambientais mapeados (ODS)",
            "Item 11. Contato ou alinhamento com certificadora",
            "Item 12. Objetivo principal com as transacoes",
            "Item 13. Acesso a capital para custeio inicial",
            "Item 14. Equipe tecnica ou consultoria dedicada",
            "Item 15. Prazo estimado para submissao oficial",
            "Item 16. Existencia de conflitos fundiarios ou disputas",
            "Item 17. Passivos ambientais criticos identificados",
            "Item 18. Garantia de permanencia florestal (20-30 anos)",
        ]),
        ("FRENTE 2: DUE DILIGENCE, CAR E COMPLIANCE (LEI 15.042/24)", [
            "Item 19. Documentacao Territorial Regular (Matricula/CCIR/ITR/SIGEF)",
            "Item 20. Estudos Tecnicos Concluidos (Inventario/Adicionalidade/Baseline)",
            "Item 21. Faixa de Emissoes Anuais perante o corte do SBCE",
            "Item 22. Enquadramento de Ativos Financeiros de Carbono (CRVE/CBE)",
            "Item 23. Analise de Restricoes e Sobreposicoes Territoriais no CAR",
            "Item 24. Deficit ou Passivo Florestal de Reserva Legal / APP"
        ])
    ]
    
    # Construção das duas linhas simétricas perfeitas por item
    for secao, itens in conteudo_template:
        pdf.ln(4)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(27, 67, 50)
        pdf.cell(190, 6, secao, ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        
        for item in itens:
            pdf.ln(1)
            pdf.set_font("Arial", "B", 9)
            pdf.set_text_color(27, 67, 50)
            pdf.cell(190, 5, item, ln=True)
            
            pdf.set_font("Arial", "", 9.5)
            pdf.set_text_color(180, 180, 180)
            pdf.cell(190, 5.5, "__________________________________________________________________________________________", ln=True)
            pdf.cell(190, 5.5, "__________________________________________________________________________________________", ln=True)
            pdf.ln(1)
            
    return pdf.output(dest='S').encode('latin-1')


# ── Estrutura do questionário ────────────────────────────────────────────────
BLOCOS = [
    {
        "titulo": "Identificação",
        "subtitulo": "01 · IDENTIFICAÇÃO DO PROJETO",
        "icone": "🌿",
        "perguntas": [
            {"chave": "1. Tipo principal do projeto", "texto": "Qual é o tipo principal do projeto?", "opcoes": ["Florestal", "Agropecuário", "Energia", "Indústria", "Resíduos", "Outro"]},
            {"chave": "2. Bioma / região", "texto": "Em qual bioma / região está localizado?", "opcoes": ["Amazônia", "Cerrado", "Mata Atlântica", "Pantanal", "Caatinga", "Pampa / Sul", "Outro"]},
            {"chave": "3. Área total envolvida", "texto": "Qual é a área total envolvida?", "opcoes": ["Menos de 50 ha", "50 a 500 ha", "500 a 5.000 ha", "Mais de 5.000 ha"]},
        ],
    },
    {
        "titulo": "Situação Atual",
        "subtitulo": "02 · SITUAÇÃO ATUAL E HISTÓRICO",
        "icone": "📋",
        "perguntas": [
            {"chave": "4. Estágio atual", "texto": "Qual é o estágio atual?", "opcoes": ["Só tenho a ideia", "Estou estruturando", "Projeto já implementado", "Em monitoramento", "Já passou por auditoria"]},
            {"chave": "5. Documentação fundiária", "texto": "Existe documentação fundiária regularizada?", "opcoes": ["Sim, escritura e CAR", "Parcialmente", "Não", "Não sei"]},
            {"chave": "6. Dados históricos", "texto": "Há dados históricos de uso do solo?", "opcoes": ["Sim, mais de 10 anos", "Sim, 5 a 10 anos", "Sim, menos de 5 anos", "Não"]},
            {"chave": "7. Certificação ambiental ou social", "texto": "Já existe alguma certificação prévia?", "opcoes": ["ISO 14001", "FSC", "Rainforest Alliance", "Nenhuma", "Outra"]},
        ],
    },
    {
        "titulo": "Potencial",
        "subtitulo": "03 · POTENCIAL DE GERAÇÃO",
        "icone": "⚡",
        "perguntas": [
            {"chave": "8. Atividade principal", "texto": "Qual é a atividade geradora de créditos?", "opcoes": ["Evitar desmatamento (REDD+)", "Reflorestamento / restauração", "Plantio direto / recuperação solo", "Biodigestor / biogás", "Energia solar / eólica", "Eficiência energética", "Outro"]},
            {"chave": "9. Estimativa de tCO2e/ano", "texto": "Qual a estimativa de volume anual?", "opcoes": ["Menos de 1.000 tCO2e/ano", "1.000 a 10.000 tCO2e/ano", "10.000 a 100.000 tCO2e/ano", "Mais de 100.000 tCO2e/ano", "Não sei estimar"]},
            {"chave": "10. Benefícios socioambientais", "texto": "Gera benefícios socioambientais extras?", "opcoes": ["Biodiversidade", "Recursos hídricos", "Comunidades locais", "Geração de emprego", "Nenhum mapeado"], "multipla": True},
        ],
    },
    {
        "titulo": "Certificação",
        "subtitulo": "04 · CERTIFICAÇÃO E MERCADO",
        "icone": "🏅",
        "perguntas": [
            {"chave": "11. Contato com certificadora", "texto": "Já teve contato com alguma certificadora?", "opcoes": ["Verra (VCS)", "Gold Standard", "RENOVABIO", "SBCE (brasileiro)", "Nenhuma ainda"]},
            {"chave": "12. Objetivo principal com os créditos", "texto": "Qual é o objetivo comercial principal?", "opcoes": ["Vender no mercado voluntário", "Cumprir obrigação legal (compliance)", "Reporte ESG / neutralização", "Ainda não definido"]},
            {"chave": "13. Acesso a capital para certificação", "texto": "Tem acesso a capital para custear o processo?", "opcoes": ["Sim", "Parcialmente, preciso de financiamento", "Não no momento"], "ajuda": "Estimativa: R$ 50k–300k."},
        ],
    },
    {
        "titulo": "Execução",
        "subtitulo": "05 · CAPACIDADE DE EXECUÇÃO",
        "icone": "🛠️",
        "perguntas": [
            {"chave": "14. Equipe técnica", "texto": "Há equipe técnica para conduzir o projeto?", "opcoes": ["Sim, equipe interna", "Sim, via consultoria", "Não ainda"]},
            {"chave": "15. Prazo para submissão", "texto": "Em quanto tempo espera estar pronto?", "opcoes": ["Menos de 6 meses", "6 a 12 meses", "1 a 2 anos", "Não sei"]},
        ],
    },
    {
        "titulo": "Riscos",
        "subtitulo": "06 · RISCOS E BARREIRAS",
        "icone": "⚠️",
        "perguntas": [
            {"chave": "16. Conflitos fundiários", "texto": "Existem conflitos fundiários na área?", "opcoes": ["Não", "Há pendências em resolução", "Sim"]},
            {"chave": "17. Passivos ambientais", "texto": "Há passivos ambientais conhecidos?", "opcoes": ["Não", "Há área de passivo, mas em recuperação", "Sim, não endereçados"]},
            {"chave": "18. Permanência por 20-30 anos", "texto": "Pode garantir permanência por 20-30 anos?", "opcoes": ["Sim, com segurança", "Provavelmente sim", "Incerto", "Não"], "ajuda": "Requisito mínimo de mercado."},
        ],
    },
    {
        "titulo": "Checklist Docs",
        "subtitulo": "07 · DOCUMENTAÇÃO ESSENCIAL AUDITÁVEL",
        "icone": "📋",
        "perguntas": [
            {"chave": "19. Documentação Territorial Obrigatória", "texto": "Quais documentos territoriais possui regularizados?", "opcoes": ["Matrícula Atualizada", "CCIR Regular", "Declaração do ITR (DITR)", "Georreferenciamento (SIGEF)"], "multipla": True},
            {"chave": "20. Documentação Técnica de Carbono", "texto": "Quais estudos técnicos já foram elaborados?", "opcoes": ["Inventário de Emissões", "Estudo de Adicionalidade", "Linha de Base (Baseline)", "Nenhum técnico ainda"], "multipla": True}
        ]
    },
    {
        "titulo": "Gap Analysis SBCE",
        "subtitulo": "08 · ENQUADRAMENTO REGULATÓRIO (LEI 15.042/24)",
        "icone": "🔍",
        "perguntas": [
            {"chave": "21. Faixa de Emissões Anuais", "texto": "Volume estimado de emissões de GEE da atividade por ano?", "opcoes": ["Abaixo de 10.000 tCO2e (Isento)", "Entre 10.000 e 25.000 tCO2e (Monitorado)", "Acima de 25.000 tCO2e (Metas Rígidas)", "Não sei estimar"]},
            {"chave": "22. Enquadramento de Ativos", "texto": "Qual será o foco principal de transação do projeto?", "opcoes": ["Gerar CRVEs", "Gerenciar CBEs (Cotas do Governo)", "Mercado Voluntário tradicional", "Ainda não definido"]}
        ]
    },
    {
        "titulo": "Análise do CAR",
        "subtitulo": "09 · RESTRIÇÕES AMBIENTAIS E MAPA DE RISCO",
        "icone": "🗺️",
        "perguntas": [
            {"chave": "23. Restrições e Sobreposições Territoriais", "texto": "A análise indicou sobreposição da área?", "opcoes": ["Não, área 100% livre e regular", "Sobreposição parcial com UC", "Sobreposição com TI ou Quilombolas", "Sobreposição com outras propriedades", "Não realizei a análise de Gaps"]},
            {"chave": "24. Passivo de Reserva Legal", "texto": "Existe déficit florestal de Reserva Legal ou APP?", "opcoes": ["Não, déficit zerado", "Sim, com PRA ativo", "Sim, passivo aberto sem plano", "Não aplicável"]}
        ]
    }
]

CORES_MATURIDADE = {"AVANCADO": ("#1E3F20", "#EBF5EE"), "INTERMEDIARIO": ("#D97706", "#FEF3C7"), "INICIAL": ("#DC2626", "#FEE2E2")}


def aplicar_estilo() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
            
            html, body, [class*="css"] { 
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                color: #1D1D1F;
                background-color: #F5F5F7;
            }
            
            /* 🏰 HEADER PRINCIPAL */
            .main-header { 
                background: #FFFFFF; 
                padding: 1.8rem 2.2rem; 
                border-radius: 24px; 
                text-align: left; 
                margin-bottom: 1.5rem; 
                border: 1px solid #E5E5EA;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.01);
            }
            .main-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; color: #1D1D1F !important; }
            .main-header p { font-size: 1.1rem; color: #86868B; margin-top: 0.4rem; }
            
            /* 📦 TRUQUE MÁGICO: Força TODAS as caixas de perguntas (st.container) a virarem cartões Premium */
            .stVerticalBlock[style*="border"] {
                border-radius: 20px !important;
                background-color: #FFFFFF !important;
                border: 1px solid #E5E5EA !important;
                padding: 1.8rem !important;
                margin-bottom: 1.2rem !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
            }
            
            /* 🟢 TAGS DE ITEM EM VERDE BOTÂNICO (Forçado por classe) */
            .pergunta-num { 
                display: inline-block !important; 
                background-color: #EBF5EE !important; 
                color: #1B4332 !important; 
                font-weight: 700 !important; 
                font-size: 0.75rem !important; 
                letter-spacing: 0.06em !important;
                padding: 0.3rem 0.8rem !important; 
                border-radius: 8px !important; 
                margin-bottom: 0.5rem !important;
                border: 1px solid #D2E7D6 !important;
            }
            
            /* ✍️ PERGUNTAS MAIS EM DESTAQUE */
            h5 {
                font-weight: 700 !important;
                color: #1D1D1F !important;
                font-size: 1.1rem !important;
                margin-top: 0.2rem !important;
                margin-bottom: 1rem !important;
            }
            
            /* 🔘 ESPAÇAMENTO DOS BOTÕES DE OPÇÃO */
            div[data-testid="stWidgetLabel"] {
                margin-bottom: 0.5rem !important;
            }
            
            /* 📊 DEMAIS ELEMENTOS */
            .relatorio-header { background: #1B4332; color: white; padding: 2.5rem; border-radius: 24px; text-align: center; margin-top: 3rem; }
            .relatorio-header h2 { color: white !important; margin: 0; font-size: 1.8rem; font-weight: 700; }
            .metric-card { background: #FFFFFF; border: 1px solid #E5E5EA; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.01); }
            .passo-item { background: #F5F5F7; border-left: 5px solid #1B4332; padding: 1rem; border-radius: 0 16px 16px 0; margin: 0.6rem 0; font-size: 1rem; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 6px; }
            .stTabs [data-baseweb="tab"] { background: #FFFFFF; border-radius: 12px; padding: 8px 16px; font-weight: 500; color: #86868B !important; border: 1px solid #E5E5EA; }
            .stTabs [aria-selected="true"] { background: #1D1D1F !important; color: #FFFFFF !important; border-color: #1D1D1F !important; font-weight: 600; }
            
            div.stButton > button[kind="primary"] { 
                background: #0071E3; 
                border: none; 
                font-size: 1.1rem; 
                font-weight: 600; 
                padding: 0.8rem 2.5rem; 
                border-radius: 16px; 
                width: 100%; 
            }

            /* 🪄 BARRA LATERAL FIXA À DIREITA */
            [data-testid="stSidebar"] { left: auto !important; right: 0 !important; transform: translate3d(0px, 0px, 0px) !important; }
            [data-testid="stAppViewContainer"] { flex-direction: row-reverse !important; }
            [data-testid="stSidebarCollapseButton"] { left: auto !important; right: 10px !important; }

            /* 🎯 COMPACTAÇÃO DA IA */
            [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; padding-bottom: 1rem !important; gap: 0.4rem !important; }
            [data-testid="stSidebar"] hr { margin: 0.6rem 0 !important; }
            [data-testid="stSidebar"] [data-testid="stChatMessage"] { padding: 0.6rem 0.8rem !important; margin-bottom: 0.4rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def extrair_numero_pergunta(chave: str) -> str:
    return chave.split(".")[0].strip()


def renderizar_pergunta(pergunta: dict, indice_bloco: int, indice_pergunta: int, numero_sequencial: int) -> Optional[str]:
    key_base = f"b{indice_bloco}_q{indice_pergunta}"

    st.markdown(f'<span class="pergunta-num">ITEM {numero_sequencial}</span>', unsafe_allow_html=True)
    st.markdown(f"##### {pergunta['texto']}")
    if pergunta.get("ajuda"):
        st.caption(pergunta["ajuda"])

    if pergunta.get("multipla"):
        selecionadas = []
        cols = st.columns(2)
        for i, opcao in enumerate(pergunta["opcoes"]):
            with cols[i % 2]:
                if st.checkbox(opcao, key=f"{key_base}_{i}_{opcao.replace(' ', '_')}"):
                    selecionadas.append(opcao)
        return ", ".join(selecionadas) if selecionadas else None

    return st.radio(
        "Opções:",
        pergunta["opcoes"],
        index=None,
        key=f"{key_base}_radio",
        label_visibility="collapsed",
    )


def validar_respostas(respostas: dict[str, str], blocos_ativos: list) -> list[str]:
    faltando = []
    for bloco in blocos_ativos:
        for pergunta in bloco["perguntas"]:
            if pergunta["chave"] not in respostas:
                faltando.append(f"Item {extrair_numero_pergunta(pergunta['chave'])}")
    return faltando


def calcular_percentual_maturidade(respostas: dict[str, str]) -> int:
    nivel, texto = avaliar_maturidade(respostas)
    inicio = texto.find("(") + 1
    fim = texto.find("%")
    return int(texto[inicio:fim]) if inicio > 0 and fim > inicio else 0


def exibir_relatorio(respostas: dict[str, str], pdf_bytes: bytes) -> None:
    nivel, _ = avaliar_maturidade(respostas)
    percentual = calcular_percentual_maturidade(respostas)
    cor_texto, _ = CORES_MATURIDADE.get(nivel, ("#1B5E20", "#E8F5E9"))
    data = datetime.now().strftime("%d/%m/%Y às %H:%M")

    st.markdown(f'<div class="relatorio-header"><h2>📊 Relatório de Diagnóstico Estratégico</h2><p>Análise de Viabilidade Emitida em {data}</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div>NÍVEL DE MATURIDADE</div><div style="font-size:1.6rem;font-weight:700;color:{cor_texto};">{nivel}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div>ÍNDICE DE COMPLIANCE</div><div style="font-size:1.6rem;font-weight:700;color:#1D1D1F;">{percentual}%</div></div>', unsafe_allow_html=True)
    with col3:
        tipo = obter(respostas, "1. Tipo principal do projeto")
        st.markdown(f'<div class="metric-card"><div>SEGMENTO ALVO</div><div style="font-size:1.2rem;font-weight:600;color:#1B4332;">{tipo}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(percentual / 100)

    st.markdown("### 📝 Resumo Executivo")
    for linha in gerar_resumo_executivo(respostas):
        if linha.strip():
            st.markdown(linha.strip())

    st.markdown("### 🗺️ Plano de Ação & Próximos Passos")
    for passo in gerar_proximos_passos(respostas):
        st.markdown(f'<div class="passo-item">➔ {passo}</div>', unsafe_allow_html=True)

    st.divider()
    
    st.download_button(
        label="⬇️ Baixar Diagnóstico Corporativo Oficial (PDF)",
        data=pdf_bytes,
        file_name="Diagnostico_Maturidade_Carbono.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(page_title="Carbon Diagnosis", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")
    aplicar_estilo()

    # 🖥️ OPERAÇÃO DA TELA LATERAL FIXA NO CANTO DIREITO (ESTILO GEMINI PREMIUM)
    with st.sidebar:
        # ── 0. LOGOTIPO DA EMPRESA ───────────────────────────────────────
        st.image("logo.png", width=100)
        
        # ── 1. TOPO FIXO (Cabeçalho do Copiloto) ─────────────────────────────
        st.header("🌱 Copiloto de Carbono")
        st.caption("Tire suas dúvidas sobre as perguntas ou envie documentos para análise em tempo real.")
        st.markdown("---")
        
        # ── 2. MEIO EXPANSÍVEL (O Histórico que rola sozinho) ─────────────────
        st.subheader("Chat de Suporte")
        
        if "historico_chat" not in st.session_state:
            st.session_state.historico_chat = [
                {"role": "assistant", "content": "Olá! Sou seu assistente de due diligence. Se não souber como responder alguma pergunta do formulário ao lado esquerdo, ou quiser que eu analise o documento anexo, é só me chamar!"}
            ]
            
        caixa_historico = st.container(height=350, border=False)
        
        with caixa_historico:
            for mensagem in st.session_state.historico_chat:
                with st.chat_message(mensagem["role"]):
                    st.write(mensagem["content"])
                    
        # ── 3. CAIXA DE TEXTO DO CHAT (DIGITAÇÃO LIVRE) ───────────────────────
        texto_digitado = st.chat_input("Ex: O que é adicionalidade? Ou analise o anexo...", key="chat_input_sidebar")
        
        # ── 4. RODAPÉ FIXO (Área de Anexar Documentos) ────────────────────────
        st.markdown("---")
        st.subheader("Anexar Documentos")
        arquivo_anexado = st.file_uploader(
            "Envie a Matrícula, CAR ou PDD (PDF)", 
            type=["pdf"], 
            help="A IA lerá o documento para te ajudar a responder o formulário ao lado.",
            key="uploader_ia_definitivo"
        )
        
        if arquivo_anexado:
            st.success("📎 Documento pronto para análise!")

        # ── 5. PROCESSAMENTO DO ENVIO COM BASE NOS MANUAIS DE AUDITORIA ──────
        if texto_digitado:
            with caixa_historico:
                with st.chat_message("user"):
                    st.write(texto_digitado)
            st.session_state.historico_chat.append({"role": "user", "content": texto_digitado})
            
            with caixa_historico:
                with st.chat_message("assistant"):
                    with st.spinner("Analisando e gerando resposta..."):
                        try:
                            api_key = st.secrets.get("GEMINI_API_KEY")
                            
                            if api_key:
                                client = genai.Client(api_key=api_key)
                                
                                # Prompt estruturado conforme padrões internacionais de Due Diligence e Compliance[cite: 2, 3, 4, 7, 10]
                                contexto_prompt = (
                                    "Você é o Copiloto de Carbono, um especialista sênior em Due Diligence e estruturação de projetos de crédito de carbono no Brasil. "
                                    "Sua missão é analisar as dúvidas do usuário e os documentos anexados (como CAR, Matrículas ou Inventários) com base rigorosa nas seguintes referências:\n"
                                    "1. GHG Protocol: Classifique e oriente sobre limites organizacionais e escopos de emissão (Escopos 1, 2 e 3)[cite: 3, 7].\n"
                                    "2. Diretrizes AFOLU: Avalie critérios de elegibilidade do solo, histórico de desmatamento/reflorestamento (ARR/REDD+) e o risco de Vazamento (Leakage)[cite: 10].\n"
                                    "3. Adicionalidade (MDL): Avalie se a atividade proposta demonstra barreira financeira, tecnológica ou regulatória, comprovando que o projeto não ocorreria sem o incentivo dos créditos[cite: 2, 4, 6].\n"
                                    "4. Manual de Verificadores: Seja criterioso com a consistência de dados. Exija perímetros digitais claros (arquivos KML/SHP) e consistência entre CAR e Matrícula[cite: 8].\n"
                                    "5. Regulamentação SBCE: Oriente sobre o enquadramento no Sistema Brasileiro de Comércio de Emissões para quem emite acima de 25.000 tCO2e/ano[cite: 4, 7].\n\n"
                                    "Responda de forma altamente profissional, porém clara, direta e executiva. Se houver um PDF anexado, use seus dados para fundamentar tecnicamente o diagnóstico.\n"
                                    f"Dúvida do usuário: {texto_digitado}"
                                )
                                conteudos_enviar = [contexto_prompt]
                                
                                if arquivo_anexado:
                                    bytes_pdf = arquivo_anexado.read()
                                    pdf_part = types.Part.from_bytes(
                                        data=bytes_pdf,
                                        mime_type="application/pdf"
                                    )
                                    conteudos_enviar.append(pdf_part)
                                
                                for tentativa in range(3):
                                    try:
                                        resposta = client.models.generate_content(
                                            model='gemini-2.5-flash',
                                            contents=conteudos_enviar,
                                        )
                                        texto_resposta = resposta.text
                                        break
                                    except Exception as e_chat:
                                        if "503" in str(e_chat) and tentativa < 2:
                                            time.sleep(2)
                                            continue
                                        raise e_chat
                            else:
                                texto_resposta = "⚠️ Chave 'GEMINI_API_KEY' não encontrada nos Secrets do Streamlit."
                                
                        except Exception as e:
                            print(f"Erro detalhado da API do Gemini: {e}")
                            texto_resposta = f"Não consegui conectar ao cérebro da IA. Detalhe técnico: {str(e)}"
                        
                        st.write(texto_resposta)
            
            st.session_state.historico_chat.append({"role": "assistant", "content": texto_resposta})
            st.rerun()

    # ── Conteúdo Principal (Lado Esquerdo) ───────────────────────────────────
    st.markdown('<div class="main-header"><h1>🌱 Diagnóstico de Projetos de Carbono</h1><p>Plataforma inteligente de avaliação e due diligence para os mercados voluntário e regulado (SBCE)</p></div>', unsafe_allow_html=True)

    template_pdf = gerar_template_pdf()
    c_btn, c_radio = st.columns([1, 2])
    with c_btn:
        st.download_button(
            label="⬇️ Baixar Template de Suporte (PDF)", 
            data=template_pdf, 
            file_name="template_suporte_carbono.pdf", 
            mime="application/pdf", 
            use_container_width=True
        )
    with c_radio:
        jornada = st.radio("Jornada do Projeto:", ["✨ Estruturar do zero (Frente 1 — Estruturação)", "🔍 Validar ativo existente (Frente 2 — Pré-Auditoria)"], index=0, horizontal=True)
        
    st.divider()

    if "relatorio_gerado" not in st.session_state:
        st.session_state.relatorio_gerado = False
        st.session_state.pdf_data = b""
        st.session_state.respostas_finais = {}

    if "Frente 1" in jornada:
        blocos_ativos = BLOCOS[:6]
    else:
        blocos_ativos = [BLOCOS[0], BLOCOS[1], BLOCOS[6], BLOCOS[7], BLOCOS[8]]

    tab_labels = [f"{b['icone']} {b['titulo']}" for b in blocos_ativos]
    tabs = st.tabs(tab_labels)
    respostas_parciais: dict[str, str] = {}

    contador_item = 1

    for tab, bloco in zip(tabs, blocos_ativos):
        with tab:
            st.markdown(f"#### {bloco['subtitulo']}")
            
            with st.container(border=True):
                perguntas = bloco["perguntas"]
                for idx in range(0, len(perguntas), 2):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        p1 = perguntas[idx]
                        indice_real = BLOCOS.index(bloco)
                        v1 = renderizar_pergunta(p1, indice_real, idx, contador_item)
                        contador_item += 1
                        if v1: 
                            respostas_parciais[p1["chave"]] = v1
                            
                    with col2:
                        if idx + 1 < len(perguntas):
                            p2 = perguntas[idx + 1]
                            indice_real = BLOCOS.index(bloco)
                            v2 = renderizar_pergunta(p2, indice_real, idx + 1, contador_item)
                            contador_item += 1
                            if v2: 
                                respostas_parciais[p2["chave"]] = v2
                        
                    if idx + 2 < len(perguntas):
                        st.divider()

    total_perguntas = sum(len(b["perguntas"]) for b in blocos_ativos)
    respondidas = len(respostas_parciais)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, col_info = st.columns([3, 1])
    with col_btn:
        gerar = st.button("🌿 Analisar Viabilidade e Emitir Relatório", type="primary", use_container_width=True)
    with col_info:
        st.metric("Itens Respondidos", f"{respondidas}/{total_perguntas}")

    if gerar:
        faltando = validar_respostas(respostas_parciais, blocos_ativos)
        if faltando:
            st.error(f"⚠️ Por favor, preencha todos os itens obrigatórios antes de gerar. Pendentes: {', '.join(faltando)}")
        else:
            st.session_state.respostas_finais = respostas_parciais
            st.session_state.pdf_data = gerar_relatorio_pdf(respostas_parciais)
            st.session_state.relatorio_gerado = True
            st.balloons()

    if st.session_state.relatorio_gerado and "pdf_data" in st.session_state and st.session_state.pdf_data:
        exibir_relatorio(st.session_state.respostas_finais, st.session_state.pdf_data)


if __name__ == "__main__":
    main()