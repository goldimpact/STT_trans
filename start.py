import time
import threading
import iat_ws_python3
import fanyi
def STT():
    while 1:
        iat_ws_python3.main()
        time.sleep(1)

def TTM():
    while 1:
        fanyi.main()
        time.sleep(1)

threads = []
f0 = open(r'test1.txt', "r+")
f0.truncate()
f0.close()
t1 = threading.Thread(target=STT)
threads.append(t1)
t2 = threading.Thread(target=TTM)
threads.append(t2)
for t in threads:
    t.start()
for t in threads:
    t.join()

