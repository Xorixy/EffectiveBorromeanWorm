import time
import h5py as h5


max_tries = 100
success = False

while not success and max_tries > 0:
    try:
        f = h5.File("res.h5", "a")
        if len(f.keys()) == 0:
            f.create_dataset("data", data=1)
        else:
            data = f["data"][()]
            del f["data"]
            f.create_dataset("data", data=(data + 1))
    except:
        time.sleep(4)
