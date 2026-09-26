# Predição de demanda no BentoML

treino:
    uv run python treino.py

serve:
    uv run bentoml serve service:PreditorDemanda --reload --port 3000

curl-exemplo:
    curl -sS -X POST http://127.0.0.1:3000/prever \
      -H 'Content-Type: application/json' \
      -d '{"produto_id":"p01"}' | python3 -m json.tool

curl-hipotetico:
    # produto novo: só técnica + região (sem id no catálogo)
    curl -sS -X POST http://127.0.0.1:3000/prever \
      -H 'Content-Type: application/json' \
      -d '{"tecnica":"ceramica","regiao":"Tracunhaém"}' | python3 -m json.tool
