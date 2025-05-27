import asyncio
import os
import json
import configparser
from flask import Flask, request, abort
from aiogram import Bot, Dispatcher, types, F
import threading
import datetime
import traceback

# === Конфигурация ===
CONF_PATH = "conf.conf"
DEFAULT_CONF = """
[bot]
token = your_telegram_bot_token_here
api_key = my_secret_key_123

[access]
allowed_ids = 123456789

[server]
http_enabled = true
"""

def ensure_conf_file():
    if not os.path.exists(CONF_PATH):
        with open(CONF_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONF.strip())
        print(f"[!] Создан конфигурационный файл {CONF_PATH}. Заполни и перезапусти.")
        exit()

def load_config():
    config = configparser.ConfigParser()
    config.read(CONF_PATH, encoding="utf-8")
    return config

ensure_conf_file()
config = load_config()
TOKEN = config["bot"]["token"]
API_KEY = config["bot"].get("api_key", "")
ALLOWED_IDS = list(map(int, config["access"]["allowed_ids"].split(",")))
HTTP_ENABLED = config.getboolean("server", "http_enabled", fallback=True)

COMMANDS_FILE = "custom_commands.json"
LOG_FILE = "command_log.txt"
command_queue = asyncio.Queue()

custom_commands = {}
http_thread = None
http_shutdown_requested = False
http_enable_requested = False

# === Flask-сервер ===
app = Flask(__name__)

@app.route("/command", methods=["GET"])
def handle():
    api_key = request.args.get("key")
    cmd = request.args.get("command", "")
    if api_key != API_KEY:
        abort(403, description="Forbidden: Invalid API Key")
    asyncio.run(command_queue.put((cmd, "HTTP")))
    return {"result": f"Команда '{cmd}' добавлена в очередь"}

def run_flask():
    try:
        app.run(host="0.0.0.0", port=8888)
    except OSError as e:
        print(f"[!] Ошибка запуска Flask: {e}")

def load_custom_commands():
    if not os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

custom_commands.update(load_custom_commands())

def save_custom_commands(commands):
    with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)

def log_command(source: str, command: str, result: str):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time}] Source: {source} | Command: {command} | Result: {result}\n")

async def notify_all(text: str):
    for user_id in ALLOWED_IDS:
        try:
            await bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            print(f"[!] Ошибка отправки уведомления: {e}")
            traceback.print_exc()

async def run_command_async(cmd: str, source: str = "local") -> str:
    try:
        if cmd in custom_commands:
            data = custom_commands[cmd]
            os.system(data["action"])
            await notify_all(f"✅ Кастомная команда: {cmd}\nИсточник: {source}\nОтвет: {data['response']}")
            log_command(source, cmd, data['response'])
            return data["response"]
        else:
            await notify_all(f"❌ Неизвестная команда: {cmd}\nИсточник: {source}")
            log_command(source, cmd, "Неизвестная команда")
            return "Неизвестная команда."
    except Exception as e:
        error_text = f"❌ Ошибка при выполнении команды: {cmd}\nИсточник: {source}\nОшибка: {str(e)}"
        await notify_all(error_text)
        log_command(source, cmd, f"Ошибка: {str(e)}")
        return "Произошла ошибка при выполнении команды."

def add_custom_command(name: str, response: str, action: str):
    custom_commands[name] = {"response": response, "action": action}
    save_custom_commands(custom_commands)

def delete_custom_command(name: str) -> bool:
    if name in custom_commands:
        del custom_commands[name]
        save_custom_commands(custom_commands)
        return True
    return False

def list_custom_commands() -> list:
    return list(custom_commands.keys())

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/disable_http")
async def disable_http_handler(message: types.Message):
    global http_shutdown_requested
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("Нет доступа.")
        return
    if not HTTP_ENABLED:
        await message.answer("HTTP-сервер уже отключён.")
        return
    await message.answer("Вы уверены, что хотите отключить HTTP-сервер? Подтвердите в консоли (y/n):")
    http_shutdown_requested = True

