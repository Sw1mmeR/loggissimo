#!/bin/python3
from loggissimo import logger
from loggissimo._logger import Logger
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


#if __name__ == "__main__":
#   main()

import multiprocessing
import time
import random
def test(name):
        log = Logger("test"+name, trace_enabled = True)
        log2 = Logger("test2 - "+name)
        log.trace('test start')
        log2.trace('test start')
        slp = random.randint(1, 10)
        time.sleep(slp)
        log.trace("test stop after "+str(slp))
        log2.info("test2 stop after "+str(slp))
if __name__ == "__main__":
    
    # log = Logger("test1")
    # log2 = Logger("test2", trace_enabled = True)
    # log.info("test")
    # log2.info("test2")
    # log.info("test3")
    # log2.info("test4")
    # log.info("test5")
    # with open(log2._trace_file_path,'r') as f:
    #     print(f.read()
    #     )
    

    processes = [multiprocessing.Process(target=test, args=(str(i),), name = f"Process {i}") for i in range(5)]
    [p.start() for p in processes]
    
    [p.join() for p in processes]
