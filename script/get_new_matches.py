from dotabet.ui import send_telegram_message
from dotabet.script.get_new import get_new_matches  

if __name__ == "__main__":
    chat_id='333091706'

    # dotabet_log_bot
    log_token = '7109559904:AAFIoKm_jJUnzjtEUQJ5TN8ukd5Pc4Go0A0'
    log_msg = get_new_matches()
    send_telegram_message(log_token, chat_id, ''.join(log_msg))
    

