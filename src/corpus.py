"""Corpus SINTÉTICO e fictício (política interna de uma empresa inventada, 'Orbita').
Cada trecho tem doc + página, para as respostas poderem citar fonte/página.
Nenhum dado real."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Passage:
    pid: str
    doc: str
    page: int
    text: str


PASSAGES = [
    Passage("p01", "politica-ferias.pdf", 1, "Todo colaborador da Orbita tem direito a 30 dias corridos de ferias por ano, apos 12 meses de trabalho."),
    Passage("p02", "politica-ferias.pdf", 2, "As ferias podem ser divididas em ate tres periodos, sendo que um deles deve ter no minimo 14 dias corridos."),
    Passage("p03", "politica-ferias.pdf", 3, "O pedido de ferias deve ser feito no portal de RH com antecedencia minima de 45 dias."),
    Passage("p04", "reembolso-viagens.pdf", 1, "Despesas de viagem a trabalho sao reembolsadas em ate 10 dias uteis apos o envio da prestacao de contas."),
    Passage("p05", "reembolso-viagens.pdf", 2, "O limite diario de alimentacao em viagens nacionais e de 120 reais por pessoa, com nota fiscal obrigatoria."),
    Passage("p06", "reembolso-viagens.pdf", 4, "Passagens aereas devem ser compradas com no minimo 15 dias de antecedencia, na classe economica."),
    Passage("p07", "seguranca-informacao.pdf", 1, "A senha corporativa deve ter no minimo 14 caracteres e ser trocada a cada 180 dias."),
    Passage("p08", "seguranca-informacao.pdf", 3, "E obrigatorio o uso de autenticacao em dois fatores para acessar a VPN e o e-mail corporativo."),
    Passage("p09", "seguranca-informacao.pdf", 5, "Incidentes de seguranca, como phishing ou perda de notebook, devem ser comunicados ao time de seguranca em ate 2 horas."),
    Passage("p10", "home-office.pdf", 1, "O regime hibrido preve 3 dias presenciais por semana, definidos em acordo com o gestor da area."),
    Passage("p11", "home-office.pdf", 2, "A empresa concede auxilio home office de 150 reais mensais para despesas de internet e energia."),
    Passage("p12", "beneficios.pdf", 2, "O vale-refeicao e de 45 reais por dia util, creditado no primeiro dia de cada mes."),
    Passage("p13", "beneficios.pdf", 4, "O plano de saude inclui cobertura para dependentes, com coparticipacao de 20 por cento em consultas."),
    Passage("p14", "codigo-conduta.pdf", 2, "Presentes de fornecedores com valor acima de 100 reais devem ser recusados ou declarados ao comite de etica."),
    Passage("p15", "codigo-conduta.pdf", 6, "Conflitos de interesse devem ser informados por escrito ao gestor e ao comite de etica antes de qualquer decisao."),
]
