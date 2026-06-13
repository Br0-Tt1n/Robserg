"""
models.py — все модели базы данных для Robserg
Расположение: папка проекта, рядом с app.py
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ═══════════════════════════════════════════════════════════
#  ПОЛЬЗОВАТЕЛИ
# ═══════════════════════════════════════════════════════════

class User(UserMixin, db.Model):
    """Зарегистрированные пользователи сайта"""
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name    = db.Column(db.String(60))
    last_name     = db.Column(db.String(60))
    phone         = db.Column(db.String(30))
    is_admin      = db.Column(db.Boolean, default=False)   # для будущей админки
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    orders   = db.relationship("Order",   back_populates="user", lazy="dynamic")
    reviews  = db.relationship("Review",  back_populates="user", lazy="dynamic")
    addresses = db.relationship("Address", back_populates="user", lazy="dynamic")

    # ── Пароль ──────────────────────────────────────────────
    def set_password(self, password: str):
        """Хэшируем пароль — никогда не храним открытым текстом"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email

    def __repr__(self):
        return f"<User {self.id} {self.email}>"


# ═══════════════════════════════════════════════════════════
#  АДРЕСА ДОСТАВКИ
# ═══════════════════════════════════════════════════════════

class Address(db.Model):
    """Сохранённые адреса доставки пользователя"""
    __tablename__ = "addresses"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    address    = db.Column(db.String(300), nullable=False)
    contact    = db.Column(db.String(200))          # контактное лицо + телефон
    is_main    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    user = db.relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"<Address {self.id} user={self.user_id}>"


# ═══════════════════════════════════════════════════════════
#  ТОВАРЫ
# ═══════════════════════════════════════════════════════════

class Product(db.Model):
    """Товары каталога"""
    __tablename__ = "products"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Integer, nullable=False)     # в рублях, целое число
    weight      = db.Column(db.String(50))                  # "500 гр.", "1 кг." и т.д.
    badge       = db.Column(db.String(50))                  # "Хит", "Новинка" и т.д.
    is_active   = db.Column(db.Boolean, default=True)       # скрыть/показать товар
    sort_order  = db.Column(db.Integer, default=0)          # порядок в каталоге
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    images      = db.relationship(
        "ProductImage",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan"   # удаление товара → удаление фото
    )
    reviews     = db.relationship("Review",     back_populates="product", lazy="dynamic")
    order_items = db.relationship("OrderItem",  back_populates="product", lazy="dynamic")

    @property
    def main_image(self):
        """Возвращает главное фото товара (или первое, если главное не задано)"""
        img = self.images.filter_by(is_main=True).first()
        if not img:
            img = self.images.first()
        return img.image_url if img else "images/placeholder.png"

    @property
    def all_images(self):
        """Список всех фото товара"""
        return self.images.all()

    @property
    def rating(self):
        """Средний рейтинг по отзывам"""
        approved = self.reviews.filter_by(is_approved=True).all()
        if not approved:
            return None
        return round(sum(r.rating for r in approved) / len(approved), 1)

    @property
    def reviews_count(self):
        return self.reviews.filter_by(is_approved=True).count()

    def to_dict(self):
        """Для передачи в Jinja2 / JSON"""
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "price":       self.price,
            "weight":      self.weight,
            "badge":       self.badge,
            "image_url":   self.main_image,
        }

    def __repr__(self):
        return f"<Product {self.id} {self.name}>"


class ProductImage(db.Model):
    """Фотографии товаров — хранятся отдельно, у одного товара может быть несколько"""
    __tablename__ = "product_images"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    image_url  = db.Column(db.String(500), nullable=False)  # путь static/images/... или URL CDN
    is_main    = db.Column(db.Boolean, default=False)       # главное фото в карточке
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    product = db.relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage {self.id} product={self.product_id}>"


# ═══════════════════════════════════════════════════════════
#  ЗАКАЗЫ
# ═══════════════════════════════════════════════════════════

