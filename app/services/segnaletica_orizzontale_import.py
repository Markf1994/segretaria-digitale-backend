import pandas as pd
from typing import Any, Dict, List
from fastapi import HTTPException


def parse_excel(path: str) -> List[Dict[str, Any]]:
    df = pd.read_excel(path)
    lower_cols = {c.lower(): c for c in df.columns}
    required = {"azienda", "descrizione"}
    missing = required - set(lower_cols.keys())
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    azienda_col = lower_cols["azienda"]
    descr_col = lower_cols["descrizione"]

    rows: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        azienda = row.get(azienda_col)
        descr = row.get(descr_col)
        if pd.isna(azienda) or str(azienda).strip() == "":
            raise HTTPException(status_code=400, detail=f"Row {idx+2}: Missing azienda")
        if pd.isna(descr) or str(descr).strip() == "":
            raise HTTPException(status_code=400, detail=f"Row {idx+2}: Missing descrizione")
        rows.append(
            {
                "azienda": str(azienda).strip(),
                "descrizione": str(descr).strip(),
            }
        )
    return rows
