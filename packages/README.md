# Packages

This directory contains the open-source packages that make up the BetterDB ecosystem. All packages are designed to work with Valkey (and Redis) and integrate with [BetterDB Monitor](https://betterdb.com) for observability and self-tuning.

## Caching

| Package | Language | Registry | Description |
|---|---|---|---|
| [`semantic-cache`](./semantic-cache) | TypeScript | [npm: @betterdb/semantic-cache](https://www.npmjs.com/package/@betterdb/semantic-cache) | Semantic cache for LLM applications backed by Valkey vector search. Embeddings-based similarity matching with reranking, LLM-as-judge, embedding caching, cost tracking, and OpenTelemetry/Prometheus instrumentation. |
| [`semantic-cache-py`](./semantic-cache-py) | Python | [PyPI: betterdb-semantic-cache](https://pypi.org/project/betterdb-semantic-cache/) | Python counterpart to `@betterdb/semantic-cache`. Same Valkey data format — a TypeScript app and a Python app can share the same cache index. |
| [`agent-cache`](./agent-cache) | TypeScript | [npm: @betterdb/agent-cache](https://www.npmjs.com/package/@betterdb/agent-cache) | Multi-tier exact-match cache for AI agent workloads. Caches LLM responses, tool results, and session state with per-tool TTL policies and cost tracking. |
| [`agent-cache-py`](./agent-cache-py) | Python | [PyPI: betterdb-agent-cache](https://pypi.org/project/betterdb-agent-cache/) | Python counterpart to `@betterdb/agent-cache`. |

## Retrieval & memory

| Package | Language | Registry | Description |
|---|---|---|---|
| [`valkey-search-kit`](./valkey-search-kit) | TypeScript | [npm: @betterdb/valkey-search-kit](https://www.npmjs.com/package/@betterdb/valkey-search-kit) | Shared low-level helpers for Valkey Search (`FT.*`): vector byte encoding, `FT.SEARCH`/`FT.INFO` reply parsing, TAG filter escaping, and error classification. No runtime dependencies. Foundation for the retrieval and agent-memory packages. |
| [`valkey-search-kit-py`](./valkey-search-kit-py) | Python | [PyPI: betterdb-valkey-search-kit](https://pypi.org/project/betterdb-valkey-search-kit/) | Python counterpart to `@betterdb/valkey-search-kit`. |
| [`retrieval`](./retrieval) | TypeScript | [npm: @betterdb/retrieval](https://www.npmjs.com/package/@betterdb/retrieval) | Developer-facing retrieval SDK over Valkey Search. Typed index schema, idempotent index lifecycle, upsert/delete, and vector + filtered + hybrid query. Built on `@betterdb/valkey-search-kit`. |
| [`retrieval-py`](./retrieval-py) | Python | [PyPI: betterdb-retrieval](https://pypi.org/project/betterdb-retrieval/) | Python counterpart to `@betterdb/retrieval`. Same Valkey data format — a TypeScript app and a Python app can share the same index. |
| [`agent-memory`](./agent-memory) | TypeScript | [npm: @betterdb/agent-memory](https://www.npmjs.com/package/@betterdb/agent-memory) | Long-term semantic memory for AI agents backed by Valkey Search, plus the short-term cache tiers from `@betterdb/agent-cache`. `remember()`/`recall()` with similarity blended with recency and importance, capacity eviction, and consolidation. |
| [`agent-memory-py`](./agent-memory-py) | Python | [PyPI: betterdb-agent-memory](https://pypi.org/project/betterdb-agent-memory/) | Python counterpart to `@betterdb/agent-memory`. |

## Tools

| Package | Language | Registry | Description |
|---|---|---|---|
| [`cli`](./cli) | TypeScript | [npm: @betterdb/monitor](https://www.npmjs.com/package/@betterdb/monitor) | CLI for monitoring and observing Valkey/Redis databases. Connects to BetterDB Monitor for real-time metrics, slowlog analysis, and client inspection. |
| [`mcp`](./mcp) | TypeScript | [npm: @betterdb/mcp](https://www.npmjs.com/package/@betterdb/mcp) | MCP server for Valkey/Redis observability. Integrates with Claude Code and other MCP-compatible AI assistants to query database health, latency, memory, and cache metrics. |
| [`agent`](./agent) | TypeScript | [npm: @betterdb/agent](https://www.npmjs.com/package/@betterdb/agent) | Remote monitoring agent that connects a Valkey/Redis instance to BetterDB Monitor Cloud. Runs as a sidecar or standalone container. |

## Benchmarking

| Package | Language | Registry | Description |
|---|---|---|---|
| [`cache-benchmark`](./cache-benchmark) | Python | — (not published) | Replay harness for benchmarking semantic cache implementations (BetterDB, RedisVL, GPTCache) against labeled query-pair datasets. Supports STSb, SICK, SemBenchmarkLmArena, and PAWS-Wiki. |

## Internal

| Package | Language | Description |
|---|---|---|
| [`shared`](./shared) | TypeScript | Shared types, constants, and utilities used across the API, CLI, MCP server, and cache proposal system. Not intended for direct consumption. |
