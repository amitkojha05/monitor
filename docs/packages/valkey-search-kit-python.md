---
layout: default
title: Valkey Search Kit (Python)
parent: Packages
nav_order: 6
---

# Valkey Search Kit (Python)

`betterdb-valkey-search-kit` is the Python counterpart to [`@betterdb/valkey-search-kit`](/docs/packages/valkey-search-kit): shared low-level helpers for working with [Valkey Search](https://valkey.io/topics/search/) (`FT.*`) from Python.

It has no runtime dependencies and exposes only pure functions, so it stays trivial to vendor and test. It is the shared foundation the [`betterdb-retrieval`](/docs/packages/retrieval-python) and [`betterdb-agent-memory`](/docs/packages/agent-memory-python) packages build on.

## Prerequisites

- **Valkey 8.0+** with the `valkey-search` module loaded (for the `FT.*` commands these helpers target)
- Python >= 3.11

## Installation

```bash
pip install betterdb-valkey-search-kit
```

## Usage

### Vector encoding

```python
from betterdb_valkey_search_kit import encode_float32, decode_float32

blob = encode_float32([0.1, 0.2, 0.3])   # little-endian Float32 bytes
vec = decode_float32(blob)               # back to list[float]
```

Use `encode_float32` to store embeddings as binary `HSET` field values and as the `PARAMS` vector for a KNN `FT.SEARCH`.

### TAG escaping

```python
from betterdb_valkey_search_kit import escape_tag

f"@model:{{{escape_tag('gpt-4o')}}}"   # -> "@model:{gpt\\-4o}"
```

Escapes every character with special meaning in the TAG filter syntax, including spaces (unescaped spaces are treated as OR term separators).

### FT.SEARCH reply parsing

```python
from betterdb_valkey_search_kit import parse_ft_search_response

raw = await client.execute_command("FT.SEARCH", index, query)
hits = parse_ft_search_response(raw)
# [{"key": "cache:entry:abc", "fields": {"prompt": "...", "__score": "0.05"}}]
```

Handles valkey-py's mixed `bytes`/`str` replies, `RETURN 0` mode (keys with no field list), and odd-length field lists. Binary field values that are not valid UTF-8 (e.g. raw embedding bytes) are skipped. Never raises - returns `[]` on any malformed input.

### FT.INFO parsing (version-skew tolerant)

```python
from betterdb_valkey_search_kit import (
    parse_dimension_from_info,
    parse_ft_info_stats,
)

info = await client.execute_command("FT.INFO", index)
dims = parse_dimension_from_info(info)        # 1536, or 0 if no vector field
stats = parse_ft_info_stats(info)             # FtIndexStats(num_docs=..., indexing_state=...)
```

`parse_dimension_from_info` understands both the flat `DIM` attribute pair and the nested `index`/`dimensions` shape introduced in Valkey Search 1.2.

### Error classification

```python
from betterdb_valkey_search_kit import is_index_not_found_error

try:
    await client.execute_command("FT.INFO", index)
except Exception as err:
    if is_index_not_found_error(err):
        ...  # index does not exist yet
    else:
        raise
```

Matches the "index does not exist" message variants emitted across Valkey Search / RediSearch versions, case-insensitively.

## Interoperability with the TypeScript package

The Python and TypeScript kits implement the same byte encodings and the same reply-parsing rules. An embedding encoded by `encode_float32` is byte-identical to one from `encodeFloat32`, so a Python writer and a TypeScript reader (or vice versa) can share the same Valkey Search index.

## See also

- [Valkey Search Kit](/docs/packages/valkey-search-kit) - the TypeScript original.
- [Retrieval (Python)](/docs/packages/retrieval-python) and [Agent Memory (Python)](/docs/packages/agent-memory-python) - higher-level SDKs built on this kit.
