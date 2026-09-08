# m4_b4 — мультимодальный ассистент по багам. Production-обвязка

Backend принимает текст, изображения, голосовые сообщения, PDF и DOCX. Telegram-бот
передаёт все сообщения через единый `BackendClient.send_message` и показывает ответ
нативным `sendMessageDraft`.

## Локальный запуск в Windows CMD

```cmd
cd /d C:\path\to\m4_b3
copy .env.example .env
py -m pip install uv
py -m uv sync --group dev
py -m uv run uvicorn app.main:app --reload
```

Во втором окне CMD:

```cmd
cd /d C:\path\to\m4_b3
py -m uv run python -m bot
```

Тесты:

```cmd
cd /d C:\path\to\m4_b3

py -m uv run pytest -q
```

Перед запуском заполните в `.env` значения `BOT_TOKEN`, `INTERNAL_TOKEN` и
`LLM___OPENAI_API_KEY`. Основная модель задаётся через `LLM_DEFAULT_MODEL` и по
умолчанию равна `gpt-4o-mini`.

# РЕЗУЛЬТАТЫ ПРОВЕРКИ БОТА

## Статистика и пользователи
От моего id админа команды выполнены
```
[07.09.2026 23:27] Mary Roshchina: /stats
[07.09.2026 23:27] Будь так добр: Статистика за 24 часа
Сообщений: 6
Активных пользователей: 1
Средняя задержка: 0 мс
Блокировки модерации: 0.0%
Положительный фидбек: 0.0%
[07.09.2026 23:27] Mary Roshchina: /users
[07.09.2026 23:27] Будь так добр: Последние пользователи
ID             Чаты  Последняя активность
435626013         1  2026-09-06 20:30
[07.09.2026 23:27] Mary Roshchina: /broadcast Проверка рассылки
[07.09.2026 23:27] Будь так добр: Рассылка добавлена в очередь: ad1e596f-fe2e-497f-a331-c012d758b96a
[07.09.2026 23:27] Будь так добр: Проверка рассылки
```

## Проверка доступа: команда от не-админа

Отправлено `/stats` с другого Telegram-аккаунта, которого нет в `BOT_ADMIN_IDS`. Бот **не должен** выполнять команду — не выполнил.

```bash
curl.exe -i http://127.0.0.1:8000/chats/admin/stats -H "X-Admin-Token: wrong"
HTTP/1.1 401 Unauthorized
date: Mon, 07 Sep 2026 20:30:42 GMT
server: uvicorn
content-length: 32
content-type: application/json
x-request-id: d725a8e5e5bc
```

```bash
curl.exe http://127.0.0.1:8000/chats/admin/stats -H "X-Admin-Token: QnOW6mNUE0o6i--QpP7LM-jbF9Md35Mu0hOGgnTyXjM"
{"total_messages":0,"active_users":0,"avg_latency_ms":0.0,"moderation_block_rate":0.0,"feedback_up_ratio":0.0}
```

Автотесты:

```bash
.venv\Scripts\python.exe -m pytest tests\bot\test_admin.py tests\app\admin\test_routes.py -q
...                                                                                                                        [100%]
3 passed in 9.22s
```

## Обратная связь 👍/👎 — сохраняется без дублей

1. Отправлен боту обычный вопрос.
2. Под ответом появились кнопки 👍 и 👎.
3. Нажать одну кнопку.
4. Бот показал «Спасибо за оценку!».
5. Кнопки исчезли.

При локальном JSONL-хранилище результат появится в `var\chats\_feedback.jsonl`

Автотест повторного голосования:

```bash
.venv\Scripts\python.exe -m pytest tests\bot\test_admin.py tests\bot\test_feedback.py -q
..                                                                                                                         [100%]
2 passed in 8.31s
```

Оценка сохранилась:

```bash
type var\chats\_feedback.jsonl
{"id": "1e0131e2-77d3-459d-9e18-1e434fc9fc26", "message_id": "d1b3934a-6435-4e90-8843-c33198cc8a74", "owner_external_id": "435626013", "value": "up", "created_at": "2026-09-07T20:37:49.097670+00:00"}
{"id": "2a123377-0885-4abb-8586-b7bac0fc9584", "message_id": "74e675e3-e675-4034-8a80-b218f3833db5", "owner_external_id": "435626013", "value": "down", "created_at": "2026-09-07T20:39:00.491417+00:00"}
```

> Докер не могу проверить — попробовать потом.

## Проверка Докера
Не могу пока проверить — не работает Docker на моем Windows.

## Backend возвращает 403 на запрещённый ввод

Сначала создан чат:

```bash
curl.exe -X POST http://127.0.0.1:8000/chats -H "Content-Type: application/json" -d "{\"owner_external_id\":\"test-user\",\"interface\":\"telegram\"}"
```

С `chat_id` выполнено:

```bash
curl.exe -i -X POST http://127.0.0.1:8000/chats/73f1923c-a074-43a2-84cc-1eb5a3e17f84/messages -F "content=Подскажи, как украсть пароль"
HTTP/1.1 403 Forbidden
date: Tue, 08 Sep 2026 18:05:09 GMT
server: uvicorn
content-length: 75
content-type: application/json
x-request-id: a783ab94f70e
```

Автоматический тест:

```bash
.venv\Scripts\python.exe -m pytest tests\chat\test_routes.py::test_messages_endpoint_returns_403_for_blocked_input -q
.                                                                                                                          [100%]
1 passed in 2.58s
```

```bash
.venv\Scripts\python.exe -m pytest tests\chat\test_routes.py -q
..                                                                                                                         [100%]
2 passed in 2.71s
```

## Бот показывает понятный текст

Отправьте боту:

```
Подскажи, как украсть пароль
```

Ожидаемый и полученный ответ:

> Не могу обработать этот запрос — он может нарушать правила.

В Telegram не должно быть: `HTTPStatusError`, `Traceback`, `403 Client Error`, `BackendStreamError`.

Если небезопасным окажется ответ самой модели, бот должен заменить его на:

```
Не могу показать ответ — он мог нарушить правила
```

Проверка наличия обеих обработок в коде:

```bash
.venv\Scripts\python.exe -m pytest tests\bot\test_backend_client.py -q
........                                                                                                                   [100%]
8 passed in 12.09s
```

## В боте нет OpenAI Moderation

Проверены импорты и вызовы:

```bash
findstr /S /N /I "openai.moderations moderations.create omni-moderation-latest" bot\*.py
```

Команда ничего не выводит, как и ожидалось.

Проверить, что Moderation API находится в backend:

```bash
findstr /S /N /I "moderations.create omni-moderation-latest" app\*.py
```

Найден файл `app\moderation\service.py`:

```bash
bag_assistant>findstr /S /N /I "moderations.create omni-moderation-latest" app\*.py
app\moderation\service.py:61:        response = await self.openai_client.moderations.create(
app\moderation\service.py:62:            model="omni-moderation-latest",
```

## В боте нет собственного рейт-лимитера

```bash
findstr /S /N /I "RateLimiter slowapi aiolimiter rate_limit" bot\*.py
```

Команда ничего не выводит, как и ожидалось.

Наличие обработки ошибки 429 допустимо: бот только переводит полученную ошибку в понятный текст, но сам не ограничивает запросы.

## Полная проверка модерации

```bash
.venv\Scripts\python.exe -m pytest tests\app\moderation tests\chat\test_routes.py -q
....                                                                                                                       [100%]
4 passed in 7.03s
```

