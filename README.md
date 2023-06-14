# Foodrgam

 Продуктовый помощник - дипломный проект курса на Яндекс.Практикум.

## О проекте 

- Проект упакован в Docker-контейнерах;
- Проект был развернут на сервере: <http://51.250.9.96>
  
## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker

## Зависимости
- Перечислены в файле backend/requirements.txt


## Для запуска на собственном сервере

1. Установите на сервере `docker` и `docker compose`
2. Создайте файл `/infra/.env` Шаблон для заполнения файла нахоится в `/infra/.env.example`
3. Из директории `/infra/` выполните команду `docker-compose up -d --build`
5. Выполните миграции `docker compose exec -it app python manage.py migrate`
6. Создайте Администратора `docker compose exec -it app python manage.py createsuperuser`
7. Соберите статику `docker compose exec app python manage.py collectstatic --no-input`
8. Из директории `/backend/` Загрузите фикстуры в Базу 

    `sudo docker exec -it app python manage.py load_data fixtures.json`


