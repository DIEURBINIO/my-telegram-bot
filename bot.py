import os
import random
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Берём токен из переменной окружения
TOKEN = os.getenv("TOKEN")

# Состояния для ConversationHandler
WAITING_FOR_DATE, WAITING_FOR_DATE_BIRTHDAY, WAITING_FOR_DATE_LIFE = range(3)

# Клавиатура
keyboard = [["Сколько дней я прожил"],
            ["Сколько дней до дня рождения"],
            ["Сколько мне осталось жить"]]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

async def ask_birthdate_lived(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите дату рождения в формате ДД.ММ.ГГГГ:")
    return WAITING_FOR_DATE

async def ask_birthdate_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите дату рождения в формате ДД.ММ.ГГГГ:")
    return WAITING_FOR_DATE_BIRTHDAY

async def ask_birthdate_life(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите дату рождения в формате ДД.ММ.ГГГГ:")
    return WAITING_FOR_DATE_LIFE

async def calculate_lived(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        birth_date = datetime.strptime(update.message.text, "%d.%m.%Y")
        days_lived = (datetime.now() - birth_date).days
        await update.message.reply_text(f"Вы прожили {days_lived} дней.", reply_markup=markup)
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Попробуйте снова.")
        return WAITING_FOR_DATE
    return ConversationHandler.END

async def calculate_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        birth_date = datetime.strptime(update.message.text, "%d.%m.%Y")
        today = datetime.now()
        next_birthday = birth_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        days_left = (next_birthday - today).days
        await update.message.reply_text(f"До вашего дня рождения осталось {days_left} дней.", reply_markup=markup)
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Попробуйте снова.")
        return WAITING_FOR_DATE_BIRTHDAY
    return ConversationHandler.END

async def calculate_life_expectancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        birth_date = datetime.strptime(update.message.text, "%d.%m.%Y")
        life_expectancy_years = random.randint(60, 100)  # Рандомный прогноз
        death_date = birth_date.replace(year=birth_date.year + life_expectancy_years)
        remaining_time = death_date - datetime.now()

        years = remaining_time.days // 365
        months = (remaining_time.days % 365) // 30
        days = (remaining_time.days % 365) % 30
        hours = remaining_time.seconds // 3600

        await update.message.reply_text(
            f"Вам осталось примерно {years} лет, {months} месяцев, {days} дней и {hours} часов.\n"
            f"Предположительная дата смерти: {death_date.strftime('%d.%m.%Y')}",
            reply_markup=markup
        )
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Попробуйте снова.")
        return WAITING_FOR_DATE_LIFE
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_lived = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Сколько дней я прожил$"), ask_birthdate_lived)],
        states={WAITING_FOR_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_lived)]},
        fallbacks=[],
    )

    conv_birthday = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Сколько дней до дня рождения$"), ask_birthdate_birthday)],
        states={WAITING_FOR_DATE_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_birthday)]},
        fallbacks=[],
    )

    conv_life = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Сколько мне осталось жить$"), ask_birthdate_life)],
        states={WAITING_FOR_DATE_LIFE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_life_expectancy)]},
        fallbacks=[],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_lived)
    application.add_handler(conv_birthday)
    application.add_handler(conv_life)

    application.run_polling()

if __name__ == "__main__":
    main()
