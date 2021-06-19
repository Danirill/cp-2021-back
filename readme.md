# Wellbe REST api

### Ссылки
1.  <a href="https://wellbehealth.github.io/wellbe-api-docs/#/">Документация API</a>
2. <a href="https://trello.com/b/edDeHHdM/%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0">Trello</a>
3. `188.166.73.50` Wellbe-dev droplet

### Запуск на digital ocean
1. `git checkout master` Если не на мастере
2. `git pull origin master`
3. `docker-compose up --build -d`
4. `docker-compose run web python manage.py makemigrations`
5. `docker-compose run web python manage.py migrate`
6. в папку `compose/nginx/` нужно установить SSL Сертификаты при необходимости

### Админ панели
1. `api.wellbe.club/admin` - Django Administration
2. `http://138.197.100.209/:9090` - PGadmin

### Перезапуск сервера
1. `ssh root@188.166.73.50` Пароль есть в Notion/Trello либо через ssh ключ
2. `docker-machine ssh wellbe-backend`
3. `cd django-wellbe-api/`
4. `docker-compose restart` Если не сработало, то  `docker-compose stop` и `docker-compose up --build -d`
----------------------
#### Используемые технологии
Python, Django + DRF + CELERY,  PostgreSQL, Redis, Docker

#### Интеграции
Gmail, Daily.co
