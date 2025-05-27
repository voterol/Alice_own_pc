
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

[server]
http_enabled = true
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
## Управление через Яндекс Алису
[Источник](https://wiki.yaboard.com/w/%D0%90%D0%BB%D0%B8%D1%81%D0%B0_%D1%83%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D1%8F%D0%B5%D1%82_%D0%BA%D0%BE%D0%BC%D0%BF%D1%8C%D1%8E%D1%82%D0%B5%D1%80%D0%BE%D0%BC)


## 🐧 Поддержка ОС

- Windows — по умолчанию
- Linux/macOS — при адаптации команд (например, shutdown)

## 📄 Лицензия

MIT © 
