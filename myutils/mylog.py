import logging

"""
https://docs.python.org/2/library/logging.html
"""

class mylog:
    Table = {
        "error"    : logging.ERROR,
        "debug"    : logging.DEBUG,
        "info"     : logging.INFO,
        "warning"  : logging.WARNING
    }

    def __init__(self, filename=None, level="debug"):
        LOG_FORMAT = "%(asctime)s [%(levelname)-7s] %(message)s"
        DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

        """
        2018/11/24 22:28:21 [DEBUG  ] This is a debug log.
        2018/11/24 22:28:21 [INFO   ] This is a info log.
        2018/11/24 22:28:21 [WARNING] This is a warning log.
        2018/11/24 22:28:21 [ERROR  ] This is a error log.
        """

        l = self.Table.get(level)

        if filename is None:
            logging.basicConfig(level=l, format=LOG_FORMAT, datefmt=DATE_FORMAT)
        else:
            logging.basicConfig(filename=filename, level=l, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    def d(self, str):
        logging.debug(str)

    def i(self, str):
        logging.info(str)

    def w(self, str):
        logging.warning(str)

    def e(self, str):
        logging.error(str)

if __name__ == '__main__':
    log = mylog(level="debug")
    log.d("This is a debug log.")
    log.i("This is a info log.")
    log.w("This is a warning log.")
    log.e("This is a error log.")