"""Обработчики первой лабораторной работы (Flask Blueprint)."""

from datetime import datetime
from flask import Blueprint, current_app, redirect, render_template_string, request, url_for

bp = Blueprint("lab1", __name__)
STUDENT = "Маврин Матвей Евгеньевич"
GROUP = "ФБИ-44"
FACULTY = "ФБ"


@bp.route("/lab1/web")
def start():
    return """<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>WEB-сервер на Flask</title></head>
    <body><h1>web-сервер на flask</h1><a href="/lab1/author">Автор</a></body>
    </html>""", 200, {"X-Server": "sample", "Content-Type": "text/html; charset=utf-8"}


@bp.route("/lab1/author")
def author():
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head><meta charset="utf-8"><title>Автор лабораторной</title></head>
    <body>
      <p>Студент: {{ student }}</p>
      <p>Группа: {{ group }}</p>
      <p>Факультет: {{ faculty }}</p>
      <a href="{{ url_for('lab1.start') }}">web</a>
    </body>
    </html>""", student=STUDENT, group=GROUP, faculty=FACULTY)


@bp.route("/lab1/image")
def image():
    return render_template_string("""<!doctype html>
    <html lang="ru">
    <head>
      <meta charset="utf-8">
      <title>Изображение</title>
      <link rel="stylesheet" href="{{ url_for('static', filename='lab1/lab1.css') }}">
    </head>
    <body class="image-page">
      <main class="picture-card">
        <h1>Трактор</h1>
        <p>Пример подключения статического изображения и CSS во Flask.</p>
        <img class="tractor" src="{{ url_for('static', filename='lab1/traktor.svg') }}" alt="Трактор">
        <p><a href="{{ url_for('lab1.start') }}">Вернуться к WEB-серверу</a></p>
      </main>
    </body>
    </html>"""), 200, {
        "Content-Language": "ru-RU",
        "X-Student": "Mavrin-Matvey",
        "X-Laboratory": "Flask-Lab-1",
    }


count = 0


@bp.route("/lab1/counter")
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
      <p><a href="{{ url_for('lab1.reset_counter') }}">Очистить счётчик</a></p>
    </body>
    </html>""", count=count, time=time, url=request.url, ip=request.remote_addr)


@bp.route("/lab1/counter/reset")
def reset_counter():
    global count
    count = 0
    return render_template_string("""<!doctype html>
    <html lang="ru"><head><meta charset="utf-8"><title>Счётчик очищен</title></head>
    <body>
      <h1>Счётчик очищен</h1>
      <p>Теперь значение счётчика равно нулю.</p>
      <a href="{{ url_for('lab1.counter') }}">Вернуться к счётчику</a>
    </body></html>""")


@bp.route("/lab1/info")
def info():
    return redirect(url_for("lab1.author"))


@bp.route("/created")
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


@bp.route("/lab1")
@bp.route("/lab1/")
def lab1_index():
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
    for rule in sorted(current_app.url_map.iter_rules(), key=lambda rule: rule.rule):
        if rule.endpoint == "static" or rule.endpoint.startswith(("lab2.", "lab3.")):
            continue
        if rule.endpoint == "lab1.http_status":
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


@bp.route("/lab1/status/<int:code>")
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
      <a href="{{ url_for('lab1.lab1_index') }}">К списку роутов</a>
    </body>
    </html>""", code=code, title=title, description=description)
    return html, code


@bp.route("/lab1/raise-error")
def raise_error():
    result = 1 / 0  # Намеренно вызываем ошибку 500 для проверки обработчика.
    return str(result)


