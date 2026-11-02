from src.answer import Answer, answer, citations_valid
from src.retrieval import HybridIndex, tok

I = HybridIndex()


def test_resposta_cita_doc_e_pagina_corretos():
    a = answer(I, "Quantos dias de ferias o colaborador tem por ano?")
    assert not a.abstained
    assert a.citations[0]["doc"] == "politica-ferias.pdf" and a.citations[0]["page"] == 1
    assert "[politica-ferias.pdf, p.1]" in a.text


def test_toda_citacao_e_valida_no_corpus():
    for q in ("dias de ferias", "reembolso de viagem", "senha corporativa", "vale-refeicao"):
        assert citations_valid(I, answer(I, q))


def test_verificador_pega_citacao_falsa_pagina_inexistente():
    a = Answer("x", [{"doc": "politica-ferias.pdf", "page": 99, "pid": "p01", "quote": "qualquer"}])
    assert citations_valid(I, a) is False


def test_verificador_pega_citacao_com_trecho_que_nao_esta_na_pagina():
    a = Answer("x", [{"doc": "politica-ferias.pdf", "page": 1, "pid": "p01", "quote": "frase inventada que nao existe"}])
    assert citations_valid(I, a) is False


def test_abstem_quando_pergunta_fora_do_dominio():
    a = answer(I, "Qual o procedimento para pedir demissao?")
    assert a.abstained and a.citations == []


def test_nao_se_abstem_em_pergunta_parafraseada_dificil():
    # q05 do eval: nenhuma palavra em comum além de 'dia' — não pode ser recusada.
    assert not answer(I, "Qual o teto de gasto com comida por dia quando viajo no Brasil?").abstained


def test_bm25_acha_match_exato_de_termo_raro():
    top = I.search("coparticipacao dependentes", k=1, mode="bm25")[0][0]
    assert top.pid == "p13"


def test_denso_acha_por_subpalavra_sem_match_exato():
    # 'reembolsadas' no texto vs 'reembolso' na pergunta: BM25 exato falha, n-gramas pegam.
    top = I.search("reembolso", k=1, mode="dense")[0][0]
    assert top.doc == "reembolso-viagens.pdf"


def test_busca_e_deterministica():
    a = [p.pid for p, _ in HybridIndex().search("ferias antecedencia", k=3)]
    b = [p.pid for p, _ in HybridIndex().search("ferias antecedencia", k=3)]
    assert a == b


def test_tokenizacao_ignora_acento_e_stopwords():
    assert tok("Férias do Colaborador") == ["ferias", "colaborador"]
