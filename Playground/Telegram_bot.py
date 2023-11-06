import requests

def telegram_bot_sendtext(bot_message):
    bot_token = ''
    chat_id = ""
    send_text1 = 'https://api.telegram.org/bot' + bot_token + \
                 '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
    response1 = requests.get(send_text1)

    return (response1.json())

"""trouve le bot_token et chad_id sur internet petit tuot youtube ou autre"""