# Fay Course Knowledge Base

This directory contains Fay course knowledge packages in `.zip` format. The Course Knowledge Base MCP server in `mcp_servers/fay_player_knowledge/` loads these packages so Fay can search and cite them during conversations.

## Creating course packages

Use [Fay Player](https://player.fay-agent.com) to create or browse course packages. It supports:

- Browsing and creating course knowledge packages
- Playing course content online
- Exporting a course as an explanatory video
- Exporting course content as a Markdown document

Fay Player is fully open source at [gitee.com/xszyou/fay-player](https://gitee.com/xszyou/fay-player).

Place downloaded `.zip` packages in this directory to make them available to Fay.

## Included courses

| Course package | Description |
| --- | --- |
| `Fay介绍（面向开发者）.zip` | Overview of the Fay digital-human architecture and a developer getting-started guide |
| `Fay多用户对话消息分发逻辑.zip` | Message routing and session isolation in multi-user scenarios |
| `Fay的think标签处理逻辑.zip` | The complete lifecycle of `<think>` tags, from generation through memory archiving |
| `Fay的prestart标签处理逻辑.zip` | Registration, scheduling, and dual-channel injection of `<prestart>` tags |
| `OfficeEcho-course.zip` | Example OfficeEcho course |

## Usage

1. Create or download a package from [Fay Player](https://player.fay-agent.com).
2. Put the `.zip` file in this directory.
3. Start Fay. The Course Knowledge Base MCP server loads the package and exposes the `search` and `get_section` tools.
4. Ask Fay to retrieve the course knowledge during a conversation.
