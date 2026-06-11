import json
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
DEMO_CART = [
    {**PRODUCTS[0], "qty": 2},
    {**PRODUCTS[1], "qty": 1},
    {**PRODUCTS[3], "qty": 1},
]

REVIEWS = [
    {
        "id": 1,
        "author": "Алексей П.",
        "date": "12 мая 2024",
        "rating": 5,
        "text": "Щепа отличного качества! Настойки приобретают мягкий аромат и красивый янтарный цвет. Заказываю не в первый раз.",
        "photos": ["images/WoodChips.png", "images/WoodChipsLow.png", "images/Cube.png"],
        "product": "Дубовая щепа, сильный обжиг",
        "avatar": None,
    },
    {
        "id": 2,
        "author": "Мария С.",
        "date": "7 мая 2024",
        "rating": 5,
        "text": "Добавляю щепу в сыр при созревании — вкус становится глубже и интереснее. Очень довольна результатом!",
        "photos": ["images/CubeMedium.png", "images/WoodChips.png", "images/Cube.png"],
        "product": "Кубики дубовые, средний обжиг",
        "avatar": None,
    },
    {
        "id": 3,
        "author": "Игорь К.",
        "date": "3 мая 2024",
        "rating": 5,
        "text": "Использую щепу для выдержки пива — получается отличный результат. Спасибо за стабильное качество!",
        "photos": ["images/WoodChipsLow.png", "images/WoodChips.png", "images/CubeMedium.png"],
        "product": "Дубовая щепа, средний обжиг",
        "avatar": None,
    },
    {
        "id": 4,
        "author": "Екатерина Л.",
        "date": "29 апреля 2024",
        "rating": 5,
        "text": "Очень понравилась упаковка и быстрая доставка. Щепа чистая, без пыли и посторонних запахов.",
        "photos": ["images/Cube.png", "images/WoodChips.png", "images/WoodChipsLow.png"],
        "product": "Дубовая щепа, лёгкий обжиг",
        "avatar": None,
    },
    {
        "id": 5,
        "author": "Виктор Д.",
        "date": "20 апреля 2024",
        "rating": 4,
        "text": "Хорошая щепа, аромат насыщенный. Чуть дольше ждал доставку, чем ожидал, но качеством доволен.",
        "photos": [],
        "product": "Дубовая щепа, сильный обжиг",
        "avatar": None,
    },
    {
        "id": 6,
        "author": "Наталья В.",
        "date": "15 апреля 2024",
        "rating": 5,
        "text": "Заказала для домашнего самогона — результат превзошёл ожидания. Напиток приобрёл благородный вкус и цвет.",
        "photos": [],
        "product": "Кубики дубовые, средний обжиг",
        "avatar": None,
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

# Подсчёт рейтинга из списка отзывов
def calc_rating(reviews):
    total = len(reviews)
    if total == 0:
        return {"average": 0, "total": 0, "breakdown": []}
    avg = round(sum(r["rating"] for r in reviews) / total, 1)
    breakdown = []
    for stars in range(5, 0, -1):
        count = sum(1 for r in reviews if r["rating"] == stars)
        breakdown.append({"stars": stars, "count": count})
    return {"average": avg, "total": total, "breakdown": breakdown}

# ─────────────────────────────────────────────
# ДОБАВЛЕНО: вспомогательная функция nav_links
# Проставляет active по имени endpoint-а
# (раньше active ставился через loop.first — ИЗМЕНЕНО)
# ─────────────────────────────────────────────

def make_nav_links(active_endpoint: str) -> list:
    links = [
        {"href": url_for("index"),   "label": "Главная",  "endpoint": "index"},
        {"href": url_for("catalog"), "label": "Каталог",  "endpoint": "catalog"},
        {"href": url_for("delivery"), "label": "Доставка", "endpoint": "delivery"},
        {"href": url_for("information"), "label": "Информация", "endpoint": "information"},
        {"href": url_for("contacts"), "label": "Контакты", "endpoint": "contacts"},
        {"href": url_for("reviews"), "label": "Отзывы",   "endpoint": "reviews"},
       
    ]
    for link in links:
        link["active"] = (link["endpoint"] == active_endpoint)
    return links


# ─────────────────────────────────────────────
# РОУТЫ
# ─────────────────────────────────────────────

# ── страница каталога главной──────────────
@app.route("/")
def index():
    return render_template(
        "index.html",
        products=PRODUCTS[:4],          # на главной — только 4 товара
        nav_links=make_nav_links("index"),
        meta=SITE_META,
    )


# ── страница каталога ──────────────
@app.route("/catalog")
def catalog():
    return render_template(
        "catalog.html",
        products=PRODUCTS,              # все товары
        nav_links=make_nav_links("catalog"),
        meta=SITE_META,
    )

@app.route("/profile")
def profile():
    # TODO: получать user из сессии/БД
    # user = db.get_user(session['user_id'])
    # orders = db.get_orders(user.id)
    # addresses = db.get_addresses(user.id)
    return render_template(
        "profile.html",
        nav_links=make_nav_links(None),
        meta=SITE_META,
        user=None,      # заглушка
        orders=None,    # заглушка
        addresses=None, # заглушка
    )

@app.route("/profile/save", methods=["POST"])
def profile_save():
    # TODO: сохранить в БД
    # first_name = request.form.get("first_name")
    # ...
    flash("Данные сохранены.", "success")
    return redirect(url_for("profile"))

@app.route("/profile/add-address", methods=["POST"])
def profile_add_address():
    # TODO: сохранить адрес в БД
    flash("Адрес добавлен.", "success")
    return redirect(url_for("profile"))

@app.route("/logout")
def logout():
    # TODO: session.clear() или logout_user() когда будет аутентификация
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("index"))

@app.route("/delivery")
def delivery():
    return render_template(
        "delivery.html",
        nav_links=make_nav_links("delivery"),
        meta=SITE_META,
    )

@app.route("/cart")
def cart():
    # TODO: получать корзину из сессии или БД
    # cart_items = session.get('cart', [])
    cart_items = DEMO_CART          # заглушка
    recommended = PRODUCTS[4:7]     # «Вам понравится»
    return render_template(
        "cart.html",
        cart_items=cart_items,
        recommended=recommended,
        nav_links=make_nav_links(None),
        meta=SITE_META,
    )

@app.route("/information")
def information():
    return render_template(
        "information.html",
        nav_links=make_nav_links("information"),
        meta=SITE_META,
    )
 
@app.route("/contacts")
def contacts():
    return render_template(
        "contacts.html",
        nav_links=make_nav_links("contacts"),
        meta=SITE_META,
    )

@app.route("/reviews")
def reviews():
    rating = calc_rating(REVIEWS)
    # На первый рендер отдаём первые 4 отзыва через Jinja,
    # все остальные — как JSON для кнопки «Показать ещё»
    return render_template(
        "reviews.html",
        nav_links=make_nav_links("reviews"),
        meta=SITE_META,
        reviews=REVIEWS[:4],
        reviews_json=json.dumps(REVIEWS, ensure_ascii=False),
        rating=rating,
    )

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
