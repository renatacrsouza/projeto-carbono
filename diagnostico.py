#!/usr/bin/env python3
"""Motor de cálculo premium integrado com Inteligência Artificial para o Diagnóstico de Carbono."""

import os
from typing import Any
from fpdf import FPDF
import streamlit as st
from google import genai  # 🟢 Biblioteca nova e pura


def obter(respostas: dict[str, str], chave: str) -> str:
    """Auxiliar para obter resposta de forma segura, retornando padrão se não houver."""
    return respostas.get(chave, "Não informado")


def avaliar_maturidade(respostas: dict[str, str]) -> tuple[str, str]:
    """Avalia o nível de maturidade do projeto com base nas respostas fornecidas."""
    pontos = 0
    total_possivel = 0

    tipo = obter(respostas, "1. Tipo principal do projeto")
    if tipo != "Não informado":
        total_possivel += 10
        if tipo in ["Florestal", "Agropecuário", "Energia"]:
            pontos += 10
        else:
            pontos += 7

    estagio = obter(respostas, "4. Estágio atual")
    if estagio != "Não informado":
        total_possivel += 15
        if estagio in ["Em monitoramento", "Já passou por auditoria"]:
            pontos += 15
        elif estagio in ["Projeto já implementado", "Estou estruturando"]:
            pontos += 10
        else:
            pontos += 5

    fundiaria = obter(respostas, "5. Documentação fundiária")
    if fundiaria != "Não informado":
        total_possivel += 20
        if fundiaria == "Sim, escritura e CAR":
            pontos += 20
        elif fundiaria == "Parcialmente":
            pontos += 10
        else:
            pontos += 0

    permanencia = obter(respostas, "18. Permanência por 20-30 anos")
    if permanencia != "Não informado":
        total_possivel += 15
        if permanencia == "Sim, com segurança":
            pontos += 15
        elif permanencia == "Provavelmente sim":
            pontos += 10
        else:
            pontos += 0

    if "21. Faixa de Emissões Anuais" in respostas:
        docs_territoriais = obter(respostas, "19. Documentação Territorial Obrigatória")
        if docs_territoriais and docs_territoriais != "Não informado":
            total_possivel += 15
            qtd_docs = len(docs_territoriais.split(","))
            pontos += min(qtd_docs * 4, 15)

        sobreposicao = obter(respostas, "23. Restrições e Sobreposições Territoriais")
        if sobreposicao != "Não informado":
            total_possivel += 15
            if "Não, área 100% livre" in sobreposicao:
                pontos += 15
            elif "Não realizei" in sobreposicao:
                pontos += 5
            else:
                pontos += 0
    else:
        estimativa = obter(respostas, "9. Estimativa de tCO2e/ano")
        if estimativa != "Não informado":
            total_possivel += 15
            if "10.000" in estimativa or "Mais de" in estimativa:
                pontos += 15
            elif "1.000" in estimativa:
                pontos += 10
            else:
                pontos += 5

    percentual = int((pontos / total_possivel) * 100) if total_possivel > 0 else 0
    nivel = "AVANCADO" if percentual >= 75 else "INTERMEDIARIO" if percentual >= 45 else "INICIAL"
    return nivel, str(percentual)


def gerar_resumo_executivo(respostas: dict[str, str]) -> list[str]:
    """Gera o resumo das principais características do projeto."""
    resumo = []
    tipo = obter(respostas, "1. Tipo principal do projeto")
    bioma = obter(respostas, "2. Bioma / região")
    area = obter(respostas, "3. Área total envolvida")
    
    resumo.append(f"Tipo de Projeto: Desenvolvido no setor {tipo}, localizado no bioma/regiao {bioma}.")
    resumo.append(f"Escala Territorial: O projeto abrange uma extensao aproximada de {area}.")
    
    if "21. Faixa de Emissões Anuais" in respostas:
        emissoes = obter(respostas, "21. Faixa de Emissões Anuais")
        resumo.append(f"Perfil Regulatorio: Enquadrado na faixa: {emissoes}.")
    
    return resumo


