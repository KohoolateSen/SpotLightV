from core import core
from configparser import ConfigParser
from telegram.ext import Application , CommandHandler , MessageHandler , CallbackQueryHandler , filters
from g4f.Provider import (Acytoo, Lockchat , Aichat, Wewordle, You , Ails, AiService, AItianhu, Bard, Bing, ChatgptAi, ChatgptLogin, DeepAi, GetGpt)
from dsm import ( NewsReader )

# Mapping providers classes
providers_map = {
    "Acytoo": Acytoo,
    "Aichat": Aichat,
    "Ails": Ails,
    "AiService": AiService,
    "AItianhu": AItianhu,
    "Bard": Bard,
    "Bing": Bing,
    "ChatgptAi": ChatgptAi,
    "ChatgptLogin": ChatgptLogin,
    "DeepAi": DeepAi,
    "GetGpt": GetGpt,
    "You" : You,
    "Wewordle" : Wewordle,
    "Lockchat" : Lockchat
}

# Mapping DSMs
distributed_sub_modules_map = {
    "coreBot" : core,
    "NewsReader" : NewsReader.NewsReader
}

# Main function
def main() :
    
    print("[*] Beep Boop Beeeep ZSHSHSH ...")
    print("[#] Please be patient Human ...")
    print("[!] Reading Configuration file ...")

    # Making instance of ConfigParser
    config = ConfigParser()

    # Reading Configuration file
    config.read('config.ini')

    # Defining initial variable configs
    api_token = config['CLIENT']['TelegramApiToken']
    newsapi_token = config['CLIENT']['NewsApiToken']
    bot_username = config['CORE']['UserName']
    mode = distributed_sub_modules_map[config['NEWSREADER']['Mode']]
    provider = providers_map[config['CORE']['Provider']]
    model = config['CORE']['Model']
  
    # Creating instance of Bot
    baseObject = mode(mode_type=str(mode) ,api_token=api_token ,bot_username=bot_username ,provider=provider,model=model,newsapi_token=newsapi_token) 

    try :
        # Building Application 
        app = Application.builder().token(api_token).build()
        
        # Commands handlers
        app.add_handler(CommandHandler('start' , baseObject.start_command ))
        app.add_handler(CommandHandler('news' , baseObject.news_command ))
        app.add_handler(CommandHandler('r' , baseObject.remember_current_message_command))
        app.add_handler(CommandHandler('help' , baseObject.help_command))
        app.add_handler(CommandHandler('m' , baseObject.send_message_command))
        app.add_handler(CallbackQueryHandler(baseObject.button_click))
        app.add_handler(CommandHandler('delete' , baseObject.delete_conversation_command ))
        app.add_handler(MessageHandler(filters.COMMAND , baseObject.unknown_command))

        # Error handler
        app.add_error_handler(baseObject.error)

        # Start Polling
        print("[!] Polling ...")
        app.run_polling(poll_interval=3)

    except Exception as e:
        print(f"An error occurred: {e}") 


if __name__ == "__main__":
    main()
