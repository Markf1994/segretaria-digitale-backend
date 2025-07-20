from typing import Tuple
from weasyprint import HTML
import tempfile
import html
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.segnaletica_orizzontale import SegnaleticaOrizzontale


def build_segnaletica_orizzontale_pdf(db: Session, year: int) -> Tuple[str, str]:
    """Generate a horizontal signage plan PDF for ``year``.

    The function fetches all ``SegnaleticaOrizzontale`` records for the given
    year from ``db``. If all records share the same ``azienda`` that value is
    displayed under the main header. Otherwise the header only contains the
    year. A single column table lists all descriptions.
    """
    styles = """
    <style>
    @page { size: A4; margin: 10mm; }
    body { font-family: Aptos, sans-serif; font-size: 10pt; }
    table { border-collapse: collapse; width: 100%; page-break-inside: avoid; }
    th, td { border: 1px solid #000; padding: 4px; text-align: left; }
    </style>
    """

    logo_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "static", "Logo.png")
    )
    if not os.path.exists(logo_path):
        raise HTTPException(status_code=500, detail="Logo file missing")

    rows = (
        db.query(SegnaleticaOrizzontale)
        .filter(SegnaleticaOrizzontale.anno == year)
        .order_by(SegnaleticaOrizzontale.descrizione)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No records found for year")

    aziende = {r.azienda for r in rows}
    header_azienda = aziende.pop() if len(aziende) == 1 else None

    rows_html = "".join(f"<tr><td>{html.escape(r.descrizione)}</td></tr>" for r in rows)

    html_content = f"""
    <html>
    <head>
    <meta charset='utf-8'>
    {styles}
    </head>
    <body>
    <div style='display:flex; align-items:center; margin-bottom:10px;'>
        <img src='{logo_path}' alt='logo' style='width:70px; margin-right:8px;' />
        <h1 style='text-align:center; flex-grow:1; margin:0;'>Piano Segnaletica Orizzontale Anno {year}</h1>
    </div>
    {f"<h2 style='text-align:center;'>{html.escape(header_azienda)}</h2>" if header_azienda else ""}
    <table>
    <tr><th>Lavori da eseguire</th></tr>
    {rows_html}
    </table>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
        tmp_html.write(html_content.encode("utf-8"))
        html_path = tmp_html.name

    pdf_path = html_path.replace(".html", ".pdf")
    HTML(filename=html_path).write_pdf(pdf_path)

    return pdf_path, html_path
