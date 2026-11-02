# PROGRESSO — rag-citacoes-eval

Último ponto onde parei (atualize ao fim de cada sessão de 1h):

- **Data:** 2026-11-02 (bloco de SEGUNDA 02/11 feito pelo Hermes a pedido do Lucas)
- **Onde parei:** RAG híbrido funcionando e medido — BM25 próprio + denso local (n-gramas) + RRF, resposta extrativa com citação doc/página, verificador de citações, abstenção calibrada. 18 perguntas com gabarito manual: hit@3 híbrido 0,933 (empata com o denso; MRR 0,867 < 0,933), citação válida 1,0, precisão de citação 0,58, abstenção 2/3. 10 testes passando, determinístico. Achados honestos no README (híbrido não ganhou; q16 alucina; q05 falha em todos os modos).
- **Próximo passo:** (1) plugar embedding neural real (barato, com teto de custo) e comparar contra o de n-gramas no mesmo eval; (2) corpus maior para testar a hipótese de que o híbrido passa a ganhar; (3) RAGAS de verdade com LLM gerador; (4) tentar fechar `q16` com um sinal melhor de abstenção.
