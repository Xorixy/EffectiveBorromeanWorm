import time
import h5py as h5


max_tries = 100
success = False


while not success and max_tries > 0:
    try:
        print("Trying to open file...")
        f = h5.File("res.h5", "a")
        print("File opened successfully.")
        if len(f.keys()) == 0:
            print("No data found, creating data = 1")
            f.create_dataset("data", data=1)
        else:
            data = f["data"][()]
            del f["data"]
            print("Data found = ", str(data))
            print("Incrementing...")
            f.create_dataset("data", data=(data + 1))
    except:
        print("Failed to open file. Sleeping for 4s...")
        time.sleep(4)
