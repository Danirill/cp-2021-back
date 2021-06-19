# Bafomet REST api

### Запуск на digital ocean
1. `git checkout master` Если не на мастере
2. `git pull origin master`
3. `docker-compose up --build -d`
4. `docker-compose run web python manage.py makemigrations`
5. `docker-compose run web python manage.py migrate`
6. в папку `compose/nginx/` нужно установить SSL Сертификаты при необходимости

### Перезапуск сервера
3. `cd django-wellbe-api/`
4. `docker-compose restart` Если не сработало, то  `docker-compose stop` и `docker-compose up --build -d`
----------------------
#### Используемые технологии
Python, Django + DRF + CELERY,  PostgreSQL, Redis, Docker, RabbitMQ
