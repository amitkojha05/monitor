# Packages

This directory contains the open-source packages that make up the BetterDB ecosystem. All packages are designed to work with Valkey (and Redis) and integrate with [BetterDB Monitor](https://betterdb.com) for observability and self-tuning.

## Caching

| Package | Language | Registry | Description |
|---|---|---|---|
| [`semantic-cache`](./semantic-cache) | TypeScript | [npm: @betterdb/semantic-cache](https://www.npmjs.com/package/@betterdb/semantic-cache) | Semantic cache for LLM applications backed by Valkey vector search. Embeddings-based similarity matching with reranking, LLM-as-judge, embedding caching, cost tracking, and OpenTelemetry/Prometheus instrumentation. |
| [`semantic-cache-py`](./semantic-cache-py) | Python | [PyPI: betterdb-semantic-cache](https://pypi.org/project/betterdb-semantic-cache/) | Python counterpart to `@betterdb/semantic-cache`. Same Valkey data format — a TypeScript app and a Python app can share the same cache index. |
| [`agent-cache`](./agent-cache) | TypeScript | [npm: @betterdb/agent-cache](https://www.npmjs.com/package/@betterdb/agent-cache) | Multi-tier exact-match cache for AI agent workloads. Caches LLM responses, tool results, and session state with per-tool TTL policies and cost tracking. |
| [`agent-cache-py`](./agent-cache-py) | Python | [PyPI: betterdb-agent-cache](https://pypi.org/project/betterdb-agent-cache/) | Python counterpart to `@betterdb/agent-cache`. |

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
