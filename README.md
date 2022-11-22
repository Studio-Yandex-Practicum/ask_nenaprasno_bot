# Бот "Спросить не напрасно".

## Содержание
1. [О чём проект?](#about)
2. [Подготовка к запуску](#start)

    2.1. [Настройка poetry](#poetry)

    2.2. [Настройка pre-commit](#pre-commit)

    2.3. [Настройка переменных окружения](#env)

3. [Запуск бота](#run-bot)

    3.1. [Запуск проекта локально](#run-local)

    3.2. [Запуск в Docker](#run-docker)


<br><br>

# 1. О чём проект? <a id="about"></a>

#### Проект телеграм-бота, который позволяет экспертам оперативно получать информацию о заявках и их статусе, а также другую интересующую информацию в рамках проекта [“Просто спросить”](https://ask.nenaprasno.ru/).

Бот общается с сайтом через API.

Информация о событиях (таких, как назначение новой заявки, получение сообщения от клиента) отправляется от API сайта боту через Webhook.

По расписанию, настроенному через переменные окружения, бот запрашивает через API и отправляет в чат пользователю сводную информацию по заявкам (стастистику за неделю/месяц, список открытых заявок), напоминает о текущих заявках, находящихся в работе, о том, что срок ответа на заявку подходит к концу и уже пришла пора над ней поработать.
Эта же информация также доступна по запросу через меню бота.

Бот позволяет настроить часовой пояс для того, чтобы уведомления приходили в удобное пользователю время.
<br>

# 2. Подготовка к запуску <a id="start"></a>

Примечение: использование Poetry и pre-commit при работе над проектом обязательно.

## 2.1. Poetry (инструмент для работы с виртуальным окружением и сборки пакетов)<a id="poetry"></a>:

Poetry - это инструмент для управления зависимостями и виртуальными окружениями, также может использоваться для сборки пакетов. В этом проекте Poetry необходим для дальнейшей разработки приложения, его установка <b>обязательна</b>.<br>

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
<br>
После установки перезапустите оболочку и введите команду

> poetry --version

Если установка прошла успешно, вы получите ответ в формате

> Poetry (version 1.2.0)

Для дальнейшей работы введите команду:

> poetry config virtualenvs.in-project true

Выполнение данной команды необходимо для создания виртуального окружения в
папке проекта.

После предыдущей команды создадим виртуальное окружение нашего проекта с
помощью команды:

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

<br>

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

## 2.1. Pre-commit (инструмент автоматического запуска различных проверок перед выполнением коммита)<a id="pre-commit"></a>:

<details>
 <summary>
 Настройка pre-commit
 </summary>
<br>

> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому стилю.
</details>

## 2.3. Настройка переменных окружения <a id="env"></a>

Перед запуском проекта необходимо создать копию файла
```.env.example```, назвав его ```.env``` и установить значение токена бота

# 3. Запуск бота <a id="run-bot"></a>

### Возможен запуск бота в режимах `polling` или `webhook`.<br/>
## 3.1. Запуск проекта локально <a id="run-local"></a>
<details>
 <summary>
 Запуск проекта локально
 </summary>
<br>

### 3.1.1. Запуск в режиме Polling
<br>

```
python src/run_bot.py
```

### 3.1.2. Запуск в режиме Webhook

#### <b>Отладка приложения с ботом в режиме webhook на локальном компьютере требует выполнения дополнительных действий:</b>
<br>
<details>
 <summary>
 Необходимые действия
 </summary><br>

В случае отсутствия сервера с доменным именем и установленным SSL-сертификатом, для отладки приложения можно воспользоваться <a href="https://ngrok.com/">ngrok</a> для построения туннеля до вашего компьютера.<br>
Для этого необходимо:
 - Скачать и установить <a href="https://ngrok.com/">ngrok</a>
 - Зарегистрироваться в сервисе <a href="https://ngrok.com/">ngrok</a> и получить <a href="https://dashboard.ngrok.com/get-started/your-authtoken">токен</a>
 - Зарегистрировать полученный токен на локальном комьютере
 ```
 ngrok config add-authtoken <ваш токен>
 ```
 - Запустить тоннель ngrok
 ```
 ngrok http 8000 --host-header=site.local
 ```
 - Скопировать из консоли адрес (`https`), предоставленный сервисом `ngrok`, в переменную окружения `APPLICATION_URL`:
 ```
 APPLICATION_URL=https://1234-56-78-9.eu.ngrok.io # пример
 ```
 - Запустить приложение с ботом в режиме webhook (см. выше)
  ```
python src/run_webhook_api.py
 ```

Более подробная информация об использовании сервиса ngrok доступна на <a href="https://ngrok.com/">официальном сайте</a>
</details>

<br>


```
python src/run_webhook_api.py
```


</details>

## 3.2. Запуск проекта в Docker <a id="run-docker"></a>
<details>
 <summary>
 Запуск проекта через Docker
 </summary>
<br>
Можно запустить бота через docker-compose в тестовом режиме. Для этого в корневой папке проекта выполнить команду
  ```
docker-compose up -d --build
```

</details>
