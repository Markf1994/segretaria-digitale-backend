import pandas as pd
from typing import Any, Dict, List
from fastapi import HTTPException
from pathlib import Path


def parse_file(path: str) -> List[Dict[str, Any]]:
    """Return rows with ``azienda`` and ``descrizione`` from ``path``.

    The file may be an Excel workbook or a CSV document. Only the
    ``azienda`` and ``descrizione`` columns are considered. Extra columns
    are ignored.
    """
    if Path(path).suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
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


# ``parse_excel`` is kept for backward compatibility
parse_excel = parse_file
