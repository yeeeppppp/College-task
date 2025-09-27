from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from database import check_user_exists, add_user, get_schedule_for_day, add_schedule

ASK_ROLE, ASK_NAME, ASK_GROUP, SHOW_MENU, ASK_SCHEDULE = range(5)

ROLE_STUDENT = 'Студент' or 'студент'
ROLE_TEACHER = 'Преподаватель' or 'преподаватель'

days_keyboard = [['Понедельник', 'Вторник', 'Среда'], ['Четверг', 'Пятница', 'Суббота']]

def start(update: Update, context):
    user_id = update.message.from_user.id

    if check_user_exists(user_id):
        update.message.reply_text(
            "Добро пожаловать! Выберите день недели для просмотра расписания:",
            reply_markup=ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True)
        )
        return SHOW_MENU
    else:
        update.message.reply_text("Привет! Кто вы? Студент или Преподаватель?")
        return ASK_ROLE

def ask_role(update: Update, context):
    role = update.message.text

    if role not in [ROLE_STUDENT, ROLE_TEACHER]:
        update.message.reply_text("Пожалуйста, выберите роль: Студент или Преподаватель.")
        return ASK_ROLE

    context.user_data['role'] = role
    update.message.reply_text("Введите ваше полное ФИО:")
    return ASK_NAME

def ask_name(update: Update, context):
    full_name = update.message.text
    context.user_data['full_name'] = full_name

    if context.user_data['role'] == ROLE_STUDENT:
        update.message.reply_text("Введите номер вашей группы:")
        return ASK_GROUP
    else:
        user_id = update.message.from_user.id
        add_user(user_id, full_name, context.user_data['role'])
        update.message.reply_text(
            "Профиль зарегистрирован! Выберите день недели для просмотра расписания:",
            reply_markup=ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True)
        )
        return SHOW_MENU

def ask_group(update: Update, context):
    group_number = update.message.text
    user_id = update.message.from_user.id
    full_name = context.user_data['full_name']

    add_user(user_id, full_name, context.user_data['role'], group_number)
    update.message.reply_text(
        "Профиль зарегистрирован! Выберите день недели для просмотра расписания:",
        reply_markup=ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True)
    )
    return SHOW_MENU

def show_schedule(update: Update, context):
    day = update.message.text
    schedule = get_schedule_for_day(day)

    if schedule:
        update.message.reply_text(f"Расписание на {day}: {schedule}")
    else:
        update.message.reply_text(f"Расписание на {day} отсутствует. Хотите добавить его? (Да/Нет)")
        return ASK_SCHEDULE

    return SHOW_MENU

def ask_schedule(update: Update, context):
    response = update.message.text.lower()

    if response == 'да':
        update.message.reply_text("Введите новое расписание:")
        return ASK_SCHEDULE
    elif response == 'нет':
        update.message.reply_text("Возвращаемся к выбору дня недели.", reply_markup=ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True))
        return SHOW_MENU
    else:
        update.message.reply_text("Пожалуйста, ответьте Да или Нет.")
        return ASK_SCHEDULE

def save_schedule(update: Update, context):
    schedule = update.message.text
    day = context.user_data['selected_day']
    add_schedule(day, schedule)
    
    update.message.reply_text(f"Расписание на {day} сохранено!")
    return SHOW_MENU

def cancel(update: Update, context):
    update.message.reply_text("Действие отменено. Возвращаемся к главному меню.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ASK_ROLE: [MessageHandler(Filters.text & ~Filters.command, ask_role)],
        ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
        ASK_GROUP: [MessageHandler(Filters.text & ~Filters.command, ask_group)],
        SHOW_MENU: [MessageHandler(Filters.text & ~Filters.command, show_schedule)],
        ASK_SCHEDULE: [MessageHandler(Filters.text & ~Filters.command, ask_schedule)],
        ASK_SCHEDULE: [MessageHandler(Filters.text & ~Filters.command, save_schedule)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
