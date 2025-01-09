import pymongo
import logging
import time


logging.basicConfig(level=logging.INFO)


client = pymongo.MongoClient("mongodb+srv://...............................")
db = client['SCENARIO']
scenarios_collection = db['generated_scenario']

def process_scenario(scenario):
    """Функция обработки сценария с генерацией аудио построчно."""
    from generate_audio import generate_audio  

    logging.info(f"Обработка сценария с ID: {scenario['_id']}")
    scenario_data = scenario.get("scenario", [])

 
    if not scenario_data:
        logging.warning(f"Сценарий с ID {scenario['_id']} пуст. Помечаем как 'failed'.")
        scenarios_collection.update_one(
            {"_id": scenario["_id"]},
            {"$set": {"unload": "failed"}}
        )
        return  

    updated_scenario_data = []

    try:
        for line in scenario_data:
            character = line.get("character")
            dialogue = line.get("line")
            audio_path = generate_audio(character, dialogue, scenario["_id"])

            if audio_path:
                updated_scenario_data.append({
                    "character": character,
                    "line": dialogue,
                    "audio_path": audio_path
                })
            else:
                logging.warning(f"Не удалось создать аудио для строки: {character}: {dialogue}")


        if updated_scenario_data:
            scenarios_collection.update_one(
                {"_id": scenario["_id"]},
                {"$set": {"scenario": updated_scenario_data, "unload": True}}
            )
            logging.info(f"Сценарий с ID {scenario['_id']} обновлен с аудио путями.")
        else:
            logging.warning(f"Не удалось создать аудио для всех строк сценария с ID {scenario['_id']}. Помечаем как 'failed'.")
            scenarios_collection.update_one(
                {"_id": scenario["_id"]},
                {"$set": {"unload": "failed"}}
            )

    except Exception as e:
        logging.error(f"Ошибка при обработке сценария с ID {scenario['_id']}: {e}")
        scenarios_collection.update_one(
            {"_id": scenario["_id"]},
            {"$set": {"unload": "failed"}}
        )

def process_unloaded_scenarios():

    try:
        scenarios_cursor = scenarios_collection.find({"unload": False})
        scenarios_count = scenarios_collection.count_documents({"unload": False})
        logging.info(f"Найдено {scenarios_count} сценариев с unload: False.")

        for scenario in scenarios_cursor:
            logging.debug(f"Обрабатываем сценарий: {scenario}")
            process_scenario(scenario)

        logging.info("Все сценарии с unload: False успешно обработаны.")
    except Exception as e:
        logging.error(f"Ошибка при извлечении и обработке сценариев: {e}")

if __name__ == "__main__":

    process_unloaded_scenarios()
