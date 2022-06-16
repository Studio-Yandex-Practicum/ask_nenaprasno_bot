# Бот "Спросить не напрасно".
### Основа для телеграм бота, которую можно запускать, как в режиме polling'а, так и в режиме webhook'а

## Подготовка к запуску:
### Создать файл ".env" с парой ключ=значение, пример есть в файле .env.example
## Запуск приложения
### В режиме polling'а:
> python3 src/run_bot.py

### В режиме webhook'а:
> python3 src/run_webhook_api.py
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

## Настройка pre-commit:

> pip3 install -r Bot/requirements.txt
>
> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка линтером, а так же будет происходить автоматическое приведение к единому стилю.

Если у вас произошло появление сообщений об ошибках, то в большинстве случаев достаточно повторить добавление файлов вызвавших ошибки в git и повторный коммит:

> git add .
>
> git commit -m "Текст комментария коммита"
