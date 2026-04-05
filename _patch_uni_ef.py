# -*- coding: utf-8 -*-
import json
import re

path = r"c:\Users\Alexandre\Desktop\Estudo\analise_clientes.ipynb"
with open(path, encoding="utf-8") as f:
    nb = json.load(f)

# Replace resumo_univariado block + insert tabela_univariada before resumo_multivariado
old = r'''def resumo_univariado_executivo(df, cat_list, mes_base, mes_comp):
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

new = r'''def tabela_univariada_efeito_total(df, cat_list, mes_base, mes_comp):
    """Uma linha por (variável × categoria): efeito_total e % do delta global."""
    delta_ref = _delta_perc_global(df, mes_base, mes_comp)
    linhas = []
    for col in cat_list:
        res = decompor_variacao(df, col, mes_base, mes_comp)
        for cat, row in res.iterrows():
            et = float(row["efeito_total (pp)"])
            pct = (100.0 * et / delta_ref) if abs(delta_ref) > 1e-9 else 0.0
            linhas.append(
                {
                    "variável": col,
                    "categoria": str(cat),
                    "efeito_total (pp)": round(et, 2),
                    "% do Δ global": round(pct, 1),
                }
            )
    return pd.DataFrame(linhas)


def resumo_univariado_executivo(df, cat_list, mes_base, mes_comp):
    """Uma linha por variável: pior categoria, efeito_total dessa categoria e % do Δ global."""
    delta_ref = _delta_perc_global(df, mes_base, mes_comp)
    linhas = []
    for col in cat_list:
        res = decompor_variacao(df, col, mes_base, mes_comp)
        smix = res["efeito_mix (pp)"].sum()
        stax = res["efeito_taxa (pp)"].sum()
        pior_idx = res["efeito_total (pp)"].idxmin()
        pior = float(res["efeito_total (pp)"].min())
        if abs(delta_ref) > 1e-9:
            pct_pior = 100.0 * pior / delta_ref
        else:
            pct_pior = 0.0
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
                "efeito_total pior (pp)": round(pior, 2),
                "% do Δ global (pior)": round(pct_pior, 1),
                "leitura": leitura,
            }
        )
    return pd.DataFrame(linhas).sort_values("efeito_total pior (pp)")'''

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if old in src:
        cell["source"] = [src.replace(old, new)]
        print("Patched functions")
        break
else:
    raise SystemExit("old block not found")

old_disp = """print('\\n### UNIVARIADO — todas as variáveis em cat_analise')
print(
    'Colunas %: participação no Δ líquido global (mix Σ e taxa Σ somam ~100%). '
    '«% do Δ — pior categ.»: quanto da queda total está na categoria mais negativa dessa variável.'
)
display(
    df_uni.style
    .set_caption(
        'Ordenado pela pior categoria. % do Δ = fração do Δ global (~37 pp); mix+taxa = 100% em cada linha.'
    )
)"""

new_disp = """print('\\n### UNIVARIADO — resumo (1 linha por variável)')
print(
    '«% do Δ global (pior)» = 100 × (efeito_total da pior categoria) / Δ global. '
    'Ex.: cat3_2 = -39 significa que a pior categoria de cat3_2 explica ~39% da queda total.'
)
display(
    df_uni.style
    .set_caption('Ordenado pelo efeito_total mais negativo (pior categoria).')
)

df_uni_det = tabela_univariada_efeito_total(df, cat_analise, MES_BASE, MES_COMP)
print('\\n### UNIVARIADO — todas as categorias (efeito_total e % do Δ global)')
display(
    df_uni_det.sort_values(['variável', 'efeito_total (pp)'])
    .style
    .set_caption(
        'Cada linha = uma categoria; efeito_total soma ao Δ global dentro de cada variável. '
        '% do Δ global = 100 × efeito_total / Δ (~-37 pp).'
    )
)"""

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if old_disp in src:
        cell["source"] = [src.replace(old_disp, new_disp)]
        print("Patched display block")
        break
else:
    raise SystemExit("display block not found")

# Fix conclusion line if it references old column
old_conc = '''r0 = df_uni.iloc[0]
print(
    f"• Maior queda concentrada numa categoria: **{r0['variável']}** → "
    f"{r0['pior categoria']} ({r0['pior linha (pp)']:.1f} pp). {r0['leitura']}"
)'''

new_conc = '''r0 = df_uni.iloc[0]
print(
    f"• Maior queda concentrada numa categoria: **{r0['variável']}** → "
    f"{r0['pior categoria']} ({r0['efeito_total pior (pp)']:.1f} pp, "
    f"{r0['% do Δ global (pior)']:.1f}% do Δ). {r0['leitura']}"
)'''

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if old_conc in src:
        cell["source"] = [src.replace(old_conc, new_conc)]
        print("Patched conclusion")
        break

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print("OK")
