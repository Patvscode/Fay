# FunASR setup

1. Install FFmpeg.

2. Install the required Python packages:

```bash
pip install torch modelscope testresources websockets torchaudio FunASR
```

3. Start the ASR service:

```bash
python -u ASR_server.py --host "0.0.0.0" --port 10197 --ngpu 0
```

4. Update the relevant settings in `fay/system.conf`, then restart Fay.

Video guide: <https://www.bilibili.com/video/BV1qs4y1g74e/?share_source=copy_web&vd_source=64cd9062f5046acba398177b62bea9ad>

## Acknowledgements

Thanks to:

1. Zhang Congcong, algorithm engineer at Zhongke Brain
2. [cgisky1980](https://github.com/cgisky1980/FunASR)
3. [ModelScope](https://github.com/modelscope/modelscope)
4. [FunASR](https://github.com/alibaba-damo-academy/FunASR)
5. [Fay Digital Human Assistant](https://github.com/TheRamU/Fay)
