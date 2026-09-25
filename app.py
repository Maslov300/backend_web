from flask import Flask, url_for, request, redirect
import datetime

app = Flask(__name__)
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

app.run(debug=True)