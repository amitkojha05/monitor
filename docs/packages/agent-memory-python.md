---
layout: default
title: Agent Memory (Python)
parent: Packages
nav_order: 10
---

# Agent Memory (Python)

`betterdb-agent-memory` is the Python counterpart to [`@betterdb/agent-memory`](/docs/packages/agent-memory): the long-term memory tier for AI agents, backed by [Valkey Search](https://valkey.io/topics/search/). It pairs with [`betterdb-agent-cache`](https://pypi.org/project/betterdb-agent-cache/) (the short-term llm/tool/session cache tiers).

Where the cache tiers are exact-match and ephemeral, the memory tier is semantic and durable: it embeds content, stores it in an HNSW vector index, and recalls it by meaning with a composite score that blends **similarity**, **recency** (half-life decay), and **importance**.

## Features

- **Semantic recall** - KNN vector search with a tunable composite score.
- **Scoping** - memories carry `thread_id` / `agent_id` / `namespace` / `tags`; recall, forget, and consolidation all filter by scope.
- **Reinforcement** - recalled memories bump `last_accessed_at` + `access_count`, so frequently-used memories stay recallable.
- **Capacity eviction** - `max_items_per_scope` evicts the lowest-scoring memories (importance + recency) once a scope exceeds its cap.
- **Consolidation** - fold a set of older/low-importance memories into a single summary memory.
- **Live config** - re-read recall threshold / weights / half-life / `max_items_per_scope` from a Valkey hash without a restart.
- **Observability** - OpenTelemetry spans + Prometheus metrics.
- **Discovery** - registers a marker so BetterDB Monitor can enumerate the tier.

## Prerequisites

- **Valkey 8.0+** with the `valkey-search` module loaded (e.g. `valkey/valkey-bundle`)
- Or **Amazon ElastiCache for Valkey** (8.0+)
- Or **Google Cloud Memorystore for Valkey**
- Python >= 3.11
- The [`valkey`](https://pypi.org/project/valkey/) async client and an embedding function you provide

## Installation

```bash
pip install betterdb-agent-memory
```

## Quick start

```python
import valkey.asyncio as valkey
from betterdb_agent_memory import AgentMemory, AgentMemoryOptions


async def embed(text: str) -> list[float]:
    # Replace with a real embedding model (OpenAI, sentence-transformers, ...).
    ...


async def main() -> None:
    client = valkey.Valkey(host="localhost", port=6379)
    agent = AgentMemory(AgentMemoryOptions(client=client, embed_fn=embed))
    await agent.initialize()

    await agent.memory.remember(
        "User prefers dark mode and concise answers.",
        importance=0.8,
        tags=["preference", "ui"],
        thread_id="t1",
    )

    hits = await agent.memory.recall("what UI settings does the user like?", thread_id="t1")
    for hit in hits:
        print(hit.score, hit.item.content)

    # Short-term cache tiers remain available: agent.llm, agent.tool, agent.session
    await agent.close()
```

## Using the memory tier standalone

If you only need the memory tier, construct `MemoryStore` directly:

```python
from betterdb_agent_memory import MemoryStore

store = MemoryStore(client=client, name="myapp", embed_fn=embed)
await store.ensure_index()
await store.remember("hello", thread_id="t1")
hits = await store.recall("hi", thread_id="t1")
```

## MemoryStore API

| Method | Signature |
|--------|-----------|
| `ensure_index` | `await ensure_index()` - create the `{name}:mem:idx` HNSW index if absent. |
| `remember` | `await remember(content, *, importance=None, tags=None, source=None, ttl=None, thread_id=None, agent_id=None, namespace=None) -> str` |
| `recall` | `await recall(query, *, k=None, threshold=None, tags=None, weights=None, reinforce=None, thread_id=None, agent_id=None, namespace=None) -> list[MemoryHit]` |
| `forget` | `await forget(id) -> bool` |
| `forget_by_scope` | `await forget_by_scope(*, thread_id=None, agent_id=None, namespace=None, tags=None) -> int` |
| `consolidate` | `await consolidate(*, summarize, older_than_seconds=None, max_importance=None, delete_sources=None, summary_importance=None, tags=None, thread_id=None, agent_id=None, namespace=None) -> ConsolidateResult` |
| `current_config` | `current_config() -> MemoryConfigSnapshot` |
| `refresh_config` | `await refresh_config()` |
| `close` | `await close()` |

### `AgentMemory`

The batteries-included facade: an `AgentCache` (llm/tool/session) plus a `MemoryStore` sharing one client and name. `initialize()` creates the index and readies discovery for both tiers; `close()` tears both down.

## Scoring

```
composite_score = w.similarity * similarity + w.recency * recency + w.importance * importance
```

where `similarity = 1 - distance / 2` (cosine distance -> 0..1) and `recency` decays with a true half-life (`0.5` at one `half_life_seconds`). Default weights are `{similarity: 0.6, recency: 0.25, importance: 0.15}`, default threshold `0.25`, default half-life 7 days.

## Interoperability with the TypeScript package

The Python and TypeScript packages use the same vector index name, hash field layout, and config hash, so a memory written by one can be recalled by the other. BetterDB Monitor enumerates them identically through the shared discovery registry.

## See also

- [Agent Memory](/docs/packages/agent-memory) - the TypeScript original.
- [Semantic Cache (Python)](/docs/packages/semantic-cache-python) and [Retrieval (Python)](/docs/packages/retrieval-python) - related Valkey Search SDKs.
- [Valkey Search Kit (Python)](/docs/packages/valkey-search-kit-python) - the low-level helpers underneath.
