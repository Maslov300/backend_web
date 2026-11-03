"""Лабораторная №3: GET-формы, cookie и Flask Blueprint."""

from datetime import date
import re

from flask import Blueprint, make_response, redirect, render_template, request, url_for

bp = Blueprint("lab3", __name__, url_prefix="/lab3")

# Цены из методички, рубли.
DRINK_PRICES = {"cofee": 120, "black-tea": 80, "green-tea": 70}
BERTHS = {
    "lower": "Нижняя",
    "upper": "Верхняя",
    "upper-side": "Верхняя боковая",
    "lower-side": "Нижняя боковая",
}

# Не менее 30 товаров: название, цена и два дополнительных атрибута.
PRODUCTS = [
    {"name": "Тетрадь 12 листов", "price": 25, "brand": "ErichKrause", "color": "синий"},
    {"name": "Тетрадь 24 листа", "price": 39, "brand": "БиДжи", "color": "зелёный"},
    {"name": "Тетрадь 48 листов", "price": 69, "brand": "Hatber", "color": "красный"},
    {"name": "Тетрадь 96 листов", "price": 129, "brand": "Hatber", "color": "фиолетовый"},
    {"name": "Блокнот А6", "price": 85, "brand": "Brauberg", "color": "чёрный"},
    {"name": "Блокнот А5", "price": 190, "brand": "Brauberg", "color": "синий"},
    {"name": "Блокнот А4", "price": 275, "brand": "ErichKrause", "color": "серый"},
    {"name": "Ручка шариковая", "price": 35, "brand": "Pilot", "color": "синий"},
    {"name": "Ручка гелевая", "price": 78, "brand": "Pilot", "color": "чёрный"},
    {"name": "Ручка капиллярная", "price": 115, "brand": "Stabilo", "color": "красный"},
    {"name": "Карандаш HB", "price": 20, "brand": "Koh-I-Noor", "color": "жёлтый"},
    {"name": "Карандаш 2B", "price": 32, "brand": "Koh-I-Noor", "color": "зелёный"},
    {"name": "Карандаш механический", "price": 180, "brand": "Pentel", "color": "чёрный"},
    {"name": "Ластик", "price": 42, "brand": "Maped", "color": "белый"},
    {"name": "Точилка", "price": 55, "brand": "Maped", "color": "красный"},
    {"name": "Линейка 20 см", "price": 60, "brand": "Стамм", "color": "прозрачный"},
    {"name": "Линейка 30 см", "price": 84, "brand": "Стамм", "color": "прозрачный"},
    {"name": "Циркуль", "price": 325, "brand": "Глобус", "color": "серый"},
    {"name": "Набор маркеров 4 шт.", "price": 230, "brand": "Stabilo", "color": "разноцветный"},
    {"name": "Набор маркеров 8 шт.", "price": 420, "brand": "Stabilo", "color": "разноцветный"},
    {"name": "Текстовыделитель", "price": 105, "brand": "Brauberg", "color": "жёлтый"},
    {"name": "Папка на кнопке", "price": 77, "brand": "Berlingo", "color": "синий"},
    {"name": "Папка-регистратор", "price": 285, "brand": "Berlingo", "color": "чёрный"},
    {"name": "Папка на кольцах", "price": 210, "brand": "Berlingo", "color": "белый"},
    {"name": "Набор стикеров", "price": 95, "brand": "Post-it", "color": "жёлтый"},
    {"name": "Бумага А4, 100 листов", "price": 165, "brand": "SvetoCopy", "color": "белый"},
    {"name": "Бумага А4, 500 листов", "price": 495, "brand": "SvetoCopy", "color": "белый"},
    {"name": "Корректор-лента", "price": 138, "brand": "Brauberg", "color": "белый"},
    {"name": "Корректор жидкий", "price": 125, "brand": "Brauberg", "color": "белый"},
    {"name": "Клей-карандаш", "price": 105, "brand": "ErichKrause", "color": "прозрачный"},
    {"name": "Ножницы канцелярские", "price": 240, "brand": "Maped", "color": "красный"},
    {"name": "Степлер", "price": 380, "brand": "Brauberg", "color": "чёрный"},
]


def _cookie_response(location):
    return make_response(redirect(location))


@bp.route("/")
def lab3_index():
    name = request.cookies.get("name") or "Аноним"
    age = request.cookies.get("age") or "не указан"
    name_color = request.cookies.get("name_color") or "black"
    return render_template("lab3/lab3.html", name=name, age=age, name_color=name_color)


@bp.route("/cookie")
def cookie():
    response = _cookie_response(url_for("lab3.lab3_index"))
    response.set_cookie("name", "Alex", max_age=5)
    response.set_cookie("age", "20")
    response.set_cookie("name_color", "magenta")
    return response


@bp.route("/del_cookie")
def del_cookie():
    response = _cookie_response(url_for("lab3.lab3_index"))
    for name in ("name", "age", "name_color"):
        response.delete_cookie(name)
    return response


@bp.route("/form1")
def form1():
    user = request.args.get("user", "").strip()
    age = request.args.get("age", "").strip()
    sex = request.args.get("sex", "male")
    errors = {}
    submitted = any(key in request.args for key in ("user", "age", "sex"))
    if submitted:
        if not user:
            errors["user"] = "Заполните поле!"
        if not age:
            errors["age"] = "Заполните поле!"
        elif not age.isdecimal() or int(age) < 1 or int(age) > 120:
            errors["age"] = "Укажите возраст от 1 до 120 лет."
        if sex not in ("male", "female"):
            errors["sex"] = "Выберите пол."
    return render_template("lab3/form1.html", user=user, age=age, sex=sex,
                           errors=errors, submitted=submitted)


