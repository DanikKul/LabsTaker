import os

import dotenv


def get_config():
    dotenv.load_dotenv()
    return {
        'db_name': os.getenv('BOT_LOCAL_DB_NAME') if os.getenv('BOT_ENV') == 'local' else os.getenv('BOT_DOCKER_DB_NAME'),
        'token': os.getenv('BOT_TOKEN'),
        'db_admin': os.getenv('BOT_DB_ADMIN'),
        'db_tables': os.getenv('BOT_DB_TABLES'),
        'group': os.getenv('BOT_GROUP'),
        'pass': os.getenv('BOT_PASS')
    }
