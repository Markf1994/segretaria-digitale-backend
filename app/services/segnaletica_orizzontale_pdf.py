from typing import Tuple
from sqlalchemy.orm import Session
from weasyprint import HTML
import tempfile
import html
import os
from fastapi import HTTPException

from app.models.segnaletica_orizzontale import SegnaleticaOrizzontale


def build_segnaletica_orizzontale_pdf(db: Session, year: int) -> Tuple[str, str]:
    """Create a PDF "piano" for horizontal signage entries of ``year``."""

    rows = (
        db.query(SegnaleticaOrizzontale.azienda, SegnaleticaOrizzontale.descrizione)
        .filter(SegnaleticaOrizzontale.anno == year)
        .order_by(SegnaleticaOrizzontale.descrizione)
        .all()
    )

    descrizioni = [r.descrizione for r in rows]
    aziende = {r.azienda for r in rows}
    azienda = aziende.pop() if len(aziende) == 1 else ""

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

    rows_html = "".join(f"<tr><td>{html.escape(d)}</td></tr>" for d in descrizioni)
    azienda_html = (
        f"<h2 style='text-align:center;'>Azienda incaricata: {html.escape(azienda)}</h2>"
        if azienda
        else ""
    )

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
    {azienda_html}
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
