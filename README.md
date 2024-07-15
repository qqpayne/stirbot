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
4. Выдача и лишение прав администратора для пользователя (который уже имеется в БД бота) производится с помощью команды:
   ```bash
   docker-compose exec -e "PYTHONPATH=/app" bot python scripts/admin.py {uid} [--demote]
   ```

## Контрибьютинг

### Необходимое ПО

- [Docker](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/) последних версий
- [VS Code](https://code.visualstudio.com/) для более удобной работы (есть вариант установки и без него)
- В случае установки без VS Code, понадобится [Poetry](https://python-poetry.org/) для добавления\обновления зависимостей

### Установка среды для разработки

1. Скопируйте репозиторий
   ```bash
   git clone https://github.com/qqpayne/stirbot
   ```
2. Откройте VS Code в папке репозитория
    ```bash
    code stirbot
    ```
3. Создайте и заполните файл `.env` по образцу файла `.env.example`
4. Установите расширение "Remote - Containers" (`ms-vscode-remote.remote-containers`); всплывающая подсказка с предложением установить его будет доступна в правом нижнем углу экрана редактора
5. В подсказке в правом нижнем углу экрана редактора нажмите "Reopen in Container" или нажмите `Ctrl+Shift+P` и выберите "Reopen in Container"

После того как контейнер забилдится, вы получите окружение со всеми установленными зависимостями, автоформатированием и линтингом (все настройки хранятся в ".vscode/settings.json"). Также внутри контейнера есть рабочая база данных и Redis, для редактирования можно пользоваться pgadmin4 на 7731 порту.

#### Полезные команды

Эти команды нужно вводить в встроенном интервале VS Code, то есть так чтобы они исполнялись внутри Dev Container'а.

1. Запуск бота (убедитесь что ввели токен не с продакшна в `.env`)
   ```bash
   python -m app
   ```
2. Создание новой миграции
   ```bash
   alembic revision --autogenerate -m "<описание изменений>"
   ```
3. Применение всех миграций базы данных
   ```bash
   alembic upgrade head
   ```
4. Выдать права администратора пользователю с указанным Telegram ID (он должен уже быть в БД бота)
   ```bash
   python scripts/admin.py {uid}
   ```

#### Без Dev Container

Если вы не хотите разворачивать [Dev Container](https://code.visualstudio.com/docs/remote/containers), но хотите пользоваться автоформатированием и линтингом, то следуйте этим шагам:

1. Установите линтеры, форматтеры и прочее
   ```bash
    cd stirbot
    poetry install
   ```
2. Зарегистрируйте [pre-commit](https://pre-commit.com/) хук
   ```bash
    ./.venv/bin/pre-commit install
   ```
3. Откройте VS Code в папке репозитория
   ```bash
    code .
   ```

Правда, для запуска бота необходима база данных PostgreSQL и Redis, поэтому для тестов придется каждый раз полноценно развертывать проект.
