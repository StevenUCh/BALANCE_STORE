from flask import Flask, render_template, request, send_file
import pandas as pd
from weasyprint import HTML, CSS
from report_logic import procesar_datos
import os
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    # Cargar archivos
    ventas = pd.read_excel(request.files['ventas'])
    inventario = pd.read_excel(request.files['inventario'])

    # Capturar fechas
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Procesar datos
    resultados = procesar_datos(ventas, inventario)
    resultados['fecha_inicio'] = fecha_inicio
    resultados['fecha_fin'] = fecha_fin

    # Generar HTML
    html_content = render_template('report_v3.html', **resultados)

    # Configurar CSS para márgenes y tamaño de página
    css = CSS(string="""
        @page {
            size: Letter;
            margin-top: 10mm;
            margin-right: 10mm;
            margin-bottom: 10mm;
            margin-left: 10mm;
        }
        body {
            font-family: Arial, sans-serif;
            encoding: UTF-8;
        }
    """)

    # Generar PDF en memoria
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file, stylesheets=[css])
    pdf_file.seek(0)

    return send_file(pdf_file, download_name=f"Reporte_{fecha_inicio}_{fecha_fin}.pdf", as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5716))
    app.run(host="0.0.0.0", port=port, debug=True)
