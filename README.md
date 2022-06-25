# Бот "Спросить не напрасно".
### Основа для телеграм бота, которую можно запускать, как в режиме polling'а, так и в режиме webhook'а

## Подготовка к запуску:
### Создать файл ".env" с парой ключ=значение, пример есть в файле .env.example
## Запуск приложения
### В режиме polling'а:
> python3 src/run_bot.py

### В режиме webhook'а (также в этом режиме будет запущена точка доступа для webhook'а trello):
> python3 src/run_webhook_api.py
#### Запросы от trello ожидаются на /trelloCallback, приходят в формате:
```
{
  "action": {
    "id": "51f9424bcd6e040f3c002412",
    "idMemberCreator": "4fc78a59a885233f4b349bd9",
    "data": {
      "board": {
        "name": "Trello Development",
        "id": "4d5ea62fd76aa1136000000c"
      },
      "card": {
        "idShort": 1458,
        "name": "Webhooks",
        "id": "51a79e72dbb7e23c7c003778"
      },
      "voted": true
    },
    "type": "voteOnCard",
    "date": "2013-07-31T16:58:51.949Z",
    "memberCreator": {
      "id": "4fc78a59a885233f4b349bd9",
      "avatarHash": "2da34d23b5f1ac1a20e2a01157bfa9fe",
      "fullName": "Doug Patti",
      "initials": "DP",
      "username": "doug"
    }
  },
  "model": {
    "id": "4d5ea62fd76aa1136000000c",
    "name": "Trello Development",
    "desc": "Trello board used by the Trello team to track work on Trello.  How meta!\n\nThe development of the Trello API is being tracked at https://trello.com/api\n\nThe development of Trello Mobile applications is being tracked at https://trello.com/mobile",
    "closed": false,
    "idOrganization": "4e1452614e4b8698470000e0",
    "pinned": true,
    "url": "https://trello.com/b/nC8QJJoZ/trello-development",
    "prefs": {
      "permissionLevel": "public",
      "voting": "public",
      "comments": "public",
      "invitations": "members",
      "selfJoin": false,
      "cardCovers": true,
      "canBePublic": false,
      "canBeOrg": false,
      "canBePrivate": false,
      "canInvite": true
    },
    "labelNames": {
      "yellow": "Infrastructure",
      "red": "Bug",
      "purple": "Repro'd",
      "orange": "Feature",
      "green": "Mobile",
      "blue": "Verified"
    }
  }
}
```
#### Пример создания curl-запроса для отправки данных на другой endpoint:
```
import requests
import json

payload = {'query': json.dumps({"test_key": "test_value"})}
url = "https://www.test.com/test_endpoint"

response = requests.post(url, data=payload)
```
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


## Настройка poetry:

Poetry - это инструмент для управления зависимостями и виртуальными окружениями,
также может использоваться для сборки пакетов.

### Установка:

Для UNIX систем вводим в консоль следующую команду

> *curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -*

Для WINDOWS вводим в PowerShell

> *(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -*

После установки перезапустите оболочку и введите команду

> poetry --version

Ответ должен быть в формате

> Poetry version 1.1.13

Для дальнейшей работы введите команду:

> poetry config virtualenvs.in-project true

Выполнение данной команды необходимо для создания виртуального окружения в папке проекта,
по умолчанию папка .venv создается по пути **C:\Users\<username>\AppData\Local\pypoetry\Cache\virtualenvs**

После предыдущей команды создадим виртуальное окружение нашего проекта с помощью команды

> poetry install

Результатом выполнения команды станет создание в корне проекта папки .venv.
Зависимости для создания окружения берутся из файлов poetry.lock (приоритетнее) и pyproject.toml

Для добавления новой зависимости в окружение необходимо выполнить команду

> poetry add <package_name>
>
> poetry add starlette *пример использования*

Также poetry позволяет разделять зависимости необходимые для разработки, от основных.
Для добавления зависимости необходимой для разработки и тестирования необходимо добавить флаг ***--dev***

> poetry add <package_name> --dev
>
> poetry add pytest --dev *пример использования*

### Порядок работы после настройки

Существует возможность запуска скриптов и команд с помощью команды без активации окружения:

> poetry run <script_name>.py
>
> poetry run pytest
>
> poetry run black

Можно вызвать консоль poetry с помощью команды:

> poetry shell

В вызванной оболочке будет автоматически активировано окружение.
Порядок работы в оболочке не меняется. Пример команды для Win:

> C:\Dev\nenaprasno_bot\ask_nenaprasno_bot>python src\run_bot.py

Доступен стандартный метод работы с активацией окружения в терминале с помощью команд:

Для WINDOWS:

> source .venv/Scripts/activate

Для UNIX:

> source .venv/bin/activate


## Настройка pre-commit:

> poetry install
>
> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка линтером, а так же будет происходить автоматическое приведение к единому стилю.

Если у вас произошло появление сообщений об ошибках, то в большинстве случаев достаточно повторить добавление файлов вызвавших ошибки в git и повторный коммит:

> git add .
>
> git commit -m "Текст комментария коммита"
