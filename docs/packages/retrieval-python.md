---
layout: default
title: Retrieval (Python)
parent: Packages
nav_order: 8
---

# Retrieval (Python)

`betterdb-retrieval` is the Python counterpart to [`@betterdb/retrieval`](/docs/packages/retrieval): a developer-facing retrieval SDK over [Valkey Search](https://valkey.io/topics/search/) (`FT.*`) with a typed index schema, idempotent index lifecycle, upsert/delete, and vector + filtered + hybrid query. Built on [`betterdb-valkey-search-kit`](/docs/packages/valkey-search-kit-python).

Same architecture and same Valkey data format as the TypeScript package - a TypeScript app and a Python app can share the same index.

## Prerequisites

- **Valkey 8.0+** with the `valkey-search` module loaded
- Or **Amazon ElastiCache for Valkey** (8.0+)
- Or **Google Cloud Memorystore for Valkey**
- Python >= 3.11

## Installation

```bash
pip install betterdb-retrieval valkey
```

## Quick start

```python
from valkey.asyncio import Valkey

from betterdb_retrieval import Retriever, UpsertEntry

client = Valkey.from_url("redis://localhost:6379")


async def embed(text: str) -> list[float]:
    ...  # return an embedding


retriever = Retriever(
    client=client,
    name="docs",
    schema={
        "fields": {
            "category": {"type": "tag"},
            "year": {"type": "numeric", "sortable": True},
        },
        "vector": {"algorithm": "hnsw", "metric": "cosine"},
    },
    embed_fn=embed,
)

# Create the index if it doesn't exist (idempotent; dims resolved from embed_fn).
await retriever.create_index()

await retriever.upsert([
    UpsertEntry(
        id="doc1",
        text="Valkey is a high-performance key-value store",
        fields={"category": "db", "year": 2024},
    ),
])

hits = await retriever.query(
    text="fast in-memory database",
    k=5,
    filter={"category": "db"},
)
```

## Retriever API

| Method | Description |
|--------|-------------|
| `create_index()` | Create the index if absent (idempotent). Vector dimension is taken from `schema["vector"]["dims"]` or resolved by probing `embed_fn`. |
| `upsert(entries)` | Embed each entry's `text` and write it as a hash with its `fields`. |
| `delete(ids)` | Delete documents by id. |
| `query(*, k, text=None, vector=None, filter=None, hybrid=None)` | KNN search. Provide `text` (embedded for you) or a precomputed `vector`, a positive `k`, an optional `filter` (tag/numeric fields), and `hybrid="rerank"` to post-process hits through a `rerank_fn`. Returns `list[QueryHit]`. |
| `describe_index()` / `health()` | Index stats: doc count, indexing state, dimension, percent indexed, and an optional estimated recall. |
| `drop_index()` | Drop the index (no-op if it doesn't exist). |
| `register()` / `unregister()` | Publish/remove a discovery marker in the shared `__betterdb:caches` registry, ownership-checked so it never clobbers a foreign cache type. |

> `QueryHit.score` is the raw KNN vector **distance** (lower is closer), not a similarity. Rank ascending.

The `query()` method is keyword-only. `UpsertEntry`, `QueryHit`, and `IndexDescription` are dataclasses with snake_case fields; the schema TypedDicts keep camelCase keys (`fieldName`, `efConstruction`) to match the wire format.

## Observability

Pass `metrics` (a `RetrievalMetrics`) and/or `tracer` (a `RetrievalTracer`) to instrument every operation. `create_prometheus_metrics()` provides a ready-made [prometheus-client](https://github.com/prometheus/client_python) implementation.

## Interoperability with the TypeScript package

The Python and TypeScript packages use the same index schema and the same hash field layout, so an index written by one can be queried by the other. BetterDB Monitor treats them identically through the shared discovery registry.

## See also

- [Retrieval](/docs/packages/retrieval) - the TypeScript original.
- [Valkey Search Kit (Python)](/docs/packages/valkey-search-kit-python) - the low-level helpers this package is built on.
- [Agent Memory (Python)](/docs/packages/agent-memory-python) - a semantic memory tier built on the same foundation.
