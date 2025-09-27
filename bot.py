from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from config import TELEGRAM_BOT_TOKEN
from database import (
    add_user,
    check_user_exists,
    add_schedule,
    get_schedule_for_day,
    update_schedule,
    initialize_user_database
)

ROLE, FULL_NAME, DAY, SCHEDULE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск бота и запрос роли пользователя."""
    user_id = update.effective_user.id
    user_data = check_user_exists(user_id)

    if user_data is None:
        await update.message.reply_text("Привет! Введите вашу роль: 'Студент' или 'Преподаватель'.")
        return ROLE
    else:
        await update.message.reply_text("Добро пожаловать обратно!")
        await choose_day(update, context)  
        return DAY

async def handle_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ролей пользователя."""
    role = update.message.text.strip()
    if role in ['Студент', 'Преподаватель']:
        context.user_data['role'] = role
        await update.message.reply_text(f"Вы указали роль: {role}. Пожалуйста, введите ваше ФИО и номер группы (если применимо).")
        return FULL_NAME
    else:
        await update.message.reply_text("Неизвестная роль. Пожалуйста, введите 'Студент' или 'Преподаватель'.")
        return ROLE

async def handle_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение ФИО и переход к выбору дня недели."""
    full_name = update.message.text.strip()
    user_id = update.effective_user.id
    role = context.user_data['role']

    add_user(user_id, full_name, role)

    initialize_user_database(user_id)
    
    await update.message.reply_text("Пользователь успешно зарегистрирован! Пожалуйста, выберите день недели: Понедельник, Вторник, Среда, Четверг, Пятница, Суббота, Воскресенье.")
    return DAY

async def choose_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Предлагаем выбрать день недели."""
    await update.message.reply_text("Пожалуйста, выберите день недели: Понедельник, Вторник, Среда, Четверг, Пятница, Суббота, Воскресенье.")
    return DAY

async def handle_day_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем выбор дня недели."""
    day = update.message.text.strip()
    valid_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    if day in valid_days:
        context.user_data["chosen_day"] = day
        await choose_day_details(update, context)
        return SCHEDULE
    else:
        await update.message.reply_text("Пожалуйста, выберите корректный день недели.")
        return DAY

async def choose_day_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Предлагаем расписание на выбранный день."""
    day = context.user_data.get("chosen_day")
    user_id = update.effective_user.id
    schedule = get_schedule_for_day(user_id, day)

    if schedule:
        await update.message.reply_text(f"Расписание на {day}:\n{schedule}\nЕсли хотите его редактировать, напишите новое расписание или отправьте 'Назад' для выбора другого дня.")
    else:
        await update.message.reply_text(f"На {day} расписание еще не добавлено. Напишите расписание для добавления:")
    
    return SCHEDULE

async def handle_schedule_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем ввод расписания от пользователя."""
    day = context.user_data.get("chosen_day")
    user_id = update.effective_user.id
    if day:
        user_input = update.message.text.strip()

        if user_input.lower() == "назад":
            context.user_data.pop("chosen_day", None)
            await choose_day(update, context)
            return DAY
        else:
            schedule = get_schedule_for_day(user_id, day)
            if schedule:
                update_schedule(user_id, day, user_input)
                await update.message.reply_text(f"Расписание на {day} успешно обновлено.")
            else:
                add_schedule(user_id, day, user_input)
                await update.message.reply_text(f"Расписание на {day} успешно добавлено.")

        await choose_day(update, context)
        return DAY

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_role)],
        FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_full_name)],
        DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_day_choice)],
        SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_schedule_input)],
    },
    fallbacks=[],
)

application.add_handler(conv_handler)

if __name__ == '__main__':
    application.run_polling()
