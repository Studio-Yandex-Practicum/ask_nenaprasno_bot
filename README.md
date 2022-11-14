# Бот "Спросить не напрасно". <br />
## Содержание
1. [О чём проект?](#about)
2. [Начало работы](#start)

    2.1. [Настройка poetry](#poetry)

    2.2. [Настройка pre-commit](#pre-commit)

3. [Настройка переменных окружения](#env)

4. [Запуск бота](#run-bot)

    4.1. [Запуск проекта локально](#run-local)

    4.2. [Запуск в Docker](#run-docker)


<br /><br />

# 1. О чём проект? <a id="about"></a>

#### Проект телеграм-бота, который позволяет экспертам оперативно получать информацию о заявках и их статусе, а также другую интересующую информацию в рамках проекта [“Просто спросить”](https://ask.nenaprasno.ru/).<br />
Бот общается с сайтом через API, документацию для которой можно найти [здесь](https://api-ask-nnyp.klbrtest.ru/__docs-ask/#/).
<br />

# 2. Начало работы <a id="start"></a>

## 2.1. Poetry (инструмент для работы с виртуальным окружением и сборки пакетов)<a id="poetry"></a>:

Poetry - это инструмент для управления зависимостями и виртуальными окружениями, также может использоваться для сборки пакетов. В этом проекте Poetry необходим для дальнейшей разработки приложения.<br />

<details>
 <summary>
 Как скачать и установить?
 </summary>

### Установка:

Установите poetry следуя [инструкции с официального сайта](https://python-poetry.org/docs/#installation).
<details>
 <summary>
 Команды для установки:
 </summary>
Для UNIX-систем и Bash on Windows вводим в консоль следующую команду:

> *curl -sSL https://install.python-poetry.org | python -*

Для WINDOWS PowerShell:

> *(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -*
</details>
<br />
После установки перезапустите оболочку и введите команду

> poetry --version

Если установка прошла успешно, вы получите ответ в формате

> Poetry (version 1.2.0)

Для дальнейшей работы введите команду:

> poetry config virtualenvs.in-project true

Выполнение данной команды необходимо для создания виртуального окружения в
папке проекта, по умолчанию папка .venv создается по пути **C:\Users\username\AppData\Local\pypoetry\Cache\virtualenvs**

После предыдущей команды создадим виртуальное окружение нашего проекта с
помощью команды

> poetry install

Результатом выполнения команды станет создание в корне проекта папки .venv.
Зависимости для создания окружения берутся из файлов poetry.lock (приоритетнее)
и pyproject.toml

Для добавления новой зависимости в окружение необходимо выполнить команду

> poetry add <package_name>

_Пример использования:_

> poetry add starlette

Также poetry позволяет разделять зависимости необходимые для разработки, от
основных.
Для добавления зависимости необходимой для разработки и тестирования необходимо
добавить флаг ***--dev***

> poetry add <package_name> --dev

_Пример использования:_

> poetry add pytest --dev

</details>

<details>
 <summary>
 Порядок работы после настройки
 </summary>

<br />

Чтобы активировать виртуальное окружение введите команду:

> poetry shell

Существует возможность запуска скриптов и команд с помощью команды без
активации окружения:

> poetry run <script_name>.py

_Примеры:_

> poetry run python script_name>.py
>
> poetry run pytest
>
> poetry run black

Порядок работы в оболочке не меняется. Пример команды для Win:

> python src\run_bot.py

Доступен стандартный метод работы с активацией окружения в терминале с помощью команд:

Для WINDOWS:

> source .venv/Scripts/activate

Для UNIX:

> source .venv/bin/activate

</details>

<details>
 <summary>
 Настройка pre-commit <a id="pre-commit"></a>
 </summary>
<br />

> poetry install
>
> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому стилю.
</details>

# 3. Настройка переменных окружения <a id="env"></a>
Перед запуском проекта необходимо создать копию файла
```.env.example```, назвав его ```.env``` и установить значение токена бота
<details>
 <summary>
 Переменные окружения
 </summary>
<br />

```dotenv
TELEGRAM_TOKEN=1234567890:ABCDEFGHIGKLMNOPQRST-UVWXYZ12345678   # Токен телеграм бота
APPLICATION_URL=http://example.url/                             # адрес сервера, где будет запущен бот
HOST=127.0.0.1                                                  # host для доступа к uvicorn серверу, по умолчанию localhost или 127.0.0.1
SECRET_TELEGRAM_TOKEN=Secret-telegram_token1                    # токен, с которым телеграм будет обращаться к боту. Допускаются только символы A-Z, a-z, 0-9, _, -

WEEKLY_STAT_TIME=10:00                                          # время еженедельной статистики (UTC)
WEEKLY_STAT_WEEK_DAYS=0                                         # дни недели для еженедельной статистики 0-6, где 0 - воскресенье

MONTHLY_STAT_TIME=11:00                                         # время ежемесячной статистики (UTC)
MONTHLY_STAT_DAY=28                                             # день для даты ежемесячной статистики

MONTHLY_RECEIPT_REMINDER_TIME=12:00                             # время для ежемесячного напоминания о чеке
MONTHLY_RECEIPT_REMINDER_DAY=20                                 # день для даты ежемесячного напоминания о чеке

DAILY_CONSULTATIONS_REMINDER_TIME=17:00                         # время ежедневного получения напоминаний о просроченных заявках

STAT_COLLECTION_TIME=00:00                                      # запуск сбора недельной и месячной статистики - по умолчанию, полночь GTM+12

SITE_API_BOT_TOKEN=3422b448-2460-4fd2-9183-8000de6f8343         # Токен(uuid) для идентификации бота на сайте.
URL_ASK_NENAPRASNO_API=http://example.url/                      # адрес сервера, к которому будет отправлять запросы АПИ клиент
URL_ASK_NENAPRASNO=http://example.url/                          # главный url nenaprasno
IS_FAKE_API=False                                               # флаг, определяющий какой АПИ клиент используется - боевой или "заглушка", отдающая фейковые данные

LOG_LEVEL=DEBUG                                                 # Уровень записи логов

TRELLO_BORD_ID=14nNNGRp                                         # доска в TRELLO

```

</details>

# 4. Запуск бота <a id="run-bot"></a>

### Возможен запуск бота в режимах `polling` или `webhook`.<br/>
## 4.1. Запуск проекта локально <a id="run-local"></a>
<details>
 <summary>
 Запуск проекта локально
 </summary>
<br />

### 4.1.1. Запуск в режиме Polling
<br />

```shell
python src/run_bot.py
```

### 4.1.2. Запуск в режиме Webhook

#### <b>Отладка приложения с ботом в режиме webhook на локальном компьютере требует выполнения дополнительных действий:</b>
<br />
<details>
 <summary>
 Необходимые действия
 </summary><br>

В случае отсутствия сервера с доменным именем и установленным SSL-сертификатом, для отладки приложения можно воспользоваться <a href="https://ngrok.com/">ngrok</a> для построения туннеля до вашего компьютера.<br>
Для этого необходимо:
 - Скачать и установить <a href="https://ngrok.com/">ngrok</a>
 - Зарегистрироваться в сервисе <a href="https://ngrok.com/">ngrok</a> и получить <a href="https://dashboard.ngrok.com/get-started/your-authtoken">токен</a>
 - Зарегистрировать полученный токен на локальном комьютере
 ```shell
 ngrok config add-authtoken <ваш токен>
 ```
 - Запустить тоннель ngrok
 ```shell
 ngrok http 8000 --host-header=site.local
 ```
 - Скопировать из консоли адрес (`https`), предоставленный сервисом `ngrok`, в переменную окружения `APPLICATION_URL`:
 ```dotenv
 APPLICATION_URL=https://1234-56-78-9.eu.ngrok.io # пример
 ```
 - Запустить приложение с ботом в режиме webhook (см. выше)
  ```shell
python src/run_webhook_api.py
 ```

Более подробная информация об использовании сервиса ngrok доступна на <a href="https://ngrok.com/">официальном сайте</a>
</details>

<br />


```shell
python src/run_webhook_api.py
```


</details>

## 4.2. Запуск проекта в Docker <a id="run-docker"></a>
<details>
 <summary>
 Запуск проекта через Docker
 </summary>
<br />
Можно запустить бота через docker-compose в тестовом режиме. Для этого в корневой папке проекта выполнить команду
  ```shell
docker-compose up -d --build
```

В папке infrastructure лежит набор файлов для запуска бота на сервере в контейнерах docker

**infrastructure/docker-compose.yaml** - файл для запуска контейнеров nginx и docker

**infrastructure/nginx/nginx.conf** - конфигурационный файл сервера nginx

**infrastructure/nginx/robots.txt** - файл с инструкциями по индексации для роботов

Для запуска на сервере необходимо выполнить следующую последовательность действий:
1. Скопировать файл infrastructure/docker-compose.yaml в ~/code/docker-compose.yaml на сервере
2. Остановить nginx на сервере и запретить ему автозапуск
3. Перейти в эту папку и запустить бота
4. Проверить, что веб-сервер работает командой curl

> sudo systemctl stop nginx
>
> sudo systemctl disable nginx
>
> cd code
>
> sudo docker-compose up -d
>
> curl https://nenaprasno.agamova.ru/healthcheck

</details>
