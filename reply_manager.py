"""
Module containing classes and functions for generating the response.

At the moment only the free mode of chatgpt via requst is present,
in the future implementation of other api of various models and responses
do not generate via ai.
"""
import requests
from bs4 import BeautifulSoup

from system import Configurations as Conf, ConfigKey
from system import write_log

def _ask_to_chatgpt_no_api(message:str)->str:
    """
    Processing the response using chatgpt without using its api.
    The response is made by using post requests to https://www.chatgpt.it,
    a third-party site that also uses the official api.

    First we need to get _wpnonce for the post request.
    So we must do a get and then serach wpaicg-chat-shortcode class
    and get the "data-nonce" data.
    That will be the _wpnonce to put in the payload.
    We can generate a random client_id.
    Post_id and bot_id can get at same way and put all in the payload.

    The system prompt will be added to the chat history to set a context
    """
    url = "https://chatgpt.it/"
    session = requests.Session()
    response = session.get(url)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    chat_div = soup.find("div", class_="wpaicg-chat-shortcode")

    if not chat_div:
        write_log("Error to find wpaicg-chat-shortcode. Aborting request.")
        return ""

    nonce = chat_div.get("data-nonce")
    post_id = chat_div.get("data-post-id")
    bot_id = chat_div.get("data-bot-id")
    client_id = "NzaxpK6bZf"

    post_url = "https://chatgpt.it/wp-admin/admin-ajax.php"
    payload = {
        "_wpnonce": nonce,
        "post_id": post_id,
        "url": url,
        "action": "wpaicg_chat_shortcode_message",
        "message": message,
        "bot_id": bot_id,
        "chatbot_identity": "shortcode",
        "wpaicg_chat_history": "[]",
        "wpaicg_chat_client_id": client_id
    }
    payload["wpaicg_chat_history"] = f"""[{{"text":"Human:
                                    {Conf.get_conf_data(ConfigKey.SYSTEM_PROMPT)}"}}]"""
    headers = {
        "Origin": "https://chatgpt.it",
        "Referer": "https://chatgpt.it/",
        "User-Agent": "Mozilla/5.0",
    }

    response = session.post(post_url, data=payload, headers=headers)

    re_json = response.json()
    return re_json["data"]

def callback_for_pipeline(message:str)->str:
    """
    Method that uses appropriate response processing functions
    based on configurations and input type,
    and processes the response for the pipeline.

    For now only chatgpt_no_api is implemented, so it will simply be executed
    """
    return _ask_to_chatgpt_no_api(message)
