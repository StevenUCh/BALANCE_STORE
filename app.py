from flask import Flask, render_template, request, send_file
import pandas as pd
import pdfkit
from report_logic import procesar_datos
from datetime import datetime
import os
import sys
import signal

app = Flask(__name__)


if getattr(sys, 'frozen', False):
    wkhtml = os.path.join(sys._MEIPASS, "wkhtmltopdf", "bin", "wkhtmltopdf.exe")
else:
    wkhtml = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

config = pdfkit.configuration( wkhtmltopdf=wkhtml )

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

    # Agregar fechas al contexto
    resultados['fecha_inicio'] = fecha_inicio
    resultados['fecha_fin'] = fecha_fin

    # Generar HTML
    html = render_template('report_v3.html', **resultados)

    # Nombre del PDF con fechas
    pdf_filename = f"Reporte_{fecha_inicio}_{fecha_fin}.pdf"

    # Opciones de PDF
    options = {
        'page-size': 'Letter',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'encoding': "UTF-8",
        'enable-local-file-access': None
    }

    pdfkit.from_string(html, pdf_filename, configuration=config, options=options)

    return send_file(pdf_filename, as_attachment=True)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    # Leer PID del launcher
    with open("flask_pid.txt", "r") as f:
        pid = int(f.read())
    # Matar proceso Flask
    os.kill(pid, signal.SIGTERM)
    return "<h3>Servidor detenido. Puedes cerrar esta ventana.</h3>"

if __name__ == '__main__':
    app.run(debug=False, port=5716, host="127.0.0.1", use_reloader=False)
