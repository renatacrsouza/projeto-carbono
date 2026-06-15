#!/usr/bin/env python3
"""Questionário interativo de identificação de projeto de créditos de carbono."""

from pathlib import Path

OUTPUT_FILE = Path(__file__).parent / "resposta_cliente.txt"


def perguntar(texto: str, opcoes: list[str], multipla: bool = False) -> str:
    """Exibe uma pergunta e retorna a resposta escolhida pelo usuário."""
    print(f"\n{texto}")
    for i, opcao in enumerate(opcoes, start=1):
        print(f"  {i}. {opcao}")

    if multipla:
        print("\n  Digite os números separados por vírgula (ex: 1,3,4)")
        while True:
            entrada = input("Sua resposta: ").strip()
            try:
                indices = [int(x.strip()) for x in entrada.split(",") if x.strip()]
            except ValueError:
                print("Entrada inválida. Use apenas números separados por vírgula.")
                continue
            if not indices or any(i < 1 or i > len(opcoes) for i in indices):
                print(f"Escolha números entre 1 e {len(opcoes)}.")
                continue
            escolhidas = [opcoes[i - 1] for i in sorted(set(indices))]
            return ", ".join(escolhidas)

    while True:
        entrada = input("Sua resposta: ").strip()
        try:
            indice = int(entrada)
        except ValueError:
            print("Entrada inválida. Digite o número da opção.")
            continue
        if 1 <= indice <= len(opcoes):
            return opcoes[indice - 1]
        print(f"Escolha um número entre 1 e {len(opcoes)}.")


