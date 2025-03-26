from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

#def google_crawler(str, )
# 원래 문자열
original_string = "태영"

# URL 인코딩
encoded_string = quote(original_string)

print(encoded_string)
target_url = "https://www.google.com/search?q=" + encoded_string + "&tbm=nws&"

response = requests.get(target_url)
html = response.text
print(html);exit(1)


soup = BeautifulSoup(html, 'html.parser')
print(soup);exit(1)
# target_divs = soup.find_all(class_=['BNeawe vvjwJb AP7Wnd'])
target_divs = soup.find_all(class_=['rQMQod Xb5VRe'])

text_contents = [div.get_text() for div in target_divs]
for content in text_contents:
    print(content)