#!/bin/python3

import os
import sys
from _logger import Logger

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

# from loggissimo import logger

logger = Logger()


class Device:
    def __init__(self) -> None:
        self.logger = Logger(self.__class__.__name__)
        self.logger.info(f"init {self.__class__.__name__}")

    def send(self, cmd: str):
        self.logger.debug(f"Send {cmd}")
        return "response"


def test_func():
    logger.info("test")


class AccessPoint(Device):
    def __init__(self) -> None:
        super().__init__()

    # def send(self, cmd: str):
    #     time.sleep(5)
    #     resp = super().send(cmd)
    #     self.logger.trace(
    #         (
    #             "Response is: '"
    #             """
    #             'enp2s0.1592: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
    #             inet 172.15.92.100  netmask 255.255.255.0  broadcast 172.15.92.255
    #             inet6 fe80::1ac0:4dff:fec8:a75  prefixlen 64  scopeid 0x20<link>
    #             ether 18:c0:4d:c8:0a:75  txqueuelen 1000  (Ethernet)
    #             RX packets 0  bytes 0 (0.0 B)
    #             RX errors 0  dropped 0  overruns 0  frame 0
    #             TX packets 60404  bytes 8443805 (8.4 MB)
    #             TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0'
    #             """
    #         )
    #     )
    #     return resp


class Raspberry(Device):
    def __init__(self) -> None:
        super().__init__()

    # def send(self, cmd: str):
    #     time.sleep(1)
    #     resp = super().send(cmd)
    #     self.logger.trace(
    #         (
    #             "Response is '"
    #             """
    #             enp2s0.1001@enp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    #                 link/ether 18:c0:4d:c8:0a:75 brd ff:ff:ff:ff:ff:ff
    #                 inet 10.24.80.58/24 brd 10.24.80.255 scope global dynamic noprefixroute enp2s0.1001
    #                     valid_lft 20924sec preferred_lft 20924sec
    #                 inet6 fe80::1ac0:4dff:fec8:a75/64 scope link
    #                     valid_lft forever preferred_lft forever'
    #             """
    #         )
    #     )
    #     return resp


def main():
    test_func()
    logger.info("test2")
    # logger.debug("test")
    # logger.trace("test")
    # logger.success("test")
    # logger.error("test")
    # logger.critical("test")

    # logger.info("test")

    # logger.add("logger.log")

    # logger.info("!!!")

    # logger.clear()

    # logger.remove(1)

    # logger.info("testest")

    # logger.add(sys.stdout)

    # logger.debug("traces :)")
    # log = Logger("file_l", "test.log")
    # log.info("Hello")
    # log.add(sys.stdout)

    # log.info("Not hello")
    # logger.info("test")
    # processes: List[Process] = list()

    # ap = AccessPoint()
    # rpi = Raspberry()

    # processes.append(Process(target=ap.send, args=("ifconfig",)))
    # processes.append(Process(target=rpi.send, args=("ip a",)))

    # [proc.start() for proc in processes]
    # [proc.join() for proc in processes]

    # for inst in Logger._instances.keys():
    #     print(inst)

    # logger.remove("AccessPoint")

    # logger.info()

    # for inst in _Logger._instances.keys():
    #     print(inst)
    # logger = Logger()
    # logger.info("Hello World!")

    # logger2 = Logger()
    # logger2.info("Hello World!")

    # logger3 = Logger("WEP-30L")
    # logger3.info("Hello World!")

    # logger4 = Logger("WEP-30L")
    # logger4.info("Hello World!")

    # logger5 = Logger("WEP-30L")
    # logger5.info("Hello World!")


if __name__ == "__main__":
    main()
