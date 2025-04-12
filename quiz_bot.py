from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import time

questions = [
    {"question": "Что такое тест-кейс?", "options": ["Программа для автоматизации", "Документ с действиями", "Отчет о дефектах", "Инструмент управления"], "answer": 1},
    {"question": "Какой вид тестирования нефункциональный?", "options": ["Регрессионное", "Производительность", "Модульное", "Системное"], "answer": 1},
    {"question": "Что означает термин 'баг'?", "options": ["Новая функция", "Изменение кода", "Ошибка в программе", "Инструмент автоматизации"], "answer": 2},
    {"question": "Инструмент для отслеживания дефектов:", "options": ["JIRA", "Selenium", "Postman", "Git"], "answer": 0},
    {"question": "Что такое регрессионное тестирование?", "options": ["Тест новых функций", "Проверка производительности", "Проверка влияния изменений", "Тест безопасности"], "answer": 2},
    {"question": "Какой тип тестирования без знания кода?", "options": ["Белый ящик", "Черный ящик", "Серый ящик", "Статический анализ"], "answer": 1},
    {"question": "Что такое тест-план?", "options": ["Список багов", "Стратегия тестирования", "Код автоматизации", "График релизов"], "answer": 1},
    {"question": "Инструмент автоматизации веб-тестов:", "options": ["Jenkins", "Selenium", "Docker", "Kubernetes"], "answer": 1},
    {"question": "Что такое Smoke Testing?", "options": ["Глубокое тестирование", "Поверхностная проверка", "Тест безопасности", "Тест производительности"], "answer": 1},
    {"question": "Метод динамического тестирования:", "options": ["Анализ кода", "Рецензия", "Выполнение тестов", "Статический анализ"], "answer": 2},
    {"question": "Что такое юзабилити-тестирование?", "options": ["Проверка безопасности", "Оценка удобства", "Тест производительности", "Анализ кода"], "answer": 1},
    {"question": "Какой тип тестирования делают разработчики?", "options": ["Системное", "Приемочное", "Модульное", "Регрессионное"], "answer": 2},
    {"question": "Что такое белый ящик?", "options": ["Без знания кода", "С полным знанием кода", "Тест UI", "Тест производительности"], "answer": 1},
    {"question": "Инструмент управления версиями:", "options": ["Git", "JIRA", "Selenium", "Postman"], "answer": 0},
    {"question": "Что такое defect density?", "options": ["Кол-во тестов", "Баги на строку кода", "Скорость тестов", "Время фикса"], "answer": 1},
    {"question": "Какое тестирование проводят пользователи?", "options": ["Системное", "Приемочное", "Модульное", "Регрессионное"], "answer": 1},
    {"question": "Что такое баг-репорт?", "options": ["Инструкция для тестирования", "Запрос на изменение", "Документ с описанием ошибки", "Фича"], "answer": 2},
    {"question": "Что такое тестовая среда?", "options": ["Документация", "Сервер разработки", "Среда для тестов", "Репозиторий"], "answer": 2},
    {"question": "К какому тестированию относится нагрузочное?", "options": ["Функциональное", "Нефункциональное", "Модульное", "Приемочное"], "answer": 1},
    {"question": "Что такое exploratory testing?", "options": ["Сценарное тестирование", "Автоматизация", "Спонтанное исследование", "Базовое тестирование"], "answer": 2}
]

user_progress = {}
user_last_test_time = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()
    last_time = user_last_test_time.get(user_id, 0)

    if now - last_time < 21600:  # 6 часов = 21600 секунд
        hours_left = int((21600 - (now - last_time)) / 3600)
        minutes_left = int((21600 - (now - last_time)) % 3600 / 60)
        await update.message.reply_text(f"Вы уже проходили тест. Попробуйте снова через {hours_left} ч. {minutes_left} мин.")
        return

    user_progress[user_id] = {"current": 0, "score": 0, "start_time": now}
    user_last_test_time[user_id] = now
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = user_progress[user_id]
    index = progress["current"]

    if index < len(questions):
        q = questions[index]
        buttons = [[InlineKeyboardButton(text=opt, callback_data=str(i))] for i, opt in enumerate(q["options"])]
        reply_markup = InlineKeyboardMarkup(buttons)
        progress['start_time'] = time.time()
        if update.message:
            await update.message.reply_text(q["question"], reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.edit_text(q["question"], reply_markup=reply_markup)
    else:
        score = progress["score"]
        total = len(questions)
        keyboard = [[InlineKeyboardButton("Пройти снова", callback_data="retry")]]
        markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.edit_text(
            f"Тест завершён!\n\nРезультат: {score} из {total} правильных ответов.", reply_markup=markup)
        del user_progress[user_id]

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "retry":
        fake_update = Update(update.update_id, message=query.message)
        await start(fake_update, context)
        return

    if user_id not in user_progress:
        await query.message.reply_text("Напишите /start, чтобы начать тест.")
        return

    progress = user_progress[user_id]
    q = questions[progress["current"]]
    elapsed = time.time() - progress["start_time"]

    selected_option = int(query.data)
    correct = selected_option == q["answer"]

    feedback = "✅ Верно!" if correct else f"❌ Неверно! Правильный ответ: {q['options'][q['answer']]}"
    if elapsed > 30:
        feedback += "\n⏰ Время вышло! Ответ не засчитан."
    elif correct:
        progress["score"] += 1

    await query.message.edit_text(f"{q['question']}\n\n{feedback}")
    progress["current"] += 1
    await asyncio.sleep(2)
    await send_question(update, context)

if __name__ == "__main__":
    import os
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_answer))

    app.run_polling()
