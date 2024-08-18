START_TEXT = "Этот бот предназначен для записи на стирку и в комнату отдыха ФФФХИ."
ADMIN_USER_START_TEXT = (
    START_TEXT
    + " Ваш аккаунт подтвержден и имеет администраторский доступ. Для получения списка команд используйте /help."
)
REGISTERED_USER_START_TEXT = START_TEXT + " Ваш аккаунт подтвержден. Для получения списка команд используйте /help."

SUGGEST_SIGNUP_TEXT = """
Если вы учитесь на ФФФХИ, то отправьте команду /signup.
Если вы не учитесь на ФФФХИ, то хорошего вам дня, всего счастливого.
"""
UNKNOWN_USER_START_TEXT = START_TEXT + SUGGEST_SIGNUP_TEXT

SIGNUP_TEXT = (
    "Ваш аккаунт зарегистрирован и ждет подтверждения. Обратитесь к администратору {admin_link} для подтверждения."
)
SIGNUP_WAIT_TEXT = "Ожидайте подтверждения аккаунта. Можете вновь обратиться к администратору {admin_link}."

commands = {
    "help": "список команд",
    "booking": "меню для записи",
    "notifications": "управление уведомлениями",
    "rules": "правила пользования",
    "report": "сообщить о нарушении или ошибке",
}
admin_commands = {
    "new_users": "подтверждение новых аккаунтов",
}

HELP_TEXT = "Доступны следующие команды:\n" + "\n".join(
    [f"/{command} - {description}" for command, description in commands.items()]
)
ADMIN_HELP_TEXT = (
    HELP_TEXT
    + "\n\nАдминистраторские команды:\n"
    + "\n".join([f"/{command} - {description}" for command, description in admin_commands.items()])
)

RULES_TEXT = """
Правила пользования стиральными машинами:
1) Записаться можно максимум на 2 часа в день.
2) Если вы просыпали порошок, необходимо убрать за собой.
3) Если машина закончила работу, но на табло остаётся время - не стоит пробовать её открыть; нужно дождаться остывания встроенного термозамка.
4) Если вы пришли стираться, а машинка занята и никто не появляется, то можете смело принудительно завершать стирку и отложить мокрые вещи. Хозяин этих вещей поймет, что прежде чем стираться, нужно записаться.
"""  # noqa: E501

REPORT_TEXT = "Доложить о проблемах с ботом или каком-либо происшествии можно администратору {admin_link}."

NOT_A_USER_ERROR_TEXT = "Ошибка. Вы не пользователь. Кто вы вообще?"

NO_NEW_USERS_TEXT = "Нет пользователей ожидающих подтверждения аккаунта."
NEW_USER_TEXT = "Пользователь {user_name} запрашивает доступ к боту."
NEW_USER_ALREADY_DENIED_TEXT = "Доступ для пользователя c id={user_id} уже был ранее отклонен"
NEW_USER_ALREADY_APPROVED_TEXT = "Доступ для пользователя {user_name} уже был одобрен ранее."
NEW_USER_DENIED_TEXT = "Запрос доступа пользователя {user_name} был отклонен."
NEW_USER_APPROVED_TEXT = "Доступ для пользователя {user_name} был одобрен."
NEW_USER_ERROR_TEXT = "Произошла ошибка! Попробуйте еще раз."

BOOKING_CHOOSE_ACTION_TEXT = "Выберите действие:"
BOOKING_ACTION_NEW_TEXT = "Создать новую запись"
BOOKING_ACTION_EDIT_TEXT = "Просмотр и удаление записей"

NEW_BOOKING_CHOOSE_PLACE_TEXT = "Выберите место:"
NEW_BOOKING_CHOOSE_DAY_TEXT = "Выберите день:"
NEW_BOOKING_AVAILABLE_INTERVALS_TEXT = "{date} в {place} доступны интервалы:"
NEW_BOOKING_INTERVAL_HELP_TEXT = (
    'Для записи отправьте сообщение в формате {начало записи} - {конец записи}, например "11:00 - 12:30"'
)
NEW_BOOKING_RESULT_TEXT = "Записал в {place} на {date} с {start_time} до {end_time}"

EDIT_BOOKING_LIST_TEXT = "Список ваших активных записей:"
EDIT_BOOKING_DELETE_TEXT = "Выберите запись для отмены:"
EDIT_BOOKING_DELETE_ACTION_TEXT = "Редактировать"

BACK_TEXT = "↩️ Назад"
ERROR_TEXT = "Ошибка: {error}"
