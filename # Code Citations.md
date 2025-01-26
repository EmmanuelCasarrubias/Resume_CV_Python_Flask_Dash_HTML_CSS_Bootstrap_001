# Code Citations

## License: unknown
https://github.com/HishamSha3098/Invoice_PrintingAPP/tree/8adf253beefd3b45ba398b5e245abfc812cfd8a8/api/utils.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import qrcode
from datetime import datetime
import time
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import numpy as np

# Configuración de Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')

# Configuración de la base de datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo para la tabla Celda
class Celda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.String(80), nullable=False)

# Inicializar celdas vacías en la base de datos
def inicializar_celdas_vacias(n):
    if Celda.query.count() == 0:
        for _ in range(n):
            celda_vacia = Celda(valor=0, texto="")
            db.session.add(celda_vacia)
        db.session.commit()

@app.route('/')
def cv():
    celdas = Celda.query.all()
    return render_template('cv.html', celdas=celdas)

@app.route('/add_celda', methods=['POST'])
def add_celda():
    if Celda.query.count() < 8:
        try:
            valor = int(request.form['valor'])
            texto = str(request.form['texto'])
        except ValueError:
            flash('Valor debe ser un número entero y texto debe ser una cadena.')
            return redirect(url_for('cv'))
        
        celda_vacia = Celda.query.filter_by(valor=0, texto="").first()
        if celda_vacia:
            celda_vacia.valor = valor
            celda_vacia.texto = texto
            db.session.commit()
            flash('Celda actualizada con éxito')
        else:
            nueva_celda = Celda(valor=valor, texto=texto)
            db.session.add(nueva_celda)
            db.session.commit()
            flash('Celda añadida con éxito')
    else:
        flash('Límite de celdas alcanzado. No se pueden añadir más celdas.')

    return redirect(url_for('cv'))

@app.route('/eliminar_celda/<int:celda_id>', methods=['POST'])
def eliminar_celda(celda_id):
    celda_a_eliminar = Celda.query.get(celda_id)
    if celda_a_eliminar:
        db.session.delete(celda_a_eliminar)
        db.session.commit()
        flash('Celda eliminada con éxito')

        if Celda.query.count() == 0:
            inicializar_celdas_vacias(1)
    else:
        flash('Celda no encontrada')

    return redirect(url_for('cv'))

@app.route('/generar_qr')
def generar_qr():
    qr_data = "Datos QR - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Crear directorio si no existe
    pki_dir = os.path.join(basedir, 'static', 'pki')
    if not os.path.exists(pki_dir):
        os.makedirs(pki_dir)

    qr_filename = f'qr-{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
    qr_path = os.path.join(pki_dir, qr_filename)
    img.save(qr_path)

    return url_for('static', filename=f'pki/{qr_filename}')

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')
inicio_tiempo = time.time()

# Layout de Dash
dash_app.layout = html.Div([
    dcc.Graph(id='senal-senoidal'),
    dcc.Interval(id='interval-component', interval=100, n_intervals=0),
    html.Div([
        html.P("Descripción: Esta gráfica muestra una señal senoidal con ruido",
               style={'fontSize': '18px'})
    ], style={'textAlign': 'center', 'marginTop': '20px'})
])

# Cache the noise
cached_noise = np.random.normal(0, 0.2, 100)

@dash_app.callback(
    Output('senal-senoidal', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    tiempo = np.linspace(0, 10, 100)
    desplazamiento = n * 0.5
    amplitud = np.sin(tiempo + desplazamiento)
    ruido = cached_noise
    amplitud_con_ruido = amplitud + ruido

    figura = {
        'data': [{'x': tiempo, 'y': amplitud_con_ruido, 'type': 'line', 'name': 'Señal Senoidal con Ruido'}],
        'layout': {
            'title': 'Señal Senoidal en Tiempo Real con Ruido',
            'xaxis': {'showline': False, 'zeroline': False},
            'yaxis': {'showline': False, 'zeroline': False}
        }
    }
    return figura

with app.app_context():
    db.create_all()
    inicializar_celdas_vacias(5)

if __name__ == '__main__':
    app.run(debug=True)

