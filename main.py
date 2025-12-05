import os
import datetime
import time
import feedparser
import requests
import google.generativeai as genai
from datetime import timedelta
from email.utils import parsedate_to_datetime

GEMINI_KEY = os.environ["GEMINI_KEY"]
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

TOPIC_IDS = {
    "INBOX": 2, 
}
RSS_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCEqHK7Ib89eR2B895T-sTgw", 
]

def get_gemini_summary(text):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an English Learning Assistant.
    Analyze this content snippet: "{text}"
    
    1. Summarize the main idea in 1 Chinese sentence (keep it interesting).
    2. Extract 3 useful English words/phrases with Chinese definitions.
    3. Rate difficulty (1-5 stars).
    
    Output Format:
    **Summary:** ...
    **Vocab:** - Word: Def
    ...
    **Difficulty:** ⭐⭐⭐
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Summary Failed: {e}"

def send_telegram(title, summary, link):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    msg = f"📺 *{title}*\n\n{summary}\n\n[👉 Watch Video]({link})"
    
    payload = {
        "chat_id": TG_CHAT_ID,
        "message_thread_id": TOPIC_IDS["INBOX"],
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    one_day_ago = now - timedelta(hours=24)
    
    print(f"Checking feeds since: {one_day_ago}")

    for feed_url in RSS_FEEDS:
        print(f"Parsing: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            if 'published' in entry:
                dt = parsedate_to_datetime(entry.published)
            elif 'updated' in entry:
                dt = parsedate_to_datetime(entry.updated)
            else:
                continue

            if dt > one_day_ago:
                print(f"Found new item: {entry.title}")
                summary = get_gemini_summary(entry.title + "\n" + entry.summary)
                send_telegram(entry.title, summary, entry.link)
                time.sleep(5) 

if __name__ == "__main__":
    main()
