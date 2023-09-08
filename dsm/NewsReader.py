from newsapi import NewsApiClient
from telegram import Update , InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from bs4 import BeautifulSoup
import sys

"""       
                    *** NEWSREADER SUB MODULE ***
"""

sys.path.append("..")
from core import core

# Defining a list to keep articles, titles, etc., ordered.
sections = [[] for i in range(7)]

class NewsReader(core) :
    # Constructor
    def __init__(self , mode_type , api_token , bot_username  , provider , model , newsapi_token) :
        super().__init__(mode_type , api_token , bot_username  , provider , model )
        self.newsApiObject = NewsApiClient(newsapi_token)
    
    # News command 
    async def news_command(self , update=Update , context=ContextTypes.DEFAULT_TYPE) :
        await self._async_init(update , context)

        global sections

        if max(map(len, sections)) > 0 :
            sections = [[] for i in range(7)]
    
        args = context.args 
        combination = " ".join(args[:-1])

        try : 
            self.article_n = int(args[-1])
            self._dig_out(combination) 
            self.buttons = [
                [
                    InlineKeyboardButton("Previous", callback_data="prev"),
                    InlineKeyboardButton("Read Article", callback_data="read"),
                    InlineKeyboardButton("Next", callback_data="next")
                ]
            ]
            self.reply_markup = InlineKeyboardMarkup(self.buttons)
            data = self._go_to_article(self.article_n)

        except Exception as e :
            await update.message.reply_text(
                "Somthing went wrong !"
                + "\nPerhaps there wasn't any result according to your query !"
                + "\nArticle number range must be between (0,99)"
                + "\nCorrect arguments order should be like : /news query article_number")
            return e

        await context.bot.send_message(chat_id=self.chat_id, text=data , reply_markup=self.reply_markup)

    # Private scraper method 
    def _scrape_news(self , url) :
        content = ""
        page = requests.get(url)
        soup = BeautifulSoup(page.text , 'html.parser')
        table = soup.find_all('p')
        for item in table :
            if len(content) <= 2000 :
                content += item.text
        content += f"\n...\nRead More at {url}"
        return content

    # Private method to organize output from 'sections' list
    def _go_to_article(self , article_n) :
        return f"📰Title : {sections[1][article_n]}\n🖌️Author : {sections[0][article_n]}\n🔎Description : {sections[2][article_n]}\n🖇️Url : {sections[3][article_n]}\n🌠UrlToImage : {sections[4][article_n]}\n⏰PublishedAt : {sections[5][article_n]}\n❇️Article : {article_n}/{len(sections[0])-1}"

    # Private method to send forged query & get news 
    def _dig_out(self , query) :
        all_articles = self.newsApiObject.get_everything(q=query,sort_by='relevancy')

        for i in range(len(all_articles['articles'])) : 
            sections[0].append(all_articles['articles'][i]['author'])
            sections[1].append(all_articles['articles'][i]['title'])
            sections[2].append(all_articles['articles'][i]['description'])
            sections[3].append(all_articles['articles'][i]['url'])
            sections[4].append(all_articles['articles'][i]['urlToImage'])
            sections[5].append(all_articles['articles'][i]['publishedAt'])
            sections[6].append(all_articles['articles'][i]['content'])
    
    # Button click listener
    async def button_click(self , update=Update , context=ContextTypes.DEFAULT_TYPE):
        await self._async_init(update , context)
        query = update.callback_query
        
        if query.data == "prev" and self.article_n >= 1 :
            self.article_n -= 1
            data = self._go_to_article(self.article_n)
            await context.bot.send_message(chat_id=self.chat_id, text=data , reply_markup=self.reply_markup)
        
        if query.data == "next" and self.article_n <= 99 :
            self.article_n += 1
            data = self._go_to_article(self.article_n)
            await context.bot.send_message(chat_id=self.chat_id, text=data , reply_markup=self.reply_markup)

        if query.data == "read":
            await context.bot.send_message(chat_id=self.chat_id, text=self._scrape_news(sections[3][self.article_n]))
        

    def __str__(self) :
        return "Mode's currently set to NewsReader !"
