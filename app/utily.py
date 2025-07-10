import openai
from sqlalchemy.orm import Session
from app.crud import update_translation_task
from dotenv import load_dotenv
from openai.error import OpenAIError, RateLimitError, AuthenticationError


import os
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# MOCK_TRANSLATION = os.getenv("MOCK_TRANSLATION", "false").lower() == "true"

# if not MOCK_TRANSLATION:
#     import openai
#     openai.api_key = OPENAI_API_KEY

def perform_translation(task_id:int, text: str, languages:list, db:Session):
    translations = {}
    for lang in languages:
        try:
            # if MOCK_TRANSLATION:
            #     # Simulated translation for development
            #     translations[lang] = f"{text} (translated to {lang})"
            # else:
            response=openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that translates text in into {lang}."},
                {"role": "user", "content": text}
            ],
            max_tokens=1000
        )
            translated_text = response['choices'][0]['message']['content'].strip()
            translations[lang] = translated_text
        except RateLimitError as e:
            print(f"[Rate Limit Error] {lang}: {e}")
            translations[lang] = f"[Rate Limit Error] {e}"

        except AuthenticationError as e:
            print(f"[Auth Error] {lang}: {e}")
            translations[lang] = f"[Authentication Error] {e}"

        except OpenAIError as e:
            print(f"[OpenAI Error] {lang}: {e}")
            translations[lang] = f"[OpenAI Error] {e}"

        except Exception as e:
            print(f"[Unexpected Error] {lang}: {e}")
            translations[lang] = f"[Unexpected Error] {e}"

    update_translation_task(db,task_id,translations)
