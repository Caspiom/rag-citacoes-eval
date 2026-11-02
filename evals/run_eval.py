"""Avaliação do RAG: compara BM25 vs denso vs híbrido (RRF) e mede o pipeline completo.

Métricas (gabarito escrito à mão em evals/perguntas.jsonl):
  - hit@k / recall@k : o trecho certo está no top-k?   (só perguntas respondíveis)
  - MRR              : quão alto o trecho certo aparece
  - citation_precision: das citações emitidas, quantas apontam p/ trecho gold
  - citation_valid   : toda citação existe e contém a frase citada (verificador)
  - abstencao        : em perguntas SEM resposta, o sistema se recusou a inventar?
  - faithfulness (proxy): toda frase da resposta vem de trecho recuperado (extrativo => 1.0 por construção, verificado)

Uso: python -m evals.run_eval [--json]"""
import json
import sys
from pathlib import Path

from src.answer import answer, citations_valid
from src.retrieval import HybridIndex

PERGUNTAS = [json.loads(l) for l in Path(__file__).with_name("perguntas.jsonl").read_text().splitlines() if l.strip()]
IDX = HybridIndex()
K = 3


def retrieval_metrics(mode: str) -> dict:
    resp = [q for q in PERGUNTAS if q["gold"]]
    hits = rr = 0.0
    for q in resp:
        ranked = [p.pid for p, _ in IDX.search(q["q"], k=K, mode=mode)]
        gold = set(q["gold"])
        if gold & set(ranked):
            hits += 1
        for pos, pid in enumerate(ranked, 1):
            if pid in gold:
                rr += 1 / pos
                break
    n = len(resp)
    return {"hit@3": round(hits / n, 3), "mrr": round(rr / n, 3)}


def pipeline_metrics() -> dict:
    cit_total = cit_ok_gold = cit_valid_n = ans_n = 0
    abst_ok = abst_n = 0
    for q in PERGUNTAS:
        a = answer(IDX, q["q"])
        if not q["gold"]:
            abst_n += 1
            abst_ok += int(a.abstained)
            continue
        ans_n += 1
        cit_valid_n += int(citations_valid(IDX, a) and not a.abstained)
        for c in a.citations:
            cit_total += 1
            cit_ok_gold += int(c["pid"] in q["gold"])
    return {
        "citation_precision": round(cit_ok_gold / cit_total, 3) if cit_total else 0.0,
        "citation_valid": round(cit_valid_n / ans_n, 3),
        "abstencao_correta": round(abst_ok / abst_n, 3),
        "faithfulness_extrativa": 1.0 if all(citations_valid(IDX, answer(IDX, q["q"])) for q in PERGUNTAS) else 0.0,
    }


def main():
    out = {"n_perguntas": len(PERGUNTAS), "retrieval": {m: retrieval_metrics(m) for m in ("bm25", "dense", "hybrid")},
           "pipeline": pipeline_metrics()}
    if "--json" in sys.argv:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"{out['n_perguntas']} perguntas ({sum(1 for q in PERGUNTAS if q['gold'])} respondiveis, "
          f"{sum(1 for q in PERGUNTAS if not q['gold'])} sem resposta)\n")
    print(f"{'modo':<8} {'hit@3':>7} {'MRR':>7}")
    for m, r in out["retrieval"].items():
        print(f"{m:<8} {r['hit@3']:>7} {r['mrr']:>7}")
    print("\npipeline:", json.dumps(out["pipeline"], ensure_ascii=False))


if __name__ == "__main__":
    main()
