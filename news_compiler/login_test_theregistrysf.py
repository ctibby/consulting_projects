import requests
from bs4 import BeautifulSoup
from credentials import trsfuser, trsfpass

def theregistrysf_login():
    # Create a session object
    session = requests.Session()

    # Set headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session.headers.update(headers)

    # Login payload
    payload = {
        'username': trsfuser,
        'password': trsfpass,
    }

    # URL for the login action
    login_url = 'https://news.theregistrysf.com/log-in-lp/'

    # Post the login payload to the site
    response = session.post(login_url, data=payload)

    # Check if login was successful
    if response.ok:
        print("theregistrysf login successful")
    
    else:
        print("theregistrysf login failed")
        print(response.text)  # Print the response text to help debug

'''
# URL to the page that lists the articles
articles_list_url = 'https://news.theregistrysf.com/category/commercial/'

# Fetch the page that lists the articles
response = session.get(articles_list_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Iterate over each article found and print its title and hyperlink
article_containers = soup.find_all('div', class_ = 'item-details', limit=10)

urladd = ""

for article in article_containers:
    headline_tag = article.find('h3')
    if headline_tag:
        a_tag = headline_tag.find('a')
        if a_tag and a_tag.has_attr('href'):
            full_url = a_tag['href']
            headline = a_tag.get_text(strip=True)
            date_span = article.find('time', class_=['published', 'tnt-date', 'entry-date'])
            date_time = date_span['datetime'] if date_span and 'datetime' in date_span.attrs else "Date not found"
            full_url = f"{urladd}{full_url}"
            print(headline)
'''