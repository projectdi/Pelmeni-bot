import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

MENU = {
    "Классика": 12,
    "С курицей": 10,
    "Веган": 11
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Заказать", "Инфо"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "*Домашние Пельмени ЛА*\nСвежие, как у бабушки!\nВыбери:",
        parse_mode='Markdown', reply_markup=reply_markup
    )

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[f"{k} — ${v}/кг" for k, v in MENU.items()]]
    keyboard.append(["Назад"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Что берём?", reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Заказать":
        await order(update, context)
    elif text == "Инфо":
        await update.message.reply_text("Доставка LA — $5\nГотовим 2 часа\n+1 (424) 666-1488")
    elif " — $" in text:
        name = text.split(" — ")[0]
        context.user_data['pelmen'] = name
        await update.message.reply_text(f"Сколько кг *{name}*?", parse_mode='Markdown')
    elif text.isdigit() and 'pelmen' in context.user_data:
        kg = int(text)
        name = context.user_data['pelmen']
        total = kg * MENU[name]
        await update.message.reply_text(
            f"Заказ: *{name}* — {kg} кг\nК оплате: *${total + 5}* (с доставкой)\nНапиши адрес!",
            parse_mode='Markdown'
        )
        del context.user_data['pelmen']
    elif text == "Назад":
        await start(update, context)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Бот запущен...")
    await app.run_polling()

if name == "__main__":
    import asyncio
    asyncio.run(main())
