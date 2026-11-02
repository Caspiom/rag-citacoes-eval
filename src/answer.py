"""Resposta com citação. Geração EXTRATIVA: a resposta é montada só com frases
dos trechos recuperados, cada uma marcada [doc.pdf, p.N]. Garantia estrutural:
toda citação aponta para um trecho que existe e contém o texto citado.
(Um LLM real entra depois no lugar de `answer`, mantendo o mesmo contrato e o
mesmo verificador de citações.)

Abstenção (calibrada com dados, ver README): o sistema recusa quando NENHUM termo
da pergunta aparece no melhor trecho recuperado (cobertura = 0 e bm25 = 0).
Regra conservadora: 0 recusas indevidas nas perguntas respondíveis do eval, ao
custo de deixar passar perguntas fora do domínio que casam por acaso com algum
termo (limitação conhecida e medida)."""
from __future__ import annotations
import re
from dataclasses import dataclass

from .retrieval import HybridIndex, tok

# Cita o 2º trecho só se o score dele for >= esta fração do 1º (evita citação "de enfeite").
SEGUNDA_CITACAO_RATIO = 0.80


@dataclass
class Answer:
    text: str
    citations: list[dict]  # [{"doc","page","pid","quote"}]
    abstained: bool = False


def _sentences(t: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]


def _should_abstain(index: HybridIndex, question: str, top_text: str) -> bool:
    q = set(tok(question))
    if not q:
        return True
    cobertura = len(q & set(tok(top_text))) / len(q)
    return cobertura == 0.0 and max(index.bm25(question)) == 0.0


def answer(index: HybridIndex, question: str, k: int = 2) -> Answer:
    hits = index.search(question, k=k)
    if not hits or _should_abstain(index, question, hits[0][0].text):
        return Answer("Nao encontrei essa informacao nos documentos disponiveis.", [], abstained=True)
    keep = [hits[0]]
    if len(hits) > 1 and hits[1][1] >= SEGUNDA_CITACAO_RATIO * hits[0][1]:
        keep.append(hits[1])
    parts, cits = [], []
    for p, _ in keep:
        sent = max(_sentences(p.text), key=lambda s: len(set(tok(s)) & set(tok(question))))
        parts.append(f"{sent} [{p.doc}, p.{p.page}]")
        cits.append({"doc": p.doc, "page": p.page, "pid": p.pid, "quote": sent})
    return Answer(" ".join(parts), cits)


def citations_valid(index: HybridIndex, ans: Answer) -> bool:
    """Verificador: cada citação existe no corpus E o trecho citado está no texto da página."""
    by_key = {(p.doc, p.page): p for p in index.passages}
    for c in ans.citations:
        p = by_key.get((c["doc"], c["page"]))
        if p is None or c["quote"] not in p.text:
            return False
    return True
