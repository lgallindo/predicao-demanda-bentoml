"""Serve predição de demanda (pedidos previstos) via BentoML."""

from __future__ import annotations

import pickle
from pathlib import Path

import bentoml
import numpy as np

MODELO = "predicao-demanda:latest"
modelo = bentoml.models.get(MODELO)
ARTEFATO = "model.pkl"


@bentoml.service(resources={"cpu": "1"})
class PreditorDemanda:

    def __init__(self) -> None:
        caminho = Path(modelo.path_of(ARTEFATO))
        self.artefato = pickle.loads(caminho.read_bytes())

    @bentoml.api
    def prever(
        self,
        produto_id: str | None = None,
        tecnica: str | None = None,
        regiao: str | None = None,
    ) -> dict:
        """Prevê pedidos a partir do id do catálogo ou de (tecnica, regiao).

        Preferência: se `produto_id` existir no catálogo, usa os atributos dele.
        Caso contrário, exige `tecnica` e `regiao` (produto novo / hipotético).
        """
        produtos = self.artefato["produtos"]
        pipe = self.artefato["pipeline"]

        if produto_id:
            if produto_id not in produtos:
                return {
                    "erro": "produto_inexistente",
                    "produto_id": produto_id,
                }
            p = produtos[produto_id]
            tecnica = p["tecnica"]
            regiao = p["regiao"]
            pedidos_reais = float(p["pedidos"])
        else:
            if not tecnica or not regiao:
                return {
                    "erro": "informe_produto_id_ou_tecnica_e_regiao",
                    "produto_id": produto_id,
                }
            pedidos_reais = None

        x = np.array([[tecnica, regiao]], dtype=object)
        previsto = float(pipe.predict(x)[0])

        out: dict = {
            "pedidos_previstos": round(previsto, 2),
            "tecnica": tecnica,
            "regiao": regiao,
            "strategy": self.artefato["estrategia"],
            "mae_treino": round(self.artefato["mae_treino"], 3),
            "modelo": str(modelo.tag),
        }
        if produto_id:
            out["produto_id"] = produto_id
            out["nome"] = produtos[produto_id]["nome"]
            out["pedidos_reais"] = pedidos_reais
            out["erro_absoluto"] = round(abs(previsto - pedidos_reais), 2)
        return out
