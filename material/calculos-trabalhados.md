# Contas trabalhadas — jarro de Tracunhaém

O estoquista abre a ficha do **Jarro barro Tracunhaém** (id `p01`). Técnica
*ceramica*, região *Tracunhaém*, **42** pedidos no período de exemplo. A pergunta
é: com o modelo deste repositório, **quantos pedidos a regra prevê** — e quão
longe isso fica do 42 observado?

Catálogo: [`dados/catalogo.json`](../dados/catalogo.json).  
Modelo: `OneHotEncoder` + `Ridge(alpha=1.0)`, como em `treino.py`.  
Números abaixo saem desse ajuste; diferenças de arredondamento na terceira casa
são normais.

## Passo A — features e rótulo

A loja separa o que o modelo **vê** do que ela quer **aproximar**:

```text
# Variáveis:
#   tecnica, regiao — strings do produto (features)
#   y               — pedidos observados (rótulo)

tecnica ← "ceramica"
regiao  ← "Tracunhaém"
y       ← 42
```

Motivação: se só existisse o id `p01`, uma peça nova sem id ficaria sem chute.
Técnica e região são atributos que uma peça nova **já tem** no briefing do
artesão.

## Passo B — one-hot do jarro

Categorias na ordem do treino (alfabética do scikit-learn):

- técnicas: `ceramica`, `cestaria`, `renda`, `xilogravura`
- regiões: `Alto do Moura`, `Comunidade do Pilar`, `Tracunhaém`

| ceramica | cestaria | renda | xilogravura | Alto do Moura | Pilar | Tracunhaém |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | 0 | 0 | 0 | 1 |

Só duas colunas “acesas”. Motivação: codificar cerâmica=1 e renda=2 inventaria
uma ordem falsa; o one-hot dá a cada valor o próprio interruptor 0/1.

## Passo C — pesos da Ridge neste catálogo

Depois de `just treino`, o regressor guarda um intercepto e um peso por coluna:

| Termo | Valor ≈ | Leitura informal |
| --- | ---: | --- |
| intercepto \(b\) | 21,938 | patamar perto da média global (~21,67) |
| \(w\) tecnica_ceramica | +3,312 | cerâmica puxa a previsão para cima |
| \(w\) tecnica_cestaria | −4,139 | cestaria puxa para baixo |
| \(w\) tecnica_renda | +3,070 | renda também puxa para cima |
| \(w\) tecnica_xilogravura | −2,243 | xilo puxa um pouco para baixo |
| \(w\) regiao_Alto do Moura | −3,365 | Alto do Moura puxa para baixo |
| \(w\) regiao_Comunidade do Pilar | +0,053 | Pilar quase neutro |
| \(w\) regiao_Tracunhaém | +3,312 | Tracunhaém puxa para cima |

A Ridge mantém esses pesos **moderados** (penalidade L2). Com só doze linhas,
isso evita que o ajuste cole demais em cada célula do catálogo.

## Passo D — previsão do jarro

Com as duas colunas acesas:


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

O jarro é o best-seller do grupo: o modelo vê “cerâmica em Tracunhaém”, e o 42
fica acima do chute de grupo — daí o erro grande *nesta* linha.

## Passo E — o grupo inteiro leva o mesmo \(\hat{y}\)

`p01`, `p02` e `p03` compartilham o par (ceramica, Tracunhaém):

| id | pedidos reais \(y\) | \(\hat{y}\) | \(\lvert y-\hat{y}\rvert\) |
| --- | ---: | ---: | ---: |
| p01 | 42 | 28,56 | 13,44 |
| p02 | 28 | 28,56 | 0,56 |
| p03 | 19 | 28,56 | 9,56 |

Média do grupo: \((42+28+19)/3 \approx 29{,}67\). A Ridge prevê **28,56** —
um pouco abaixo da média do grupo, puxada na direção da média global
(\(\approx 21{,}67\)). Esse é o efeito visível da regularização (`alpha=1`) com
catálogo pequeno: generalizar um pouco mais do que colar na média das três
linhas.

## Passo F — métricas no catálogo inteiro

Com os doze \(\hat{y}_i\) do treino:

| Métrica | Valor ≈ | O que responde ao estoque |
| --- | ---: | --- |
| MAE | 7,43 | erro médio em pedidos |
| RMSE | 8,70 | sensível a erros grandes (o jarro puxa) |
| R² | 0,29 | fração da variação de `pedidos` que técnica+região explicam |

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

Na raiz do repositório, com o serviço no ar:

```bash
just curl-exemplo
```

Corpo enviado: `{"produto_id":"p01"}`.

| Campo | Valor esperado ≈ |
| --- | ---: |
| `pedidos_previstos` | 28,56 |
| `pedidos_reais` | 42 |
| `erro_absoluto` | 13,44 |
| `mae_treino` | 7,425 |

Peça hipotética (mesmo grupo, sem id — o briefing do artesão antes do primeiro
pedido):

```bash
just curl-hipotetico
```

`pedidos_previstos` ≈ 28,56 — a mesma previsão de grupo, agora para uma linha
que o catálogo ainda vai ganhar. É o momento em que a regra passa de “olhar o
passado do id” para **generalizar** a partir de técnica e região.
