import openai
import os
import logging

def load_api_key():
    """Loads the OpenAI API key from gpt_api_key.txt."""
    key_path = "gpt_api_key.txt"

    if os.path.exists(key_path):
        with open(key_path, "r") as key_file:
            return key_file.read().strip()
    else:
        logging.error("API key file not found. Please create 'gpt_api_key.txt' and store your key there.")
        return None  # Return None instead of proceeding with an undefined key

# Load API key
api_key = load_api_key()
if api_key:
    openai.api_key = api_key
    client = openai.OpenAI(api_key=api_key)  # ✅ Correctly define `client`
    print("✅ OpenAI API client initialized successfully!")
else:
    client = None
    print("❌ OpenAI API key missing. Exiting.")

# Ensure the client is available for imports
__all__ = ["client"]
