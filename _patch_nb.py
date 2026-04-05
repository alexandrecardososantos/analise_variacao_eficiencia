# -*- coding: utf-8 -*-
import json

path = r"c:\Users\Alexandre\Desktop\Estudo\analise_clientes.ipynb"
with open(path, encoding="utf-8") as f:
    nb = json.load(f)

c14 = nb["cells"][14]
s14 = "".join(c14["source"])
if "def resumo_univariado_executivo" not in s14:
    add = """

# --- Resumo executivo (poucas linhas na tela) ---
K_MULTIV_MIN = 2
K_MULTIV_MAX = 5          # até qual k mostrar no resumo multivariado
TOP_COMBOS_POR_K = 2      # melhores combinações por valor de k


def resumo_univariado_executivo(df, cat_list, mes_base, mes_comp):
    \"\"\"Uma linha por variável: pior categoria e se a decomposição marginal puxa mais mix ou taxa.\"\"\"
    linhas = []
    for col in cat_list:
        res = decompor_variacao(df, col, mes_base, mes_comp)
        smix = res["efeito_mix (pp)"].sum()
        stax = res["efeito_taxa (pp)"].sum()
        pior_idx = res["efeito_total (pp)"].idxmin()
        pior = float(res["efeito_total (pp)"].min())
        if abs(smix) >= abs(stax):
            leitura = "História principal: mudança de mix (composição)"
        else:
            leitura = "História principal: mudança de eficiência (taxa interna)"
        if smix * stax < 0 and abs(smix) > 0.5 and abs(stax) > 0.5:
            leitura += " — mix e taxa em sentidos opostos"
        linhas.append(
            {
                "variável": col,
                "mix Σ (pp)": round(smix, 2),
                "taxa Σ (pp)": round(stax, 2),
                "pior categoria": str(pior_idx),
                "pior linha (pp)": round(pior, 2),
                "leitura": leitura,
            }
        )
    return pd.DataFrame(linhas).sort_values("pior linha (pp)")


def resumo_multivariado_enxuto(df, mes_base, mes_comp, df_rank, k_min, k_max, top_por_k):
    \"\"\"Poucas linhas por k: combinações com queda mais concentrada no pior segmento.\"\"\"
    linhas = []
    k_max = min(k_max, int(df_rank["k"].max()))
    for k in range(k_min, k_max + 1):
        sub = df_rank[df_rank["k"] == k]
        if sub.empty:
            continue
        sub = sub.sort_values("pior_segmento (pp)")
        for _, row in sub.head(top_por_k).iterrows():
            cols = row["variáveis"].split(" × ")
            res = decompor_variacao(df, cols, mes_base, mes_comp)
            pior_idx = res["efeito_total (pp)"].idxmin()
            ln = res.loc[pior_idx]
            em, et = float(ln["efeito_mix (pp)"]), float(ln["efeito_taxa (pp)"])
            if abs(em) >= abs(et):
                dica = "no pior segmento: pesa mais mix"
            else:
                dica = "no pior segmento: pesa mais taxa"
            linhas.append(
                {
                    "k": k,
                    "combinação": row["variáveis"],
                    "pior segmento": str(pior_idx),
                    "pior (pp)": round(float(row["pior_segmento (pp)"]), 2),
                    "mix seg. (pp)": round(em, 2),
                    "taxa seg. (pp)": round(et, 2),
                    "dica": dica,
                }
            )
    return pd.DataFrame(linhas)
"""
    if isinstance(c14["source"], list) and c14["source"]:
        c14["source"][-1] = c14["source"][-1].rstrip("\n") + add
    else:
        c14["source"] = [s14 + add]

nb["cells"][13]["source"] = [
    "### Decomposição da Queda no perc_indicador (Shift-Share)\n",
    "\n",
    "- **efeito_mix**: mudança na **composição** do público (peso de cada categoria).\n",
    "- **efeito_taxa**: mudança na **eficiência** dentro da categoria (`qtd_indicador` / `qtd`).\n",
    "\n",
    "A célula seguinte define as funções; a próxima mostra um **resumo executivo**: "
    "tabela **univariada** (uma linha por variável) e tabela **multivariada enxuta** "
    "(poucas combinações por tamanho k). O ranking completo pode ser salvo em CSV sem exibir mil linhas.\n",
]

