"""Shared test fixtures."""
from __future__ import annotations

from typing import Any

from unittest.mock import AsyncMock, MagicMock

import pytest

from betterdb_agent_cache.telemetry import AgentCacheMetrics, Telemetry


def _noop_span():
    """Return a context-manager span that does nothing."""
    span = MagicMock()
    span.__enter__ = MagicMock(return_value=span)
    span.__exit__ = MagicMock(return_value=False)
    span.set_attribute = MagicMock()
    span.record_exception = MagicMock()
    return span


def make_telemetry() -> Telemetry:
    tracer = MagicMock()
    tracer.start_as_current_span = MagicMock(return_value=_noop_span())

    def _counter():
        m = MagicMock()
        m.labels = MagicMock(return_value=MagicMock(inc=MagicMock()))
        return m

    def _histogram():
        m = MagicMock()
        m.labels = MagicMock(return_value=MagicMock(observe=MagicMock()))
        return m

    def _gauge():
        m = MagicMock()
        m.labels = MagicMock(return_value=MagicMock(inc=MagicMock(), dec=MagicMock(), set=MagicMock()))
        return m

    metrics = AgentCacheMetrics(
        requests_total=_counter(),
        operation_duration=_histogram(),
        cost_saved=_counter(),
        stored_bytes=_counter(),
        active_sessions=_gauge(),
        config_refresh_failed=_counter(),
        discovery_write_failed=_counter(),
    )
    return Telemetry(tracer=tracer, metrics=metrics)


def make_client() -> MagicMock:
    """Return an async mock that behaves like a valkey.asyncio.Valkey client."""
    client = MagicMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.expire = AsyncMock(return_value=1)
    client.hincrby = AsyncMock(return_value=1)
    client.hget = AsyncMock(return_value=None)
    client.hgetall = AsyncMock(return_value={})
    client.hset = AsyncMock(return_value=1)
    client.scan = AsyncMock(return_value=(0, []))

    # pipeline() returns a mock that queues commands and executes them
    pipe = MagicMock()
    pipe.get = MagicMock()
    pipe.set = MagicMock()
    pipe.delete = MagicMock()
    pipe.expire = MagicMock()
    pipe.hincrby = MagicMock()
    pipe.execute = AsyncMock(return_value=[])
    pipe.__aenter__ = AsyncMock(return_value=pipe)
    pipe.__aexit__ = AsyncMock(return_value=False)
    client.pipeline = MagicMock(return_value=pipe)

    return client


def make_persisting_valkey_client() -> MagicMock:
    """Async Redis/Valkey-shaped client with in-memory persistence for adapter tests.

    Supports GET/SET/DELETE, HGET/HSET, SCAN (no-op), and pipeline
    (hincrby/get/set/delete + execute) used by LLM cache and discovery.
    """
    kv: dict[str, bytes] = {}
    hmaps: dict[str, dict[str, bytes]] = {}

    def nk(x: str | bytes) -> str:
        return x.decode() if isinstance(x, bytes) else str(x)

    def hincrby_store(name: str, field: str, amount: int) -> int:
        m = hmaps.setdefault(name, {})
        cur = int(m.get(field, b"0").decode() or "0")
        newv = cur + amount
        m[field] = str(newv).encode()
        return newv

    client = make_client()

    async def _get(key: str | bytes) -> bytes | None:
        return kv.get(nk(key))

    async def _set(key: str | bytes, value: Any, *args: Any, **kwargs: Any) -> bool:
        kv[nk(key)] = value if isinstance(value, bytes) else str(value).encode()
        return True

    async def _delete(key: str | bytes) -> int:
        k = nk(key)
        return 1 if kv.pop(k, None) is not None else 0

    async def _hget(name: str | bytes, field: str | bytes) -> bytes | None:
        m = hmaps.get(nk(name), {})
        return m.get(nk(field))

    async def _hset(name: str | bytes, field: str | bytes, value: Any) -> int:
        n, f = nk(name), nk(field)
        bval = value if isinstance(value, bytes) else str(value).encode()
        hmaps.setdefault(n, {})[f] = bval
        return 1

    async def _hgetall(name: str | bytes) -> dict[bytes, bytes]:
        m = hmaps.get(nk(name), {})
        return {fk.encode(): fv for fk, fv in m.items()}

    async def _scan(cursor: int, match: str = "*", count: int = 100) -> tuple[int, list[Any]]:
        return 0, []

    client.get = AsyncMock(side_effect=_get)
    client.set = AsyncMock(side_effect=_set)
    client.delete = AsyncMock(side_effect=_delete)
    client.hget = AsyncMock(side_effect=_hget)
    client.hset = AsyncMock(side_effect=_hset)
    client.hgetall = AsyncMock(side_effect=_hgetall)
    client.scan = AsyncMock(side_effect=_scan)

    def _pipeline(transaction: bool = False) -> MagicMock:
        pipe = MagicMock()
        ops: list[tuple[Any, ...]] = []

        def _hincrby(name: str | bytes, field: str | bytes, amount: int) -> MagicMock:
            ops.append(("hincrby", nk(name), nk(field), int(amount)))
            return pipe

        def _pget(key: str | bytes) -> MagicMock:
            ops.append(("get", nk(key)))
            return pipe

        def _pset(key: str | bytes, val: Any, **kw: Any) -> MagicMock:
            ops.append(("set", nk(key), val))
            return pipe

        def _pdel(key: str | bytes) -> MagicMock:
            ops.append(("delete", nk(key)))
            return pipe

        pipe.hincrby = MagicMock(side_effect=_hincrby)
        pipe.get = MagicMock(side_effect=_pget)
        pipe.set = MagicMock(side_effect=_pset)
        pipe.delete = MagicMock(side_effect=_pdel)

        async def _execute() -> list[Any]:
            results: list[Any] = []
            for op in ops:
                if op[0] == "hincrby":
                    results.append(hincrby_store(op[1], op[2], op[3]))
                elif op[0] == "get":
                    results.append(kv.get(op[1]))
                elif op[0] == "set":
                    v = op[2]
                    kv[op[1]] = v if isinstance(v, bytes) else str(v).encode()
                    results.append(True)
                elif op[0] == "delete":
                    results.append(1 if kv.pop(op[1], None) is not None else 0)
            ops.clear()
            return results

        pipe.execute = AsyncMock(side_effect=_execute)
        return pipe

    client.pipeline = MagicMock(side_effect=_pipeline)
    return client


@pytest.fixture
def telemetry() -> Telemetry:
    return make_telemetry()


@pytest.fixture
def valkey_client() -> MagicMock:
    return make_client()
