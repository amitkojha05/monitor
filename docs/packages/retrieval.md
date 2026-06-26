---
layout: default
title: Retrieval
parent: Packages
nav_order: 7
---

# Retrieval

`@betterdb/retrieval` is a developer-facing retrieval SDK over [Valkey Search](https://valkey.io/topics/search/) (`FT.*`): a typed index schema, idempotent index lifecycle, upsert/delete, and vector + filtered + hybrid query. It is built on [`@betterdb/valkey-search-kit`](/docs/packages/valkey-search-kit).

Use it when you want vector search with structured metadata filtering and a clean, typed API, without hand-writing `FT.CREATE` / `FT.SEARCH` strings.

## Prerequisites

- **Valkey 8.0+** with the `valkey-search` module loaded
- Or **Amazon ElastiCache for Valkey** (8.0+)
- Or **Google Cloud Memorystore for Valkey**
- Node.js >= 20

## Installation

```bash
npm install @betterdb/retrieval iovalkey
```

`iovalkey` is a peer dependency - install it alongside the package. You also provide an embedding function.

## Quick start

```typescript
import Valkey from 'iovalkey';
import { Retriever } from '@betterdb/retrieval';

const client = new Valkey('redis://localhost:6379');

const retriever = new Retriever({
  client,
  name: 'docs',
  schema: {
    fields: {
      category: { type: 'tag' },
      year: { type: 'numeric', sortable: true },
    },
    vector: { algorithm: 'hnsw', metric: 'cosine' },
  },
  embedFn: async (text) => embed(text), // returns number[]
});

// Create the index if it doesn't exist (idempotent; dims resolved from embedFn).
await retriever.createIndex();

await retriever.upsert([
  {
    id: 'doc1',
    text: 'Valkey is a high-performance key-value store',
    fields: { category: 'db', year: 2024 },
  },
]);

const hits = await retriever.query({
  text: 'fast in-memory database',
  k: 5,
  filter: { category: 'db' },
});
```

## Retriever API

| Method | Description |
|--------|-------------|
| `createIndex()` | Create the index if absent (idempotent). Vector dimension is taken from `schema.vector.dims` or resolved by probing `embedFn`. |
| `upsert(entries)` | Embed each entry's `text` and write it as a hash with its `fields`. |
| `delete(ids)` | Delete documents by id. |
| `query(options)` | KNN search. Provide `text` (embedded for you) or a precomputed `vector`, a positive `k`, an optional `filter` (tag/numeric fields), and `hybrid: 'rerank'` to post-process hits through a `rerankFn`. Returns `QueryHit[]`. |
| `describeIndex()` / `health()` | Index stats: doc count, indexing state, dimension, percent indexed, and an optional estimated recall. |
| `dropIndex()` | Drop the index (no-op if it doesn't exist). |
| `register()` / `unregister()` | Publish/remove a discovery marker in the shared `__betterdb:caches` registry, ownership-checked so it never clobbers a foreign cache type. |

> `QueryHit.score` is the raw KNN vector **distance** (lower is closer), not a similarity. Rank ascending.

## Schema

The `schema` declares the metadata fields you filter on plus the vector configuration:

```typescript
schema: {
  fields: {
    category: { type: 'tag' },
    year: { type: 'numeric', sortable: true },
  },
  vector: {
    algorithm: 'hnsw',   // or 'flat'
    metric: 'cosine',    // 'cosine' | 'l2' | 'ip'
    // dims: 1536,       // optional - otherwise resolved by probing embedFn
  },
}
```

`tag` fields support exact-match filtering; `numeric` fields support range filters and (when `sortable`) ordering.

## Filtered and hybrid query

```typescript
// Filter on indexed fields:
await retriever.query({ text: 'database', k: 5, filter: { category: 'db' } });

// Bring your own precomputed vector:
await retriever.query({ vector: myEmbedding, k: 10 });

// Hybrid rerank - retrieve k candidates, reorder with your own function:
await retriever.query({
  text: 'database',
  k: 10,
  hybrid: 'rerank',
  rerankFn: async (query, hits) => hits, // return reordered hits
});
```

## Observability

Pass a `metrics` (`RetrievalMetrics`) and/or `tracer` (`RetrievalTracer`) to instrument every operation. `createPrometheusMetrics()` provides a ready-made Prometheus implementation.

## See also

- [Retrieval (Python)](/docs/packages/retrieval-python) - the Python port with the same surface and on-disk format.
- [Valkey Search Kit](/docs/packages/valkey-search-kit) - the low-level helpers this package is built on.
- [Agent Memory](/docs/packages/agent-memory) - a semantic memory tier that layers recency and importance scoring on top of vector search.