def main() -> None:
    respostas: dict[str, str] = {}

    print("=" * 60)
    print("  QUESTIONÁRIO DE PROJETO — CRÉDITOS DE CARBONO")
    print("=" * 60)
    print("\nResponda digitando o número da opção desejada.")

    # BLOCO 1 — IDENTIFICAÇÃO DO PROJETO
    print("\n" + "─" * 60)
    print("BLOCO 1 — IDENTIFICAÇÃO DO PROJETO")
    print("─" * 60)

    respostas["1. Tipo principal do projeto"] = perguntar(
        "1. Qual é o tipo principal do projeto?",
        ["Florestal", "Agropecuário", "Energia", "Indústria", "Resíduos", "Outro"],
    )

    respostas["2. Bioma / região"] = perguntar(
        "2. Em qual bioma / região está localizado?",
        [
            "Amazônia",
            "Cerrado",
            "Mata Atlântica",
            "Pantanal",
            "Caatinga",
            "Pampa / Sul",
            "Outro",
        ],
    )

    respostas["3. Área total envolvida"] = perguntar(
        "3. Qual é a área total envolvida?",
        ["Menos de 50 ha", "50 a 500 ha", "500 a 5.000 ha", "Mais de 5.000 ha"],
    )

    # BLOCO 2 — SITUAÇÃO ATUAL DO PROJETO
    print("\n" + "─" * 60)
    print("BLOCO 2 — SITUAÇÃO ATUAL DO PROJETO")
    print("─" * 60)

    respostas["4. Estágio atual"] = perguntar(
        "4. Qual é o estágio atual?",
        [
            "Só tenho a ideia",
            "Estou estruturando",
            "Projeto já implementado",
            "Em monitoramento",
            "Já passou por auditoria",
        ],
    )

    respostas["5. Documentação fundiária"] = perguntar(
        "5. Existe documentação fundiária regularizada?",
        ["Sim, escritura e CAR", "Parcialmente", "Não", "Não sei"],
    )

    respostas["6. Dados históricos"] = perguntar(
        "6. Há dados históricos de uso do solo ou emissões?",
        [
            "Sim, mais de 10 anos",
            "Sim, 5 a 10 anos",
            "Sim, menos de 5 anos",
            "Não",
        ],
    )

    respostas["7. Certificação ambiental ou social"] = perguntar(
        "7. Já existe alguma certificação ambiental ou social no projeto?",
        ["ISO 14001", "FSC", "Rainforest Alliance", "Nenhuma", "Outra"],
    )

    # BLOCO 3 — POTENCIAL DE GERAÇÃO
    print("\n" + "─" * 60)
    print("BLOCO 3 — POTENCIAL DE GERAÇÃO")
    print("─" * 60)

    respostas["8. Atividade principal"] = perguntar(
        "8. Qual é a atividade principal que gerará créditos?",
        [
            "Evitar desmatamento (REDD+)",
            "Reflorestamento / restauração",
            "Plantio direto / recuperação solo",
            "Biodigestor / biogás",
            "Energia solar / eólica",
            "Eficiência energética",
            "Outro",
        ],
    )

    respostas["9. Estimativa de tCO₂e/ano"] = perguntar(
        "9. Há uma estimativa de toneladas de CO₂ eq. por ano?",
        [
            "Menos de 1.000 tCO₂e/ano",
            "1.000 a 10.000 tCO₂e/ano",
            "10.000 a 100.000 tCO₂e/ano",
            "Mais de 100.000 tCO₂e/ano",
            "Não sei estimar",
        ],
    )

    respostas["10. Benefícios socioambientais"] = perguntar(
        "10. O projeto gera benefícios socioambientais além do carbono? (múltipla escolha)",
        [
            "Biodiversidade",
            "Recursos hídricos",
            "Comunidades locais",
            "Geração de emprego",
            "Nenhum mapeado",
        ],
        multipla=True,
    )

    # BLOCO 4 — CERTIFICAÇÃO E MERCADO
    print("\n" + "─" * 60)
    print("BLOCO 4 — CERTIFICAÇÃO E MERCADO")
    print("─" * 60)

    respostas["11. Contato com certificadora"] = perguntar(
        "11. Já teve contato com alguma certificadora?",
        ["Verra (VCS)", "Gold Standard", "RENOVABIO", "SBCE (brasileiro)", "Nenhuma ainda"],
    )

    respostas["12. Objetivo principal com os créditos"] = perguntar(
        "12. Qual é o objetivo principal com os créditos?",
        [
            "Vender no mercado voluntário",
            "Cumprir obrigação legal (compliance)",
            "Reporte ESG / neutralização",
            "Ainda não definido",
        ],
    )

    respostas["13. Acesso a capital para certificação"] = perguntar(
        "13. Tem acesso a capital para custear a certificação?",
        [
            "Sim",
            "Parcialmente, preciso de financiamento",
            "Não no momento",
        ],
    )

    # BLOCO 5 — CAPACIDADE DE EXECUÇÃO
    print("\n" + "─" * 60)
    print("BLOCO 5 — CAPACIDADE DE EXECUÇÃO")
    print("─" * 60)

    respostas["14. Equipe técnica"] = perguntar(
        "14. Há equipe técnica para conduzir o projeto?",
        ["Sim, equipe interna", "Sim, via consultoria", "Não ainda"],
    )

    respostas["15. Prazo para submissão"] = perguntar(
        "15. Em quanto tempo espera estar pronto para submissão?",
        ["Menos de 6 meses", "6 a 12 meses", "1 a 2 anos", "Não sei"],
    )

    # BLOCO 6 — RISCOS E BARREIRAS
    print("\n" + "─" * 60)
    print("BLOCO 6 — RISCOS E BARREIRAS")
    print("─" * 60)

    respostas["16. Conflitos fundiários"] = perguntar(
        "16. Existem conflitos fundiários ou disputas sobre a área?",
        ["Não", "Há pendências em resolução", "Sim"],
    )

    respostas["17. Passivos ambientais"] = perguntar(
        "17. Há passivos ambientais conhecidos na área?",
        ["Não", "Há área de passivo, mas em recuperação", "Sim, não endereçados"],
    )

    respostas["18. Permanência por 20–30 anos"] = perguntar(
        "18. O projeto pode garantir permanência por 20–30 anos?",
        ["Sim, com segurança", "Provavelmente sim", "Incerto", "Não"],
    )

    # Salvar respostas
    linhas = [
        "RESPOSTAS DO QUESTIONÁRIO — PROJETO DE CRÉDITOS DE CARBONO",
        "=" * 60,
        "",
    ]

    blocos = {
        "BLOCO 1 — IDENTIFICAÇÃO DO PROJETO": list(respostas.keys())[:3],
        "BLOCO 2 — SITUAÇÃO ATUAL DO PROJETO": list(respostas.keys())[3:7],
        "BLOCO 3 — POTENCIAL DE GERAÇÃO": list(respostas.keys())[7:10],
        "BLOCO 4 — CERTIFICAÇÃO E MERCADO": list(respostas.keys())[10:13],
        "BLOCO 5 — CAPACIDADE DE EXECUÇÃO": list(respostas.keys())[13:15],
        "BLOCO 6 — RISCOS E BARREIRAS": list(respostas.keys())[15:],
    }

    for bloco, chaves in blocos.items():
        linhas.append(bloco)
        linhas.append("-" * 60)
        for chave in chaves:
            linhas.append(f"{chave}: {respostas[chave]}")
        linhas.append("")

    OUTPUT_FILE.write_text("\n".join(linhas), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Questionário concluído! Respostas salvas em: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
