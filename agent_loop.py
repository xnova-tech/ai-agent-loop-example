"""Учебный цикл вызова инструментов: решения задаёт код, а не LLM."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Call:
    name: str
    service: str


@dataclass(frozen=True)
class Finish:
    message: str


@dataclass(frozen=True)
class Observation:
    tool: str
    result: str


@dataclass(frozen=True)
class RunResult:
    status: str
    trace: tuple[str, ...]
    message: str


def get_status(service: str) -> str:
    return {"api": "HTTP 503", "worker": "HTTP 200"}[service]


def get_runbook(service: str) -> str:
    return {"api": "проверить журнал и upstream"}[service]


def choose_next(observations: list[Observation]) -> Call | Finish:
    """Детерминированная заглушка решения, НЕ языковая модель."""
    if not observations:
        return Call("get_status", "api")
    last = observations[-1]
    if last.tool == "get_status" and last.result == "HTTP 503":
        return Call("get_runbook", "api")
    if last.tool == "get_status":
        return Finish("Сервис отвечает; дополнительных проверок нет.")
    return Finish("HTTP 503; следующий шаг: " + last.result + ".")


def run_loop(
    decide: Callable[[list[Observation]], Call | Finish] = choose_next,
    tools: dict[str, Callable[[str], str]] | None = None,
    max_steps: int = 3,
) -> RunResult:
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    available = tools if tools is not None else {
        "get_status": get_status,
        "get_runbook": get_runbook,
    }
    observations: list[Observation] = []
    trace: list[str] = []

    while True:
        action = decide(list(observations))
        if isinstance(action, Finish):
            return RunResult("completed", tuple(trace), action.message)
        if not isinstance(action, Call):
            return RunResult("blocked", tuple(trace), "неверный формат решения")
        if len(observations) >= max_steps:
            return RunResult("limit", tuple(trace), "достигнут лимит вызовов")
        if action.name not in available:
            return RunResult("blocked", tuple(trace), "инструмент не разрешён: " + action.name)
        if not isinstance(action.service, str) or action.service not in {"api", "worker"}:
            return RunResult("blocked", tuple(trace), "недопустимый аргумент service")
        try:
            value = available[action.name](action.service)
        except (KeyError, RuntimeError) as exc:
            return RunResult("error", tuple(trace), "ошибка инструмента: " + type(exc).__name__)
        observations.append(Observation(action.name, value))
        trace.append(f"{action.name}({action.service}) -> {value}")


def main() -> None:
    result = run_loop()
    for event in result.trace:
        print(event)
    print(f"{result.status}: {result.message}")


if __name__ == "__main__":
    main()
