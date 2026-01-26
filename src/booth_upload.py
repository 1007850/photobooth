from supabase import create_client
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()
print(f"URL: {os.getenv("DB_HOST")}")
print(f"KEY: {os.getenv("DB_KEY")}")
supabase = create_client(
    os.getenv("DB_HOST"),
    os.getenv("DB_KEY")
)


def upload(imgPath: Path) -> str:
    print(f"log: uploading file {imgPath.name}")
    with open(imgPath, "rb") as f:
        result = supabase.storage.from_("photobooth").upload(imgPath.name, f)
    url = f"{os.getenv("DB_HOST")}/storage/v1/object/public/{result.fullPath}"
    print(f"log: uploaded image available at {url}")
    return url

