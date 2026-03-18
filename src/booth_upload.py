from supabase import create_client
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from booth_messaging import logger, loglevels
import booth_config as config


def testconnection(host: str, key: str):
    try:
        supabase = create_client(host, key)
        supabase.storage.list_buckets()
        return True
    except:
        return False

def upload(imgPath: Path) -> str:
    logger.post(f"INFO: uploading file {imgPath.name}", loglevels.INFO)
    try:
        with open(imgPath, "rb") as f:
            result = supabase.storage.from_("photobooth").upload(imgPath.name, f)
    except:
        logger.post('ERROR: failed to connect or upload to database', loglevels.ERROR)
    url = f"{os.getenv("DB_HOST")}/storage/v1/object/public/{result.fullPath}"
    logger.post(f'INFO: uploaded image available at {url}', loglevels.INFO)
    return url


if getattr(sys, 'frozen', False):
    envPath = Path(sys.executable).parent / '.env'
else:
    envPath = Path(__file__).parent.resolve() / '.env'

if load_dotenv(envPath):
    DB_HOST = os.getenv("DB_HOST")
    DB_KEY = os.getenv("DB_KEY")
else:
    DB_HOST = 'https://google.com'
    DB_KEY = ' '

# load client if upload is enabled
if config.upload:
    try:
        supabase = create_client(
            DB_HOST,
            DB_KEY
        )

        # test connection
        connected = testconnection(DB_HOST, DB_KEY)

        # log error if upload is configured and cannot connect to db
        if not connected:
            logger.post('ERROR: cannot connect to database, check database config in settings', loglevels.ERROR)
    except:
        connected = False
        logger.post('ERROR: cannot connect to database, check database config in settings', loglevels.ERROR)

else:
    connected = False





