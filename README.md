# Custom Auth & RBAC (Django DRF + PostgreSQL)

Кастомные аутентификация (bcrypt+JWT) и авторизация (RBAC).
— Регистрация, логин/логаут, профиль (GET/PUT/DELETE soft)
— RBAC через таблицы Role, BusinessElement, AccessRoleRule
— Mock products с проверкой "свои/все"

## Установка
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# переменные окружения (пример)
export DJANGO_SECRET_KEY='dev-secret'
export DB_NAME='authdb'
export DB_USER='authuser'
export DB_PASSWORD='authpass'
export DB_HOST='127.0.0.1'
export DB_PORT='5432'

python manage.py makemigrations access accounts business
python manage.py migrate

## Сидинг (минимум)
python manage.py shell <<'PY'
from access.models import Role,BusinessElement,AccessRoleRule
from accounts.models import User

r_admin=Role.objects.create(name='admin')
r_manager=Role.objects.create(name='manager')
r_user=Role.objects.create(name='user')
r_guest=Role.objects.create(name='guest')

el_users=BusinessElement.objects.create(name='users')
el_products=BusinessElement.objects.create(name='products')
el_orders=BusinessElement.objects.create(name='orders')

for el in (el_users,el_products,el_orders):
    AccessRoleRule.objects.create(role=r_admin, element=el,
        read_permission=True, read_all_permission=True,
        create_permission=True,
        update_permission=True, update_all_permission=True,
        delete_permission=True, delete_all_permission=True)

AccessRoleRule.objects.create(role=r_user, element=el_users,
    read_permission=True, update_permission=True, delete_permission=True)
AccessRoleRule.objects.create(role=r_user, element=el_products,
    read_permission=True, create_permission=True, update_permission=True, delete_permission=True)
AccessRoleRule.objects.create(role=r_user, element=el_orders,
    read_permission=True, create_permission=True, update_permission=True, delete_permission=True)

AccessRoleRule.objects.create(role=r_manager, element=el_products,
    read_permission=True, read_all_permission=True, create_permission=True, update_permission=True, update_all_permission=True)
AccessRoleRule.objects.create(role=r_manager, element=el_orders,
    read_permission=True, read_all_permission=True)

User.objects.create_user(email='admin@example.com', password='admin123', first_name='Admin', last_name='Root', role=r_admin)
User.objects.create_user(email='user1@example.com', password='user12345', first_name='Ivan', last_name='Ivanov', role=r_user)
User.objects.create_user(email='user2@example.com', password='user12345', first_name='Petr', last_name='Petrov', role=r_user)
print('Seed complete')
PY

## Запуск
python manage.py runserver

## Эндпоинты
POST /api/register/
POST /api/login/
POST /api/logout/
GET  /api/profile/
PUT  /api/profile/
DELETE /api/profile/  # soft delete (is_active=False)
GET  /api/products/   # mock, по правилам RBAC
GET  /api/access-rules/ ; POST /api/access-rules/ ; PUT /api/access-rules/  # только admin
GET/POST /api/roles/ ; GET/POST /api/elements/  # только admin

## Авторизация
— Без токена или неверный токен → 401
— Токен есть, но прав нет → 403

## Примечание
Мы намеренно не используем встроенный DRF TokenAuth / SessionAuth. request.user выставляется кастомным JWT-мидлваром.
