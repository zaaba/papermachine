# backend/settings.py
import os

GPT_API_KEY = os.getenv("GPT_API_KEY")

if GPT_API_KEY is None:
    raise ValueError("GPT_API_KEY is not set.")