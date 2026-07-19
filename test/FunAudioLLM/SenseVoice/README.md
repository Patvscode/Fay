# SenseVoice setup

## Install

```bash
pip install -r requirements.txt
```

## Start the server

```bash
python -u server.py --host "0.0.0.0" --port 10197 --ngpu 0
```

## Connect Fay

Set the relevant option in `fay/system.conf` to `funasr`, then restart Fay.

## Acknowledgements

Thanks to:

1. [FunAudioLLM/SenseVoice](https://github.com/FunAudioLLM/SenseVoice)
2. [ModelScope](https://github.com/modelscope/modelscope)
3. [FunASR](https://github.com/alibaba-damo-academy/FunASR)
4. [Fay Digital Human Assistant](https://github.com/TheRamU/Fay)
