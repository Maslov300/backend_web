from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime
from html import escape
from pathlib import Path

app = Flask(__name__)

STUDENT = "Маврин Матвей Евгеньевич"
GROUP = "ФБИ-44"
FACULTY = "ФБ"

# Журнал хранится локально. Не добавляйте его в git.
LOG_FILE = Path(__file__).resolve().parent.parent / "access.log"


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


@app.errorhandler(404)
def not_found(error):
    visits = read_visits()
    rows = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in visit) + "</tr>"
        for visit in visits
    )
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head>
      <meta charset="utf-8">
      <title>Ошибка 404 — страница не найдена</title>
      <link rel="stylesheet" href="{{ url_for('static', filename='lab1.css') }}">
    </head>
    <body class="error-page">
      <main class="error-card">
        <img class="error-picture" src="{{ url_for('static', filename='not-found.svg') }}" alt="Страница потерялась">
        <h1>404 — кажется, мы не туда свернули!</h1>
        <p>Такого адреса на сайте нет. Возможно, ссылка устарела.</p>
        <p>Ваш IP-адрес: <strong>{{ ip }}</strong></p>
        <p>Дата и время обращения: <strong>{{ date }}</strong></p>
        <a href="{{ url_for('index') }}">Вернуться на главную</a>
      </main>
      <section class="journal">
        <h2>Полный журнал обращений</h2>
        <div class="journal-scroll">
        <table>
          <thead><tr><th>Когда</th><th>Кто (IP)</th><th>Метод</th><th>Адрес</th></tr></thead>
          <tbody>{{ rows|safe }}</tbody>
        </table>
        </div>
      </section>
    </body>
    </html>""", ip=request.remote_addr or "неизвестно",
           date=datetime.now().strftime("%d.%m.%Y %H:%M:%S"), rows=rows), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>Ошибка 500</title></head>
    <body>
      <h1>500 — внутренняя ошибка сервера</h1>
      <p>При обработке запроса возникла ошибка. Попробуйте позже.</p>
      <a href="{{ url_for('index') }}">На главную страницу</a>
    </body>
    </html>"""), 500


@app.route("/")
@app.route("/index")
def index():
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>НГТУ, ФБ, Лабораторные работы</title></head>
    <body>
      <header><h1>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</h1></header>
      <main><nav><ul><li><a href="/lab1">Первая лабораторная</a></li><li><a href="/lab2/">Вторая лабораторная</a></li></ul></nav></main>
      <footer>
        <hr>
        <p>{{ student }}, {{ group }}. Курс: WEB-программирование, часть 2. 2026 год.</p>
      </footer>
    </body>
    </html>""", student=STUDENT, group=GROUP)


@app.route("/lab1/web")
def start():
    return """<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>WEB-сервер на Flask</title></head>
    <body><h1>web-сервер на flask</h1><a href="/lab1/author">Автор</a></body>
    </html>""", 200, {"X-Server": "sample", "Content-Type": "text/html; charset=utf-8"}


@app.route("/lab1/author")
def author():
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>Автор лабораторной</title></head>
    <body>
      <p>Студент: {{ student }}</p>
      <p>Группа: {{ group }}</p>
      <p>Факультет: {{ faculty }}</p>
      <a href="{{ url_for('start') }}">web</a>
    </body>
    </html>""", student=STUDENT, group=GROUP, faculty=FACULTY)


@app.route("/lab1/image")
def image():
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head>
      <meta charset="utf-8">
      <title>Изображение</title>
      <link rel="stylesheet" href="{{ url_for('static', filename='lab1.css') }}">
    </head>
    <body class="image-page">
      <main class="picture-card">
        <h1>Трактор</h1>
        <p>Пример подключения статического изображения и CSS во Flask.</p>
        <img class="tractor" src="{{ url_for('static', filename='traktor.svg') }}" alt="Трактор">
        <p><a href="{{ url_for('start') }}">Вернуться к WEB-серверу</a></p>
      </main>
    </body>
    </html>"""), 200, {
        "Content-Language": "ru-RU",
        "X-Student": "Mavrin-Matvey",
        "X-Laboratory": "Flask-Lab-1",
    }


count = 0


@app.route("/lab1/counter")
def counter():
    global count
    count += 1
    time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>Счётчик посещений</title></head>
    <body>
      <h1>Счётчик посещений</h1>
      <p>Количество посещений: {{ count }}</p>
      <p>Текущее время: {{ time }}</p>
      <p>Запрошенный адрес: {{ url }}</p>
      <p>Адрес клиента: {{ ip }}</p>
      <p><a href="{{ url_for('reset_counter') }}">Очистить счётчик</a></p>
    </body>
    </html>""", count=count, time=time, url=request.url, ip=request.remote_addr)


