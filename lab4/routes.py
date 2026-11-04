"""Лабораторная №4: POST, PRG, авторизация и сессии."""
from decimal import Decimal, InvalidOperation
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes
from uuid import uuid4

from flask import Blueprint, redirect, render_template, request, session, url_for

bp = Blueprint('lab4', __name__)


def hash_password(password, salt=None):
    salt = salt or token_bytes(16)
    digest = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
    return salt.hex() + ':' + digest.hex()


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split(':', 1)
        digest = pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), 200_000)
        return compare_digest(digest, bytes.fromhex(digest_hex))
    except (ValueError, TypeError):
        return False


# Список пользователей хранится в оперативной памяти, как предписано методичкой.
users = [
    {'id': 'alex', 'login': 'alex', 'password': hash_password('123'), 'name': 'Александр', 'sex': 'male'},
    {'id': 'bob', 'login': 'bob', 'password': hash_password('555'), 'name': 'Борис', 'sex': 'male'},
    {'id': 'anna', 'login': 'anna', 'password': hash_password('anna123'), 'name': 'Анна', 'sex': 'female'},
    {'id': 'maria', 'login': 'maria', 'password': hash_password('maria123'), 'name': 'Мария', 'sex': 'female'},
]

tree_count = 0
TREE_MAX = 10
OPERATIONS = {
    'add': ('Сложение', '+'), 'sub': ('Вычитание', '−'),
    'mul': ('Умножение', '×'), 'div': ('Деление', '÷'), 'pow': ('Возведение в степень', '^'),
}
CONCRETE = {'М200': Decimal('4200'), 'М300': Decimal('4800'), 'М400': Decimal('5400'), 'М500': Decimal('6100')}


def current_user():
    user_id = session.get('user_id')
    return next((u for u in users if u['id'] == user_id), None)


def authorized_or_redirect():
    if not current_user():
        return redirect(url_for('lab4.login'))
    return None


@bp.route('/lab4/')
def home():
    return render_template('lab4/lab4.html')


@bp.route('/lab4/div-form')
def div_form():
    return render_template('lab4/arithmetic_form.html', operation='div', title='Деление')


@bp.route('/lab4/div', methods=['POST'])
def division():
    return calculate('div')


@bp.route('/lab4/<operation>-form')
def arithmetic_form(operation):
    if operation not in OPERATIONS or operation == 'div':
        return 'Неизвестная операция', 404
    return render_template('lab4/arithmetic_form.html', operation=operation, title=OPERATIONS[operation][0])


@bp.route('/lab4/<operation>', methods=['POST'])
def arithmetic(operation):
    if operation not in OPERATIONS or operation == 'div':
        return 'Неизвестная операция', 404
    return calculate(operation)


def calculate(operation):
    x1_text = request.form.get('x1', '').strip()
    x2_text = request.form.get('x2', '').strip()
    title, sign = OPERATIONS[operation]
    error = None
    default = '0' if operation == 'add' else '1' if operation == 'mul' else None
    if default is None and (not x1_text or not x2_text):
        error = 'Оба поля должны быть заполнены!'
    else:
        try:
            x1 = Decimal(x1_text or default)
            x2 = Decimal(x2_text or default)
            if not x1.is_finite() or not x2.is_finite():
                error = 'Укажите конечные числа.'
            elif operation == 'div' and x2 == 0:
                error = 'На ноль делить нельзя.'
            elif operation == 'pow' and x1 == x2 == 0:
                error = 'Нельзя вычислить 0 в степени 0.'
            else:
                if operation == 'add': result = x1 + x2
                elif operation == 'sub': result = x1 - x2
                elif operation == 'mul': result = x1 * x2
                elif operation == 'div': result = x1 / x2
                else: result = x1 ** x2
                if not result.is_finite() or abs(result) > Decimal('1e100'):
                    error = 'Результат слишком большой.'
        except (InvalidOperation, ValueError, OverflowError, ZeroDivisionError):
            error = 'Введите корректные числа.'
    return render_template('lab4/arithmetic_result.html', title=title, operation=operation,
                           x1=x1_text, x2=x2_text, sign=sign, error=error,
                           result=str(result) if not error else None)