@bp.route("/order")
def order():
    return render_template("lab3/order.html")


@bp.route("/pay")
def pay():
    drink = request.args.get("drink", "")
    if drink not in DRINK_PRICES:
        return redirect(url_for("lab3.order"))
    price = DRINK_PRICES[drink]
    if request.args.get("milk") == "on":
        price += 30
    if request.args.get("sugar") == "on":
        price += 10
    return render_template("lab3/pay.html", price=price)


@bp.route("/success", methods=["GET", "POST"])
def success():
    # Учебная имитация: реальные банковские реквизиты не храним и не обрабатываем.
    if request.method != "POST":
        return redirect(url_for("lab3.order"))
    price_raw = request.form.get("price", "")
    if not price_raw.isdecimal() or not 70 <= int(price_raw) <= 160:
        return redirect(url_for("lab3.order"))
    return render_template("lab3/success.html", price=int(price_raw))


# Настройки сохраняются как cookie, подключены в общем templates/base.html.
DEFAULT_SETTINGS = {
    "color": "#1f2937",
    "background_color": "#f8fafc",
    "font_size": "16",
    "font_style": "normal",
}


def _valid_setting(key, value):
    if key in ("color", "background_color"):
        return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", value))
    if key == "font_size":
        return value.isdecimal() and 12 <= int(value) <= 32
    if key == "font_style":
        return value in ("normal", "italic")
    return False


@bp.route("/settings")
def settings():
    if any(key in request.args for key in DEFAULT_SETTINGS):
        response = _cookie_response(url_for("lab3.settings"))
        for key in DEFAULT_SETTINGS:
            value = request.args.get(key)
            if value is not None and _valid_setting(key, value):
                response.set_cookie(key, value)
        return response
    values = {key: request.cookies.get(key, default) for key, default in DEFAULT_SETTINGS.items()}
    for key, default in DEFAULT_SETTINGS.items():
        if not _valid_setting(key, values[key]):
            values[key] = default
    return render_template("lab3/settings.html", **values)


@bp.route("/clear_settings")
def clear_settings():
    response = _cookie_response(url_for("lab3.settings"))
    for key in DEFAULT_SETTINGS:
        response.delete_cookie(key)
    return response


@bp.route("/train")
def train():
    names = ("passenger", "berth", "linen", "luggage", "age", "from_city", "to_city", "travel_date", "insurance")
    values = {key: request.args.get(key, "").strip() for key in names}
    errors = {}
    submitted = request.args.get("submit") == "1"
    ticket = None
    if submitted:
        for key in names:
            if not values[key]:
                errors[key] = "Заполните поле!"
        if values["age"] and (not values["age"].isdecimal() or not 1 <= int(values["age"]) <= 120):
            errors["age"] = "Возраст должен быть от 1 до 120 лет."
        if values["berth"] and values["berth"] not in BERTHS:
            errors["berth"] = "Выберите полку."
        for field in ("linen", "luggage", "insurance"):
            if values[field] and values[field] not in ("yes", "no"):
                errors[field] = "Выберите да или нет."
        if values["travel_date"]:
            try:
                date.fromisoformat(values["travel_date"])
            except ValueError:
                errors["travel_date"] = "Укажите корректную дату."
        if not errors:
            child = int(values["age"]) < 18
            price = 700 if child else 1000
            if values["berth"] in ("lower", "lower-side"):
                price += 100
            if values["linen"] == "yes":
                price += 75
            if values["luggage"] == "yes":
                price += 250
            if values["insurance"] == "yes":
                price += 150
            ticket = {**values, "price": price, "child": child,
                      "berth_title": BERTHS[values["berth"]]}
    return render_template("lab3/train.html", values=values, errors=errors, ticket=ticket)


def _read_price(text):
    if not text:
        return None
    try:
        value = int(text)
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


@bp.route("/products")
def products():
    if "reset" in request.args:
        response = _cookie_response(url_for("lab3.products"))
        response.delete_cookie("min_price")
        response.delete_cookie("max_price")
        return response
    if "search" in request.args:
        min_price = _read_price(request.args.get("min_price", ""))
        max_price = _read_price(request.args.get("max_price", ""))
        if min_price is not None and max_price is not None and min_price > max_price:
            min_price, max_price = max_price, min_price
        response = _cookie_response(url_for("lab3.products"))
        for name, value in (("min_price", min_price), ("max_price", max_price)):
            if value is None:
                response.delete_cookie(name)
            else:
                response.set_cookie(name, str(value), max_age=30 * 24 * 3600)
        return response
    min_price = _read_price(request.cookies.get("min_price", ""))
    max_price = _read_price(request.cookies.get("max_price", ""))
    result = [item for item in PRODUCTS if (min_price is None or item["price"] >= min_price)
              and (max_price is None or item["price"] <= max_price)]
    return render_template("lab3/products.html", products=result,
                           min_price=min_price, max_price=max_price,
                           placeholder_min=min(item["price"] for item in PRODUCTS),
                           placeholder_max=max(item["price"] for item in PRODUCTS))