@app.route("/lab1/counter/reset")
def reset_counter():
    global count
    count = 0
    return render_template_string("""<!doctype html>
    <html lang="ru"><head><meta charset="utf-8"><title>Счётчик очищен</title></head>
    <body>
      <h1>Счётчик очищен</h1>
      <p>Теперь значение счётчика равно нулю.</p>
      <a href="{{ url_for('counter') }}">Вернуться к счётчику</a>
    </body></html>""")


@app.route("/lab1/info")
def info():
    return redirect(url_for("author"))


@app.route("/created")
def created():
    return """<!doctype html>
    <html lang="ru"><head><meta charset="utf-8"><title>Создано</title></head>
    <body><h1>Создано успешно</h1><div>Что-то создано</div></body></html>""", 201


FLASK_DESCRIPTION = (
    "Flask — фреймворк для создания веб-приложений на языке "
    "программирования Python, использующий набор инструментов Werkzeug, "
    "а также шаблонизатор Jinja2. Относится к категории так называемых "
    "микрофреймворков — минималистичных каркасов веб-приложений, "
    "сознательно предоставляющих лишь самые базовые возможности."
)


@app.route("/lab1")
def lab1():
    titles = {
        "/": "Главная страница",
        "/index": "Главная страница (index)",
        "/lab1": "Лабораторная работа 1",
        "/lab1/web": "WEB-сервер",
        "/lab1/author": "Автор",
        "/lab1/image": "Изображение",
        "/lab1/counter": "Счётчик",
        "/lab1/counter/reset": "Очистка счётчика",
        "/lab1/info": "Перенаправление",
        "/created": "Код ответа 201",
        "/lab1/raise-error": "Ошибка сервера (500)",
    }
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda rule: rule.rule):
        if rule.endpoint == "static" or rule.endpoint.startswith("lab2."):
            continue
        if rule.endpoint == "http_status":
            for code, (title, _) in HTTP_MESSAGES.items():
                routes.append((f"/lab1/status/{code}", f"HTTP {code} — {title}"))
            continue
        address = rule.rule
        label = titles.get(address, "Код ответа " + address.split("/")[-1])
        routes.append((address, label))
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>Лабораторная 1</title></head>
    <body>
      <h1>Лабораторная работа № 1 — Введение во Flask</h1>
      <p>{{ description }}</p>
      <a href="{{ url_for('index') }}">На главную страницу</a>
      <h2>Список роутов</h2>
      <ul>
        {% for address, label in routes %}
          <li><a href="{{ address }}">{{ label }} — {{ address }}</a></li>
        {% endfor %}
      </ul>
    </body>
    </html>""", description=FLASK_DESCRIPTION, routes=routes)


HTTP_MESSAGES = {
    400: ("Неверный запрос", "Сервер не смог обработать запрос из-за ошибки в его содержимом."),
    401: ("Не авторизован", "Для доступа к ресурсу требуется авторизация."),
    402: ("Требуется оплата", "Для доступа к ресурсу требуется оплата."),
    403: ("Доступ запрещён", "У пользователя нет прав на просмотр этого ресурса."),
    405: ("Метод не разрешён", "Указанный HTTP-метод не разрешён для ресурса."),
    418: ("Я чайник", "Я чайник, поэтому не могу заварить кофе."),
}


@app.route("/lab1/status/<int:code>")
def http_status(code):
    if code not in HTTP_MESSAGES:
        return "Неизвестный учебный код ответа", 404
    title, description = HTTP_MESSAGES[code]
    html = render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>HTTP {{ code }} — {{ title }}</title></head>
    <body>
      <h1>HTTP {{ code }} — {{ title }}</h1>
      <p>{{ description }}</p>
      <a href="{{ url_for('lab1') }}">К списку роутов</a>
    </body>
    </html>""", code=code, title=title, description=description)
    return html, code


@app.route("/lab1/raise-error")
def raise_error():
    result = 1 / 0  # Намеренно вызываем ошибку 500 для проверки обработчика.
    return str(result)


if __name__ == "__main__":
    # Для проверки собственной страницы 500 debug должен быть выключен.
    app.run(debug=False)
