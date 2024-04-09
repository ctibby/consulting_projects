import requests
from bs4 import BeautifulSoup
from credentials import sbvjuser, sbvjpass

# Create a session object
session = requests.Session()

# Set headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
session.headers.update(headers)

# Login payload
payload = {
    'username': sbvjuser,
    'password': sbvjpass,
}

# URL for the login action
login_url = 'https://www.bizjournals.com/sanjose/login'

# Post the login payload to the site
response = session.post(login_url, data=payload)

# Check if login was successful
if response.ok:
    print("Login Successful")

    # URL to the page that lists the articles
    articles_list_url = 'https://www.bizjournals.com/sanjose/news/commercial-real-estate'

    # Fetch the page that lists the articles
    response = session.get(articles_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    print(soup)

    articles = soup.select('li', class_='media')

    # Iterate over each article found and print its title and hyperlink
    for article in articles:
        title = article.get_text(strip=True)  # Get the text and strip any extra whitespace
        link = article['href']  # Get the 'href' attribute directly
        full_link = response.urljoin(link)  # This will make the link absolute if it is relative
        print(f"Title: {title}")
        print(f"Link: {full_link}")
        print()  # Print a newline for better readability

else:
    print("Login failed")
    print(response.text)  # Print the response text to help debug
