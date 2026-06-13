import os
import json
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from models import db, Product, ProductImage, User, Order, OrderItem, Review, ContactRequest, Address

pymysql.install_as_MySQLdb()
load_dotenv()

app = Flask(__name__)

# ─── КОНФИГУРАЦИЯ ────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", "dev-fallback-key")

# Глобальный флаг доступности БД
DB_AVAILABLE = False

# Пробуем настроить БД, но не блокируем запуск при ошибке
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_timeout": 20,
        "max_overflow": 0,
    }
    db.init_app(app)
    
    # Создаём таблицы при старте, но не блокируем запуск при ошибке подключения
    try:
        with app.app_context():
            db.create_all()
        DB_AVAILABLE = True
        print("[INFO] База данных подключена успешно")
    except Exception as e:
        print(f"[WARNING] Не удалось создать таблицы БД: {e}")
        print("[WARNING] Приложение запустится в режиме без БД")
else:
    # Режим без БД
    print("[INFO] DATABASE_URL не указан, работа без БД")

# ─── FLASK-LOGIN ──────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = "index"          # куда редиректить если не авторизован
login_manager.login_message = "Войдите в аккаунт для доступа к этой странице."
login_manager.login_message_category = "error"

@login_manager.user_loader
def load_user(user_id):
    if not DB_AVAILABLE:
        return None
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


# ─────────────────────────────────────────────────────────
# СТАТИЧЕСКИЕ ДАННЫЕ
# ─────────────────────────────────────────────────────────

