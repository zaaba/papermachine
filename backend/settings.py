# settings.py
import os

# This line only needed locally. On Render, it's not required unless you're using .env files
# from dotenv import load_dotenv
# load_dotenv()

GPT_API_KEY = os.getenv("GPT_API_KEY")

if GPT_API_KEY is None:
    raise ValueError("GPT_API_KEY is not set!")