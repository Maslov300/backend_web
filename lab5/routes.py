"""Лабораторная работа №5: база знаний на Flask и PostgreSQL."""
import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
from flask import Blueprint, abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('lab5', __name__)


def db_connect():
    """Открыть соединение с PostgreSQL по настройкам окружения."""
    return psycopg2.connect(
        host=os.environ.get('LAB5_DB_HOST', '127.0.0.1'),
        port=int(os.environ.get('LAB5_DB_PORT', '5432')),
        dbname=os.environ.get('LAB5_DB_NAME', 'matvey_mavrin_knowledge_base'),
        user=os.environ.get('LAB5_DB_USER', 'matvey_mavrin_knowledge_base'),
        password=os.environ.get('LAB5_DB_PASSWORD', ''),
        connect_timeout=5,
    )


@contextmanager
def db_cursor():
    """Всегда закрывать соединение; commit только при успехе."""
    conn = db_connect()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
    finally:
        conn.close()


def current_user():
    user_id = session.get('lab5_user_id')
    if not user_id:
        return None
    with db_cursor() as cur:
        cur.execute('SELECT id, login, name FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
    if not user:
        session.pop('lab5_user_id', None)
    return user


def require_user():
    user = current_user()
    if user is None:
        return None, redirect(url_for('lab5.login'))
    return user, None


@bp.route('/lab5/')
def home():
    return render_template('lab5/lab5.html', user=current_user())


@bp.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    login = request.form.get('login', '').strip()
    name = request.form.get('name', '').strip()
    password = request.form.get('password', '')
    confirmation = request.form.get('confirmation', '')
    error = None
    if not login or not name or not password or not confirmation:
        error = 'Заполните все поля.'
    elif len(login) > 30 or len(name) > 100:
        error = 'Слишком длинный логин или имя.'
    elif password != confirmation:
        error = 'Пароли не совпадают.'
    elif len(password) < 4:
        error = 'Пароль должен содержать не менее 4 символов.'
    if error:
        return render_template('lab5/register.html', error=error, login=login, name=name), 400
    password_hash = generate_password_hash(password)
    try:
        with db_cursor() as cur:
            cur.execute('INSERT INTO users (login, password, name) VALUES (%s, %s, %s)',
                        (login, password_hash, name))
    except errors.UniqueViolation:
        return render_template('lab5/register.html', error='Такой логин уже существует.',
                               login=login, name=name), 400
    return render_template('lab5/success.html', login=login)


@bp.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html', user=current_user())
    login_value = request.form.get('login', '').strip()
    password = request.form.get('password', '')
    if not login_value or not password:
        return render_template('lab5/login.html', error='Заполните логин и пароль.',
                               login_value=login_value), 400
    with db_cursor() as cur:
        cur.execute('SELECT id, login, password, name FROM users WHERE login = %s', (login_value,))
        user = cur.fetchone()
    if user is None or not check_password_hash(user['password'], password):
        return render_template('lab5/login.html', error='Логин или пароль неверны.',
                               login_value=login_value), 401
    session['lab5_user_id'] = user['id']
    return redirect(url_for('lab5.home'))


@bp.route('/lab5/logout', methods=['POST'])
def logout():
    session.pop('lab5_user_id', None)
    return redirect(url_for('lab5.login'))


@bp.route('/lab5/create', methods=['GET', 'POST'])
def create():
    user, response = require_user()
    if response is not None:
        return response
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    title = request.form.get('title', '').strip()
    article_text = request.form.get('article_text', '').strip()
    is_public = request.form.get('is_public') == 'on'
    is_favorite = request.form.get('is_favorite') == 'on'
    if not title or not article_text:
        return render_template('lab5/create_article.html', title=title,
                               article_text=article_text,
                               error='Название и текст статьи обязательны.'), 400
    if len(title) > 50:
        return render_template('lab5/create_article.html', title=title,
                               article_text=article_text,
                               error='Название должно быть не длиннее 50 символов.'), 400
    with db_cursor() as cur:
        cur.execute('''INSERT INTO articles (login_id, title, article_text, is_favorite, is_public, likes)
                       VALUES (%s, %s, %s, %s, %s, 0)''',
                    (user['id'], title, article_text, is_favorite, is_public))
    return redirect(url_for('lab5.article_list'))


@bp.route('/lab5/list')
def article_list():
    user, response = require_user()
    if response is not None:
        return response
    with db_cursor() as cur:
        cur.execute('''SELECT id, title, article_text, is_favorite, is_public, likes
                       FROM articles WHERE login_id = %s
                       ORDER BY is_favorite DESC NULLS LAST, id DESC''', (user['id'],))
        articles = cur.fetchall()
    return render_template('lab5/articles.html', articles=articles, user=user)


@bp.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit(article_id):
    user, response = require_user()
    if response is not None:
        return response
    with db_cursor() as cur:
        cur.execute('SELECT * FROM articles WHERE id = %s AND login_id = %s',
                    (article_id, user['id']))
        article = cur.fetchone()
    if article is None:
        abort(404)
    if request.method == 'GET':
        return render_template('lab5/edit_article.html', article=article)
    title = request.form.get('title', '').strip()
    article_text = request.form.get('article_text', '').strip()
    if not title or not article_text or len(title) > 50:
        return render_template('lab5/edit_article.html', article={**article, 'title': title,
                               'article_text': article_text},
                               error='Укажите название (не более 50 символов) и текст.'), 400
    with db_cursor() as cur:
        cur.execute('''UPDATE articles SET title = %s, article_text = %s,
                       is_favorite = %s, is_public = %s WHERE id = %s AND login_id = %s''',
                    (title, article_text, request.form.get('is_favorite') == 'on',
                     request.form.get('is_public') == 'on', article_id, user['id']))
    return redirect(url_for('lab5.article_list'))


@bp.route('/lab5/delete/<int:article_id>', methods=['POST'])
def delete(article_id):
    user, response = require_user()
    if response is not None:
        return response
    with db_cursor() as cur:
        cur.execute('DELETE FROM articles WHERE id = %s AND login_id = %s',
                    (article_id, user['id']))
        if cur.rowcount == 0:
            abort(404)
    return redirect(url_for('lab5.article_list'))


@bp.route('/lab5/favorite/<int:article_id>', methods=['POST'])
def favorite(article_id):
    user, response = require_user()
    if response is not None:
        return response
    with db_cursor() as cur:
        cur.execute('''UPDATE articles SET is_favorite = NOT COALESCE(is_favorite, FALSE)
                       WHERE id = %s AND login_id = %s''', (article_id, user['id']))
        if cur.rowcount == 0:
            abort(404)
    return redirect(url_for('lab5.article_list'))


@bp.route('/lab5/public')
def public_articles():
    with db_cursor() as cur:
        cur.execute('''SELECT a.id, a.title, a.article_text, a.likes, u.login, u.name
                       FROM articles a JOIN users u ON a.login_id = u.id
                       WHERE a.is_public = TRUE ORDER BY a.id DESC''')
        articles = cur.fetchall()
    return render_template('lab5/public.html', articles=articles, user=current_user())


@bp.route('/lab5/users')
def users():
    with db_cursor() as cur:
        cur.execute('SELECT login, name FROM users ORDER BY login')
        people = cur.fetchall()
    return render_template('lab5/users.html', people=people)


@bp.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    user, response = require_user()
    if response is not None:
        return response
    if request.method == 'GET':
        return render_template('lab5/profile.html', user=user)
    name = request.form.get('name', '').strip()
    password = request.form.get('password', '')
    confirmation = request.form.get('confirmation', '')
    if not name or len(name) > 100:
        return render_template('lab5/profile.html', user=user,
                               error='Укажите имя длиной не более 100 символов.'), 400
    if password != confirmation:
        return render_template('lab5/profile.html', user=user,
                               error='Пароли не совпадают.'), 400
    if password and len(password) < 4:
        return render_template('lab5/profile.html', user=user,
                               error='Пароль должен содержать не менее 4 символов.'), 400
    with db_cursor() as cur:
        if password:
            cur.execute('UPDATE users SET name = %s, password = %s WHERE id = %s',
                        (name, generate_password_hash(password), user['id']))
        else:
            cur.execute('UPDATE users SET name = %s WHERE id = %s', (name, user['id']))
    return redirect(url_for('lab5.home'))


@bp.route('/lab5/react/<int:article_id>', methods=['POST'])
def react(article_id):
    """Учебные лайк/дизлайк публичной статьи: один POST изменяет счётчик на 1."""
    user, response = require_user()
    if response is not None:
        return response
    action = request.form.get('action')
    if action not in ('like', 'dislike'):
        abort(400)
    delta = 1 if action == 'like' else -1
    with db_cursor() as cur:
        cur.execute('''UPDATE articles SET likes = COALESCE(likes, 0) + %s
                       WHERE id = %s AND is_public = TRUE''', (delta, article_id))
        if cur.rowcount == 0:
            abort(404)
    return redirect(url_for('lab5.public_articles'))
