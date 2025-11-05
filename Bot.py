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
    keyboard = [["🍖 Заказать", "ℹ️ Инфо"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🥟 *Домашние Пельмени ЛА*\n"
        "Свежие, как у бабушки! Без химии\n"
        "Выбери:", parse_mode='Markdown', reply_markup=reply_markup
    )

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[f"{name} — ${price}/кг" for name, price in MENU.items()]]
    keyboard.append(["🔙 Назад"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Что лепим?", reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🍖 Заказать":
        await order(update, context)
    elif text == "ℹ️ Инфо":
        await update.message.reply_text("🚚 Доставка по LA: $5\n⏰ Готовим за 2 часа\n📞 +1 (твой номер)")
    elif " — $" in text:
        name = text.split(" — ")[0]
        context.user_data['order'] = name
        await update.message.reply_text(f"Сколько кг *{name}*?\n(напиши цифру)", parse_mode='Markdown')
    elif text.isdigit() and 'order' in context.user_data:
        kg = int(text)
        name = context.user_data['order']
        price = MENU[name]
        total = kg * price
        await update.message.reply_text(
            f"✅ Заказ: *{name}* — {kg} кг\n"
            f"💰 К оплате: *${total}* + $5 доставка\n"
            f"📍 Напиши адрес и телефон!", parse_mode='Markdown'
        )
        del context.user_data['order']

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
print("Бот запущен...")
app.run_polling()
