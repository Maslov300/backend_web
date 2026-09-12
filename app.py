from flask import Flask, url_for

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
    return f"""<!doctype html >
    <html>
    <body>
    Сколько раз вы сюда заходили:{count}
    </body>
    </html>
    """

app.run(debug=True)