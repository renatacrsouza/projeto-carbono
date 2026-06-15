#!/usr/bin/env python3
"""Motor de cálculo e geração de relatórios premium para o Diagnóstico de Carbono."""

from typing import Any
from fpdf import FPDF


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

    # Lógica adaptada para frentes dinâmicas
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

    if percentual >= 75:
        nivel = "AVANCADO"
        descricao = f"Seu projeto possui um nivel de maturidade excelente ({percentual}%). As bases estao prontas para avancar rumo a auditoria ou certificacao no mercado regulado (SBCE) ou voluntario."
    elif percentual >= 45:
        nivel = "INTERMEDIARIO"
        descricao = f"Seu projeto possui nivel intermediario de maturidade ({percentual}%). Existem lacunas importantes (gaps) que precisam ser resolvidas, principalmente em documentacao ou estruturacao de riscos."
    else:
        nivel = "INICIAL"
        descricao = f"Seu projeto esta em estagio inicial de viabilidade ({percentual}%). Recomenda-se focar na regularizacao fundiaria da area, analise detalhada do CAR e modelagem da linha de base antes de investir em auditorias dispendiosas."

    return nivel, f"Nivel de Maturidade: {nivel} ({percentual}%)\n\n{descricao}"


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


def gerar_relatorio_pdf(respostas: dict[str, str]) -> bytes:
    """Gera o relatório final formatado em PDF sem quebras e com margens seguras."""
    nivel, desc = avaliar_maturidade(respostas)
    
    pdf = FPDF()
    pdf.add_page()
    
    # 🟢 MARGEM DE SEGURANÇA CONTRA QUEBRAS PREMATURAS: Reduzida de 15 para 10mm
    pdf.set_auto_page_break(auto=True, margin=10)
    
    verde_escuro = (27, 67, 50)
    cinza_texto = (60, 60, 60)
    
    # Cabeçalho Estilo Corporativo
    pdf.set_fill_color(*verde_escuro)
    pdf.rect(0, 0, 210, 38, "F")
    
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "DIAGNOSTICO DE PROJETO DE CARBONO", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, "Relatorio Gerado via Consultoria Inteligente Premium", ln=True, align="C")
    
    pdf.ln(22)
    
    # 1. Resultado Geral (LARGURA FIXA 190)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*verde_escuro)
    pdf.cell(190, 8, "1. RESULTADO GERAL DE MATURIDADE", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*cinza_texto)
    desc_limpa = desc.encode('latin-1', 'ignore').decode('latin-1').strip()
    pdf.multi_cell(190, 6, desc_limpa)
    pdf.ln(6)
    
    # 2. Resumo do Perfil (LARGURA FIXA 190)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*verde_escuro)
    pdf.cell(190, 8, "2. RESUMO DO PERFIL DO PROJETO", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*cinza_texto)
    for r in gerar_resumo_executivo(respostas):
        linha_limpa = r.encode('latin-1', 'ignore').decode('latin-1').strip()
        if linha_limpa:
            pdf.multi_cell(190, 6, f"- {linha_limpa}")
        
    pdf.ln(6)
    
    # 3. Próximos Passos (LARGURA FIXA 190)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*verde_escuro)
    pdf.cell(190, 8, "3. DIRETRIZES E PROXIMOS PASSOS RECOMENDADOS", ln=True)
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
    pdf.cell(190, 5, "Relatorio parametrizado em conformidade com as regras do SBCE e CVM.", ln=True, align="C")
    
    return bytes(pdf.output())