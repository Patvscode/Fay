<div align="center">
    <br>
    <img src="readme/icon.png" alt="Fay">
    <h1>FAY</h1>
    <h3>Fay Digital Human Framework</h3>
</div>

> **Important:** Fay's three editions have been merged into a single version so the project can provide a more stable and complete feature set.

Fay explores practical, device-oriented digital-human applications and makes those ideas available as a complete open-source implementation. The framework can work with a variety of digital-human rendering technologies and large language models, makes components such as TTS and ASR easy to replace, and exposes a comprehensive set of APIs for microcontrollers, apps, websites, and other products.

- [Changelog](https://qqk9ntwbcit.feishu.cn/wiki/UlbZwfAXgiKSquk52AkcibhHngg)
- [Documentation](https://qqk9ntwbcit.feishu.cn/wiki/JzMJw7AghiO8eHktMwlcxznenIg)

## Features

- Completely open source and available for commercial use without liability
- Fully offline operation
- End-to-end streaming support
- Mix and match digital-human models, OpenAI-compatible LLMs, ASR engines, and TTS engines
- Automatic digital-human presentation modes for virtual teachers, virtual hosts, and news broadcasts
- Integration with microcontrollers, apps, websites, large displays, and third-party business systems
- Concurrent multi-user and multi-channel operation
- APIs for text interaction, voice interaction, digital-human control, administration, automatic announcements, and intent handling
- Configurable voice-command actions through `qa.csv`
- Custom knowledge bases, question-and-answer pairs, and character profiles
- Wake-word support and interruptible conversations
- Server and standalone modes
- Robot facial-expression output
- Agent-driven tool selection and execution
- Proactive, schedule-based conversations
- Silent background startup
- Support for reasoning models such as DeepSeek
- Improved self-awareness and biomimetic memory
- MCP tool management over SSE and stdio
- A central configuration-management interface
- End-to-end interoperability across the interaction pipeline

## Framework preview

![](readme/chat.png)

![](readme/controller.png)

![](readme/mcp.png)

## Run from source

### Requirements

- Python 3.12
- Windows, macOS, or Ubuntu
- On Ubuntu, install GCC and PortAudio first:

```bash
sudo apt update
sudo apt install build-essential
sudo apt install portaudio19-dev
```

### Install dependencies

```shell
pip install -r requirements.txt
```

### Quick start

Run locally:

```shell
python main.py start -config_center d19f7b0a-2b8a-4503-8c0d-1a587b90eb69  # Uses slow public resources; replace this with your own key.
```

Prebuilt image:

```text
https://www.compshare.cn/images/compshareImage-1cft3sk9gvta?ytag=GPU_fay
```

### Personal configuration

Rename `system.conf.bak` in the repository root to `system.conf`, then edit its settings.

### Administration page

Open <http://127.0.0.1:5000> in a browser.

## Advanced usage

![](readme/interface.png)

### Use a digital-human renderer (optional)

<https://qqk9ntwbcit.feishu.cn/wiki/GHevwqxwfiX4hCk8yJCcoJ54nqg>

### Integrate Fay into your own product (optional)

<https://qqk9ntwbcit.feishu.cn/wiki/Mcw3wbA3RiNZzwkexz6cnKCsnhh>

## Contact

For the community group, learning materials, and tutorials, follow the **Fay Digital Human** public account. Please star this repository first.

Business contact: QQ 467665317

## Acknowledgements

Fay thanks the following open-source projects for their technical support and inspiration:

- [openclaw](https://github.com/openclaw/openclaw) — reference for memory mechanisms and skill design
- [OpenAI Codex](https://github.com/openai/codex) — reference for reliable tool calling
- [FunASR](https://github.com/modelscope/FunASR) — speech-recognition (ASR) capabilities
