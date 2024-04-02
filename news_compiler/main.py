from bs4 import BeautifulSoup
import requests
import pandas as pd

def fetch_article_summary(article_url):
    try:
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        article_content = soup.find('div', class_ = 'entry-content')
        paragraphs = article_content.find_all('p')[1:]
        
        summary = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
        return summary
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Summary could not be retrieved."

def scrape_pal_articles_to_db():
    url = "https://www.paloaltoonline.com/palo-alto-city/"
    response = requests.get(url)
    soup1 = BeautifulSoup(response.content, 'html.parser')

    url = "https://www.paloaltoonline.com/category/palo-alto-city/page/2/"
    response = requests.get(url)
    soup2 = BeautifulSoup(response.content, 'html.parser')

    url = "https://www.paloaltoonline.com/category/palo-alto-city/page/3/"
    response = requests.get(url)
    soup3 = BeautifulSoup(response.content, 'html.parser')

    article_containers = soup1.find_all('article') + soup2.find_all('article') + soup3.find_all('article')

    articles_df = pd.DataFrame(columns=['Headline', 'URL', 'Date and Time', 'Summary'])

    for article in article_containers:
        headline_tag = article.find('h2')
        if headline_tag:
            a_tag = headline_tag.find('a')
            if a_tag and a_tag.has_attr('href'):
                full_url = a_tag['href']
                headline = a_tag.get_text(strip=True)
                date_span = article.find('time', class_='updated')
                date_time = date_span.get_text(strip=True) if date_span else "Date not found"
                
                # Create a temporary DataFrame for the new row
                temp_df = pd.DataFrame([{'Headline': headline, 'URL': full_url, 'Date and Time': date_time, 'Summary': fetch_article_summary(full_url)}])
                articles_df = pd.concat([articles_df, temp_df], ignore_index=True)

    articles_df = articles_df.drop_duplicates(subset='URL')
    articles_df['Date and Time'] = pd.to_datetime(articles_df['Date and Time'], errors='coerce', format='%B %d, %Y %I:%M %p')
    articles_df.sort_values(by='Date and Time', ascending=False, inplace=True)

    # Use the most recent date in the filename
    if not articles_df.empty and not pd.isna(articles_df.iloc[0]['Date and Time']):
        most_recent_date = articles_df.iloc[0]['Date and Time'].strftime('%Y-%m-%d')
        filename = f'article_summaries_{most_recent_date}.txt'
    else:
        filename = 'article_summaries_no_date.txt'

    with open(filename, 'w', encoding='utf-8') as file:
        for index, row in articles_df.iterrows():
            file.write(f"Headline: {row['Headline']}\nURL: {row['URL']}\nDate and Time: {row['Date and Time'].strftime('%b %d, %Y %I:%M %p') if not pd.isna(row['Date and Time']) else 'Date not found'}\nSummary:\n{row['Summary']}\n\n---\n\n")

    articles_df.to_csv(f'article_summaries_{most_recent_date}.csv', index=False, encoding='utf-8')

    print(f"Article summaries have been saved to {filename}.")

scrape_pal_articles_to_db()
