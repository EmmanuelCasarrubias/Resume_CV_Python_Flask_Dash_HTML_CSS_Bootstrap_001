from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
db = SQLAlchemy(app)

# Modelo para la tabla Celda
class Celda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.String(80), nullable=False)

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
    limite_alcanzado = False
    if Celda.query.count() < 8:
        valor = request.form['valor']
        texto = request.form['texto']
        
        # Buscar la primera celda vacía y actualizarla con los nuevos valores
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
        limite_alcanzado = True
        flash('Límite de celdas alcanzado. No se pueden añadir más celdas.')

    return redirect(url_for('cv'))

@app.route('/eliminar_celda/<int:celda_id>', methods=['POST'])
def eliminar_celda(celda_id):
    celda_a_eliminar = Celda.query.get(celda_id)
    if celda_a_eliminar:
        db.session.delete(celda_a_eliminar)
        db.session.commit()
        flash('Celda eliminada con éxito')

        # Verificar si quedan celdas en la base de datos
        if Celda.query.count() == 0:
            inicializar_celdas_vacias(1)  # Si no quedan celdas, inicializar una vacía
        
    else:
        flash('Celda no encontrada')

    return redirect(url_for('cv'))

@app.route('/generar_qr')
def generar_qr():
    data = "Datos que quieres en el QR - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_filename = 'qr-{}.png'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
    qr_path = os.path.join('static', qr_filename)
    img.save(qr_path)

    return url_for('static', filename=qr_filename)

# Punto de inicio del tiempo cuando se lanza la aplicación
inicio_tiempo = time.time()

# Inicializar Dash en tu aplicación Flask
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')






# Definir el layout de Dash
dash_app.layout = html.Div([
    # Componente de gráfica
    dcc.Graph(id='senal-senoidal'),
    # Componente de intervalo para actualización en tiempo real
    dcc.Interval(
        id='interval-component',
        interval=100,  # en milisegundos
        n_intervals=0
    ),
    # Agregar una descripción debajo de la gráfica
    html.Div([
        html.P("Descripción de la Gráfica: Esta gráfica muestra una señal senoidal con ruido",
               style={'fontSize': '18px'})
    ], style={'textAlign': 'center', 'marginTop': '20px'})  # Ajusta el estilo según necesites
])

@dash_app.callback(
    Output('senal-senoidal', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    tiempo = np.linspace(0, 10, 100)

    # Cambia el desplazamiento para mover la gráfica hacia la izquierda
    desplazamiento = n * 0.5  # Ajusta este valor para controlar la velocidad del desplazamiento

    # Generar señal senoidal
    amplitud = np.sin(tiempo + desplazamiento)

    # Generar ruido estocástico y sumarlo a la amplitud
    ruido = np.random.normal(0, 0.2, tiempo.shape)  # Media 0, desviación estándar 0.2
    amplitud_con_ruido = amplitud + ruido
    figura = {
            'data': [{'x': tiempo, 'y': amplitud_con_ruido, 'type': 'line', 'name': 'Señal Senoidal con Ruido'}],
            'layout': {
                'title': 'Señal Senoidal en Tiempo Real con Ruido Estocástico',
                'xaxis': {
                    'showline': False,  # Ocultar la línea del eje X
                    'zeroline': False  # Opcional: también oculta la línea en x=0 si es necesario
                },
                'yaxis': {
                    'showline': False,  # Ocultar la línea del eje Y
                    'zeroline': False  # Ocultar la línea en y=0
                }
            }
        }
    return figura




if __name__ == '__main__':
    app.run(debug=True)

