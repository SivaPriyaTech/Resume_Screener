import os
from openai import OpenAI
# from dotenv import load_dotenv

from src.config_loader import load_config

def main():

    try:

        # Load config
        config = load_config(config_path="config/config.yaml")

        # Load environment variables
        #load_env() - when we use this fn, it will check is there env in project folder, is yes, use that key else it will system envrt variables
        api_key = os.getenv(config['llm']['api_key'])

        client = OpenAI(api_key=api_key)

        config['client'] = client

        # Import processor  and load config

        from src.processor import processor

        # Start piple line
        processor(config=config)

    except Exception as e:
        print(f"Pipe line failed, {e}")

if __name__ == '__main__':
    main()

