import requests
import os

ELN_API_URL = os.getenv("ELN_API_URL", "https://eln.example/api/experiments")
ELN_API_TOKEN = os.getenv("ELN_API_TOKEN", "")

def create_eln_entry(metadata: dict) -> str:
    headers = {
        "Authorization": f"Bearer {ELN_API_TOKEN}",
        "Content-Type": "application/json"}

    payload = {
        "title": f"Microscopy: {metadata['filename']}",
        "user": metadata["user"],
        "instrument": metadata["microscope"],
        "metadata": metadata}

    response = requests.post(
        ELN_API_URL,
        json=payload,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    return response.json().get("id")
