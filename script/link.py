from dotabet.ui import send_telegram_message
from dotabet.script.link import link  
import dotabet

if __name__ == "__main__":
    kapitan_chat_id='333091706'

    # Dotabet_link
    link_token = '7074261020:AAG5hh_xsFvGXW7gBDnwH4ocwJzrmCGYSPY'
    link_msg = link()
    send_telegram_message(link_token, kapitan_chat_id, ''.join(link_msg))
    
    # dotabet_checkout_bot
    checkout_token = '7311473809:AAFqyhg7HIbtTu7UawrGCU5qr5v2XMmT9No'
    checkout_msg = dotabet.checkout.compute_elo_results()
    send_telegram_message(checkout_token, kapitan_chat_id, ''.join(checkout_msg))
    