@dp.message(F.text == "/enable_http")
async def enable_http_handler(message: types.Message):
    global http_enable_requested
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("Нет доступа.")
        return
    if HTTP_ENABLED:
        await message.answer("HTTP-сервер уже включён.")
        return
    await message.answer("Вы уверены, что хотите включить HTTP-сервер? Подтвердите в консоли (y/n):")
    http_enable_requested = True

@dp.message(F.text.startswith("/add"))
async def add_command_handler(message: types.Message):
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("Нет доступа.")
        return
    try:
        parts = message.text.split(maxsplit=3)
        if len(parts) < 4:
            await message.answer("Формат: /add [имя] [ответ] [команда]")
            return
        name, response, action = parts[1], parts[2], parts[3]
        add_custom_command(name, response, action)
        await message.answer(f"Команда '{name}' добавлена.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@dp.message(F.text.startswith("/del"))
async def delete_command_handler(message: types.Message):
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("Нет доступа.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Формат: /del [имя_команды]")
        return
    name = parts[1]
    if delete_custom_command(name):
        await message.answer(f"Команда '{name}' удалена.")
    else:
        await message.answer(f"Команда '{name}' не найдена.")

@dp.message(F.text.startswith("/list"))
async def list_commands_handler(message: types.Message):
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("Нет доступа.")
        return
    cmds = list_custom_commands()
    if not cmds:
        await message.answer("Пользовательские команды отсутствуют.")
    else:
        text = "📋 Список пользовательских команд:\n" + "\n".join(f"• {c}" for c in cmds)
        await message.answer(text)

@dp.message()
async def command_handler(message: types.Message):
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("Нет доступа.")
        return
    cmd = message.text.strip().lower()
    await run_command_async(cmd, source=f"Telegram от @{message.from_user.username or message.from_user.id}")

async def queue_worker():
    while True:
        cmd, source = await command_queue.get()
        await run_command_async(cmd, source)

async def console_monitor():
    global HTTP_ENABLED, http_shutdown_requested, http_enable_requested, http_thread
    while True:
        await asyncio.sleep(1)
        if http_shutdown_requested:
            answer = input("Вы действительно хотите отключить HTTP-сервер? (y/n): ").strip().lower()
            if answer == "y":
                print("[!] HTTP-сервер будет отключён.")
                if not config.has_section("server"):
                    config.add_section("server")
                config.set("server", "http_enabled", "false")
                with open(CONF_PATH, "w", encoding="utf-8") as f:
                    config.write(f)
                HTTP_ENABLED = False
                custom_commands.clear()
                custom_commands.update(load_custom_commands())
                http_shutdown_requested = False
                await notify_all("❌ HTTP-сервер был отключён.")
            else:
                print("Отключение отменено.")
                http_shutdown_requested = False
        elif http_enable_requested:
            answer = input("Вы действительно хотите включить HTTP-сервер? (y/n): ").strip().lower()
            if answer == "y":
                print("[!] HTTP-сервер запускается...")
                if not config.has_section("server"):
                    config.add_section("server")
                config.set("server", "http_enabled", "true")
                with open(CONF_PATH, "w", encoding="utf-8") as f:
                    config.write(f)
                HTTP_ENABLED = True
                custom_commands.clear()
                custom_commands.update(load_custom_commands())
                http_enable_requested = False
                http_thread = threading.Thread(target=run_flask, daemon=True)
                http_thread.start()
                await notify_all("✅ HTTP-сервер был включён.")
            else:
                print("Включение отменено.")
                http_enable_requested = False

async def main():
    if HTTP_ENABLED:
        global http_thread
        http_thread = threading.Thread(target=run_flask, daemon=True)
        http_thread.start()
    await notify_all("✅ Бот и HTTP-сервер запущены и готовы к работе" if HTTP_ENABLED else "✅ Бот запущен. HTTP-сервер отключён.")
    asyncio.create_task(queue_worker())
    asyncio.create_task(console_monitor())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
