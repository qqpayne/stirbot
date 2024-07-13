# stirbot
Телеграм-бот для записи на пользование стиральной машиной в коливингах и общежитиях.

## Развертывание

Для развертывания понадобится [Docker](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/) последних версий.

1. Скопируйте репозиторий
   ```bash
   git clone https://github.com/qqpayne/stirbot
   ```
2. Создайте и заполните файл `.env` с вашими данными по образцу файла `.env.example`. Если вы хотите применить миграции БД созданные с помощью `alembic`, то укажите `DO_MIGRATE=true`.
3. Запустите контейнеры
   ```bash
   docker-compose up -d
   ```