PRODUCTS = [
    {
        "id": 1,
        "name": "Щепа дубовая — лёгкий обжиг",
        "description": "Мягкий ванильный аромат, золотистый цвет. Идеально для самогона и кальвадоса.",
        "price": 700,
        "weight": "500 гр.",
        "badge": "Хит",
        "image_url": "images/WoodChipsLow.png",
    },
    {
        "id": 2,
        "name": "Щепа дубовая — средний обжиг",
        "description": "Баланс ванили и карамели. Универсальный выбор для виски и коньяка.",
        "price": 700,
        "weight": "500 гр.",
        "badge": "Топ продаж",
        "image_url": "images/WoodChips.png",
    },
    {
        "id": 3,
        "name": "Щепа дубовая — сильный обжиг",
        "description": "Глубокий дымный вкус с нотами шоколада и кофе. Для тёмных дистиллятов.",
        "price": 700,
        "weight": "500 гр.",
        "badge": None,
        "image_url": "images/Cube.png",
    },
    {
        "id": 4,
        "name": "Кубик дубовый - средний обжиг",
        "description": "Дубовые кубики для настаивания самогона, спирта и других крепких напитков.",
        "price": 700,
        "weight": "500 гр.",
        "badge": "Новинка",
        "image_url": "images/CubeMedium.png",
    },
    {
        "id": 5,
        "name": "Щепа дубовая — лёгкий обжиг",
        "description": "Мягкий ванильный аромат, золотистый цвет. Идеально для самогона и кальвадоса.",
        "price": 700,
        "weight": "500 гр.",
        "badge": "Хит",
        "image_url": "images/WoodChipsLow.png",
    },
    {
        "id": 6,
        "name": "Щепа дубовая — средний обжиг",
        "description": "Баланс ванили и карамели. Универсальный выбор для виски и коньяка.",
        "price": 700,
        "weight": "500 гр.",
        "badge": "Топ продаж",
        "image_url": "images/WoodChips.png",
    },
    {
        "id": 7,
        "name": "Щепа дубовая — сильный обжиг",
        "description": "Глубокий дымный вкус с нотами шоколада и кофе. Для тёмных дистиллятов.",
        "price": 700,
        "weight": "500 гр.",
        "badge": None,
        "image_url": "images/Cube.png",
    },
    {
        "id": 8,
        "name": "Кубик дубовый - средний обжиг",
        "description": "Крупная фракция для длительной выдержки. Равномерная экстракция.",
        "price": 700,
        "weight": "500 гр.",
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
        "text": "Щепа отличного качества! Настойки приобретают мягкий аромат и красивый янтарный цвет.",
        "photos": ["images/WoodChips.png", "images/WoodChipsLow.png", "images/Cube.png"],
        "product": "Дубовая щепа, сильный обжиг",
        "avatar": None,
    },
    {
        "id": 2,
        "author": "Мария С.",
        "date": "7 мая 2024",
        "rating": 5,
        "text": "Добавляю щепу в сыр при созревании — вкус становится глубже и интереснее.",
        "photos": ["images/CubeMedium.png", "images/WoodChips.png"],
        "product": "Кубики дубовые, средний обжиг",
        "avatar": None,
    },
    {
        "id": 3,
        "author": "Игорь К.",
        "date": "3 мая 2024",
        "rating": 5,
        "text": "Использую щепу для выдержки пива — получается отличный результат.",
        "photos": ["images/WoodChipsLow.png", "images/WoodChips.png"],
        "product": "Дубовая щепа, средний обжиг",
        "avatar": None,
    },
    {
        "id": 4,
        "author": "Екатерина Л.",
        "date": "29 апреля 2024",
        "rating": 5,
        "text": "Очень понравилась упаковка и быстрая доставка. Щепа чистая, без пыли.",
        "photos": [],
        "product": "Дубовая щепа, лёгкий обжиг",
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


# ─────────────────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────────────────

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


def make_nav_links(active_endpoint: str) -> list:
    links = [
        {"href": url_for("index"),       "label": "Главная",    "endpoint": "index"},
        {"href": url_for("catalog"),     "label": "Каталог",    "endpoint": "catalog"},
        {"href": url_for("delivery"),    "label": "Доставка",   "endpoint": "delivery"},
        {"href": url_for("information"), "label": "Информация", "endpoint": "information"},
        {"href": url_for("contacts"),    "label": "Контакты",   "endpoint": "contacts"},
        {"href": url_for("reviews"),     "label": "Отзывы",     "endpoint": "reviews"},
    ]
    for link in links:
        link["active"] = (link["endpoint"] == active_endpoint)
    return links


# ─────────────────────────────────────────────────────────
# АУТЕНТИФИКАЦИЯ
# ─────────────────────────────────────────────────────────

@app.route("/login", methods=["POST"])
def login():
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    remember = bool(request.form.get("remember"))
    next_url = request.form.get("next") or url_for("index")

    if not email or not password:
        flash("Заполните все поля.", "error")
        return redirect(next_url)

    if not DB_AVAILABLE:
        flash("База данных недоступна. Вход невозможен.", "error")
        return redirect(next_url)

    try:
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Добро пожаловать, {user.first_name or user.email}!", "success")
            return redirect(next_url)
        flash("Неверный e-mail или пароль.", "error")
    except Exception as e:
        print(f"[ERROR] Ошибка при входе: {e}")
        flash("Ошибка базы данных. Попробуйте позже.", "error")
    return redirect(next_url)


@app.route("/register", methods=["POST"])
def register():
    first_name = request.form.get("first_name", "").strip()
    email      = request.form.get("email", "").strip().lower()
    password   = request.form.get("password", "")
    password2  = request.form.get("password2", "")
    next_url   = request.form.get("next") or url_for("index")

    if not first_name or not email or not password:
        flash("Заполните все обязательные поля.", "error")
        return redirect(next_url)

    if password != password2:
        flash("Пароли не совпадают.", "error")
        return redirect(next_url)

    if len(password) < 6:
        flash("Пароль должен быть не менее 6 символов.", "error")
        return redirect(next_url)

    if not DB_AVAILABLE:
        flash("База данных недоступна. Регистрация невозможна.", "error")
        return redirect(next_url)

    try:
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким e-mail уже существует.", "error")
            return redirect(next_url)

        user = User(first_name=first_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Аккаунт создан! Добро пожаловать, {first_name}!", "success")
    except Exception as e:
        print(f"[ERROR] Ошибка при регистрации: {e}")
        flash("Ошибка базы данных. Попробуйте позже.", "error")
    return redirect(next_url)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────
# ОСНОВНЫЕ РОУТЫ
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        products=PRODUCTS[:4],
        nav_links=make_nav_links("index"),
        meta=SITE_META,
    )


@app.route("/catalog")
def catalog():
    return render_template(
        "catalog.html",
        products=PRODUCTS,
        nav_links=make_nav_links("catalog"),
        meta=SITE_META,
    )


@app.route("/profile")
@login_required
def profile():
    # Реальные заявки пользователя из БД
    orders = []
    addresses = []

    if DB_AVAILABLE:
        try:
            orders = ContactRequest.query.filter_by(
                email=current_user.email
            ).order_by(ContactRequest.created_at.desc()).all()
            addresses = Address.query.filter_by(user_id=current_user.id).all()
        except Exception as e:
            print(f"[ERROR] Ошибка при загрузке профиля: {e}")
            flash("Не удалось загрузить данные из БД", "warning")

    return render_template(
        "profile.html",
        nav_links=make_nav_links(None),
        meta=SITE_META,
        user=current_user,
        orders=orders,
        addresses=addresses,
    )


@app.route("/profile/save", methods=["POST"])
@login_required
def profile_save():
    if not DB_AVAILABLE:
        flash("База данных недоступна. Сохранение невозможно.", "error")
        return redirect(url_for("profile"))

    try:
        current_user.first_name = request.form.get("first_name", "").strip()
        current_user.last_name  = request.form.get("last_name", "").strip()
        current_user.email      = request.form.get("email", "").strip().lower()
        current_user.phone      = request.form.get("phone", "").strip()
        db.session.commit()
        flash("Данные сохранены.", "success")
    except Exception as e:
        print(f"[ERROR] Ошибка при сохранении профиля: {e}")
        flash("Ошибка при сохранении данных.", "error")
    return redirect(url_for("profile"))


@app.route("/profile/add-address", methods=["POST"])
@login_required
def profile_add_address():
    address_text = request.form.get("address", "").strip()
    contact      = request.form.get("contact", "").strip()
    is_main      = bool(request.form.get("is_main"))

    if not address_text:
        flash("Укажите адрес.", "error")
        return redirect(url_for("profile"))

    if not DB_AVAILABLE:
        flash("База данных недоступна. Добавление адреса невозможно.", "error")
        return redirect(url_for("profile"))

    try:
        # Если новый адрес — основной, снимаем флаг с остальных
        if is_main:
            Address.query.filter_by(user_id=current_user.id).update({"is_main": False})

        addr = Address(
            user_id=current_user.id,
            address=address_text,
            contact=contact,
            is_main=is_main,
        )
        db.session.add(addr)
        db.session.commit()
        flash("Адрес добавлен.", "success")
    except Exception as e:
        print(f"[ERROR] Ошибка при добавлении адреса: {e}")
        flash("Ошибка при добавлении адреса.", "error")
    return redirect(url_for("profile"))


@app.route("/delivery")
def delivery():
    return render_template(
        "delivery.html",
        nav_links=make_nav_links("delivery"),
        meta=SITE_META,
    )


@app.route("/cart")
def cart():
    cart_items  = DEMO_CART
    recommended = PRODUCTS[4:7]
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

    if not DB_AVAILABLE:
        flash("Ваша заявка принята! (База данных недоступна, заявка не сохранена)", "warning")
        return redirect(url_for("index") + "#faq")

    try:
        new_request = ContactRequest(
            name=name,
            phone=phone,
            email=email,
            contact_method=contact_method,
            call_time=call_time if contact_method == "phone" else None,
            message=message,
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Ваша заявка принята! Мы свяжемся с вами в ближайшее время.", "success")
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке заявки: {e}")
        flash("Ошибка при отправке заявки. Попробуйте позже.", "error")
    return redirect(url_for("index") + "#faq")


if __name__ == "__main__":
    app.run(debug=True, port=5000)