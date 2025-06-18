import time
time.sleep(10)
try:
    f = open("out/myfile1.txt", "x")
except Exception as e:
    f = open("out/myfile2.txt", "w")
