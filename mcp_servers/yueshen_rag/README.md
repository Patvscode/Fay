# YueShen RAG MCP Server

This server scans PDF and DOCX files from `新知识库` (or a custom directory), splits them by paragraph and sentence, stores their embeddings in Chroma, and exposes retrieval tools. Embedding settings can be supplied through MCP parameters or environment variables.

## Dependencies

```bash
pip install -r requirements.txt
```

Convert legacy `.doc` files to `.docx` first; the current dependencies support PDF and DOCX files only.

## Optional environment variables

- `YUESHEN_CORPUS_DIR`: Source-document directory; defaults to `新知识库`
- `YUESHEN_PERSIST_DIR`: Chroma persistence directory; defaults to `cache_data/chromadb_yueshen`
- `YUESHEN_EMBED_BASE_URL`: Embedding API base URL; `/embeddings` is appended automatically
- `YUESHEN_EMBED_API_KEY`: Embedding API key
- `YUESHEN_EMBED_MODEL`: Embedding model; defaults to `text-embedding-3-small`
- `YUESHEN_AUTO_INGEST`: Scan and ingest automatically at startup; defaults to `1`, set to `0` to disable
- `YUESHEN_AUTO_INTERVAL`: Automatic scan interval in seconds; defaults to `300`, minimum `30`
- `YUESHEN_AUTO_RESET_ON_START`: Reset and rebuild the index at startup; defaults to `0`

## Run

```bash
cd mcp_servers/yueshen_rag
python server.py
```

## Add the server to Fay

From the MCP management page, add a server with:

- transport: `stdio`
- command: `python` or the path to a virtual-environment Python executable
- args: `["mcp_servers/yueshen_rag/server.py"]`
- cwd: The project root
- env: Optional embedding base URL, API key, and model settings

You can also add the corresponding entry directly to `faymcp/data/mcp_servers.json`, then restart the Fay MCP service.

## Recommended pre-start configuration

- Enable **Pre-start** for `query_yueshen` with parameters such as `{"query": "{{question}}", "top_k": 4}`. Fay replaces `{{question}}` with the user's question.
- To scan for new documents automatically, configure `ingest_yueshen` as a pre-start tool with parameters such as `{"reset": false}` and optional `corpus_dir` or `batch_size` values.

## Tools

- `ingest_yueshen`: Scan and ingest documents. Parameters include `corpus_dir`, `reset`, `chunk_size`, `overlap`, `batch_size`, and `max_files`. Optional embedding parameters override the environment variables.
- `query_yueshen`: Perform vector retrieval. Parameters include `query`, optional `top_k` and `where`, and optional embedding settings matching those used for ingestion.
- `yueshen_stats`: Show vector-store status, including the persistence directory, collection name, and vector count.

## Default paths and chunking

- Corpus directory: `悦肾e家知识库202511/新知识库`
- Persistence directory: `cache_data/chromadb_yueshen`
- Default chunking: Approximately 600 characters with 120 characters of overlap
