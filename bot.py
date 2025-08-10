import random
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
TOKEN = "8036801420:AAE1OcHvCHK2lL0_iX0kRVl1G2ld9v3dFMg"

# === КНОПКИ ===
main_menu = ReplyKeyboardMarkup(
    [["📅 Сколько я прожил", "🎂 До дня рождения"], ["💀 Прогноз жизни"]],
    resize_keyboard=True
)

# === ОБРАБОТЧИК ЗАПУСКА ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выбери одну из команд ниже:",
        reply_markup=main_menu
    )

# === РАСЧЁТ ПРОЖИТЫХ ДНЕЙ ===
async def lived_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите дату рождения в формате ДД.ММ.ГГГГ")
    context.user_data["action"] = "lived_days"

# === РАСЧЁТ ДНЕЙ ДО ДР ===
async def to_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите дату рождения в формате ДД.ММ.ГГГГ")
    context.user_data["action"] = "to_birthday"

# === ФАНОВЫЙ ПРОГНОЗ ===
async def death_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите дату рождения в формате ДД.ММ.ГГГГ")
    context.user_data["action"] = "death_prediction"

# === ОБРАБОТКА ДАТЫ ===
async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_str = update.message.text
        birth_date = datetime.strptime(date_str, "%d.%m.%Y")
        action = context.user_data.get("action")

        if action == "lived_days":
            days = (datetime.now() - birth_date).days
            await update.message.reply_text(f"Вы прожили {days} дней! 🗓")

        elif action == "to_birthday":
            today = datetime.now()
            next_birthday = datetime(year=today.year, month=birth_date.month, day=birth_date.day)
            if next_birthday < today:
                next_birthday = datetime(year=today.year + 1, month=birth_date.month, day=birth_date.day)
            days_left = (next_birthday - today).days
            await update.message.reply_text(f"До дня рождения осталось {days_left} дней 🎉")

        elif action == "death_prediction":
            life_expectancy = random.randint(50, 100)
            death_date = birth_date + timedelta(days=life_expectancy * 365)
            remaining = death_date - datetime.now()

            years = remaining.days // 365
            months = (remaining.days % 365) // 30
            days = (remaining.days % 365) % 30
            hours = remaining.seconds // 3600

            await update.message.reply_text(
                f"Вам осталось примерно {years} лет, {months} месяцев, {days} дней и {hours} часов.\n"
                f"Предполагаемая дата смерти: {death_date.strftime('%d.%m.%Y')} 💀"
            )

        context.user_data["action"] = None

    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты. Попробуйте снова (ДД.ММ.ГГГГ).")

# === ОБРАБОТКА КНОПОК ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📅 Сколько я прожил":
        await lived_days(update, context)
    elif text == "🎂 До дня рождения":
        await to_birthday(update, context)
    elif text == "💀 Прогноз жизни":
        await death_prediction(update, context)

# === ЗАПУСК ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📅 Сколько я прожил"), button_handler))
    app.add_handler(MessageHandler(filters.Regex("🎂 До дня рождения"), button_handler))
    app.add_handler(MessageHandler(filters.Regex("💀 Прогноз жизни"), button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date))

    app.run_polling()

if __name__ == "__main__":
    main()
