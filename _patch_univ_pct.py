# -*- coding: utf-8 -*-
"""Patch notebook: participação % do delta no resumo univariado."""
import json

path = r"c:\Users\Alexandre\Desktop\Estudo\analise_clientes.ipynb"
with open(path, encoding="utf-8") as f:
    nb = json.load(f)

old_fn = '''def resumo_univariado_executivo(df, cat_list, mes_base, mes_comp):
    """Uma linha por variável: pior categoria e se a decomposição marginal puxa mais mix ou taxa."""
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
    return pd.DataFrame(linhas).sort_values("pior linha (pp)")'''

new_fn = '''def _delta_perc_global(df, mes_base, mes_comp):
    """Δ do perc_indicador entre os dois meses (pp), mesmo número usado no resumo."""
    agg = (
        df[df["ano_mes"].isin([mes_base, mes_comp])]
        .groupby("ano_mes")
        .agg(qtd=("qtd", "sum"), qtd_indicador=("qtd_indicador", "sum"))
    )
    pb = agg.loc[mes_base, "qtd_indicador"] / agg.loc[mes_base, "qtd"]
    pc = agg.loc[mes_comp, "qtd_indicador"] / agg.loc[mes_comp, "qtd"]
    return (pc - pb) * 100


def resumo_univariado_executivo(df, cat_list, mes_base, mes_comp):
    """Uma linha por variável: pior categoria, mix vs taxa, e % do Δ líquido global."""
    delta_ref = _delta_perc_global(df, mes_base, mes_comp)
    linhas = []
    for col in cat_list:
        res = decompor_variacao(df, col, mes_base, mes_comp)
        smix = res["efeito_mix (pp)"].sum()
        stax = res["efeito_taxa (pp)"].sum()
        pior_idx = res["efeito_total (pp)"].idxmin()
        pior = float(res["efeito_total (pp)"].min())
        if abs(delta_ref) > 1e-9:
            pct_mix = 100.0 * smix / delta_ref
            pct_taxa = 100.0 * stax / delta_ref
            pct_pior = 100.0 * pior / delta_ref
        else:
            pct_mix = pct_taxa = pct_pior = 0.0
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
                "% do Δ — mix": round(pct_mix, 1),
                "% do Δ — taxa": round(pct_taxa, 1),
                "% do Δ — pior categ.": round(pct_pior, 1),
                "pior categoria": str(pior_idx),
                "pior linha (pp)": round(pior, 2),
                "leitura": leitura,
            }
        )
    return pd.DataFrame(linhas).sort_values("pior linha (pp)")'''

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if old_fn in src:
        cell["source"] = [src.replace(old_fn, new_fn)]
        print("Patched: resumo_univariado_executivo")
        break
else:
    raise SystemExit("Function block not found")

# Patch display cell: add explanation after df_uni = ...
old_disp = '''print('\\n### UNIVARIADO — todas as variáveis em cat_analise')
display(
    df_uni.style
    .set_caption('Ordenado pela pior categoria. «leitura»: mix vs eficiência no agregado da variável.')
)'''

new_disp = '''print('\\n### UNIVARIADO — todas as variáveis em cat_analise')
print(
    'Colunas %: participação no Δ líquido global (mix Σ e taxa Σ somam ~100%). '
    '«% do Δ — pior categ.»: quanto da queda total está na categoria mais negativa dessa variável.'
)
display(
    df_uni.style
    .set_caption(
        'Ordenado pela pior categoria. % do Δ = fração do Δ global (~37 pp); mix+taxa = 100% em cada linha.'
    )
)'''

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if old_disp in src:
        cell["source"] = [src.replace(old_disp, new_disp)]
        print("Patched: display df_uni")
        break
else:
    raise SystemExit("Display block not found")

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print("OK")
