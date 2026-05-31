from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "robserg-secret-key"

# ─────────────────────────────────────────────
# ДАННЫЕ
# ИЗМЕНЕНО: добавлено поле "weight" в каждый товар
# ─────────────────────────────────────────────

PRODUCTS = [
    {
        "id": 1,
        "name": "Щепа дубовая — лёгкий обжиг",
        "description": "Мягкий ванильный аромат, золотистый цвет. Идеально для самогона и кальвадоса.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": "Хит",
        "image_url": "images/WoodChipsLow.png",
    },
    {
        "id": 2,
        "name": "Щепа дубовая — средний обжиг",
        "description": "Баланс ванили и карамели. Универсальный выбор для виски и коньяка.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": "Топ продаж",
        "image_url": "images/WoodChips.png",
    },
    {
        "id": 3,
        "name": "Щепа дубовая — сильный обжиг",
        "description": "Глубокий дымный вкус с нотами шоколада и кофе. Для тёмных дистиллятов.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": None,
        "image_url": "images/Cube.png",
    },
    {
        "id": 4,
        "name": "Кубик дубовый - средний обжиг",
        "description": "Дубовые кубики для настаивания самогона, спирта и других крепких напитков. Изготовлены из натурального дуба без химических добавок и ароматизаторов. Придают напиткам благородные нотки ванили, карамели, шоколада и миндаля, создавая эффект выдержки в дубовой бочке. Просты в использовании и помогают получить насыщенный вкус и аромат в домашних условиях.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": "Новинка",
        "image_url": "images/CubeMedium.png",
    },
        {
        "id": 5,
        "name": "Щепа дубовая — лёгкий обжиг",
        "description": "Мягкий ванильный аромат, золотистый цвет. Идеально для самогона и кальвадоса.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": "Хит",
        "image_url": "images/WoodChipsLow.png",
    },
    {
        "id": 6,
        "name": "Щепа дубовая — средний обжиг",
        "description": "Баланс ванили и карамели. Универсальный выбор для виски и коньяка.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": "Топ продаж",
        "image_url": "images/WoodChips.png",
    },
    {
        "id": 7,
        "name": "Щепа дубовая — сильный обжиг",
        "description": "Глубокий дымный вкус с нотами шоколада и кофе. Для тёмных дистиллятов.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": None,
        "image_url": "images/Cube.png",
    },
    {
        "id": 8,
        "name": "Кубик дубовый - средний обжиг",
        "description": "Крупная фракция для длительной выдержки. Равномерная экстракция дубильных веществ.",
        "price": 700,
        "weight": "500 гр.",          # ДОБАВЛЕНО
        "badge": "Новинка",
        "image_url": "images/CubeMedium.png",
    },
]

SITE_META = {
    "title":      "Robserg — Дубовая щепа и кубик с Кавказа",
    "logo_text":  "ROBSERG",
    "logo_since": "SINCE 2020",
    "hero_title": "Натуральный\nвкус выдержки",
    "hero_sub":   "Дубовая щепа и кубик с кавказа",
    "wb_url":     "https://wb.ru",
    "vk_url":     "https://vk.com",
    "max_url":    "https://max.ru",
}

# ─────────────────────────────────────────────
# ДОБАВЛЕНО: вспомогательная функция nav_links
# Проставляет active по имени endpoint-а
# (раньше active ставился через loop.first — ИЗМЕНЕНО)
# ─────────────────────────────────────────────

def make_nav_links(active_endpoint: str) -> list:
    links = [
        {"href": url_for("index"),   "label": "Главная",  "endpoint": "index"},
        {"href": url_for("catalog"), "label": "Каталог",  "endpoint": "catalog"},
        {"href": "#contacts",        "label": "Контакты", "endpoint": None},
        {"href": "#reviews",         "label": "Отзывы",   "endpoint": None},
        {"href": "#delivery",        "label": "Доставка", "endpoint": None},
        {"href": "#information",     "label": "Информация", "endpoint": None},
    ]
    for link in links:
        link["active"] = (link["endpoint"] == active_endpoint)
    return links


# ─────────────────────────────────────────────
# РОУТЫ
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        products=PRODUCTS[:4],          # на главной — только 4 товара
        nav_links=make_nav_links("index"),
        meta=SITE_META,
    )


# ── ДОБАВЛЕНО: страница каталога ──────────────
@app.route("/catalog")
def catalog():
    return render_template(
        "catalog.html",
        products=PRODUCTS,              # все товары
        nav_links=make_nav_links("catalog"),
        meta=SITE_META,
    )
# ──────────────────────────────────────────────


@app.route("/submit", methods=["POST"])
def submit():
    name           = request.form.get("name", "").strip()
    phone          = request.form.get("phone", "").strip()
    email          = request.form.get("email", "").strip()
    contact_method = request.form.get("contact_method", "").strip()
    call_time      = request.form.get("call_time", "").strip()
    message        = request.form.get("message", "").strip()

    method_labels = {
        "phone": "Позвонить по телефону",
        "email": "Почта",
        "vk":    "ВКонтакте",
        "max":   "МАКС",
    }
    method_str    = method_labels.get(contact_method, contact_method)
    call_time_str = f" (удобное время: {call_time})" if contact_method == "phone" and call_time else ""

    print(
        f"[ЗАЯВКА] {name} | {phone} | {email}\n"
        f"  Способ связи: {method_str}{call_time_str}\n"
        f"  Сообщение: {message}"
    )

    flash("Ваша заявка принята! Мы свяжемся с вами в ближайшее время.", "success")
    return redirect(url_for("index") + "#faq")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
