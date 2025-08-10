import os
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

TOKEN = os.getenv("TOKEN")

ASK_BIRTHDATE, CHOOSING_ACTION = range(2)

keyboard = [
    ["Сколько дней я прожил"],
    ["Сколько дней до дня рождения"],
    ["Сколько мне осталось жить"],
    ["/reset"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пожалуйста, введи дату рождения в формате ДД.ММ.ГГГГ:"
    )
    return ASK_BIRTHDATE

async def ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        birth_date = datetime.strptime(text, "%d.%m.%Y")
        context.user_data["birth_date_str"] = text
        await update.message.reply_text(
            "Отлично! Теперь выбери действие:",
            reply_markup=markup
        )
        return CHOOSING_ACTION
    except ValueError:
        await update.message.reply_text(
            "Неверный формат даты! Попробуй снова в формате ДД.ММ.ГГГГ:"
        )
        return ASK_BIRTHDATE

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    birth_date_str = context.user_data.get("birth_date_str")
    if not birth_date_str:
        await update.message.reply_text(
            "Дата рождения не найдена. Введи её заново в формате ДД.ММ.ГГГГ:"
        )
        return ASK_BIRTHDATE

    birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y")
    now = datetime.now()

    if choice == "Сколько дней я прожил":
        days_lived = (now - birth_date).days
        await update.message.reply_text(f"Вы прожили {days_lived} дней.", reply_markup=markup)
    elif choice == "Сколько дней до дня рождения":
        next_birthday = birth_date.replace(year=now.year)
        if next_birthday < now:
            next_birthday = next_birthday.replace(year=now.year + 1)
        days_left = (next_birthday - now).days
        await update.message.reply_text(f"До вашего дня рождения осталось {days_left} дней.", reply_markup=markup)
    elif choice == "Сколько мне осталось жить":
        life_expectancy_years = random.randint(60, 100)
        death_date = birth_date.replace(year=birth_date.year + life_expectancy_years)
        remaining = death_date - now
        years = remaining.days // 365
        months = (remaining.days % 365) // 30
        days = (remaining.days % 365) % 30
        hours = remaining.seconds // 3600
        await update.message.reply_text(
            f"Вам осталось примерно {years} лет, {months} месяцев, {days} дней и {hours} часов.\n"
            f"Предположительная дата смерти: {death_date.strftime('%d.%m.%Y')}",
            reply_markup=markup
        )
    else:
        await update.message.reply_text("Пожалуйста, выберите действие с помощью кнопок.", reply_markup=markup)
    return CHOOSING_ACTION

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("birth_date_str", None)
    await update.message.reply_text(
        "Дата рождения удалена. Введите новую дату рождения в формате ДД.ММ.ГГГГ:"
    )
    return ASK_BIRTHDATE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("До встречи!")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_birthdate)],
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)]
        },
        fallbacks=[CommandHandler('reset', reset), CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
