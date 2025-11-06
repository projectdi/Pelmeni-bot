import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("🔥 TOKEN НЕ НАЙДЕН! Поставь в .env или окружение, дебил!")

MENU = {"Классика": 12, "С курицей": 10, "Веган": 11}
DELIVERY_PRICE = 5

# === СТАРТ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  # На всякий пожарный
    keyboard = [
        [KeyboardButton("🍽 Заказать"), KeyboardButton("ℹ Инфо")],
        [KeyboardButton("❌ Отмена")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "*Пельмени ЛА* 🍤\nСвежие, как у бабушки!\n\nВыбери действие:",
        parse_mode='Markdown', reply_markup=reply_markup
    )

# === ОТМЕНА ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await start(update, context)

# === ИНФО ===
async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ *Информация:*\n\n"
        "🚚 Доставка по LA — *$5*\n"
        "⏳ Готовим ~2 часа\n"
        "📞 +1 (424) 666-1488\n"
        "💳 Оплата при получении",
        parse_mode='Markdown'
    )

# === ЗАКАЗ — МЕНЮ ===
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(f"{k} — ${v}/кг")] for k, v in MENU.items()]
    keyboard.append([KeyboardButton("⬅ Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🍲 *Что лепим сегодня?*", parse_mode='Markdown', reply_markup=reply_markup)

# === ОБРАБОТКА ТЕКСТА ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # === ОТМЕНА В ЛЮБОЙ МОМЕНТ ===
    if text == "❌ Отмена":
        await cancel(update, context)
        return

    # === ГЛАВНОЕ МЕНЮ ===
    if text == "🍽 Заказать":
        await order(update, context)
        return
    if text == "ℹ Инфо":
        await show_info(update, context)
        return
    if text == "⬅ Назад":
        await start(update, context)
        return

    # === ВЫБОР ПЕЛЬМЕНЕЙ ===
    if " — $" in text:
        name = text.split(" — $")[0]
        if name not in MENU:
            await update.message.reply_text("🤨 Чё за хрень? Выбирай из меню!")
            return
        context.user_data["pelmen"] = name
        await update.message.reply_text(f"🍴 Сколько кг *{name}* хочешь?", parse_mode='Markdown')
        return

    # === ВВОД КГ ===
    if "pelmen" in context.user_data:
        try:
            # Поддержка: 5, 5.5, 5,5, 5 кг, 5кг
            clean = ''.join(c for c in text.lower() if c.isdigit() or c in ".,")
            kg = float(clean.replace(',', '.'))
            if kg <= 0 or kg > 50:
                raise ValueError
        except:
            await update.message.reply_text("😡 *ЦИФРУ, Я СКАЗАЛ!* Например: `2` или `1.5`", parse_mode='Markdown')
            return

        name = context.user_data.pop("pelmen")
        price_per_kg = MENU[name]
        total = kg * price_per_kg + DELIVERY_PRICE
        summary = (
            f"📦 *Заказ:*\n"
            f"   • {name} — {kg} кг × ${price_per_kg} = ${kg * price_per_kg}\n"
            f"   • Доставка — ${DELIVERY_PRICE}\n"
            f"💰 *Итого: ${total}*"
        )
        context.user_data["summary"] = summary
        context.user_data["awaiting_address"] = True
        await update.message.reply_text(f"{summary}\n\n📍 *Куда везти?* (улица, дом, квартира)", parse_mode='Markdown')
        return

    # === ВВОД АДРЕСА ===
    if context.user_data.get("awaiting_address"):
        address = text
        if len(address) < 5 or " " not in address:
            await update.message.reply_text("🚨 Адрес какой-то мутный. Пиши нормально: *Ленинская 5, кв 88*")
            return

        summary = context.user_data.pop("summary")
        context.user_data.pop("awaiting_address", None)

        await update.message.reply_text(
            f"{summary}\n"
            f"📍 *Адрес:* {address}\n\n"
            f"✅ *Заказ принят!* Готовим, скоро будет у тебя.\n"
            f"⏳ ~2 часа. Оплата при получении.",
            parse_mode='Markdown'
        )
        # Можно сюда добавить: сохранение в БД, уведомление админу и т.д.
        return

    # === НЕПОНЯТНОЕ СООБЩЕНИЕ ===
    await update.message.reply_text("🤔 Чё ты несёшь? Жми кнопки или пиши по делу!")

# === ОСНОВНОЙ ЦИКЛ ===
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 Бот пельменей ЛА запущен и готов жрать заказы!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
