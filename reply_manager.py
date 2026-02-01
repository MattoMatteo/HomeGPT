"""
Module containing classes and functions for generating the response.

At the moment only the free mode of chatgpt via requst is present,
in the future implementation of other api of various models and responses
do not generate via ai.
"""
import os
import json

import requests
from bs4 import BeautifulSoup

from system import Configurations as Conf, ConfigKey
from log_manager import setup_logger

logger = setup_logger("REPLY_MANAGER")


def _ask_to_openrouter_model(message:str)->str:
    """
    """
    api_key = Conf.get_conf_data(ConfigKey.OPEN_ROUTER_API)
    model = Conf.get_conf_data(ConfigKey.OPEN_ROUTER_MODEL)

    if not api_key or not model:
        raise ValueError(
            "OPENROUTER_API_KEY or OPEN_ROUTER_MODEL not found in environment."
            "Please check .env file and docker-compose.yml."
        )
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "HomeGPY",
    }

    prompt = Conf.get_conf_data(ConfigKey.SYSTEM_PROMPT) + "\n" + message
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return ""

def callback_for_pipeline(message:str)->str:
    """
    Method that uses appropriate response processing functions
    based on configurations and input type,
    and processes the response for the pipeline.

    For now only chatgpt_no_api is implemented, so it will simply be executed
    """
    return _ask_to_openrouter_model(message)
