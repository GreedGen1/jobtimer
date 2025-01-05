from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import csv
import os
from datetime import datetime

# Глобальная переменная для хранения пользователей
users = set()  # Хранит список username пользователей

# Функция для записи чекина (входа)
def write_checkin(username, checkin_time):
    current_date = checkin_time.split(' ')[0]  # Получаем дату в формате YYYY-MM-DD
    file_exists = os.path.isfile('data.csv')  # Проверяем, существует ли файл
    updated = False

    # Если файл существует, проверяем наличие записи на сегодня
    rows = []
    if file_exists:
        with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username and row[1].startswith(current_date):
                    row[1] = checkin_time  # Обновляем время входа
                    updated = True
                rows.append(row)

    # Если запись на сегодня не найдена, добавляем новую строку
    if not updated:
        rows.append([username, checkin_time, '', ''])  # Чек-аут и рабочее время пустые

    # Сохраняем обновлённые данные обратно в CSV
    with open('data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'checkin', 'checkout', 'work_time'])  # Заголовок
        writer.writerows(rows)
    return not updated  # Возвращаем True, если добавлена новая запись

# Функция для записи чекаута (выхода)
def write_checkout(username, checkout_time):
    current_date = checkout_time.split(' ')[0]
    file_exists = os.path.isfile('data.csv')
    rows = []
    updated = False
    work_time_str = None

    if file_exists:
        with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username and row[1].startswith(current_date) and row[2] == '':
                    row[2] = checkout_time
                    checkin_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    checkout_time_dt = datetime.strptime(checkout_time, '%Y-%m-%d %H:%M:%S')
                    work_time = checkout_time_dt - checkin_time
                    hours, remainder = divmod(work_time.total_seconds(), 3600)
                    minutes = remainder // 60
                    work_time_str = f'{int(hours)} ч {int(minutes)} мин'
                    row[3] = work_time_str
                    updated = True
                rows.append(row)

    if updated:
        with open('data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'checkin', 'checkout', 'work_time'])
            writer.writerows(rows)
        return work_time_str
    return None

# Обработчик команды /checkin
async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    user = update.effective_user
    username = user.username if user.username else user.first_name
    checkin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    success = write_checkin(username, checkin_time)

    # Добавляем пользователя в список для уведомлений
    users.add(update.effective_chat.id)

    if success:
        await update.message.reply_text(f'Вы успешно зачекинились в {checkin_time}, {username}!')
    else:
        await update.message.reply_text(f'Вы уже зачекинились сегодня, {username}. Повторный вход невозможен.')

# Обработчик команды /checkout
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username if user.username else user.first_name
    checkout_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    work_time = write_checkout(username, checkout_time)

    if work_time is not None:
        await update.message.reply_text(
            f'Вы успешно зачекаутились в {checkout_time}, {username}!\n'
            f'Ваше рабочее время сегодня: {work_time}.'
        )
    else:
        await update.message.reply_text(
            f'Вы не можете зачекаутиться, так как не зачекинились сегодня или уже выходили.'
        )

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    users.add(update.effective_chat.id)  # Добавляем пользователя в список для уведомлений
    await update.message.reply_text("Добро пожаловать! Используйте /checkin для отметки прихода и /checkout для ухода.")

# Основная функция для запуска бота
def main():
    application = ApplicationBuilder().token("7818620141:AAEIIL7knGHtZotOvk9BD6viyunBU3sFKH0").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("checkin", checkin))
    application.add_handler(CommandHandler("checkout", checkout))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
gfgfgfgf