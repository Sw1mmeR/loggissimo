#!/bin/python3
from multiprocessing import Process
from loggissimo import logger, Logger
from loggissimo.constants import Level

# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# )


# logger.level = Level.DEBUG


def logs():
    logger.info("1")
    logger.debug("2")
    logger.critical("3")


def main():
    Logger.addall("test.log")
    logger.level = "DEBUG"
    proc = Process(target=logs, name="Access Point 212")
    proc.start()
    proc.join()
    logger.info("test1")
    logger.destructor("test")
    # log1 = Logger("my_logger")

    # log2 = Logger("my_logger2")

    # # logger.add("my_test.log")
    # log1.info("test")
    # logger.debug("test2")
    # log2.critical("Test")

    # for st in logger._streams.values():
    #     print(st.closed)

    # del log1

    # log1 = Logger("my_logger")
    # print()
    # print(Logger._aggregated_streams["test.log"].closed)
    # for st in logger._streams.values():
    #     print(st.closed)

    # log1.info("end")
    # log1.info("end")
    # log1.info("end")
    # log1.info("end")

    # del log1

    # log1 = Logger("test1")
    # log1.info("!!!!!!!!!!!")


if __name__ == "__main__":
    main()
