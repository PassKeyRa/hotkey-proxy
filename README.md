# Hotkey proxy

This is a simple script to intercept a hotkey during the specified program execution.

The script uses [python-xlib](https://pypi.org/project/python-xlib/) X library to listen for KeyPress events in specified program. Now it's possible to run any program and specify our shell command to be executed on the hotkey pressed.

## Usage

```
usage: hotkey-proxy.py [-h] --key KEY [--modifier MODIFIER] --cmd CMD program

positional arguments:
  program               Program to run

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -k KEY     Key to capture (examples: S, M, etc.)
  --modifier MODIFIER, -m MODIFIER
                        Modifier to capture (examples: shift, ctrl, alt, any, none)
  --cmd CMD, -c CMD     Shell command to run on captured key
```

* `key` argument specifies the keyboard button to be pressed
* `modifier` sets the modifier for `key` that could be one of the following: `shift, ctrl, alt, any, none`. `any` modifier will trigger when `key` is pressed with any of `shift, ctrl, alt` or none of them (just `key`). `none` will trigger only when `key` is pressed without modifiers
* `cmd` specifies the shell string to be executed

## Example

There is an example `./example.sh` that runs `obsidian` program and sets the execution of `echo lol >> /tmp/log.txt` shell string after pressing the hotkey `Ctrl+S` each time.
