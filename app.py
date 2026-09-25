from flask import Flask, url_for, request, redirect
import datetime

app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "Страница не найдена", 404

@app.route("/")
@app.route("/web")
def start():
    return "<!doctype html>" \
            "<html>" \
            "<body> <h1>web-сервер на flask</h1> </body>" \
            "</html>"
@app.route("/author")
def author():
    name = "Маврин Матвей Евгеньевич"
    group = "ФБИ-44"
    faculcy = "ФБ"
    return f"""
    <!doctype html>
    <html>
    <body>
    <p>Студент {name}</p>
    <p>Группа {group}</p>
    <p>Факультет {faculcy}</p>
    <a href="/web">web</a>
    </body>
    </html>
    """
@app.route("/image")
def image():
    return '''
    <!doctype html>
    <html>
    <body>
    <h1>Трактор</h1>
    <img src="./static/traktor.jpeg">
    </body>
    </html>
    '''

count = 0
@app.route("/counter")
def counter():
    global count
    count += 1

    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return f"""<!doctype html >
    <html>
    <body>
    Сколько раз вы сюда заходили:{count}
    <hr>
    Сколько время: {time} <br>
    Запрошенный адрес: {url} <br>
    Адрес клиента: {client_ip}
    </body>
    </html>
    """

@app.route("/info")
def info():
    return redirect("/author")

@app.route("/created")
def created():
    return """<!doctype html >
    <html>
    <body>
    <h1>Создано успешно</h1>
    <div>Что-то создано</div>
    </body>
    </html>
    """, 201

app.run(debug=True)