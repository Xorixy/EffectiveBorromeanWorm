import time
time.sleep(30)
try:
    f = open("out/myfile1.txt", "x")
except Exception as e:
    f = open("out/myfile2.txt", "w")