@bp.route('/lab4/tree', methods=['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'POST':
        operation = request.form.get('operation')
        if operation == 'plant' and tree_count < TREE_MAX:
            tree_count += 1
        elif operation == 'cut' and tree_count > 0:
            tree_count -= 1
        return redirect(url_for('lab4.tree'))
    return render_template('lab4/tree.html', tree_count=tree_count, tree_max=TREE_MAX)


@bp.route('/lab4/login', methods=['GET', 'POST'])
def login():
    user = current_user()
    if request.method == 'GET':
        return render_template('lab4/login.html', user=user)
    login_value = request.form.get('login', '').strip()
    password = request.form.get('password', '')
    if not login_value:
        error = 'Не введён логин.'
    elif not password:
        error = 'Не введён пароль.'
    else:
        matched = next((u for u in users if u['login'] == login_value and verify_password(password, u['password'])), None)
        if matched:
            session.clear()
            session['user_id'] = matched['id']
            return redirect(url_for('lab4.login'))
        error = 'Неверные логин или пароль.'
    return render_template('lab4/login.html', user=None, login_value=login_value, error=error), 400


@bp.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('lab4.login'))


@bp.route('/lab4/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab4/register.html')
    login_value = request.form.get('login', '').strip()
    name = request.form.get('name', '').strip()
    sex = request.form.get('sex', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm', '')
    if not login_value or not name or not password or not confirm or sex not in ('male', 'female'):
        error = 'Заполните все поля формы.'
    elif any(u['login'] == login_value for u in users):
        error = 'Этот логин уже занят.'
    elif password != confirm:
        error = 'Пароли не совпадают.'
    else:
        user = {'id': uuid4().hex, 'login': login_value, 'name': name, 'sex': sex,
                'password': hash_password(password)}
        users.append(user)
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('lab4.login'))
    return render_template('lab4/register.html', error=error, values=request.form), 400


@bp.route('/lab4/users')
def user_list():
    check = authorized_or_redirect()
    if check is not None: return check
    return render_template('lab4/users.html', users=users, me=current_user())


@bp.route('/lab4/edit', methods=['GET', 'POST'])
def edit_user():
    check = authorized_or_redirect()
    if check is not None: return check
    user = current_user()
    if request.method == 'GET': return render_template('lab4/edit.html', user=user)
    new_login = request.form.get('login', '').strip()
    new_name = request.form.get('name', '').strip()
    new_sex = request.form.get('sex', '')
    pwd = request.form.get('password', '')
    confirm = request.form.get('confirm', '')
    if not new_login or not new_name or new_sex not in ('male', 'female'):
        error = 'Имя, логин и пол обязательны.'
    elif any(u['login'] == new_login and u['id'] != user['id'] for u in users):
        error = 'Логин уже занят.'
    elif pwd != confirm:
        error = 'Пароли не совпадают.'
    else:
        user.update(login=new_login, name=new_name, sex=new_sex)
        if pwd:
            user['password'] = hash_password(pwd)
        return redirect(url_for('lab4.user_list'))
    return render_template('lab4/edit.html', error=error, user=user, values=request.form), 400


@bp.route('/lab4/delete', methods=['POST'])
def delete_user():
    check = authorized_or_redirect()
    if check is not None: return check
    user = current_user()
    users.remove(user)
    session.pop('user_id', None)
    return redirect(url_for('lab4.login'))


@bp.route('/lab4/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'GET': return render_template('lab4/weather.html')
    temp_text = request.form.get('temperature', '').strip()
    if not temp_text:
        error, result = 'ошибка: не задана температура', None
    else:
        try:
            temp = Decimal(temp_text)
            if not temp.is_finite(): raise InvalidOperation
            if temp < -30: status = 'слишком холодно'
            elif temp <= -17: status = 'Очень холодно'
            elif temp <= 0: status = 'Холодно'
            elif temp <= 15: status = 'Прохладно'
            elif temp <= 25: status = 'Тепло'
            elif temp <= 30: status = 'Жарко'
            else: status = 'слишком жарко'
            result = status if temp < -30 or temp > 30 else f'{status}. Температура: {temp}°С'
            error = None
        except InvalidOperation:
            error, result = 'Введите корректную температуру.', None
    return render_template('lab4/weather.html', result=result, error=error, temperature=temp_text)


@bp.route('/lab4/concrete', methods=['GET', 'POST'])
def concrete():
    if request.method == 'GET': return render_template('lab4/concrete.html', prices=CONCRETE)
    grade = request.form.get('grade', '')
    volume_text = request.form.get('volume', '').strip()
    error = None
    calculation = None
    if grade not in CONCRETE:
        error = 'Выберите марку бетона.'
    elif not volume_text:
        error = 'Не указан объём бетона.'
    else:
        try:
            volume = Decimal(volume_text)
            if not volume.is_finite() or volume <= 0:
                error = 'Объём должен быть больше нуля.'
            elif volume > 100:
                error = 'Такого объёма сейчас нет в наличии.'
            else:
                subtotal = CONCRETE[grade] * volume
                discount = (subtotal * Decimal('0.10')) if volume > 10 else Decimal('0')
                calculation = {'grade': grade, 'volume': volume, 'discount': discount,
                               'price': subtotal - discount}
        except InvalidOperation:
            error = 'Укажите корректный объём.'
    return render_template('lab4/concrete.html', prices=CONCRETE, error=error,
                           calculation=calculation, grade=grade, volume=volume_text)
