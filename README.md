# Бот "Спросить не напрасно". 
### Основа для телеграм бота, которую можно запускать, как в режиме polling'а, так и в режиме webhook'а

## Подготовка к запуску:
### Создать файл ".env" с парой ключ=значение, пример есть в файле Bot/.env.example
## Запуск приложения
### В режиме polling'а:
> python3 Bot/src/run_bot.py

### В режиме webhook'а:
> python3 Bot/src/run_webhook_api.py
## Проверка API сервера с использованием ngrok на локальном компьютере:
- Установить ngrok с [сайта](https://ngrok.com/download)
- [Зарегистрироваться](https://dashboard.ngrok.com/) и получить [токен](https://dashboard.ngrok.com/get-started/your-authtoken)
- в консоль вставить:
> ngrok config add-authtoken TOKEN  # (TOKEN). - токен с сайта ngrok
- запустить ngrok
> ngrok http 8000 --host-header=site.local
- скопировать адрес сайта из консоли, наподобие: https://8250-31-148-16-235.eu.ngrok.io в файл .env: WEBHOOK_URL=https://8250-31-148-16-235.eu.ngrok.io
- запустить приложение (см. выше).
### Больше информации по ngrok на [сайте](https://ngrok.com/docs/getting-started)

