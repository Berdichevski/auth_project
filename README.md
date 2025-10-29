# Custom Auth & RBAC (Django DRF + PostgreSQL)

Кастомные аутентификация (bcrypt+JWT) и авторизация (RBAC).<br>
— Регистрация, логин/логаут, профиль (GET/PUT/DELETE soft)<br>
— RBAC через таблицы Role, BusinessElement, AccessRoleRule<br>
— Mock products с проверкой "свои/все"<br>

## Установка
python -m venv venv <br>
.\venv\Scripts\Activate.ps1 <br>
pip install -r requirements.txt

# Переменные окружения
DJANGO_SECRET_KEY <br>
DB_NAME <br>
DB_USER <br>
DB_PASSWORD <br>
DB_HOST <br>
DB_PORT

python manage.py makemigrations access accounts business <br>
python manage.py migrate

## Сидинг (пример)
python manage.py shell <<'PY' <br>
from access.models import Role,BusinessElement,AccessRoleRule <br>
from accounts.models import User

r_admin=Role.objects.create(name='admin') <br>
r_manager=Role.objects.create(name='manager') <br>
r_user=Role.objects.create(name='user') <br>
r_guest=Role.objects.create(name='guest') <br>

el_users=BusinessElement.objects.create(name='users') <br>
el_products=BusinessElement.objects.create(name='products') <br>
el_orders=BusinessElement.objects.create(name='orders') <br>

for el in (el_users,el_products,el_orders): <br>
    AccessRoleRule.objects.create(role=r_admin, element=el, <br>
        read_permission=True, read_all_permission=True, <br>
        create_permission=True,<br>
        update_permission=True, update_all_permission=True, <br>
        delete_permission=True, delete_all_permission=True) <br>

AccessRoleRule.objects.create(role=r_user, element=el_users, <br>
    read_permission=True, update_permission=True, delete_permission=True) <br>
AccessRoleRule.objects.create(role=r_user, element=el_products, <br>
    read_permission=True, create_permission=True, update_permission=True, delete_permission=True) <br>
AccessRoleRule.objects.create(role=r_user, element=el_orders, <br>
    read_permission=True, create_permission=True, update_permission=True, delete_permission=True) <br>

AccessRoleRule.objects.create(role=r_manager, element=el_products, <br>
    read_permission=True, read_all_permission=True, create_permission=True, update_permission=True, update_all_permission=True) <br>
AccessRoleRule.objects.create(role=r_manager, element=el_orders, <br>
    read_permission=True, read_all_permission=True) <br>

User.objects.create_user(email='admin@example.com', password='admin123', first_name='Admin', last_name='Root', role=r_admin) <br>
User.objects.create_user(email='user1@example.com', password='user12345', first_name='Ivan', last_name='Ivanov', role=r_user) <br>
User.objects.create_user(email='user2@example.com', password='user12345', first_name='Petr', last_name='Petrov', role=r_user) <br>
PY

## Запуск
python manage.py runserver

## Эндпоинты
POST /api/register/ <br>
POST /api/login/ <br>
POST /api/logout/ <br>
GET  /api/profile/ <br>
PUT  /api/profile/ <br>
DELETE /api/profile/  # soft delete (is_active=False) <br>
GET  /api/products/   # mock <br>
GET  /api/access-rules/ <br>
POST /api/access-rules/ <br>
PUT /api/access-rules/  # только admin <br>
GET/POST /api/roles/ <br> 
GET/POST /api/elements/  # только admin <br>

## Авторизация
— Без токена или неверный токен → 401 <br>
— Токен есть, но прав нет → 403 

## Примечание
Мы не используем встроенный DRF TokenAuth / SessionAuth. <br> 
