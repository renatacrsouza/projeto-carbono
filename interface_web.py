#!/usr/bin/env python3
"""Interface web premium do diagnóstico de carbono - Estilo Minimalista Apple."""

import time
from datetime import datetime
from typing import Optional
import streamlit as st
from fpdf import FPDF
from google import genai
from google.genai import types
import pandas as pd

from diagnostico import (
    avaliar_maturidade,
    gerar_proximos_passos,
    gerar_relatorio_pdf,
    gerar_resumo_executivo,
    obter,
)


def gerar_template_pdf() -> bytes:
    """Gera o modelo de relatório completo em bytes."""
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
            "Item 12. Objective principal com as transacoes",
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
            
    # Substitua o 'return pdf.output(dest='S')' por estas linhas:
    resultado = pdf.output(dest='S')
    
    # Se for string, converte para bytes. Se já for bytes, retorna como está.
    if isinstance(resultado, str):
        return resultado.encode('latin-1')
    return bytes(resultado)


# ── Estrutura do questionário atualizada ──────────────────────────────────────
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
        "subtitulo": "03 · SITUAÇÃO ATUAL E HISTÓRICO",
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
        "subtitulo": "04 · POTENCIAL DE GERAÇÃO",
        "icone": "⚡",
        "perguntas": [
            {"chave": "8. Atividade principal", "texto": "Qual é a atividade geradora de créditos?", "opcoes": ["Evitar desmatamento (REDD+)", "Reflorestamento / restauração", "Plantio direto / recuperação solo", "Biodigestor / biogás", "Energia solar / eólica", "Eficiência energética", "Outro"]},
            {"chave": "9. Estimativa de tCO2e/ano", "texto": "Qual a estimativa de volume anual?", "opcoes": ["Menos de 1.000 tCO2e/ano", "1.000 a 10.000 tCO2e/ano", "10.000 a 100.000 tCO2e/ano", "Mais de 100.000 tCO2e/ano", "Não sei estimar"]},
            {"chave": "10. Benefícios socioambientais", "texto": "Gera benefícios socioambientais extras?", "opcoes": ["Biodiversidade", "Recursos hídricos", "Comunidades locais", "Geração de emprego", "Nenhum mapeado"], "multipla": True},
        ],
    },
    {
        "titulo": "Certificação",
        "subtitulo": "05 · CERTIFICAÇÃO E MERCADO",
        "icone": "🏅",
        "perguntas": [
            {"chave": "11. Contato com certificadora", "texto": "Já teve contato com alguma certificadora?", "opcoes": ["Verra (VCS)", "Gold Standard", "RENOVABIO", "SBCE (brasileiro)", "Nenhuma ainda"]},
            {"chave": "12. Objetivo principal com os créditos", "texto": "Qual é o objetivo comercial principal?", "opcoes": ["Vender no mercado voluntário", "Cumprir obrigação legal (compliance)", "Reporte ESG / neutralização", "Ainda não definido"]},
            {"chave": "13. Acesso a capital para certificação", "texto": "Tem acesso a capital para custear o processo?", "opcoes": ["Sim", "Parcialmente, preciso de financiamento", "Não no momento"], "ajuda": "Estimativa: R$ 50k–300k."},
        ],
    },
    {
        "titulo": "Execução",
        "subtitulo": "06 · CAPACIDADE DE EXECUÇÃO",
        "icone": "🛠️",
        "perguntas": [
            {"chave": "14. Equipe técnica", "texto": "Há equipe técnica para conduzir o projeto?", "opcoes": ["Sim, equipe interna", "Sim, via consultoria", "Não ainda"]},
            {"chave": "15. Prazo para submissão", "texto": "Em quanto tempo espera estar pronto?", "opcoes": ["Menos de 6 meses", "6 a 12 meses", "1 a 2 anos", "Não sei"]},
        ],
    },
    {
        "titulo": "Riscos",
        "subtitulo": "07 · RISCOS E BARREIRAS",
        "icone": "⚠️",
        "perguntas": [
            {"chave": "16. Conflitos fundiários", "texto": "Existem conflitos fundiários na área?", "opcoes": ["Não", "Há pendências em resolução", "Sim"]},
            {"chave": "17. Passivos ambientais", "texto": "Há passivos ambientais conhecidos?", "opcoes": ["Não", "Há área de passivo, mas em recuperação", "Sim, não endereçados"]},
            {"chave": "18. Permanência por 20-30 anos", "texto": "Pode garantir permanência por 20-30 anos?", "opcoes": ["Sim, com segurança", "Provavelmente sim", "Incerto", "Não"], "ajuda": "Requisito mínimo de mercado."},
        ],
    },
    {
        "titulo": "Checklist Docs",
        "subtitulo": "08 · DOCUMENTAÇÃO ESSENCIAL AUDITÁVEL",
        "icone": "📋",
        "perguntas": [
            {"chave": "19. Documentação Territorial Obrigatória", "texto": "Quais documentos territoriais possui regularizados?", "opcoes": ["Matrícula Atualizada", "CCIR Regular", "Declaração do ITR (DITR)", "Georreferenciamento (SIGEF)"], "multipla": True},
            {"chave": "20. Documentação Técnica de Carbono", "texto": "Quais estudos técnicos já foram elaborados?", "opcoes": ["Inventário de Emissões", "Estudo de Adicionalidade", "Linha de Base (Baseline)", "Nenhum técnico ainda"], "multipla": True}
        ]
    },
    {
        "titulo": "Gap Analysis SBCE",
        "subtitulo": "09 · ENQUADRAMENTO REGULATÓRIO (LEI 15.042/24)",
        "icone": "🔍",
        "perguntas": [
            {"chave": "21. Faixa de Emissões Anuais", "texto": "Volume estimado de emissões de GEE da atividade por ano?", "opcoes": ["Abaixo de 10.000 tCO2e (Isento)", "Entre 10.000 e 25.000 tCO2e (Monitorado)", "Acima de 25.000 tCO2e (Metas Rígidas)", "Não sei estimar"]},
            {"chave": "22. Enquadramento de Ativos", "texto": "Qual será o foco principal de transação do projeto?", "opcoes": ["Gerar CRVEs", "Gerenciar CBEs (Cotas do Governo)", "Mercado Voluntário tradicional", "Ainda não definido"]}
        ]
    },
    {
        "titulo": "Análise do CAR",
        "subtitulo": "10 · RESTRIÇÕES AMBIENTAIS E MAPA DE RISCO",
        "icone": "🗺️",
        "perguntas": [
            {"chave": "23. Restrições e Sobreposições Territoriais", "texto": "A análise indicou sobreposição da área?", "opcoes": ["Não, área 100% livre e regular", "Sobreposição parcial com UC", "Sobreposição com TI ou Quilombolas", "Sobreposição com outras propriedades", "Não realizei a análise de Gaps"]},
            {"chave": "24. Passivo de Reserva Legal", "texto": "Existe déficit florestal de Reserva Legal ou APP?", "opcoes": ["Não, déficit zerado", "Sim, com PRA ativo", "Sim, passivo aberto sem plano", "Não aplicável"]}
        ]
    },
    {
        "titulo": "Mapeamento",
        "subtitulo": "11 · MAPEAMENTO GEOGRÁFICO DA ÁREA",
        "icone": "🗺️",
        "perguntas": [] 
    }
]

