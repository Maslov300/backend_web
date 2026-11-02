"""Лабораторная работа №2: динамические пути и шаблоны Flask/Jinja."""

from flask import Blueprint, abort, redirect, render_template, request, url_for

bp = Blueprint("lab2", __name__, url_prefix="/lab2", template_folder="templates", static_folder="static")

STUDENT = "Маврин Матвей Евгеньевич"
GROUP = "ФБИ-44"
COURSE = 3

# Для основной и дополнительной частей лабораторной работы.
flower_list = [
    {"name": "роза", "price": 300},
    {"name": "тюльпан", "price": 310},
    {"name": "незабудка", "price": 320},
    {"name": "ромашка", "price": 330},
]

books = [
    {"author": "А. С. Пушкин", "title": "Капитанская дочка", "genre": "Историческая повесть", "pages": 192},
    {"author": "Н. В. Гоголь", "title": "Мёртвые души", "genre": "Поэма", "pages": 352},
    {"author": "Ф. М. Достоевский", "title": "Преступление и наказание", "genre": "Роман", "pages": 672},
    {"author": "Л. Н. Толстой", "title": "Анна Каренина", "genre": "Роман", "pages": 864},
    {"author": "И. С. Тургенев", "title": "Отцы и дети", "genre": "Роман", "pages": 288},
    {"author": "М. А. Булгаков", "title": "Мастер и Маргарита", "genre": "Роман", "pages": 480},
    {"author": "А. П. Чехов", "title": "Палата № 6", "genre": "Повесть", "pages": 112},
    {"author": "М. Ю. Лермонтов", "title": "Герой нашего времени", "genre": "Роман", "pages": 224},
    {"author": "А. И. Куприн", "title": "Гранатовый браслет", "genre": "Повесть", "pages": 96},
    {"author": "И. А. Гончаров", "title": "Обломов", "genre": "Роман", "pages": 640},
]

objects = [
    {"name": "Яблоко", "emoji": "apple", "description": "Сочный плод яблони."},
    {"name": "Банан", "emoji": "banana", "description": "Тропический плод с мягкой мякотью."},
    {"name": "Апельсин", "emoji": "orange", "description": "Цитрус с яркой ароматной кожурой."},
    {"name": "Лимон", "emoji": "lemon", "description": "Кислый цитрус с жёлтой кожурой."},
    {"name": "Арбуз", "emoji": "watermelon", "description": "Крупная сладкая бахчевая культура."},
    {"name": "Виноград", "emoji": "grapes", "description": "Сладкие ягоды, растущие гроздьями."},
    {"name": "Клубника", "emoji": "strawberry", "description": "Ароматная красная садовая ягода."},
    {"name": "Вишня", "emoji": "cherries", "description": "Небольшой плод с косточкой."},
    {"name": "Ананас", "emoji": "pineapple", "description": "Тропический плод с колючей кожурой."},
    {"name": "Киви", "emoji": "kiwi", "description": "Плод с зелёной мякотью и мелкими семенами."},
    {"name": "Персик", "emoji": "peach", "description": "Сладкий плод с бархатистой кожицей."},
    {"name": "Груша", "emoji": "pear", "description": "Мягкий плод грушевого дерева."},
    {"name": "Зелёное яблоко", "emoji": "green_apple", "description": "Сорт яблок с зелёной кожурой."},
    {"name": "Кокос", "emoji": "coconut", "description": "Плод кокосовой пальмы."},
    {"name": "Манго", "emoji": "mango", "description": "Тропический плод с оранжевой мякотью."},
    {"name": "Черника", "emoji": "blueberries", "description": "Мелкие тёмно-синие ягоды."},
    {"name": "Дыня", "emoji": "melon", "description": "Сладкий ароматный бахчевой плод."},
    {"name": "Авокадо", "emoji": "avocado", "description": "Маслянистый плод с крупной косточкой."},
    {"name": "Помидор", "emoji": "tomato", "description": "Красный сочный плод томата."},
    {"name": "Кукуруза", "emoji": "corn", "description": "Зерновая культура с початками."},
]


@bp.route("/a")
def slash_without():
    return "без слэша"


@bp.route("/a/")
def slash_with():
    return "со слэшем"


@bp.route("/flowers/<int:flower_id>")
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    return render_template("flower_detail.html", flower=flower_list[flower_id], flower_id=flower_id)


@bp.route("/flowers/")
def all_flowers():
    return render_template("flowers.html", flowers=flower_list)


def append_flower(name, price=300):
    flower_list.append({"name": name, "price": price})
    return render_template("flower_added.html", flower=name, flowers=flower_list)


@bp.route("/add_flower/<name>")
def add_flower(name):
    return append_flower(name)


@bp.route("/add_flower/")
def add_flower_form():
    name = request.args.get("name", "").strip()
    if not name:
        return "вы не задали имя цветка", 400
    return append_flower(name)


@bp.route("/clear_flowers")
def clear_flowers():
    flower_list.clear()
    return render_template("flowers_cleared.html")


@bp.route("/del_flower/<int:flower_id>")
def del_flower(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    flower_list.pop(flower_id)
    return redirect(url_for("lab2.all_flowers"))


@bp.route("/sort_flowers/name")
def sort_flowers_by_name():
    flower_list.sort(key=lambda flower: flower["name"].lower())
    return redirect(url_for("lab2.all_flowers"))


@bp.route("/sort_flowers/price")
def sort_flowers_by_price():
    flower_list.sort(key=lambda flower: flower["price"])
    return redirect(url_for("lab2.all_flowers"))


@bp.route("/example")
def example():
    fruits = [
        {"name": "яблоки", "price": 100},
        {"name": "груши", "price": 120},
        {"name": "апельсины", "price": 80},
        {"name": "мандарины", "price": 95},
        {"name": "манго", "price": 321},
    ]
    # ?empty=1 демонстрирует работу ветки else в Jinja.
    context = {} if request.args.get("empty") == "1" else {"name": STUDENT, "lab_num": 2, "group": GROUP, "course": COURSE}
    return render_template("example.html", fruits=fruits, **context)


@bp.route("/")
def lab2_index():
    return render_template("lab2.html")


@bp.route("/filters")
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template("filter.html", phrase=phrase)


@bp.route("/calc/")
def calc_default():
    return redirect(url_for("lab2.calc", a=1, b=1))


@bp.route("/calc/<int:a>")
def calc_one_number(a):
    return redirect(url_for("lab2.calc", a=a, b=1))


@bp.route("/calc/<int:a>/<int:b>")
def calc(a, b):
    return render_template("calc.html", a=a, b=b)


@bp.route("/books")
def show_books():
    return render_template("books.html", books=books)


@bp.route("/gallery")
def show_gallery():
    return render_template("gallery.html", objects=objects)
