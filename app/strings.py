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
UNAUTH_CALLBACK_TEXT = "Ошибка. У вас нет доступа к этому функционалу."

NO_NEW_USERS_TEXT = "Нет пользователей ожидающих подтверждения аккаунта."
NEW_USER_TEXT = "Пользователь {user_name} запрашивает доступ к боту."
NEW_USER_APPROVE_TEXT = "Подтвердить"
NEW_USER_DENY_TEXT = "Отказать"
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
NEW_BOOKING_NO_INTERVALS_LEFT_TEXT = "{date} в {place} нет свободного времени для записи"
NEW_BOOKING_INTERVAL_HELP_TEXT = (
    'Для записи отправьте сообщение в формате {начало записи} - {конец записи}, например "11:00 - 12:30"'
)
INCORRECT_INTERVAL_FORMAT_TEXT = "неправильный формат"
INCORRECT_INTERVAL_TIME_TEXT = "введено некорректное время"
NEGATIVE_INTERVAL_TIME_TEXT = "отрицательный интервал времени"
EMPTY_INTERVAL_TIME_TEXT = "пустой интервал времени"
OCCUPIED_INTERVAL_TIME_TEXT = "этот промежуток времени занят"
NEW_BOOKING_RESULT_TEXT = "Записал в {place} на {date} с {start_time} до {end_time}"

EDIT_BOOKING_LIST_TEXT = "Список ваших активных записей:"
EDIT_BOOKING_EMPTY_TEXT = "У вас нет активных записей"
EDIT_BOOKING_LIST_ITEM_TEXT = (
    "{item.place_id} на {item.local_start.day:02d}.{item.local_start.month:02d} "
    "с {item.local_start.hour:02d}:{item.local_start.minute:02d} "
    "до {item.local_end.hour:02d}:{item.local_end.minute:02d}"
)
EDIT_BOOKING_DELETE_TEXT = "Выберите запись для отмены:"
EDIT_BOOKING_DELETE_ACTION_TEXT = "Редактировать"
DELETE_NONEXISTING_BOOKING_TEXT = "такой записи не существует"
DELETE_ANOTHERS_BOOKING_TEXT = "эта запись принадлежит другому пользователю"
DELETE_PAST_BOOKING_TEXT = "нельзя удалить идущую или уже прошедшую запись"

EXIT_TEXT = "Выйти"
BACK_TEXT = "↩️ Назад"
ERROR_TEXT = "Ошибка: {error}"

TODAY_TEXT = "Сегодня"
MON_TEXT = "Пн"
TUE_TEXT = "Вт"
WED_TEXT = "Ср"
THU_TEXT = "Чт"
FRI_TEXT = "Пт"
SAT_TEXT = "Сб"
SUN_TEXT = "Вс"
