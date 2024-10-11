# Сборник Мини-игр в Telegram

## Обзор
Этот проект — Telegram-бот, который предлагает мини-игры в формате веб-страниц или текста. Пользователи могут играть в различные игры и взаимодействовать с другими игроками прямо в Telegram.

## Структура Файлов
- `setup.py`: Скрипт для настройки локального окружения и установки зависимостей.
- `.env.template`: Шаблон для создания файлов окружения.
- `.env`: Содержит переменные окружения.
- `.env.test`: Содержит переменные окружения для тестирования.
- `.env.dev`: Содержит переменные окружения для разработки.
- `requirements.txt`: Список зависимостей Python, необходимых для проекта.
- `main.py`: Основной скрипт приложения.

## Установка и Локальное Развертывание
1. Убедитесь, чо установлены: Python3.9 или новее, pip и python3-venv
```bash
python3 --version
sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3-venv
```
2. Скачайте репозиторий
```bash
git clone https://github.com/spreda/indi-games.git
cd indi-games
```
3. Настройте переменные окружения по примеру из файла .env.template или пропишите их в .env
```bash
export BOT_TOKEN="Bot token can be obtained via https://t.me/BotFather"
export WEB_APP_URL="https://example.com"
```
5. Запустите скрипт установки
```bash
python3 setup.py
```

## Настройка Тестового Окружения
```bash
python3 setup.py .env.test
```

## Использование
После настройки переменных окружения и установки зависимостей вы можете запустить бота с помощью команды:
```bash
python3 main.py
```
