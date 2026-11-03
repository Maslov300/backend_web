"""Единая точка запуска, общее меню и обработчики ошибок."""

from datetime import datetime
from html import escape
from pathlib import Path

from flask import Flask, render_template_string, request, url_for
from lab1.app import bp as lab1_bp
from lab2.routes import bp as lab2_bp
from lab3.routes import bp as lab3_bp

app = Flask(__name__)
app.register_blueprint(lab1_bp)
app.register_blueprint(lab2_bp)
app.register_blueprint(lab3_bp)

LOG_FILE = Path(__file__).resolve().parent / "access.log"


@app.before_request
def save_visit():
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    ip = (request.remote_addr or "неизвестно").replace("\t", " ").replace("\n", " ")
    path = request.full_path.rstrip("?").replace("\t", " ").replace("\n", " ")
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(f"{timestamp}\t{ip}\t{request.method}\t{path}\n")


def read_visits():
    if not LOG_FILE.exists():
        return []
    visits = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t", 3)
        if len(parts) == 4:
            visits.append(parts)
    return visits


@app.route("/")
@app.route("/index")
def index():
    return render_template_string("""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>НГТУ, ФБ, Лабораторные работы</title></head>
<body>
  <h1>НГТУ, ФБ, WEB-программирование, часть 2</h1>
  <h2>Список лабораторных работ</h2>
  <ol>
    <li><a href="{{ url_for('lab1.lab1_index') }}">Лабораторная №1 — Введение во Flask</a></li>
    <li><a href="{{ url_for('lab2.lab2_index') }}">Лабораторная №2 — Шаблоны во Flask</a></li>
    <li><a href="{{ url_for('lab3.lab3_index') }}">Лабораторная №3 — Формы (GET), cookie</a></li>
  </ol>
  <footer>© Маврин Матвей Евгеньевич, ФБИ-44, 3 курс, 2026</footer>
</body></html>""")


@app.errorhandler(404)
def not_found(error):
    rows = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in visit) + "</tr>"
        for visit in read_visits()
    )
    return render_template_string("""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>Ошибка 404</title>
<link rel="stylesheet" href="{{ url_for('static', filename='lab1/lab1.css') }}"></head>
<body class="error-page">
<main class="error-card">
  <img class="error-picture" src="{{ url_for('static', filename='lab1/not-found.svg') }}" alt="Страница не найдена">
  <h1>404 — кажется, мы не туда свернули!</h1>
  <p>Такого адреса на сайте нет.</p>
  <p>Ваш IP-адрес: <strong>{{ ip }}</strong></p>
  <p>Дата и время обращения: <strong>{{ date }}</strong></p>
  <a href="{{ url_for('index') }}">Вернуться на главную</a>
</main>
<section class="journal"><h2>Журнал обращений</h2>
<div class="journal-scroll"><table><thead><tr><th>Дата</th><th>IP</th><th>Метод</th><th>Путь</th></tr></thead>
<tbody>{{ rows | safe }}</tbody></table></div></section>
</body></html>""", ip=request.remote_addr or "неизвестно",
            date=datetime.now().strftime("%d.%m.%Y %H:%M:%S"), rows=rows), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template_string("""<!doctype html><html lang="ru">
<head><meta charset="utf-8"><title>Ошибка 500</title></head>
<body><h1>500 — внутренняя ошибка сервера</h1>
<p>При обработке запроса возникла ошибка.</p>
<a href="{{ url_for('index') }}">Вернуться на главную</a></body></html>"""), 500


if __name__ == "__main__":
    app.run(debug=True)
