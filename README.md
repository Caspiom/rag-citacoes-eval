# rag-citacoes-eval

> **Pilar do portfólio — Segunda** · parte de uma série de 7 projetos de Engenharia de Software de IA (1h/dia).

## O problema
Q&A sobre um corpus de documentos com **busca híbrida (BM25 + densa)**, respostas com **citação de fonte e página** e **avaliação medida** (recall, MRR, precisão/validade de citação, abstenção).

## O que tem (e o que NÃO tem ainda)
- **Tem:** BM25 próprio + embedding denso local (hashing de n-gramas de caracteres) fundidos por **RRF**; resposta **extrativa** com `[doc.pdf, p.N]`; **verificador de citações**; **abstenção** calibrada com dados; eval com gabarito escrito à mão; tudo **offline, grátis e determinístico** (sem chave, sem LLM).
- **Não tem (honestidade):** embedding neural, LLM gerador, RAGAS e pgvector/Chroma. A "densa" daqui é um embedding barato de subpalavras, **não** um modelo neural. O contrato (`dense_search`, `answer`) é o mesmo, então trocar é local. Corpus: 15 trechos sintéticos e fictícios de uma empresa inventada (sem dado real).

## Resultados medidos (18 perguntas: 15 respondíveis + 3 sem resposta)
| Retrieval | hit@3 | MRR |
|---|---|---|
| BM25 | 0,867 | 0,833 |
| Denso (n-gramas) | **0,933** | **0,933** |
| Híbrido (RRF) | **0,933** | 0,867 |

| Pipeline completo | Valor |
|---|---|
| Validade das citações (existem e contêm a frase citada) | **1,00** |
| Faithfulness (extrativa, verificada) | **1,00** |
| Precisão das citações (apontam p/ trecho correto) | **0,58** |
| Abstenção correta (perguntas sem resposta) | **0,67** (2 de 3) |
| Testes | **10 passando**; resultados idênticos com 3 `PYTHONHASHSEED` diferentes |

### Leitura honesta dos números
- **O híbrido não ganhou aqui.** Empata com o denso em hit@3 e perde em MRR (0,867 vs 0,933). Com só 15 trechos, o RRF dilui o sinal do denso quando o BM25 erra. O ganho do híbrido costuma aparecer em corpus maiores; **não afirmo isso como resultado**, só como hipótese a testar.
- **Onde erra:** `q05` (*"teto de gasto com comida... viajo no Brasil"* → trecho diz *"limite diario de alimentacao... viagens nacionais"*): paráfrase sem termo em comum, nenhum dos 3 modos acerta. O BM25 também erra `q14`.
- **Abstenção — limitação medida:** nenhum sinal isolado (score BM25, cosseno, cobertura de termos) separa respondíveis de sem-resposta (varri os limiares; `q16` *"licença maternidade"* casa por acaso com "ferias"). Regra adotada: abster só se **nenhum termo da pergunta** aparece no melhor trecho. Custo: **0 de 15 respostas boas recusadas**, mas `q16` passa (alucina). Subir o limiar pegaria `q16` ao custo de recusar 2–3 perguntas válidas.
- **Precisão de citação 0,58:** o 2º trecho citado nem sempre é o gold. Só cito o 2º quando o score dele é ≥ 80% do 1º (era 0,47 citando sempre 2).

## Dois bugs que o eval pegou no meu próprio código
1. `hash()` do Python para `str` muda a cada execução (`PYTHONHASHSEED`) → embedding e números **não reproduzíveis**. Trocado por `zlib.crc32`; verificado com 3 seeds.
2. Primeira abstenção (`min_score=0.012`, **chutado**) acertava **0 de 3**: os scores RRF ficam todos na mesma faixa. Calibrada medindo o trade-off acima.

## Validação por mutação
Quebrei o código de propósito: verificador ignorando o texto citado / sempre aprovando / abstenção desligada → **os 3 testes unitários pegam cada uma** (1–2 falhas). Nota: o **eval** só pega a abstenção desligada (0,67 → 0,0); as mutações do verificador passam no eval porque o pipeline extrativo nunca emite citação falsa. Quem protege o verificador são os testes que injetam citações forjadas.

## Como rodar (< 5 min)
```bash
make setup    # cria .venv e instala pytest
make all      # testes + eval (imprime a tabela acima)
python -m evals.run_eval --json   # métricas em JSON
```

## Estrutura
- `src/corpus.py` — trechos sintéticos (doc + página) · `src/retrieval.py` — BM25 + denso + RRF
- `src/answer.py` — resposta extrativa com citação, abstenção e verificador
- `evals/perguntas.jsonl` — gabarito manual · `evals/run_eval.py` — métricas · `tests/test_rag.py`

## Status
- [x] Esqueleto / setup roda em < 15 min
- [x] Núcleo funcional (BM25 + denso + RRF + citação + abstenção)
- [x] Avaliação / métricas medidas (hit@3, MRR, citações, abstenção, mutação)
- [x] README com números e limitações
- [ ] Embedding neural + LLM gerador (com teto de custo) e RAGAS de verdade
- [ ] Corpus maior/real para testar se o híbrido passa a ganhar
- [ ] FastAPI + pgvector/Chroma; deploy / demo

---
Autor: Gappy · Série montada com apoio do Hermes
