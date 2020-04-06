import time
import sys

from qcat_lib import QCAT

qcat = QCAT()
qcat.launch()
time.sleep(5)
qcat.quit()
