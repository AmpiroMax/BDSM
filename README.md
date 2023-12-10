# MIShA

Multimodal chat bot

Pet-project of Patratskiy Maxim and Evgrafov Michail. All code, however, was written by Maxim Patratskiy.

The name BDSM comes from Broker Docker SQL and ML. Nothing really controversial.

## Linux

To run project on Linux one should take next steps:

1. install docker
2. request sequre.py from authors and place it in /bdsm_project/api_managers
3. run run_linux.sh
4. add <https://vk.com/public219590693> to you VK Chat
5. Write "/t2i [prompt]" to generate image via Bot
6. enjoy

Authors of MIShA work on win11 and have not tested pipeline on Linux. However, it should work preatty fine.

## Windows

To run project on Windows one should take next steps:

1. install docker
2. request sequre.py from authors and place it in /bdsm_project/api_managers
3. run run_win.sh
4. add <https://vk.com/public219590693> to you VK Chat
5. Write "/t2i [prompt]" to generate image via Bot
6. enjoy

## Statistics

We've used Kandinsky 2.1
GPU: NVIDIA RTX 2070m 8Gb VRAM
CPU: i7-10750H
RAM: 16Gb

Approximate time of:

- model download 20 min
- model load on GPU 2 min 47 s
- image generation 1-2 s
- request time to message in VK ~2-3 s

## Note

Do not run at 00:00 - 02:00 Moscow time. Vk is reloading it's servers and vk_api can broke. Must be reevoke manually.

## Links

- [Idea](https://docs.google.com/document/d/1sunezogn2XQRF8IXuGWlRd4VWdmb0EyL9DSEKVfTEuw/edit#heading=h.gjdgxs)
- [Meetings logs](https://docs.google.com/document/d/1cduKaf6tQiI3LKFeZ9xUvUelG3aqCJjW1Tpw0QZaCng/edit)
