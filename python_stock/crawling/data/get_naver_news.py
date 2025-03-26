import requests
from bs4 import BeautifulSoup


def title_getter(url, titles, ans):

    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    # Extracting the sentences from the given HTML
    sentences = [[] for i in range(len(titles))] if len(ans) == 0 else ans

    # Find all the dt elements with class "photo"
    dt_elements = soup.find_all('dt', class_='photo')
    # Iterate through each dt element and extract the text from the associated dd element
    for dt_element in dt_elements:
        # Find the associated dd element
        dd_element = dt_element.find_next('dd')

        # Extract the text from the dt and dd elements
        a_element = dt_element.find('a', class_='nclicks(eco.2ndcont)')
        dt_text = a_element.find('img').get('alt')
        dd_text = dd_element.find('span', class_='lede').get_text(strip=True)

        # Combine the text from dt and dd elements to form a sentence
        sentence = f"{dt_text}"
        for idx, title in enumerate(titles):
            if title in sentence:
                sentences[idx].append(sentence)
    return sentences