from bs4 import BeautifulSoup
import requests
import pandas as pd
from transformers import BartTokenizer, BartForConditionalGeneration

model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

def fetch_article_summary(article_url, content_class):
    try:
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        article_content = soup.find('div', class_ = content_class)
        paragraphs = article_content.find_all('p')
        
        summary = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
        return summary
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Summary could not be retrieved."
    
def summarize_text(text, max_length=150, min_length=100, length_penalty=2.0, num_beams=4):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=length_penalty, num_beams=num_beams, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def add_to_db(url, articles_df, articleid, headlineid, urladd, content_class):  
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    article_containers = soup.find_all(articleid, limit=1)

    for article in article_containers:
        headline_tag = article.find(headlineid)
        if headline_tag:
            a_tag = headline_tag.find('a')
            if a_tag and a_tag.has_attr('href'):
                full_url = a_tag['href']
                headline = a_tag.get_text(strip=True)
                date_span = article.find('time', class_=['published', 'tnt-date'])
                date_time = date_span['datetime'] if date_span and 'datetime' in date_span.attrs else "Date not found"
                print(date_time)
                full_url = f"{urladd}{full_url}"
                
                article_content = fetch_article_summary(full_url, content_class)
                temp_df = pd.DataFrame([{'Headline': headline, 'URL': full_url, 'Date and Time': date_time, 'Content': article_content, 'AISummary': summarize_text(article_content)}])
                articles_df = pd.concat([articles_df, temp_df], ignore_index=True)
                print(f"{headline} - successfully entered and summarized")
    return(articles_df)

def scrape_pal_articles_to_db():
    articles_df = pd.DataFrame(columns=['Headline', 'URL', 'Date and Time', 'Content', 'AISummary'])

    articles_df = add_to_db("https://www.paloaltoonline.com/category/palo-alto-city/", articles_df, 'article', 'h2',"" ,'entry-content')
    articles_df = add_to_db("https://www.paloaltoonline.com/category/palo-alto-city/page/2/", articles_df, 'article', 'h2',"" ,'entry-content')
    articles_df = add_to_db("https://www.mv-voice.com/category/local-news/", articles_df, 'article', 'h2',"" ,'entry-content')
    articles_df = add_to_db("https://www.smdailyjournal.com/news/local/", articles_df, 'article', 'h3', "https://www.smdailyjournal.com/", 'asset-content')

    articles_df = articles_df.drop_duplicates(subset='URL')
    articles_df['Date and Time'] = pd.to_datetime(articles_df['Date and Time'], errors='coerce')
    articles_df.sort_values(by='Date and Time', ascending=False, inplace=True)

    # Use the most recent date in the filename
    if not articles_df.empty and not pd.isna(articles_df.iloc[0]['Date and Time']):
        most_recent_date = articles_df.iloc[0]['Date and Time'].strftime('%Y-%m-%d')
        filename = f'article_summaries_{most_recent_date}.txt'
    else:
        filename = 'article_summaries_no_date.txt'

    with open(filename, 'w', encoding='utf-8') as file:
        for index, row in articles_df.iterrows():
            file.write(f"Headline: {row['Headline']}\nURL: {row['URL']}\nDate and Time: {row['Date and Time'].strftime('%b %d, %Y %I:%M %p') if not pd.isna(row['Date and Time']) else 'Date not found'}\nContent:\n\n\n{row['Content']}\nAISummary:\n\n{row['AISummary']}\n\n---\n\n")

    # articles_df.to_csv(f'article_summaries_{most_recent_date}.csv', index=False, encoding='utf-8')

    print(f"Article summaries have been saved to {filename}.")

scrape_pal_articles_to_db()
