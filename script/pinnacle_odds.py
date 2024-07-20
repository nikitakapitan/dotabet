from dotabet.ui import send_telegram_message
from dotabet.script.pinnacle import scrape_dota2_odds   
from dotabet.script.recommend import recommend_elo    

if __name__ == "__main__":
    # nickapch_bot
    parse_token = "7416284654:AAGhRdKNgUlwDrBRPp_xRaMO151aMMh11jY"
    chat_id = "333091706"
    
    
    tg_msg = scrape_dota2_odds()
    send_telegram_message(parse_token, chat_id, ''.join(tg_msg))
    
    # dota2_rec_bot
    rec_token = "7227209457:AAHHtQ2mSnHyK6zzyIjQZFyrLd4CXBZn3_o"
    tg_msg_rec = recommend_elo()  
    send_telegram_message(rec_token, chat_id, ''.join(tg_msg_rec))
    
