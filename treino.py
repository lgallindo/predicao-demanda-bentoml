"""Treina regressão que prevê demanda (pedidos) a partir de atributos do produto."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import bentoml
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DADOS = Path(__file__).resolve().parent / "dados" / "catalogo.json"
ARTEFATO = "model.pkl"
MODELO = "predicao-demanda"


def main() -> None:
    catalogo = json.loads(DADOS.read_text(encoding="utf-8"))
    produtos = catalogo["produtos"]
    ids = [p["id"] for p in produtos]
    tecnicas = [p["tecnica"] for p in produtos]
    regioes = [p["regiao"] for p in produtos]
    y = np.array([float(p["pedidos"]) for p in produtos], dtype=float)

    # X tabular: só atributos categóricos (técnica, região) → OneHot no Pipeline
    X = np.column_stack([tecnicas, regioes])
    pipe = Pipeline(
        steps=[
            (
                "prep",
                ColumnTransformer(
                    transformers=[
                        (
                            "cat",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            [0, 1],
                        ),
                    ]
                ),
            ),
            ("reg", Ridge(alpha=1.0)),
        ]
    )
    pipe.fit(X, y)
    y_hat = pipe.predict(X)
    mae = float(mean_absolute_error(y, y_hat))
    rmse = float(mean_squared_error(y, y_hat) ** 0.5)
    r2 = float(r2_score(y, y_hat))

    artefato = {
        "pipeline": pipe,
        "produtos": {p["id"]: p for p in produtos},
        "ids": ids,
        "mae_treino": mae,
        "rmse_treino": rmse,
        "r2_treino": r2,
        "estrategia": "ridge_tecnica_regiao",
        "alvo": "pedidos",
    }

    with bentoml.models.create(
        MODELO,
        labels={"aula": "predicao-demanda-bentoml", "tarefa": "regressao"},
        metadata={
            "n_produtos": len(produtos),
            "mae_treino": mae,
            "rmse_treino": rmse,
            "r2_treino": r2,
            "estrategia": artefato["estrategia"],
        },
    ) as model:
        Path(model.path_of(ARTEFATO)).write_bytes(pickle.dumps(artefato))
        tag = model.tag

    print(f"produtos     {len(produtos)}")
    print(f"mae_treino   {mae:.3f}")
    print(f"rmse_treino  {rmse:.3f}")
    print(f"r2_treino    {r2:.3f}")
    print(f"tag store    {tag}")


if __name__ == "__main__":
    main()