cell15 = """# ── Delta global ──
agg_total = (
    df[df['ano_mes'].isin([MES_BASE, MES_COMP])]
    .groupby('ano_mes')
    .agg(qtd=('qtd', 'sum'), qtd_indicador=('qtd_indicador', 'sum'))
)
perc_b = agg_total.loc[MES_BASE, 'qtd_indicador'] / agg_total.loc[MES_BASE, 'qtd'] * 100
perc_c = agg_total.loc[MES_COMP, 'qtd_indicador'] / agg_total.loc[MES_COMP, 'qtd'] * 100
delta_pp = perc_c - perc_b

print(f'perc_indicador {MES_BASE}: {perc_b:.1f}%  →  {MES_COMP}: {perc_c:.1f}%  |  Δ = {delta_pp:+.1f} pp')
print('=' * 72)

# Avalia todas as combinações (usa cat_analise e MAX_TAMANHO_COMBO da célula anterior)
df_rank = varrer_todas_combinacoes(
    df, cat_analise, MES_BASE, MES_COMP, max_r=MAX_TAMANHO_COMBO
)

# Gravar ranking completo opcional (não exibe na tela)
SALVAR_RANKING_COMPLETO = None  # ex.: 'ranking_combinacoes.csv'
if SALVAR_RANKING_COMPLETO:
    df_rank.to_csv(SALVAR_RANKING_COMPLETO, index=False)

# ── 1) UNIVARIADO: todas as variáveis, uma linha cada ──
df_uni = resumo_univariado_executivo(df, cat_analise, MES_BASE, MES_COMP)
print('\\n### UNIVARIADO — todas as variáveis em cat_analise')
display(
    df_uni.style
    .set_caption('Ordenado pela pior categoria. «leitura»: mix vs eficiência no agregado da variável.')
)

print('\\n--- Conclusão rápida (univariado) ---')
r0 = df_uni.iloc[0]
print(
    f"• Maior queda concentrada numa categoria: **{r0['variável']}** → "
    f"{r0['pior categoria']} ({r0['pior linha (pp)']:.1f} pp). {r0['leitura']}"
)

# ── 2) MULTIVARIADO ENXUTO: poucas linhas por k ──
k_hi = min(K_MULTIV_MAX, len(cat_analise))
df_multi = resumo_multivariado_enxuto(
    df, MES_BASE, MES_COMP, df_rank,
    k_min=K_MULTIV_MIN, k_max=k_hi, top_por_k=TOP_COMBOS_POR_K,
)
print(
    f'\\n### MULTIVARIADO — até {TOP_COMBOS_POR_K} combinações por k '
    f'(k = {K_MULTIV_MIN} … {k_hi})'
)
display(
    df_multi.style
    .set_caption('Cruzamentos com queda mais forte no pior segmento; «dica» = só nesse segmento.')
)

print(
    '\\n*Ranking completo:*',
    len(df_rank),
    'linhas — não exibidas. Use SALVAR_RANKING_COMPLETO ou filtre df_rank no notebook.'
)
"""

nb["cells"][15]["source"] = [cell15]

cell16 = """# Detalhe opcional: tabela completa só dos segmentos explicativos
EXPANDIR_TABELAS = False   # True para ver decomposição linha a linha
N_EXPANDIR = 3             # quantas linhas do resumo multivariado abrir

if EXPANDIR_TABELAS:
    fmt_pct = lambda r: {c: '{:.1f}%' for c in r.columns if c.startswith(('mix_', 'taxa_'))}
    fmt_pp = lambda r: {c: '{:+.2f}' for c in r.columns if '(pp)' in c}
    for _, row in df_multi.head(N_EXPANDIR).iterrows():
        cols = row['combinação'].split(' × ')
        res_full = decompor_variacao(df, cols, MES_BASE, MES_COMP)
        exp = apenas_segmentos_explicativos(res_full)
        print(f"\\n--- {row['combinação']} (explicativos: {len(exp)}/{len(res_full)}) ---")
        display(
            exp.style
            .format({**fmt_pct(exp), **fmt_pp(exp)})
            .background_gradient(cmap='RdYlGn', subset=['efeito_total (pp)'], axis=0)
        )
else:
    print('Defina EXPANDIR_TABELAS = True acima para ver até N_EXPANDIR decomposições completas.')
"""

nb["cells"][16]["source"] = [cell16]

for idx in (15, 16):
    nb["cells"][idx]["outputs"] = []
    nb["cells"][idx]["execution_count"] = None

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print("OK")
