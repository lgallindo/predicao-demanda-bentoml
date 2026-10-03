# Predição de demanda no BentoML
#
# Dois momentos:
#   1) treino  — offline: lê JSON, ajusta OHE+Ridge, grava no store
#   2) serve   — online: carrega o modelo, responde HTTP
#
# Empacote (opcional, só o pipeline online):
#   treino → build (Bento) → containerize (imagem OCI) → serve-container
#
# Imagem de aula (tag estável): predicao-demanda:aula
# Pare qualquer `just serve` na :3000 antes de `just serve-container`.

# ---------------------------------------------------------------------------
# Offline — treino
# ---------------------------------------------------------------------------

treino:
    # Lê dados/catalogo.json → OneHot + Ridge → store `predicao-demanda:…`
    uv run python treino.py

# ---------------------------------------------------------------------------
# Online — processo local (sem Docker)
# ---------------------------------------------------------------------------

serve:
    # Requer `just treino` ao menos uma vez. Deixe o terminal aberto.
    uv run bentoml serve service:PreditorDemanda --reload --port 3000

# ---------------------------------------------------------------------------
# Empacote — Bento → imagem OCI → container
# ---------------------------------------------------------------------------
# O que entra no pacote está em bentofile.yaml:
#   service + *.py + dados/*.json + deps + modelo predicao-demanda:latest
# O container carrega o artefato já treinado e só faz inferência.

build:
    # Congela o serviço num Bento (ainda não é imagem Docker).
    # Pré-requisito: `just treino` (senão falta predicao-demanda:latest).
    uv run bentoml build

containerize:
    # Transforma o Bento `PreditorDemanda:latest` numa imagem OCI.
    uv run bentoml containerize PreditorDemanda:latest --image-tag predicao-demanda:aula

imagem: build containerize

serve-container:
    # Sobe a imagem. Mesma API que `just serve` (porta 3000).
    docker run --rm -p 3000:3000 predicao-demanda:aula serve

listar-bentos:
    uv run bentoml list

listar-imagens:
    docker images predicao-demanda

# ---------------------------------------------------------------------------
# Exemplos HTTP (serve local OU serve-container na :3000)
# ---------------------------------------------------------------------------

curl-exemplo:
    # Jarro de barro (p01) — caso do material/calculos-trabalhados.md
    curl -sS -X POST http://127.0.0.1:3000/prever \
      -H 'Content-Type: application/json' \
      -d '{"produto_id":"p01"}' | python3 -m json.tool

curl-hipotetico:
    # Peça nova: só técnica + região (sem id no catálogo)
    curl -sS -X POST http://127.0.0.1:3000/prever \
      -H 'Content-Type: application/json' \
      -d '{"tecnica":"ceramica","regiao":"Tracunhaém"}' | python3 -m json.tool

curl-inexistente:
    curl -sS -X POST http://127.0.0.1:3000/prever \
      -H 'Content-Type: application/json' \
      -d '{"produto_id":"nao-existe"}' | python3 -m json.tool
