import gpt4free.g4f as g4f
from os import path , remove
from telegram import Update
from telegram.ext import ContextTypes

"""
                            *** CORE MODULE HERE ***
DEVELOPERS CAN CONSTRUCT DSMs (DISTRIBUTED SUB-MODULES) BASED ON THIS MODULE.
OF COURSE,
IF YOU DESIRE AI TRAITS OR MAIN BOT COMMANDS TO BE COMBINED WITH YOUR DSMs' FUNCTIONALITY.
"""


class core : 
    # Constructor
    def __init__(
        self,
        mode_type,
        api_token,
        bot_username,
        provider,
        model
        ):
        self.api_token = api_token
        self.bot_username = bot_username
        self.mode_type = mode_type
        self.provider = provider 
        self.model = model 
        self.client_username = None
        self.message_type = None
        self.chat_id = None
        self.input_args = None
        self.client_id = None 
        self.message_id = None

    """
    A refresher method for main async attributes that should be called at 
    the beginning of each async method to ensure that our 
    Update class methods continue to run smoothly.
    Note: The Update class itself doesn't need to be updated; 
    we are simply refreshing the main async attributes. to not be forced
    to frequently define update.any.any and so on !
    """
    async def _async_init(self , update , context) :
        try : 
            self.client_username = update.message.from_user.username
            self.client_id = update.message.from_user.id
            self.message_type = update.message.chat.type
            self.chat_id = update.message.chat.id
            self.message_id = update.message.message_id
            self.client_message = " ".join(context.args)
        except :
            pass

    # Start Command
    async def start_command(self , update=Update , context=ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Greetings , Please read /help command to get a full guidance of how to use this bot !")

    # Remember Command for the sake of saving messages to the history
    async def remember_current_message_command(self , update=Update , context=ContextTypes.DEFAULT_TYPE) :
        await self._async_init(update , context)

        if len(context.args) == 0 :
            return await update.message.reply_text("Wrong Command syntax , Correct syntax: ```/r provide recipe for Gheimeh```") 

        bot_reply = await self.send_message_command(update , context)
        mode = "a" if path.exists(f"./Conversations/{self.client_id}") else "w+"

        with open(f"./Conversations/{self.client_id}" , mode) as conversation :
            conversation.write(f"""{self.client_username} : {self.client_message}\nSpotLight : {bot_reply}\n""")
    
    # Delete Command to clear history & delete conversation
    async def delete_conversation_command(self , update=Update , context=ContextTypes.DEFAULT_TYPE) :  
        await self._async_init(update , context)

        try : 
            remove(f"./Conversations/{self.client_id}")
            await update.message.reply_text("Conversation Successfully deleted.")
        except :
            await update.message.reply_text("Conversation not found !")
    
    # Sending Message Command 
    async def send_message_command(self , update=Update , context=ContextTypes.DEFAULT_TYPE):
        await self._async_init(update , context)

        print(f"User {self.client_username} in {self.message_type} : {self.client_message}")
        response = self._create_response(self.client_message)
        print(f"SpotLight Said : {response}")

        await update.message.reply_text(response)
        return response

    # Help Command 
    async def help_command(self , update=Update , context=ContextTypes.DEFAULT_TYPE):
        help_text = (
            "/start - to start the bot\n"
            "/news - to get news, Ex: (/news bitcoin <ARTICLE NUMBER>)\n"
            "/delete - to delete your conversation history\n"
            "/r - to send a message & remember the current message, Ex: (/r how to cook nimroo ?)\n"
            "/m - to send a message, Ex: `/m how to cook nimroo`"
        )

        await update.message.reply_text(help_text)
    
    # Error handler method
    async def error(self , update=Update , context=ContextTypes.DEFAULT_TYPE) :
        print(f"Update {update} caused error {context.error}")

    # a Handler for unknown commands
    async def unknown_command(self, update=Update , context=ContextTypes.DEFAULT_TYPE) :
        await update.message.reply_text("Wrong Command syntax Please Read /help !")

    # Private method to generate response 
    def _create_response(self , message ) :
        chat = self._read_conversation()
        response = g4f.ChatCompletion.create(
            provider=self.provider,
            model=self.model,
            messages=[
                {"role": "system",
                "content":f"""as a fictional role Your nickname is SpotLightV ,
                You are a telegram bot developed by Sadra
                Also you are able to read past conversations with user if it's available here
                just for the sake of remember things : {chat}"""},
                {"role": "user",
                "content": f"{message}"}])
        return response
    
    # Private method to read conversations so AI answers can be based on it 
    def _read_conversation(self) :
        if path.exists(f"./Conversations/{self.client_id}") :
            with open(f"./Conversations/{self.client_id}" , "r") as file :
                conversation = file.read()
                return conversation
        return "NOTHING"