class Order(db.Model):
    """Заказы пользователей"""
    __tablename__ = "orders"

    # Возможные статусы заказа
    STATUS_NEW        = "new"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED    = "shipped"
    STATUS_DELIVERED  = "delivered"
    STATUS_CANCELLED  = "cancelled"

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
                                                            # nullable — гость без аккаунта
    # Контактные данные (дублируем на случай если пользователь удалит аккаунт)
    contact_name     = db.Column(db.String(120))
    contact_phone    = db.Column(db.String(30))
    contact_email    = db.Column(db.String(120))

    delivery_address = db.Column(db.String(300))
    status           = db.Column(db.String(30), default=STATUS_NEW)
    total_price      = db.Column(db.Integer, nullable=False)  # в рублях
    comment          = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    user  = db.relationship("User",      back_populates="orders")
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        lazy="joined",                  # загружаем позиции вместе с заказом
        cascade="all, delete-orphan"
    )

    @property
    def status_label(self) -> str:
        """Читаемый статус на русском"""
        labels = {
            self.STATUS_NEW:        "Новый",
            self.STATUS_PROCESSING: "В обработке",
            self.STATUS_SHIPPED:    "Отправлен",
            self.STATUS_DELIVERED:  "Доставлен",
            self.STATUS_CANCELLED:  "Отменён",
        }
        return labels.get(self.status, self.status)

    @property
    def items_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f"<Order {self.id} user={self.user_id} status={self.status}>"


class OrderItem(db.Model):
    """Позиции в заказе — отдельная строка на каждый товар"""
    __tablename__ = "order_items"

    id                 = db.Column(db.Integer, primary_key=True)
    order_id           = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id         = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
                                                            # nullable — товар могут удалить
    product_name       = db.Column(db.String(200))         # фиксируем название на момент заказа
    price_at_purchase  = db.Column(db.Integer, nullable=False)  # фиксируем цену на момент заказа
    quantity           = db.Column(db.Integer, nullable=False, default=1)

    # Связи
    order   = db.relationship("Order",   back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    @property
    def subtotal(self) -> int:
        return self.price_at_purchase * self.quantity

    def __repr__(self):
        return f"<OrderItem {self.id} order={self.order_id} product={self.product_id}>"


# ═══════════════════════════════════════════════════════════
#  ОТЗЫВЫ
# ═══════════════════════════════════════════════════════════

class Review(db.Model):
    """
    Отзывы — связаны одновременно с пользователем и товаром.
    Перед показом на сайте проходят модерацию (is_approved).
    """
    __tablename__ = "reviews"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    rating      = db.Column(db.Integer, nullable=False)     # от 1 до 5
    text        = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)      # модерация
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    user    = db.relationship("User",    back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")
    photos  = db.relationship(
        "ReviewPhoto",
        back_populates="review",
        lazy="joined",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Review {self.id} user={self.user_id} product={self.product_id} ★{self.rating}>"


class ReviewPhoto(db.Model):
    """Фотографии в отзывах"""
    __tablename__ = "review_photos"

    id         = db.Column(db.Integer, primary_key=True)
    review_id  = db.Column(db.Integer, db.ForeignKey("reviews.id"), nullable=False)
    image_url  = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    review = db.relationship("Review", back_populates="photos")

    def __repr__(self):
        return f"<ReviewPhoto {self.id} review={self.review_id}>"


# ═══════════════════════════════════════════════════════════
#  ЗАЯВКИ ИЗ ФОРМЫ ОБРАТНОЙ СВЯЗИ
# ═══════════════════════════════════════════════════════════

class ContactRequest(db.Model):
    """Заявки из формы на главной и странице контактов"""
    __tablename__ = "contact_requests"

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(120), nullable=False)
    phone          = db.Column(db.String(30))
    email          = db.Column(db.String(120))
    contact_method = db.Column(db.String(20))   # phone / email / vk / max
    call_time      = db.Column(db.String(30))   # удобное время звонка
    message        = db.Column(db.Text)
    is_read        = db.Column(db.Boolean, default=False)  # прочитана ли заявка
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactRequest {self.id} {self.name}>"