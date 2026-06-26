---
layout: default
title: Valkey Search Kit
parent: Packages
nav_order: 5
---

# Valkey Search Kit

`@betterdb/valkey-search-kit` is a set of shared, low-level helpers for working with [Valkey Search](https://valkey.io/topics/search/) (`FT.*` commands): vector byte encoding, `FT.SEARCH` reply parsing, version-skew-tolerant `FT.INFO` parsing, TAG filter escaping, and error classification.

It has no runtime dependencies and exposes only pure functions, so it stays trivial to vendor and test. It is consumed by [`@betterdb/semantic-cache`](/docs/packages/semantic-cache), [`@betterdb/retrieval`](/docs/packages/retrieval), and [`@betterdb/agent-memory`](/docs/packages/agent-memory), and is the foundation you reach for when building directly against `FT.*`.

## Prerequisites

- **Valkey 8.0+** with the `valkey-search` module loaded (for the `FT.*` commands these helpers target)
- Node.js >= 20

## Installation

```bash
npm install @betterdb/valkey-search-kit
```

## Exports

| Export | Signature | Description |
|--------|-----------|-------------|
| `encodeFloat32` | `(vec: number[]) => Buffer` | Encode an embedding as a little-endian Float32 `Buffer` for binary `HSET` field values and KNN `PARAMS`. |
| `escapeTag` | `(value: string) => string` | Escape a string for safe use as a Valkey Search TAG filter value, including spaces (which would otherwise split into OR terms). |
| `parseFtSearchResponse` | `(raw: unknown) => FtSearchHit[]` | Parse a raw `FT.SEARCH` reply into hits; never throws, returns `[]` on empty or malformed input. |
| `FtSearchHit` | `{ key: string; fields: Record<string, string> }` | A single parsed search hit. |
| `parseDimensionFromInfo` | `(info: unknown) => number` | Extract the vector field dimension from an `FT.INFO` reply, handling both flat `DIM` pairs and the Valkey Search 1.2 nested `index`/`dimensions` shape. |
| `parseFtInfoStats` | `(info: unknown) => FtIndexStats` | Extract `num_docs` and indexing state from an `FT.INFO` reply. |
| `isIndexNotFoundError` | `(err: unknown) => boolean` | Classify an error as a Valkey Search "index does not exist" error across Valkey Search / RediSearch message variants. |

## Usage

### Vector encoding

```typescript
import { encodeFloat32 } from '@betterdb/valkey-search-kit';

const blob = encodeFloat32([0.1, 0.2, 0.3]); // little-endian Float32 Buffer
await client.hset('doc:1', 'embedding', blob);
```

Use `encodeFloat32` to store embeddings as binary `HSET` field values and as the `PARAMS` vector for a KNN `FT.SEARCH`.

### TAG escaping

```typescript
import { escapeTag } from '@betterdb/valkey-search-kit';

const query = `@model:{${escapeTag('gpt-4o')}}`; // -> "@model:{gpt\\-4o}"
```

Escapes every character with special meaning in the TAG filter syntax, including spaces (unescaped spaces are treated as OR term separators).

### FT.SEARCH reply parsing

```typescript
import { parseFtSearchResponse } from '@betterdb/valkey-search-kit';

const raw = await client.call('FT.SEARCH', index, query /* ... */);
const hits = parseFtSearchResponse(raw);
// [{ key: 'cache:entry:abc', fields: { prompt: '...', __score: '0.05' } }]
```

Handles mixed `Buffer`/`string` replies, `RETURN 0` mode (keys with no field list), and odd-length field lists. Binary field values that are not valid UTF-8 (e.g. raw embedding bytes) are skipped. Never throws.

### FT.INFO parsing (version-skew tolerant)

```typescript
import { parseDimensionFromInfo, parseFtInfoStats } from '@betterdb/valkey-search-kit';

const info = await client.call('FT.INFO', index);
const dims = parseDimensionFromInfo(info);  // 1536, or 0 if no vector field
const stats = parseFtInfoStats(info);       // { num_docs, indexing_state }
```

`parseDimensionFromInfo` understands both the flat `DIM` attribute pair and the nested `index`/`dimensions` shape introduced in Valkey Search 1.2.

### Error classification

```typescript
import { isIndexNotFoundError } from '@betterdb/valkey-search-kit';

try {
  await client.call('FT.INFO', index);
} catch (err) {
  if (isIndexNotFoundError(err)) {
    // index does not exist yet
  } else {
    throw err;
  }
}
```

Matches the "index does not exist" message variants emitted across Valkey Search / RediSearch versions, case-insensitively.

## See also

- [Valkey Search Kit (Python)](/docs/packages/valkey-search-kit-python) - the Python port with the same surface.
- [Retrieval](/docs/packages/retrieval) and [Agent Memory](/docs/packages/agent-memory) - higher-level SDKs built on this kit.