def gerar_proximos_passos(respostas: dict[str, str]) -> list[str]:
    """Gera uma lista de ações e próximos passos recomendados sem linhas fantasmas."""
    passos = []
    
    fundiaria = obter(respostas, "5. Documentação fundiária")
    if fundiaria in ["Não", "Não sei", "Parcialmente"]:
        passos.append("Priorizar a regularizacao dos titulos de posse, escrituras e retificacao do CAR.")
        
    if "21. Faixa de Emissões Anuais" in respostas:
        sobreposicao = obter(respostas, "23. Restrições e Sobreposições Territoriais")
        if "Não realizei" in sobreposicao or "Sobreposição" in sobreposicao:
            passos.append("Realizar analise de SIG para cruzar limites do CAR com terras protegidas.")
    else:
        passos.append("Iniciar o desenvolvimento tecnico do Documento de Concepcao do Projeto (PDD).")
        passos.append("Mapear a metodologia oficial de monitoramento (MRV) para a atividade.")

    if not passos:
        passos.append("Proceder com o agendamento da auditoria de validacao oficial.")
        
    return passos


def chamar_inteligencia_artificial(respostas: dict[str, str], nivel: str, percentual: str) -> str:
    """Conecta com a API do Gemini para gerar uma análise consultiva ultra personalizada."""
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return (
            f"DIAGNOSTICO PRE-AUDITORIA (Modo Padrao)\n\n"
            f"O projeto apresenta um indice de compliance de {percentual}% com maturidade {nivel}.\n"
            f"Principais pilares analisados: Atividade focada no segmento {obter(respostas, '1. Tipo principal do projeto')} "
            f"no bioma {obter(respostas, '2. Bioma / regiao')}. Recomenda-se a estruturacao imediata dos "
            f"gaps identificados no plano de acao da plataforma."
        )
        
    try:
        # 🟢 CORREÇÃO: Forçando a API estável aqui também!
        client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1'}
        )
        
        prompt = f"""
        Atue como um Auditor Senior Internacional de Créditos de Carbono...
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text.strip()
        
    except Exception as e:
        return f"Erro na conexao com o cerebro de IA. Relatorio gerado com base nos parametros estruturais para o nivel {nivel} ({percentual}%). Detalhe: {str(e)}"


def gerar_relatorio_pdf(respostas: dict[str, str]) -> bytes:
    """Gera o relatório final formatado em PDF sem quebras e com inteligência artificial."""
    nivel, percentual = avaliar_maturidade(respostas)
    analise_ia = chamar_inteligencia_artificial(respostas, nivel, percentual)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    verde_escuro = (27, 67, 50)
    cinza_texto = (60, 60, 60)
    
    # Cabeçalho Estilo Corporativo
    pdf.set_fill_color(*verde_escuro)
    pdf.rect(0, 0, 210, 38, "F")
    
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "DIAGNOSTICO CONSULTIVO INTELIGENTE (IA)", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, f"Analise Estrategica de Viabilidade e Due Diligence · Score: {percentual}%", ln=True, align="C")
    
    pdf.ln(22)
    
    # 1. Parâmetros Gerais
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*verde_escuro)
    pdf.cell(190, 8, "1. PARAMETROS DE TRIAGEM E COMPLIANCE", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*cinza_texto)
    pdf.multi_cell(190, 6, f"- Classificacao Geral do Ativo: Nivel {nivel}\n- Indice de Adequacao Regulada: {percentual}%\n- Escala do Projeto: {obter(respostas, '3. Área total envolvida')}")
    pdf.ln(6)
    
    # 2. Avaliação Dinâmica da IA
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*verde_escuro)
    pdf.cell(190, 8, "2. AVALIACAO ESPECIFICA DO AUDITOR INTELIGENTE", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*cinza_texto)
    texto_limpo = analise_ia.encode('latin-1', 'ignore').decode('latin-1').strip()
    pdf.multi_cell(190, 6, texto_limpo)
    pdf.ln(6)
    
    # 3. Próximos Passos
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*verde_escuro)
    pdf.cell(190, 8, "3. DIRETRIZES IMEDIATAS RECOMENDADAS", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*cinza_texto)
    for passo in gerar_proximos_passos(respostas):
        passo_limpo = passo.encode('latin-1', 'ignore').decode('latin-1').strip()
        if passo_limpo:
            pdf.multi_cell(190, 6, f"- {passo_limpo}")
        
    pdf.ln(12)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(190, 5, "Relatorio analitico gerado por integracao cognitiva de IA em conformidade com as regras do SBCE e CVM.", ln=True, align="C")
    
    return pdf.output(dest='S').encode('latin-1')