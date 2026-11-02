# Учебный цикл AI-агента на Python

Минимальный пример XNova показывает управляющий цикл с разрешёнными инструментами, наблюдениями, ограничением числа шагов и явными состояниями завершения. Функция `choose_next` использует предсказуемые правила: это макет исполняющего контура, а не настоящий LLM-агент.

## Что понадобится

- Python 3.12;
- Git;
- терминал.

## Установка

```bash
git clone https://github.com/xnova-tech/ai-agent-loop-example.git
cd ai-agent-loop-example
python3.12 -m venv .venv
```

Активируйте окружение:

- macOS и Linux: `source .venv/bin/activate`;
- Windows PowerShell: `.venv\Scripts\Activate.ps1`;
- Windows cmd: `.venv\Scripts\activate.bat`.

Установите закреплённую тестовую зависимость:

```bash
python -m pip install -r requirements-dev.txt
```

## Запуск примера

```bash
python agent_loop.py
```

Ожидаемый вывод:

```text
get_status(api) -> HTTP 503
get_runbook(api) -> проверить журнал и upstream
completed: HTTP 503; следующий шаг: проверить журнал и upstream.
```

`HTTP 503` здесь — строка из локального словаря, а не результат сетевого запроса.

## Запуск тестов

```bash
python -m pytest -q
```

Девять тестов проверяют успешный путь, раннее завершение для исправного сервиса, запрет неизвестного и изменяющего инструмента, валидацию аргумента, ошибку инструмента, лимит шагов, неверный формат решения и недопустимый `max_steps`.

## Структура

- `agent_loop.py` — самостоятельный детерминированный пример;
- `tests/test_agent_loop.py` — pytest-контракт управляющего цикла;
- `.github/workflows/check.yml` — проверки на Linux, macOS и Windows.

Проект не обращается к модели, сети, пользовательским файлам или секретам и не выполняет изменяющих операций.

Исходники распространяются по Apache-2.0; условия находятся в `LICENSE`.
