#!/bin/python3
from loggissimo import logger
from loggissimo.constants import Level

# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# )


# logger.level = Level.DEBUG


def main():
    logger.level = Level.INFO
    print(logger)
    print(logger.level)

    logger.info("test")
    logger.debug("test")
    logger.trace("test")
    logger.success("test")
    logger.warning("test")
    logger.error("test")
    logger.critical("test")

    logger.level = Level.DEBUG
    print(logger.level)
    print()

    logger.info("test")
    logger.debug("test")
    logger.trace("test")
    logger.success("test")
    logger.warning("test")
    logger.error("test")
    logger.critical("test")

    logger.level = Level.TRACE
    print(logger.level)
    print()

    logger.info("test")
    logger.debug("test")
    logger.trace("test")
    logger.success("test")
    logger.warning("test")
    logger.error("test")
    logger.critical("test")

    logger.level = Level.ERROR
    print(logger.level)
    print()

    logger.info("test")
    logger.debug("test")
    logger.trace("test")
    logger.success("test")
    logger.warning("test")
    logger.error("test")
    logger.critical("test")


if __name__ == "__main__":
    main()
