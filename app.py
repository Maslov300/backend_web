"""Общая точка входа для лабораторных работ Flask."""

from lab1.app import app
from lab2.routes import bp as lab2_bp

app.register_blueprint(lab2_bp)

if __name__ == "__main__":
    app.run(debug=True)
