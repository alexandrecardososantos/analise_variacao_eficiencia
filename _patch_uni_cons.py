# -*- coding: utf-8 -*-
import json

path = r"c:\Users\Alexandre\Desktop\Estudo\analise_clientes.ipynb"
with open(path, encoding="utf-8") as f:
    nb = json.load(f)

needle = '    return pd.DataFrame(linhas)\n\n\ndef resumo_univariado_executivo'
insert = '''    return pd.DataFrame(linhas)


def consolidado_univariado_efeito_total_pp(df, cat_list, mes_base, mes_comp):
    """Reúne todas as linhas univariadas (todas as variáveis × categorias), ordenadas por efeito_total (pp)."""
    d = tabela_univariada_efeito_total(df, cat_list, mes_base, mes_comp)
    d = d.sort_values("efeito_total (pp)", ascending=True).reset_index(drop=True)
    d.insert(0, "rank", range(1, len(d) + 1))
    return d


def resumo_univariado_executivo'''

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if needle in src:
        cell["source"] = [src.replace(needle, insert)]
        print("Inserted consolidado_univariado_efeito_total_pp")
        break
else:
    raise SystemExit("needle not found for function insert")

old_block = """df_uni_det = tabela_univariada_efeito_total(df, cat_analise, MES_BASE, MES_COMP)
print('\\n### UNIVARIADO — todas as categorias (efeito_total e % do Δ global)')
display(
    df_uni_det.sort_values(['variável', 'efeito_total (pp)'])
    .style
    .set_caption(
        'Cada linha = uma categoria; efeito_total soma ao Δ global dentro de cada variável. '
        '% do Δ global = 100 × efeito_total / Δ (~-37 pp).'
    )
)"""

new_block = """df_uni_det = tabela_univariada_efeito_total(df, cat_analise, MES_BASE, MES_COMP)

# Visão única: todas as univariadas juntas, ordenada só por efeito_total (pp)
df_uni_consolidado = consolidado_univariado_efeito_total_pp(df, cat_analise, MES_BASE, MES_COMP)
print('\\n### UNIVARIADO — consolidado (todas as variáveis; efeito_total em p.p.)')
print(
    'Uma lista única: cada linha é uma categoria numa dimensão. '
    'Ordenação global por efeito_total (pp). Não some linhas de variáveis diferentes (é a mesma queda vista por vários ângulos).'
)
display(
    df_uni_consolidado.style
    .set_caption(
        'Todas as univariadas: rank por contribuição (efeito_total em pp).'
    )
)

print('\\n### UNIVARIADO — categorias agrupadas por variável')
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
    if old_block in src:
        cell["source"] = [src.replace(old_block, new_block)]
        print("Patched display block")
        break
else:
    raise SystemExit("display block not found")

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print("OK")
