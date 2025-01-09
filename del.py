import pymongo
import logging
import os
import shutil
import time


client = pymongo.MongoClient("mongodb+srv://.....................................")
db = client['SCENARIO']
scenarios_collection = db['generated_scenario']


logging.basicConfig(level=logging.DEBUG)  


local_directory = 'D:/rvc/audio_files'

def delete_local_directory(dir_name):
    """Удаляет указанную директорию и все ее содержимое локально."""
    try:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)  
            logging.debug(f"Удалена директория локально: {dir_name}")
        else:
            logging.warning(f"Директория не найдена локально: {dir_name}")
    except Exception as e:
        logging.error(f"Ошибка при удалении локальной директории {dir_name}: {e}")

def main():
    try:

        scenarios = scenarios_collection.find({"processed": True, "deleted_audio": {"$ne": True}})
        for scenario in scenarios:
            folder_name = str(scenario['_id'])  
            logging.debug(f"Удаление папки для сценария с ID '{folder_name}'")


            full_local_path = os.path.join(local_directory, folder_name)
            logging.debug(f"Полный путь к директории: {full_local_path}")  


            delete_local_directory(full_local_path)


            scenarios_collection.update_one({"_id": scenario['_id']}, {"$set": {"deleted_audio": True}})
            logging.debug(f"Добавлен флаг DELETED_AUDIO для сценария с ID '{folder_name}'.")

            logging.debug(f"Папка '{folder_name}' успешно удалена локально.")

    except Exception as e:
        logging.error(f"Ошибка: {e}")

if __name__ == "__main__":
    while True:
        main()  
        time.sleep(60)  
