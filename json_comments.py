def LTE_bands_0xB825(code_arr : list[str], entry:dict):
    code = ""
    for line in code_arr:
        code += line + "\n"
    lte_bands = {}
    exec(code, entry, lte_bands)
    print("lte_bands", lte_bands)

    # lte_bands_str = entry["lte_bands"].strip()
    # lte_bands = [int(band) for band in lte_bands_str.split(",") if int(band.strip()) != 0]
    return lte_bands

def cell_PCC(code_arr: list[str], entry):
    if int(entry["Cell index"]) == 0:
        entry['__cell'] = 'PCC'
    elif int(entry["Cell index"]) >= 1:
        entry['__cell'] = f'SCC{entry["Cell index"]}'
    return entry

