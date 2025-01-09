import os
import logging
import time
import shutil  
from gradio_client import Client
import pymongo  


tts_client = Client("http://127.0.0.1:7860/")


character_voice_configs = {
    'PEPE': {
        'model': 'DaleGribbleKOTH',
        'params': {
            'speech_speed': 0, 
            'tts_voice': "en-US-BrianNeural-Male",
            'transpose': 8,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
    },
    'ANDY': {
        'model': 'ShaggyRogers',
        'params': {
            'speech_speed': 0,
            'tts_voice': "en-US-GuyNeural-Male",
            'transpose': 10,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
    },
    'BRETT': {
        'model': 'IagoKH',
        'params': {
            'speech_speed': 0,
            'tts_voice': "en-US-GuyNeural-Male",
            'transpose': 10,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
    },
    'LANDWOLF': {
        'model': 'VenomMovieV8',
        'params': {
            'speech_speed': 0,
            'tts_voice': "en-US-GuyNeural-Male",
            'transpose': 1,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
    },
    'BIRDDOG': {
        'model': 'Courage The Cowardly Dog - Weights.gg Model',
        'params': {
            'speech_speed': 0,
            'tts_voice': "en-US-AnaNeural-Female",
            'transpose': 6,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
    },
    'CHILLGUY': {
        'model': 'Brian_Griffin',
        'params': {
            'speech_speed': 0,
            'tts_voice': "en-US-GuyNeural-Male",
            'transpose': 4,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
   },
    'PUPPET': {
        'model': 'Cookie_Monster_v2',
        'params': {
            'speech_speed': 0,
            'tts_voice': "en-US-GuyNeural-Male",
            'transpose': 4,
            'pitch_extraction_method': "rmvpe",
            'index_rate': 1,
            'protect': 0.33,
        }
    }
}


client = pymongo.MongoClient("mongodb+srv://...................")
db = client['SCENARIO']
scenarios_collection = db['generated_scenario']

def generate_audio(character, line_text, scenario_id):
    """Generate audio for a given character and dialogue line using RVC TTS."""
    config = character_voice_configs.get(character)
    if not config:
        logging.error(f"Конфигурация для персонажа {character} не найдена.")
        return None

    model = config['model']
    params = config['params']

    audio_dir = f"audio_files/{scenario_id}"
    os.makedirs(audio_dir, exist_ok=True)
    audio_file_path = os.path.join(audio_dir, f"{character}_{int(time.time())}.wav")


    speech_speed = params['speech_speed']
    tts_voice = params['tts_voice']
    transpose = params['transpose']
    pitch_extraction_method = params['pitch_extraction_method']
    index_rate = params['index_rate']
    protect = params['protect']


    try:
        logging.debug(f"Генерация аудио для {character} с параметрами: {line_text}, {speech_speed}, {tts_voice}, {transpose}, {pitch_extraction_method}, {index_rate}, {protect}")


        result = tts_client.predict(
            model,
            speech_speed,
            line_text,
            tts_voice,
            transpose,
            pitch_extraction_method,
            index_rate,
            protect,
            fn_index=0
        )

        logging.debug(f"Результат API для {character}: {result}")

        if isinstance(result, tuple) and len(result) >= 3:

            audio_file_path_mp3 = result[1]  
            audio_file_path_wav = result[2]   
            

            shutil.move(audio_file_path_wav, audio_file_path)  

            logging.info(f"Успешно создано аудио для {character}: '{line_text}'")
            update_audio_path_in_mongo(scenario_id, character, line_text, audio_file_path)  
            return audio_file_path
        else:
            raise ValueError("Формат ответа API неожиданный.")

    except Exception as e:
        logging.error(f"Ошибка при генерации аудио для '{character}': {e}")
        return None

def update_audio_path_in_mongo(scenario_id, character, line_text, audio_path):

    scenarios_collection.update_one(
        {
            "_id": scenario_id,
            "scenario.character": character,
            "scenario.line": line_text
        },
        {
            "$set": {
                f"scenario.$.audio_path": audio_path  
            }
        }
    )
    logging.debug(f"Обновлён путь к аудио для {character} в MongoDB: {audio_path}")
