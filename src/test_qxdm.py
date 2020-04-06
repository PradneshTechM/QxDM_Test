import time
import sys

from qxdm import QXDM

qxdm = QXDM()
qxdm.launch()
time.sleep(5)
qxdm.connect(int(sys.argv[1]))
time.sleep(5)
qxdm.quit()
