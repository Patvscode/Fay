# Window Capture MCP Server

This Windows-only MCP server captures screenshots by window title or handle. It provides two tools:

- `list_windows`: List top-level windows, optionally filtered by keyword.
- `capture_window`: Capture a window by title keyword or handle, return a PNG, and save it locally.

## Setup

1. Enter this directory: `cd mcp_servers/window_capture`
2. Install dependencies: `pip install -r requirements.txt`

Pillow is required. The server supports Windows only.

Screenshots are saved to `cache_data/window_captures` by default. Set `save_dir` in a tool call to use a different directory.

## Run

```bash
python mcp_servers/window_capture/server.py
```

Alternatively, add the server from Fay's MCP management page:

- transport: `stdio`
- command: `python`
- args: `["mcp_servers/window_capture/server.py"]`
- cwd: The repository root, or leave empty

## Tool parameters

### `list_windows`

- `keyword` (optional): Case-insensitive partial title match.
- `include_hidden` (optional): Include hidden or minimized windows. Defaults to `false`.
- `limit` (optional): Maximum number of results. Defaults to `20`; use `0` for no limit.

### `capture_window`

- `window` (required): A window-title keyword or a decimal/hexadecimal window handle.
- `include_hidden` (optional): Allow hidden or minimized windows. Defaults to `false`.
- `save_dir` (optional): Custom output directory.

The tool returns a JSON text summary containing window details and the saved-file path.
