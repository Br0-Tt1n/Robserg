from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "robserg-secret-key"  # для flash-сообщений

# ─────────────────────────────────────────────
# ДАННЫЕ (пока без БД — заглушки)
# В будущем заменишь на запросы к SQLAlchemy / SQLite
# ─────────────────────────────────────────────

PRODUCTS = [
    {
        "id": 1,
        "name": "Щепа дубовая — лёгкий обжиг",
        "description": "Мягкий ванильный аромат, золотистый цвет. Идеально для самогона и кальвадоса.",
        "price": 350,
        "badge": "Хит",
        "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=500&auto=format&q=80",
    },
    {
        "id": 2,
        "name": "Щепа дубовая — средний обжиг",
        "description": "Баланс ванили и карамели. Универсальный выбор для виски и коньяка.",
        "price": 390,
        "badge": "Топ продаж",
        "image_url": "https://images.unsplash.com/photo-1605493725784-56fcb5d47a63?w=500&auto=format&q=80",
    },
    {
        "id": 3,
        "name": "Щепа дубовая — сильный обжиг",
        "description": "Глубокий дымный вкус с нотами шоколада и кофе. Для тёмных дистиллятов.",
        "price": 420,
        "badge": None,
        "image_url": "https://images.unsplash.com/photo-1574196199733-a81571fffe3e?w=500&auto=format&q=80",
    },
    {
        "id": 4,
        "name": "Кубик дубовый кавказский",
        "description": "Крупная фракция для длительной выдержки. Равномерная экстракция дубильных веществ.",
        "price": 480,
        "badge": "Новинка",
        "image_url": "https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=500&auto=format&q=80",
    },
]

NAV_LINKS = [
    {"href": "/", "label": "Главная"},
    {"href": "#catalog", "label": "Каталог"},
    {"href": "#contacts", "label": "Контакты"},
    {"href": "#reviews", "label": "Отзывы"},
    {"href": "#delivery", "label": "Доставка"},
]

SITE_META = {
    "title": "Robserg — Дубовая щепа и кубик с Кавказа",
    "logo_text": "ROBSERG",
    "logo_since": "SINCE 2020",
    "hero_title": "Натуральный\nвкус выдержки",
    "hero_sub": "Дубовая щепа и кубик с кавказа",
    "wb_url": "https://wb.ru",
    "vk_url": "https://vk.com",
}


# ─────────────────────────────────────────────
# РОУТЫ
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Главная страница."""
    return render_template(
        "index.html",
        products=PRODUCTS,
        nav_links=NAV_LINKS,
        meta=SITE_META,
    )


@app.route("/submit", methods=["POST"])
def submit():
    """Обработка формы обратной связи."""
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    # TODO: сохранить в БД или отправить email
    # Например: db.session.add(Lead(name=name, phone=phone, ...))
    print(f"[ЗАЯВКА] {name} | {phone} | {email}\n  → {message}")

    flash("Ваша заявка принята! Мы свяжемся с вами в ближайшее время.", "success")
    return redirect(url_for("index") + "#faq")


# ─────────────────────────────────────────────
# ЗАПУСК
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run()