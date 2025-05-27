
# 🖥️ Alice own pc Bot

Telegram-бот и HTTP-сервер для удалённого управления компьютером.

## 📦 Возможности

- Управление ПК через Telegram
- Выполнение команд через HTTP API
- Добавление/удаление пользовательских команд
- Уведомления о действиях в Telegram
- Логирование всех команд

## ⚙️ Установка

```bash
git clone https://github.com/voterol/Alice_own_pc
cd Alice_own_pc
pip install -r requirements.txt
```

## 🛠 Настройка

При первом запуске создаётся файл `conf.conf`. Заполните его:

```ini
[bot]
token = ваш_токен_бота
api_key = ваш_api_ключ

[access]
allowed_ids = ваш_telegram_id
```

## 🚀 Запуск

```bash
python main.py
```

## 🌐 HTTP API

Пример запроса:

```
GET /command?key=ВАШ_API_КЛЮЧ&command=open_chrome
```

## 🔒 Безопасность

- Доступ по API-ключу
- Уведомления о действиях
- Ограничение доступа по Telegram ID

## 🔒 Включение и выключение http сервера

```bash
/disable_http 
/enable_http
```

## 🐧 Поддержка ОС

- Windows — по умолчанию
- Linux/macOS — при адаптации команд (например, shutdown)

## 📄 Лицензия

MIT © 
