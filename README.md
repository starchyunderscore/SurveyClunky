# SurveyClunky

## What is it?
A survey platform that doesn't use any client side scripting

## Why?
I wanted a survey site for tor, and since it's best practice to disable javascript and wasm, I couldn't use those.

## How to deploy?
1. Download the source code from the latest release
2. Extract the file
3. Change the `HostName` & mentions of `SITE` in `index.py`
4. Edit index.html to be your own kind of thing
5. Run `index.py` with `python3`