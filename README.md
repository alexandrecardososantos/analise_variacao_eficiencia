# 📊 Shift-Share Analysis — Decomposição de Indicadores de Ativação

> Ferramenta descritiva para explicar **por que** um indicador de proporção sobe ou cai ao longo do tempo, identificando as variáveis categóricas e combinações de segmentos mais responsáveis pela variação.

---

## 🎯 Problema

Em carteiras de contas ou clientes, é comum monitorar indicadores do tipo:

```
perc_indicador = ind_indicador / qtd
```

Quando esse indicador cai de um trimestre para outro, a pergunta natural é:

> **O que explica essa queda? Foi uma piora generalizada, ou algo específico em algum segmento?**

A dificuldade é que o indicador agregado é uma **média ponderada** — ele pode cair mesmo que nenhum segmento tenha piorado internamente, simplesmente porque a composição da carteira mudou. Separar esses dois efeitos é o coração desta análise.

---

## 🧠 Abordagem: Shift-Share Analysis

A decomposição de shift-share separa a variação do indicador em três componentes para cada categoria de cada variável:

| Componente | O que mede | Exemplo |
|---|---|---|
| **Efeito Taxa** | A taxa *dentro* da categoria mudou | PJ tinha 81% de ativação e caiu para 74% |
| **Efeito Mix** | O *peso* da categoria na carteira mudou | PJ continua com 81%, mas sua fatia caiu de 40% para 20% |
| **Efeito Interação** | Resíduo quando taxa e mix mudam simultaneamente | Geralmente pequeno; pode ser incorporado ao efeito taxa |

```
efeito_taxa  = Δtaxa_k  × peso_k_base
efeito_mix   = taxa_k_base × Δpeso_k
efeito_inter = Δtaxa_k  × Δpeso_k
efeito_total = efeito_taxa + efeito_mix + efeito_inter
```

O **efeito total** de uma categoria representa, em pontos percentuais, quanto aquela categoria contribuiu para a variação do indicador agregado naquele período. Se `efeito_total(PJ) = -0.03`, então o segmento PJ sozinho é responsável por -3 p.p. da queda.

---

## 📐 Poder Explicativo

Para priorizar quais variáveis investigar, calculamos o **poder explicativo** de cada uma:

```
poder(variável) = Σ_trimestres  Σ_categorias  |efeito_total|
```

Isso acumula a magnitude de impacto ao longo de todos os pares de período analisados. Quanto maior o valor, mais aquela variável "movimenta" o indicador — para cima ou para baixo.

> ⚠️ O poder explicativo é uma medida **descritiva de magnitude**, não um coeficiente estatístico. Não deve ser interpretado como causalidade ou R².

---

## 🔍 Combinações de Variáveis (NxN)

Além da análise individual, o script suporta cruzamento de múltiplas variáveis para revelar **segmentos compostos** que não aparecem em análises univariadas.

```
Exemplo: "MEI × parceiro × safra_recente" pode ter uma queda expressiva
que não seria detectada olhando segmento, canal e safra separadamente.
```

O número de combinações cresce rapidamente:

| Pool de variáveis | Ordem 2 | Ordem 3 | Ordem 4 |
|:-----------------:|:-------:|:-------:|:-------:|
| 5 | 10 | 10 | 5 |
| 7 | 21 | 35 | 35 |
| 10 | 45 | 120 | 210 |

Recomenda-se começar com `POOL_VARS = 5` e `ORDEM_COMBO = [2, 3]`.

---

## 🗂️ Estrutura dos Dados Esperada

| Coluna | Tipo | Descrição |
|---|---|---|
| `trimestre` | string | Período de referência (ex: `2024Q1`) |
| `qtd` | int | Total de contas no período |
| `ind_indicador` | int | Total de contas ativas no período |
| `var_1` ... `var_10` | string | Variáveis categóricas de segmentação |

O indicador `perc_indicador = ind_indicador / qtd` é calculado internamente — não precisa existir na tabela de entrada.

---

## ⚙️ Configuração

No topo do script, ajuste os parâmetros conforme sua necessidade:

```python
VARIÁVEIS_CAT = ["segmento", "canal", "produto", ...]  # suas variáveis

TOP_N       = 8    # top categorias exibidas por variável
TOP_COMBOS  = 15   # top combinações exibidas por ordem

ORDEM_COMBO = [2, 3]  # ordens de combinação a calcular: 2x2, 3x3, etc.
POOL_VARS   = 5       # quantas variáveis (do ranking) entram no pool de combos
```

---

## 🚀 Como Usar

```bash
pip install pandas numpy
```

```python
# Substitua o bloco de dados sintéticos pelo seu DataFrame:
df = pd.read_csv("sua_base.csv")

# Garanta as colunas: trimestre, qtd, ind_indicador + variáveis categóricas
# Atualize VARIÁVEIS_CAT com os nomes reais das suas colunas
# Execute o script
python shift_share_analysis.py
```

---

## 📤 Outputs

O script imprime na saída padrão:

1. **Visão geral** — `perc_indicador` e `delta_perc` por trimestre
2. **Shift-share individual** — efeito taxa, mix e total por categoria de cada variável
3. **Ranking de variáveis** — ordenado por poder explicativo acumulado
4. **Ranking de combinações** — por cada ordem configurada em `ORDEM_COMBO`
5. **Drill-down** — top 5 segmentos compostos da melhor combinação, par a par de trimestre

---

## 📦 Dependências

```
pandas >= 1.5
numpy  >= 1.23
```

---

## 📝 Observações

- A análise é **totalmente descritiva** — não utiliza modelos estatísticos, testes de hipótese ou machine learning.
- Os dados permanecem locais; nenhuma informação é enviada a serviços externos.
- O script foi desenvolvido com dados sintéticos para fins de demonstração. Substitua pelo seu DataFrame real conforme indicado no código.
