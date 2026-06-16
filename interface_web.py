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
    {"titulo": "Identificação", "subtitulo": "01 · IDENTIFICAÇÃO", "icone": "🌿", "perguntas": [
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
    {"titulo": "Mapeamento", "subtitulo": "10 · MAPEAMENTO GEOGRÁFICO", "icone": "📍", "perguntas": []}
]

# ── 3. FUNÇÕES DE ESTILO E RENDERIZAÇÃO ──────────────────────────────────────
def aplicar_estilo():
    st.markdown("""<style>
        .main-header { background: #FFFFFF; padding: 1.8rem; border-radius: 24px; border: 1px solid #E5E5EA; margin-bottom: 1.5rem; }
        .stVerticalBlock[style*="border"] { border-radius: 20px !important; background-color: #FFFFFF !important; padding: 1.8rem !important; }
    </style>""", unsafe_allow_html=True)

def renderizar_pergunta(p, b_idx, p_idx, seq):
    key = f"b{b_idx}_q{p_idx}"
    valor = st.session_state.respostas_acumuladas.get(p["chave"], None)
    st.markdown(f"##### {p['texto']}")
    return st.radio("Opções:", p["opcoes"], index=p["opcoes"].index(valor) if valor in p["opcoes"] else None, key=f"{key}_radio", label_visibility="collapsed")

# ── 4. FUNÇÃO PRINCIPAL ──────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Carbon Diagnosis", layout="wide")
    aplicar_estilo()
    
    if "respostas_acumuladas" not in st.session_state: st.session_state.respostas_acumuladas = {}
    if "bloco_atual_index" not in st.session_state: st.session_state.bloco_atual_index = 0
    if "latitude_mapa" not in st.session_state: st.session_state.latitude_mapa = -23.2641
    if "longitude_mapa" not in st.session_state: st.session_state.longitude_mapa = -47.2992

    st.markdown('<div class="main-header"><h1>🌱 Diagnóstico de Projetos de Carbono</h1></div>', unsafe_allow_html=True)

    # Lógica de Jornada
    jornada = st.radio("Jornada:", ["✨ Estruturar do zero", "🔍 Validar ativo"], horizontal=True)
    blocos_ativos = [BLOCOS[0], BLOCOS[2], BLOCOS[3], BLOCOS[4], BLOCOS[5], BLOCOS[6], BLOCOS[7], BLOCOS[8], BLOCOS[9], BLOCOS[1]] if "Estruturar" in jornada else [BLOCOS[0], BLOCOS[2], BLOCOS[6], BLOCOS[7], BLOCOS[8], BLOCOS[9], BLOCOS[1]]

    # Barra de Progresso
    prog = len(st.session_state.respostas_acumuladas) / sum(len(b["perguntas"]) for b in blocos_ativos if b["titulo"] != "Mapeamento")
    st.progress(min(prog, 1.0))

    # Blocos e Mapa
    bloco = blocos_ativos[st.session_state.bloco_atual_index]
    st.markdown(f"#### {bloco['subtitulo']}")
    
    with st.container(border=True):
        if bloco["titulo"] == "Mapeamento":
            c1, c2 = st.columns(2)
            st.session_state.latitude_mapa = c1.number_input("Lat", value=st.session_state.latitude_mapa, format="%.4f")
            st.session_state.longitude_mapa = c2.number_input("Lon", value=st.session_state.longitude_mapa, format="%.4f")
            st.map(pd.DataFrame({"lat": [st.session_state.latitude_mapa], "lon": [st.session_state.longitude_mapa]}))
        else:
            for idx, p in enumerate(bloco["perguntas"]):
                res = renderizar_pergunta(p, BLOCOS.index(bloco), idx, idx+1)
                if res: st.session_state.respostas_acumuladas[p["chave"]] = res

    # Navegação
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️ Anterior") and st.session_state.bloco_atual_index > 0:
        st.session_state.bloco_atual_index -= 1
        st.rerun()
    if c3.button("Próximo ➡️") and st.session_state.bloco_atual_index < len(blocos_ativos) - 1:
        st.session_state.bloco_atual_index += 1
        st.rerun()
    elif c3.button("🌿 Emitir Relatório"):
        try:
            st.session_state.pdf_data = gerar_relatorio_pdf(st.session_state.respostas_acumuladas)
            st.session_state.relatorio_gerado = True
        except Exception:
            st.error("Erro na IA. Relatório gerado localmente.")
    
    if st.session_state.get("relatorio_gerado"):
        exibir_relatorio(st.session_state.respostas_acumuladas, st.session_state.pdf_data)

if __name__ == "__main__":
    main()