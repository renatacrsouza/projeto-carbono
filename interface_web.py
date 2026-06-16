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

# ── 1. FUNÇÃO DO PDF (BLINDADA) ──────────────────────────────────────────────
def gerar_template_pdf() -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_fill_color(27, 67, 50)
    pdf.rect(0, 0, 210, 28, "F")
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(6)
    pdf.cell(0, 8, "TEMPLATE OFICIAL DE SUPORTE - MERCADO DE CARBONO", ln=True, align="C")
    pdf.set_y(34)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(190, 5, "DADOS GERAIS DA PROPRIEDADE", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    return pdf.output(dest='S')

# ── 2. ESTRUTURA DOS BLOCOS ──────────────────────────────────────────────────
BLOCOS = [
    {"titulo": "Identificação", "subtitulo": "01 · IDENTIFICAÇÃO DO PROJETO", "icone": "🌿", "perguntas": [
        {"chave": "1. Tipo principal do projeto", "texto": "Tipo principal?", "opcoes": ["Florestal", "Agropecuário", "Energia", "Outro"]},
        {"chave": "2. Bioma", "texto": "Bioma/Região?", "opcoes": ["Amazônia", "Cerrado", "Mata Atlântica", "Outro"]},
    ]},
    {"titulo": "Situação", "subtitulo": "02 · SITUAÇÃO ATUAL", "icone": "📋", "perguntas": [
        {"chave": "4. Estágio", "texto": "Estágio?", "opcoes": ["Ideia", "Estruturando", "Implementado"]},
    ]},
    {"titulo": "Potencial", "subtitulo": "03 · POTENCIAL", "icone": "⚡", "perguntas": [
        {"chave": "8. Atividade", "texto": "Atividade geradora?", "opcoes": ["REDD+", "Reflorestamento", "Solo"]},
    ]},
    {"titulo": "Certificação", "subtitulo": "04 · CERTIFICAÇÃO", "icone": "🏅", "perguntas": [
        {"chave": "11. Certificadora", "texto": "Contato certificadora?", "opcoes": ["Verra", "Gold Standard", "Nenhuma"]},
    ]},
    {"titulo": "Execução", "subtitulo": "05 · EXECUÇÃO", "icone": "🛠️", "perguntas": [
        {"chave": "14. Equipe", "texto": "Equipe técnica?", "opcoes": ["Interna", "Consultoria", "Não"]},
    ]},
    {"titulo": "Riscos", "subtitulo": "06 · RISCOS", "icone": "⚠️", "perguntas": [
        {"chave": "16. Conflitos", "texto": "Conflitos fundiários?", "opcoes": ["Não", "Sim"]},
    ]},
    {"titulo": "Docs", "subtitulo": "07 · DOCUMENTAÇÃO", "icone": "📋", "perguntas": [
        {"chave": "19. Docs", "texto": "Docs territoriais?", "opcoes": ["Matrícula", "CCIR", "ITR"], "multipla": True},
    ]},
    {"titulo": "SBCE", "subtitulo": "08 · ENQUADRAMENTO SBCE", "icone": "🔍", "perguntas": [
        {"chave": "21. Emissões", "texto": "Volume anual?", "opcoes": ["<10k", "10k-25k", ">25k"]},
    ]},
    {"titulo": "CAR", "subtitulo": "09 · RESTRIÇÕES CAR", "icone": "🗺️", "perguntas": [
        {"chave": "23. Sobreposição", "texto": "Sobreposição?", "opcoes": ["Não", "Sim"]},
    ]},
    # 🗺️ MAPA AGORA É A ÚLTIMA ABA
    {"titulo": "Mapeamento", "subtitulo": "10 · MAPEAMENTO GEOGRÁFICO", "icone": "📍", "perguntas": []}
]

# ── 3. LÓGICA DE EXECUÇÃO (MAIN) ──────────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title="Carbon Diagnosis", layout="wide")
    
    if "respostas_acumuladas" not in st.session_state: st.session_state.respostas_acumuladas = {}
    if "bloco_atual_index" not in st.session_state: st.session_state.bloco_atual_index = 0
    if "latitude_mapa" not in st.session_state: st.session_state.latitude_mapa = -23.2641
    
    # Renderização da barra de passos e conteúdo...
    # (Copie aqui a sua lógica de navegação e botões que testamos)
    
    # No final do último bloco:
    if st.session_state.bloco_atual_index == len(BLOCOS) - 1:
        if st.button("🌿 Emitir Relatório", type="primary"):
            # Lógica com tratamento de erro 429
            try:
                st.session_state.pdf_data = gerar_relatorio_pdf(st.session_state.respostas_acumuladas)
            except Exception:
                pdf = FPDF(); pdf.add_page(); pdf.cell(0,10, "Relatório Técnico Offline", ln=True)
                st.session_state.pdf_data = pdf.output(dest='S')
            st.session_state.relatorio_gerado = True

if __name__ == "__main__":
    main()