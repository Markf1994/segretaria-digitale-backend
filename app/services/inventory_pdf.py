from typing import List, Dict, Any, Tuple
from weasyprint import HTML
import tempfile


def build_inventory_pdf(items: List[Dict[str, Any]], year: int) -> Tuple[str, str]:
    """Generate an inventory PDF for *year* from ``items``.

    Each item should be a mapping with ``name`` and ``count`` keys. The
    function returns a tuple ``(pdf_path, html_path)`` with the generated
    files.
    """

    rows_html = "".join(
        f"<tr><td>{item.get('name', '')}</td><td>{item.get('count', '')}</td></tr>"
        for item in items
    )

    html_content = f"""
    <html>
    <body>
    <h1>Inventario {year}</h1>
    <table border='1' style='border-collapse:collapse;'>
        <tr><th>Nome</th><th>Quantità</th></tr>
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
