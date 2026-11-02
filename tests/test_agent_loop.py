"""Контрактные тесты учебного цикла вызова инструментов."""

import pytest

from agent_loop import Call, run_loop


def test_successful_two_tool_path() -> None:
    result = run_loop()

    assert result.status == "completed"
    assert result.trace == (
        "get_status(api) -> HTTP 503",
        "get_runbook(api) -> проверить журнал и upstream",
    )
    assert result.message == "HTTP 503; следующий шаг: проверить журнал и upstream."


def test_healthy_service_stops_after_status() -> None:
    result = run_loop(tools={"get_status": lambda _: "HTTP 200"})

    assert result.status == "completed"
    assert len(result.trace) == 1


def test_unknown_tool_is_blocked() -> None:
    result = run_loop(decide=lambda _: Call("unlisted_tool", "api"))

    assert result.status == "blocked"
    assert "unlisted_tool" in result.message


def test_write_like_tool_is_blocked_before_execution() -> None:
    result = run_loop(decide=lambda _: Call("delete_logs", "api"))

    assert result.status == "blocked"
    assert result.trace == ()


def test_invalid_service_is_blocked_before_execution() -> None:
    result = run_loop(decide=lambda _: Call("get_status", "../../secrets"))

    assert result.status == "blocked"
    assert result.trace == ()


def test_tool_failure_is_reported() -> None:
    def fail(_: str) -> str:
        raise RuntimeError("down")

    result = run_loop(tools={"get_status": fail})

    assert result.status == "error"
    assert result.trace == ()


def test_step_limit_stops_before_second_tool() -> None:
    result = run_loop(max_steps=1)

    assert result.status == "limit"
    assert len(result.trace) == 1


def test_invalid_decision_is_blocked() -> None:
    result = run_loop(decide=lambda _: "do something")  # type: ignore[arg-type]

    assert result.status == "blocked"


def test_non_positive_step_limit_is_rejected() -> None:
    with pytest.raises(ValueError, match="max_steps must be positive"):
        run_loop(max_steps=0)