CORES_MATURIDADE = {"AVANCADO": ("#1E3F20", "#EBF5EE"), "INTERMEDIARIO": ("#D97706", "#FEF3C7"), "INICIAL": ("#DC2626", "#FEE2E2")}


def aplicar_estilo() -> None:
    st.markdown(
        """
        <style>
            /* 1. Layout Base: Inverte tudo para a IA ficar na direita */
            [data-testid="stAppViewContainer"] {
                flex-direction: row-reverse !important;
            }

            /* 2. Barra Lateral (IA) na Direita */
            [data-testid="stSidebar"] {
                width: 400px !important;
                min-width: 400px !important;
                right: 0 !important;
                left: auto !important;
                background-color: #F8F9FA !important;
                padding: 0.5rem !important;
            }

            /* 3. Conteúdo Principal: Ocupa todo o resto da tela à esquerda */
            [data-testid="stMainBlockContainer"] {
                max-width: 100% !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
            }
            
            /* 4. Chat Compacto */
            [data-testid="stChatMessage"] { 
                padding: 0.3rem !important; 
                font-size: 0.85rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def extrair_numero_pergunta(chave: str) -> str:
    return chave.split(".")[0].strip()


def renderizar_pergunta(pergunta: dict, indice_bloco: int, indice_pergunta: int, numero_sequencial: int) -> Optional[str]:
    key_base = f"b{indice_bloco}_q{indice_pergunta}"
    valor_previo = st.session_state.respostas_acumuladas.get(pergunta["chave"], None)

    st.markdown(f'<span class="pergunta-num">ITEM {numero_sequencial}</span>', unsafe_allow_html=True)
    st.markdown(f"##### {pergunta['texto']}")
    if pergunta.get("ajuda"):
        st.caption(pergunta["ajuda"])

    if pergunta.get("multipla"):
        selecionadas = []
        lista_previa = [x.strip() for x in valor_previo.split(",")] if valor_previo else []
        cols = st.columns(2)
        for i, opcao in enumerate(pergunta["opcoes"]):
            with cols[i % 2]:
                marcado_inicial = opcao in lista_previa
                if st.checkbox(opcao, value=marcado_inicial, key=f"{key_base}_{i}_{opcao.replace(' ', '_')}"):
                    selecionadas.append(opcao)
        return ", ".join(selecionadas) if selecionadas else None

    idx_inicial = None
    if valor_previo and valor_previo in pergunta["opcoes"]:
        idx_inicial = pergunta["opcoes"].index(valor_previo)

    return st.radio(
        "Opções:",
        pergunta["opcoes"],
        index=idx_inicial,
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

    # --- NOVO CABEÇALHO ---
    col_logo, col_titulo = st.columns([1, 10])
    with col_logo:
        # Se você tiver a imagem "logo.png", use a linha abaixo:
        st.image("logo.png", width=60) 
        # Se quiser usar um emoji no lugar da imagem, use: st.write("🌱")
    with col_titulo:
        st.markdown("### CarbonMind") # O nome da sua empresa
    
    st.divider() # Adiciona uma linha horizontal para separar do resto
    # --- FIM DO CABEÇALHO ---

    # (A partir daqui começa o restante do seu código original...)

    if "respostas_acumuladas" not in st.session_state:
        st.session_state.respostas_acumuladas = {}

    if "latitude_mapa" not in st.session_state:
        st.session_state.latitude_mapa = -23.2641
    if "longitude_mapa" not in st.session_state:
        st.session_state.longitude_mapa = -47.2992

    # 🖥️ OPERAÇÃO DA TELA LATERAL FIXA NO CANTO DIREITO (ESTILO GEMINI PREMIUM)
    with st.sidebar:
        #st.image("logo.png", width=100)
        st.header("🌱 Copiloto de Carbono")
        st.caption("Tire suas dúvidas sobre as perguntas ou envie documentos para análise em tempo real.")
        st.markdown("---")
        st.subheader("Chat de Suporte")
        
        if "historico_chat" not in st.session_state:
            st.session_state.historico_chat = [
                {"role": "assistant", "content": "Olá! Sou seu assistente de due diligence. Se não souber como responder alguma pergunta do formulário ao lado esquerdo, ou quiser que eu analise o documento anexo, é só me chamar!"}
            ]
            
        caixa_historico = st.container(height=350, border=False)
        
        with caixa_historico:
            for message in st.session_state.historico_chat:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
        texto_digitado = st.chat_input("Ex: O que é adicionalidade? Ou analise o anexo...", key="chat_input_sidebar")
        st.markdown("---")
        st.subheader("Anexar Documentos")
        arquivo_anexado = st.file_uploader("Envie a Matrícula, CAR ou PDD (PDF)", type=["pdf"], key="uploader_ia_definitivo")
        
        if arquivo_anexado:
            st.success("📎 Documento pronto para análise!")

        if texto_digitado:
            with caixa_historico:
                with st.chat_message("user"):
                    st.write(texto_digitado)
            st.session_state.historico_chat.append({"role": "user", "content": texto_digitado})
            
            with st.sidebar:
                st.subheader("Análise Atual")
                if arquivo_anexado:
                    st.success(f"📎 {arquivo_anexado.name}")
                else:
                    st.info("Nenhum doc. anexado.")

            if texto_digitado:
                with caixa_historico:
                    with st.chat_message("user"):
                        st.write(texto_digitado)
                st.session_state.historico_chat.append({"role": "user", "content": texto_digitado})

                with caixa_historico:
                    with st.chat_message("assistant"):
                        try:
                            # 1. Carregamento e Autenticação
                            api_key = st.secrets.get("GEMINI_API_KEY")
                            if not api_key:
                                texto_resposta = "❌ Erro: Chave GEMINI_API_KEY não encontrada no Secrets."
                            else:
                                client = genai.Client(api_key=api_key)
                                
                                # 2. Configuração do Sistema
                                system_instruction = (
                                    "Você é o Copiloto de Carbono da CarbonMind. "
                                    "REGRAS: 1. Se houver documento, entregue uma 'Tabela de Auditoria' (Item | Status | Risco). "
                                    "2. Seja direto e executivo. 3. Identifique gaps da Lei 15.042/24."
                                )
                                
                                # 3. Preparação do conteúdo
                                conteudos = [texto_digitado]
                                if arquivo_anexado:
                                    arquivo_anexado.seek(0)
                                    pdf_part = types.Part.from_bytes(
                                        data=arquivo_anexado.read(), 
                                        mime_type="application/pdf"
                                    )
                                    conteudos.append(pdf_part)
                                
                                # 4. Chamada do Modelo
                                st.write("🔍 Consultando normas...")
                                resposta = client.models.generate_content(
                                    model='gemini-1.5-flash',
                                    contents=conteudos,
                                    config=types.GenerateContentConfig(
                                        system_instruction=system_instruction,
                                        temperature=0.2
                                    )
                                )
                                texto_resposta = resposta.text
                                
                        except Exception as e:
                            st.error(f"❌ DEBUG: {type(e).__name__} - {str(e)}")
                            texto_resposta = "Falha na comunicação com o servidor."

                        st.markdown(texto_resposta)
            
            st.session_state.historico_chat.append({"role": "assistant", "content": texto_resposta})
            st.rerun()

    # ── Conteúdo Principal (Lado Esquerdo) ───────────────────────────────────
    st.markdown('<div class="main-header"><h1>🌱 Diagnóstico de Projetos de Carbono</h1><p>Plataforma inteligente de avaliação e due diligence para os mercados voluntário e regulado (SBCE)</p></div>', unsafe_allow_html=True)

    template_pdf = gerar_template_pdf()
    c_btn, c_radio = st.columns([1, 2])
    with c_btn:
        st.download_button(label="⬇️ Baixar Template de Suporte (PDF)", data=template_pdf, file_name="template_suporte_carbono.pdf", mime="application/pdf", use_container_width=True)
    with c_radio:
        # Dicionário: Chave (o que você quer mostrar) -> Valor (o que o código precisa)
        mapeamento = {
            "🚀 Estruturação": "✨ Estruturar do zero (Frente 1 — Estruturação)",
            "🔎 Pré-Auditoria": "🔍 Validar ativo existente (Frente 2 — Pré-Auditoria)"
        }

        # O radio mostra o nome limpo
        selecao_usuario = st.radio("Jornada do Projeto:", list(mapeamento.keys()), index=0, horizontal=True)
        
        # A mágica: o código recebe o nome "feio" (com Frente 1 e 2), mas você não vê
        jornada = mapeamento[selecao_usuario]
        
        # Descrição limpa abaixo
        descricoes = {
            "🚀 Estruturação": "*Foco em projetos do zero: baseline, adicionalidade e viabilidade técnica.*",
            "🔎 Pré-Auditoria": "*Revisão de ativos existentes: conformidade documental e análise de riscos.*"
        }
        st.caption(descricoes[selecao_usuario])
    st.divider()

    if "relatorio_gerado" not in st.session_state:
        st.session_state.relatorio_gerado = False
        st.session_state.pdf_data = b""
        st.session_state.respostas_finais = {}

    if "bloco_atual_index" not in st.session_state:
        st.session_state.bloco_atual_index = 0

    if "Frente 1" in jornada:
        # Pega Identificação, Mapeamento, Situação Atual, Potencial, Certificação, Execução, Riscos
        blocos_ativos = [BLOCOS[0], BLOCOS[1], BLOCOS[2], BLOCOS[3], BLOCOS[4], BLOCOS[5], BLOCOS[6]]
    else:
        # Pega Identificação, Mapeamento, Situação Atual, Checklist Docs, Gap Analysis SBCE, Análise do CAR
        blocos_ativos = [BLOCOS[0], BLOCOS[1], BLOCOS[2], BLOCOS[7], BLOCOS[8], BLOCOS[9]]

    if st.session_state.bloco_atual_index >= len(blocos_ativos):
        st.session_state.bloco_atual_index = 0

    # 📊 BARRA DE PROGRESSO EM TEMPO REAL POR PERGUNTA
    # Contamos o total apenas dos blocos de perguntas reais (excluindo o bloco de mapeamento)
    total_perguntas = sum(len(b["perguntas"]) for b in blocos_ativos if b["titulo"] != "Mapeamento")
    respondidas = len(st.session_state.respostas_acumuladas)
    percentual_preenchido = int((respondidas / total_perguntas) * 100) if total_perguntas > 0 else 0
    
    st.markdown(f"**Progresso Completo do Diagnóstico: {percentual_preenchido}%** ({respondidas} de {total_perguntas} itens concluídos)")
    st.progress(respondidas / total_perguntas if total_perguntas > 0 else 0.0)
    st.markdown("<br>", unsafe_allow_html=True)

    # 🗺️ MENU DE NAVEGAÇÃO PROGRESSIVO (Linha de passos superior)
    col_passos = st.columns(len(blocos_ativos))
    for idx_passo, b_passo in enumerate(blocos_ativos):
        with col_passos[idx_passo]:
            if idx_passo == st.session_state.bloco_atual_index:
                st.markdown(f"<div style='text-align:center; border-bottom:3px solid #0071E3; padding-bottom:5px; font-weight:700;'>{b_passo['icone']} {b_passo['titulo']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center; color:#86868B; padding-bottom:8px;'>{b_passo['icone']} {b_passo['titulo']}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    bloco = blocos_ativos[st.session_state.bloco_atual_index]
    st.markdown(f"#### {bloco['subtitulo']}")
    
    with st.container(border=True):
        # 🗺️ SE FOR A ABA DE MAPEAMENTO: Renderiza apenas o módulo do Google Maps
        if bloco["titulo"] == "Mapeamento":
            st.markdown("##### Mapeamento Geográfico da Área de Estudo")
            st.caption("Insira as coordenadas decimais da propriedade para plotar o perímetro alvo de Due Diligence no mapa de auditoria:")
            
            geo_col1, geo_col2 = st.columns(2)
            with geo_col1:
                lat_input = st.number_input("Latitude (ex: -23.2641):", value=st.session_state.latitude_mapa, format="%.4f", key="input_latitude_global")
            with geo_col2:
                lon_input = st.number_input("Longitude (ex: -47.2992):", value=st.session_state.longitude_mapa, format="%.4f", key="input_longitude_global")
            
            st.session_state.latitude_mapa = lat_input
            st.session_state.longitude_mapa = lon_input
            
            dados_mapa = pd.DataFrame({"lat": [st.session_state.latitude_mapa], "lon": [st.session_state.longitude_mapa]})
            st.map(dados_mapa, zoom=12, use_container_width=True)
            
        # SE FOR OUTRA ABA: Renderiza as perguntas normais em blocos duplos
        else:
            perguntas = bloco["perguntas"]
            # Calcula o contador dinâmico pulando o bloco de mapeamento para não quebrar a contagem matemática
            blocos_anteriores_perguntas = [b for b in blocos_ativos[:st.session_state.bloco_atual_index] if b["titulo"] != "Mapeamento"]
            contador_item = 1 + sum(len(b["perguntas"]) for b in blocos_anteriores_perguntas)
            
            for idx in range(0, len(perguntas), 2):
                col1, col2 = st.columns(2)
                with col1:
                    p1 = perguntas[idx]
                    indice_real = BLOCOS.index(bloco)
                    v1 = renderizar_pergunta(p1, indice_real, idx, contador_item)
                    contador_item += 1
                    if v1: 
                        st.session_state.respostas_acumuladas[p1["chave"]] = v1
                with col2:
                    if idx + 1 < len(perguntas):
                        p2 = perguntas[idx + 1]
                        indice_real = BLOCOS.index(bloco)
                        v2 = renderizar_pergunta(p2, indice_real, idx + 1, contador_item)
                        contador_item += 1
                        if v2: 
                            st.session_state.respostas_acumuladas[p2["chave"]] = v2
                    
                if idx + 2 < len(perguntas):
                    st.divider()

    # 🎛️ BOTÕES DE NAVEGAÇÃO INTERNA DO CARD
    st.markdown("<br>", unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        if st.session_state.bloco_atual_index > 0:
            if st.button("⬅️ Anterior", use_container_width=True):
                st.session_state.bloco_atual_index -= 1
                st.rerun()
                
    with nav_col3:
        if st.session_state.bloco_atual_index < len(blocos_ativos) - 1:
            if st.button("Próximo ➡️", use_container_width=True):
                st.session_state.bloco_atual_index += 1
                st.rerun()
        else:
            gerar_final = st.button("🌿 Emitir Relatório", key="btn_gerar_final_aba", type="primary", use_container_width=True)
            if gerar_final:
                faltando = validar_respostas(st.session_state.respostas_acumuladas, [b for b in blocos_ativos if b["titulo"] != "Mapeamento"])
                if faltando:
                    st.error(f"⚠️ Por favor, preencha todos os itens obrigatórios antes de gerar. Pendentes: {', '.join(faltando)}")
                else:
                    st.session_state.respostas_finais = st.session_state.respostas_acumuladas
                    
                    try:
                        st.session_state.pdf_data = gerar_relatorio_pdf(st.session_state.respostas_acumuladas)
                    except Exception as e_pdf:
                        st.warning("A cota diária de requisições da IA atingiu o limite temporário. Gerando relatório com base nos parâmetros de auditoria local.")
                        pdf_fallback = FPDF()
                        pdf_fallback.add_page()
                        pdf_fallback.set_font("Arial", "B", 12)
                        pdf_fallback.cell(0, 10, "DIAGNOSTICO ESTRATEGICO - RELATORIO TECNICO DE SUPORTE", ln=True, align="C")
                        pdf_fallback.ln(5)
                        pdf_fallback.set_font("Arial", "", 10)
                        pdf_fallback.cell(0, 8, f"Nivel Evaluado: {avaliar_maturidade(st.session_state.respostas_acumuladas)[0]}", ln=True)
                        st.session_state.pdf_data = pdf_fallback.output(dest='S').encode('latin-1')
                        
                    st.session_state.relatorio_gerado = True

    if st.session_state.relatorio_gerado and "pdf_data" in st.session_state and st.session_state.pdf_data:
        exibir_relatorio(st.session_state.respostas_finais, st.session_state.pdf_data)


if __name__ == "__main__":
    main()