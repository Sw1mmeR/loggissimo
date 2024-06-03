![Logo](https://github.com/Sw1mmeR/loggissimo/blob/main/assets/logo.png)

# loggissimo

Awesome and simple logger!

## Authors

- [@MikleSedrakyan](https://github.com/Sw1mmeR)
- [@AndreyAfanasiev](https://github.com/AfanasevAndrey)

## Usage/Examples

Use default logger from package.
```python
from loggissimo import logger

logger.level = "TRACE"

logger.info("info")
logger.successs("success")
logger.warning("warning")
logger.error("error")
logger.critical("critical")

logger.debug("debug")
logger.trace("trace")
logger.destructor("destructor")
```

Create instance of logger with own format.
```python
# Default format string - "format", "$name@ $time | $level | $stack: $text"

logger = Logger("my_logger", "$name | $time | $text")
logger.info("my own logger")
```

Get created instance by name.
```
log = Logger("my_logger")
my_log = Logger("my_logger")

log is my_log # True
```

Override default colors and styles.
```python
logger = Logger(
        "my_logger",
        format="<font=cyan>$name | <style=bold bg=1,2,3 font=255,0,0>$time | <font=yellow bg=red>$text",
    )
logger.info("my own logger")
```

Add output streams.
```python
logger.add("my_logger.log")
# or
file = open("my_logger.log", "w+")
logger.add(file)
```

Disable message from module.
```python
# module/__init__.py
logger.disable()

# module/engine.py
def do_somthing():
    logger.info("I'm in module funtcion")

# main.py
do_somthing() # The output is empty

logger.enable("module")
do_somthing()
# @ 2024-05-31 16:23:43 | INFO     | __main__:main:27: I'm in module funtcion
```