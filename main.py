import logging
import time
from mongo_handler import process_unloaded_scenarios


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    while True:
        process_unloaded_scenarios()
        time.sleep(20) 
