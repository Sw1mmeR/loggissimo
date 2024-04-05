#!/bin/python3
from loggissimo import logger
from loggissimo.constants import Level

# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# )


# logger.level = Level.DEBUG


def main():
    logger.level = "INFO"
    print(logger)
    print(logger.level)

    logger.info("INFO")
    logger.debug("INFO")
    logger.trace("INFO")
    logger.success("INFO")
    logger.warning("INFO")
    logger.error("INFO")
    logger.critical("INFO")

    logger.level = "DEBUG"
    print(logger.level)
    print()

    logger.info("DEBUG")
    logger.debug("DEBUG")
    logger.trace("DEBUG")
    logger.success("DEBUG")
    logger.warning("DEBUG")
    logger.error("DEBUG")
    logger.critical("DEBUG")

    logger.disable()
    logger.level = Level.TRACE
    print(logger.level)
    print()

    logger.info("TRACE")
    logger.debug("TRACE")
    logger.trace("TRACE")
    logger.success("TRACE")
    logger.warning("TRACE")
    logger.error("TRACE")
    logger.critical("TRACE")

    logger.level = Level.ERROR
    print(logger.level)
    print()
    logger.enable()

    logger.info("ERROR")
    logger.debug("ERROR")
    logger.trace("ERROR")
    logger.success("ERROR")
    logger.warning("ERROR")
    logger.error("ERROR")
    logger.critical("ERROR")


if __name__ == "__main__":
    main()
