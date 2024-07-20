import argparse
from dotabet.ui import send_telegram_message
from dotabet.script.get_new import get_new_matches  
from dotabet.script.link import link  
from dotabet.script.pinnacle import scrape_dota2_odds   
from dotabet.script.recommend import recommend_elo    
import dotabet

def get_new_matches_action(chat_id, token):
    log_msg = get_new_matches()
    send_telegram_message(token, chat_id, ''.join(log_msg))

def link_action(chat_id, link_token, checkout_token):
    link_msg = link()
    send_telegram_message(link_token, chat_id, ''.join(link_msg))
    checkout_msg = dotabet.checkout.compute_elo_results()
    send_telegram_message(checkout_token, chat_id, ''.join(checkout_msg))

def scrape_odds_action(chat_id, parse_token, rec_token):
    tg_msg = scrape_dota2_odds()
    send_telegram_message(parse_token, chat_id, ''.join(tg_msg))
    tg_msg_rec = recommend_elo()
    send_telegram_message(rec_token, chat_id, ''.join(tg_msg_rec))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute Dotabet actions')
    parser.add_argument('action', choices=['get_new', 'link', 'scrape_odds'], help='Action to perform')
    args = parser.parse_args()

    chat_id = '333091706'
    
    print(f"User Argument={args.action}")
    if args.action == 'get_new':
        log_token = '7109559904:AAFIoKm_jJUnzjtEUQJ5TN8ukd5Pc4Go0A0'
        get_new_matches_action(chat_id, log_token)
    elif args.action == 'link':
        link_token = '7074261020:AAG5hh_xsFvGXW7gBDnwH4ocwJzrmCGYSPY'
        checkout_token = '7311473809:AAFqyhg7HIbtTu7UawrGCU5qr5v2XMmT9No'
        link_action(chat_id, link_token, checkout_token)
    elif args.action == 'scrape_odds':
        parse_token = "7416284654:AAGhRdKNgUlwDrBRPp_xRaMO151aMMh11jY"
        rec_token = "7227209457:AAHHtQ2mSnHyK6zzyIjQZFyrLd4CXBZn3_o"
        scrape_odds_action(chat_id, parse_token, rec_token)
        
    input("Press Enter to close the window...")
