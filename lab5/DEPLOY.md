# Развёртывание лабораторной №5 в облаке НГТУ

## PostgreSQL и учётная запись

На сервере Ubuntu:

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
sudo systemctl status postgresql
```

Создайте отдельного владельца базы данных. **Вместо `СВОЙ_СЛОЖНЫЙ_ПАРОЛЬ` установите уникальный пароль. Не публикуйте пароль и не добавляйте его в Git.**

```bash
sudo -u postgres psql
```

```sql
CREATE ROLE matvey_mavrin_knowledge_base LOGIN PASSWORD 'СВОЙ_СЛОЖНЫЙ_ПАРОЛЬ';
CREATE DATABASE matvey_mavrin_knowledge_base OWNER matvey_mavrin_knowledge_base;
\q
```

Создайте таблицы из `/var/www/lab5/schema.sql`:

```bash
cd /var/www
git pull
source /root/venv/bin/activate
python -m pip install -r requirements.txt
psql -W -h 127.0.0.1 -U matvey_mavrin_knowledge_base -d matvey_mavrin_knowledge_base -f lab5/schema.sql
```

Ввод пароля в командной строке может попасть в историю оболочки. Для реального развертывания безопаснее использовать интерактивный запрос `psql -W` или `.pgpass` с правами `0600`.

## Переменные окружения сервиса

Параметры читаются через `os.environ`:

- `LAB5_DB_HOST=127.0.0.1`
- `LAB5_DB_PORT=5432`
- `LAB5_DB_NAME=matvey_mavrin_knowledge_base`
- `LAB5_DB_USER=matvey_mavrin_knowledge_base`
- `LAB5_DB_PASSWORD` — пароль, заданный при создании роли.
- `FLASK_SECRET_KEY` — постоянный уникальный секретный ключ для Flask (не размещайте в коде/репозитории).

При запуске через systemd создайте приватный файл `/etc/backend_web.env` (права `0600`, владелец root) и добавьте в секцию `[Service]` unit-файла строку `EnvironmentFile=/etc/backend_web.env`. Сохраните имеющиеся `WorkingDirectory`, `ExecStart`, порт `8000`. Затем:

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

Если сервис systemd ещё не настроен, используйте существующую инструкцию развёртывания лабораторной №4, не запускайте одновременно второй Gunicorn на том же порту.

## Проверка

На сервере: `curl -I http://127.0.0.1:8000/lab5/`.

В браузере проверьте `/lab5/`, регистрацию, вход, личные статьи, редактирование, удаление, избранное, публичные статьи и список пользователей. Для отчёта сохраните внешний адрес сайта, `git log` и собственные скриншоты.
