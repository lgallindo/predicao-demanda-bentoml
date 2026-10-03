# Contas trabalhadas — jarro de Tracunhaém

Usamos o catálogo em [`dados/catalogo.json`](../dados/catalogo.json). A loja
perguntou a demanda do **Jarro barro Tracunhaém** (id `p01`, técnica
*ceramica*, região *Tracunhaém*, **42** pedidos observados).

O modelo deste material: `OneHotEncoder` + `Ridge(alpha=1.0)`, como em
`treino.py`. Números abaixo saem desse ajuste; pequenas diferenças de
arredondamento são normais.

## Passo A — features e rótulo

```text
# Variáveis:
#   tecnica, regiao — strings do produto
#   y               — pedidos observados

tecnica ← "ceramica"
regiao  ← "Tracunhaém"
y       ← 42
```

## Passo B — one-hot do jarro

Categorias na ordem do treino (alfabética do scikit-learn):

- técnicas: `ceramica`, `cestaria`, `renda`, `xilogravura`
- regiões: `Alto do Moura`, `Comunidade do Pilar`, `Tracunhaém`

| ceramica | cestaria | renda | xilogravura | Alto do Moura | Pilar | Tracunhaém |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | 0 | 0 | 0 | 1 |

Só duas colunas “acesas”.

## Passo C — pesos da Ridge neste catálogo

Intercepto e coeficientes (arredondados) após `just treino`:

| Termo | Valor ≈ |
| --- | ---: |
| intercepto \(b\) | 21,938 |
| \(w\) tecnica_ceramica | +3,312 |
| \(w\) tecnica_cestaria | −4,139 |
| \(w\) tecnica_renda | +3,070 |
| \(w\) tecnica_xilogravura | −2,243 |
| \(w\) regiao_Alto do Moura | −3,365 |
| \(w\) regiao_Comunidade do Pilar | +0,053 |
| \(w\) regiao_Tracunhaém | +3,312 |

## Passo D — previsão do jarro


$$
\hat{y} = b + w_{\mathrm{ceramica}} + w_{\mathrm{Tracunhaém}}
$$


$$
\hat{y} \approx 21{,}938 + 3{,}312 + 3{,}312 = 28{,}56
$$

Erro absoluto nesta peça:


$$
\lvert 42 - 28{,}56\rvert \approx 13{,}44
$$

## Passo E — o grupo inteiro leva o mesmo \(\hat{y}\)

`p01`, `p02` e `p03` têm o mesmo par (ceramica, Tracunhaém):

| id | pedidos reais \(y\) | \(\hat{y}\) | \(\lvert y-\hat{y}\rvert\) |
| --- | ---: | ---: | ---: |
| p01 | 42 | 28,56 | 13,44 |
| p02 | 28 | 28,56 | 0,56 |
| p03 | 19 | 28,56 | 9,56 |

Média do grupo: \((42+28+19)/3 \approx 29{,}67\). A Ridge prevê **28,56** —
um pouco abaixo da média do grupo, puxada na direção da média global
(\(\approx 21{,}67\)). Esse é o efeito da regularização (`alpha=1`) com
catálogo pequeno.

## Passo F — métricas no catálogo inteiro

Com os doze \(\hat{y}_i\) do treino:

| Métrica | Valor ≈ | Leitura rápida |
| --- | ---: | --- |
| MAE | 7,43 | erro médio em pedidos |
| RMSE | 8,70 | penaliza erros grandes um pouco mais |
| R² | 0,29 | técnica + região explicam parte da variação |

```text
# Variáveis:
#   y_i, yhat_i — real e previsto do produto i
#   n           — 12
#   y_bar       — média de y
#   MAE, RMSE, R2

MAE  ← (1/n) * soma |y_i - yhat_i|
RMSE ← sqrt( (1/n) * soma (y_i - yhat_i)^2 )
R2   ← 1 - soma((y_i - yhat_i)^2) / soma((y_i - y_bar)^2)
```

## Passo G — o que a API devolve

```bash
just curl-exemplo
```

Corpo enviado: `{"produto_id":"p01"}`.

Campos a conferir:

| Campo | Valor esperado ≈ |
| --- | ---: |
| `pedidos_previstos` | 28,56 |
| `pedidos_reais` | 42 |
| `erro_absoluto` | 13,44 |
| `mae_treino` | 7,425 |

Produto hipotético (mesmo grupo, sem id):

```bash
just curl-hipotetico
```

`pedidos_previstos` ≈ 28,56 — a mesma previsão de grupo, agora para uma peça
que ainda não entrou no catálogo.
