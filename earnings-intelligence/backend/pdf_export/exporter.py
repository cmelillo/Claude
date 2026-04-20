import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__))


def generate_pdf(report_data: dict) -> bytes:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report_template.html")
    html_content = template.render(**report_data)
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
