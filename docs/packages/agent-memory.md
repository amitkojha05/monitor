---
layout: default
title: Agent Memory
parent: Packages
nav_order: 9
---

# Agent Memory

`@betterdb/agent-memory` is standalone agent memory for [Valkey](https://valkey.io/): the short-term caching tiers from [`@betterdb/agent-cache`](/docs/packages/agent-cache) plus a semantic long-term `MemoryStore` backed by [Valkey Search](https://valkey.io/topics/search/) (`FT.*`).

Where the cache tiers are exact-match and ephemeral, the memory tier is semantic and durable: store memories with `remember()`, retrieve the most relevant ones with `recall()` (semantic similarity blended with recency and importance), and keep stores bounded with TTLs, capacity eviction, and `consolidate()`.

## Prerequisites

- **Valkey 8.0+** with the `valkey-search` module loaded (for the `FT.*` commands)
- Or **Amazon ElastiCache for Valkey** (8.0+)
- Or **Google Cloud Memorystore for Valkey**
- Node.js >= 20
- An embedding function you provide

## Installation

```bash
npm install @betterdb/agent-memory iovalkey
```

`iovalkey` is a peer dependency - install it alongside the package.

## Quick start

The `AgentMemory` facade wires the short-term cache tiers and the long-term memory store together over a single client and name:

```typescript
import Valkey from 'iovalkey';
import { AgentMemory } from '@betterdb/agent-memory';

const client = new Valkey('redis://localhost:6379');

const agent = new AgentMemory({
  client,
  name: 'my_agent',
  embedFn: async (text) => embed(text), // returns number[]
});

// Create the vector index and register discovery markers (idempotent).
await agent.initialize();

// Long-term memory:
await agent.memory.remember('User prefers dark mode', {
  agentId: 'assistant',
  importance: 0.8,
  tags: ['preferences'],
});

const hits = await agent.memory.recall('what theme does the user like?', {
  agentId: 'assistant',
  k: 5,
});

// Short-term cache tiers (from @betterdb/agent-cache):
agent.llm;
agent.tool;
agent.session;

await agent.close();
```

You can also use the `MemoryStore` directly, without the cache tiers:

```typescript
import { MemoryStore } from '@betterdb/agent-memory';

const memory = new MemoryStore({ client, name: 'my_agent', embedFn });
await memory.ensureIndex();
```

## MemoryStore API

| Method | Description |
|--------|-------------|
| `ensureIndex()` | Create the `{name}:mem:idx` vector index if absent (idempotent). Resolves the vector dimension from `embedFn`. |
| `remember(content, options?)` | Embed and store a memory; returns its id. Options: `importance` (0..1), `tags`, `ttl` (seconds), and scope (`threadId`, `agentId`, `namespace`). |
| `recall(query, options?)` | Semantic search scoped by `threadId`/`agentId`/`namespace`/`tags`, ranked by a composite of similarity, recency (half-life decay), and importance. Returns `MemoryHit[]`. Recalled memories are reinforced (last-access + access-count bumped) unless `reinforce: false`. |
| `forget(id)` | Delete a single memory by id. |
| `forgetByScope(scope)` | Delete all memories matching a scope and/or tags. |
| `consolidate(options)` | Summarize a set of memories (via a `summarize` callback) into one new memory and optionally delete the sources. Select candidates by scope, tags, `olderThanSeconds`, or `maxImportance`. |
| `currentConfig()` / `refreshConfig()` | Read the live recall/eviction tunables; with `configRefresh` enabled the store periodically re-reads them from `{name}:__mem_config`. |
| `close()` | Stop the config-refresh timer and tear down discovery heartbeats. |

## Scoring and capacity

Recall ranks by `compositeScore` - a weighted blend of similarity, recency (true half-life decay), and importance. Defaults are tunable via `MemoryStoreOptions` (`weights`, `halfLifeSeconds`, `defaultThreshold`) or live via config refresh. Set `maxItemsPerScope` to cap memories per scope; over-capacity writes evict the lowest-scoring items (importance + recency).

`recall` only returns candidates whose cosine **distance** is within a threshold (default `0.25`, i.e. similarity >= ~0.875) - tuned for real semantic embeddings, where a relevant memory lands well inside it. A weak or non-semantic `embedFn` can push every candidate past the threshold and yield no hits; raise it per call (`recall(query, { threshold })`) or globally (`defaultThreshold`) if that happens.

## Observability

Set `telemetry: { registry }` to register Prometheus metrics (`agent_memory_*`: items, recall total/hits/empty/latency, embedding calls, evictions, consolidations) and OpenTelemetry spans for each operation. With `discovery` enabled (default in the facade), the store publishes a marker to the shared `__betterdb:caches` registry so [BetterDB Monitor](https://betterdb.com) can auto-discover it.

## See also

- [Agent Memory (Python)](/docs/packages/agent-memory-python) - the Python port with the same surface and data format.
- [Agent Cache](/docs/packages/agent-cache) - the short-term llm/tool/session cache tiers bundled into the facade.
- [Retrieval](/docs/packages/retrieval) - a lower-level vector retrieval SDK without the recency/importance scoring.
