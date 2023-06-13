# Продуктовый помощник - Foodgram

#### *Дипломная работа*

## Технологии:
- Python 3.9
- Django 3.2
- Django REST framework 3.13
- Nginx
- Docker
- Postgres

### http://158.160.15.136/


### Поехали:
- Скачиваем проект
```
git clone https://github.com/kvot32/foodgram-project-react.git
```
- Подключаемся к серверу
```
ssh <server user>@<public server IP>
```
- Устанавливаем докер
```
sudo apt install docker.io
```
- Устанавливаем Docker-Compose (для Linux)
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
- Получаем права для docker-compose
```
sudo chmod +x /usr/local/bin/docker-compose
```
- Скидываем файлы docker-compose.yaml и nginx.conf на сервер, сделать это можно командой (в случае удаленного запуска)
```
scp docker-compose.yaml <username>@<public ip adress>:/home/<username>/docker-compose.yaml
```
- Настройка переменных окружения:

 В корневой папке проекта необходимо создать файл .env и и заполните его данными из файла .env.example
```

Для загрузки своих ингредиентов, вам нужно в папке data заменить файл ingredients.json, наполненный вашими ингредиентами. Они заполняются после выполнения миграции.
