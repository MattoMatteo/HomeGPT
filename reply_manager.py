import requests
from bs4 import BeautifulSoup
import system

class scraping_chatGPT():
 
    def ask_to_chatgpt_noAPI(self, message:str)->str:
        
        #First we need to get _wpnonce for the post request. So we must do a get and then serach wpaicg-chat-shortcode class
        #and get the "data-nonce" data. That will be the _wpnonce to put in the payload. We can generate a random client_id.
        #post_id and bot_id can get at same way and pu all in the payload.

        url = "https://chatgpt.it/"
        session = requests.Session()
        response = session.get(url)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        chat_div = soup.find("div", class_="wpaicg-chat-shortcode")

        if not chat_div:
            raise Exception("Div della chat non trovato")

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
        payload["wpaicg_chat_history"] = f"""[{{"text":"Human: {system.conf.config["system_prompt"]}"}}]"""
        headers = {
            "Origin": "https://chatgpt.it",
            "Referer": "https://chatgpt.it/",
            "User-Agent": "Mozilla/5.0",
        }

        response = session.post(post_url, data=payload, headers=headers)

        re_json = response.json()
        return re_json["data"]

freeGPT =  scraping_chatGPT()

