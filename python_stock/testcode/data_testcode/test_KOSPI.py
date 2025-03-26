from bs4 import BeautifulSoup
import requests


def KOSPI():
    ans = []
    # URL of the page containing the HTML table
    url = "https://finance.naver.com/sise/sise_upper.naver"

    # Fetch the HTML content from the URL
    response = requests.get(url)
    html_content = response.text

    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # print(soup)
    # exit(1)

    # Extract table rows
    tables = soup.find_all('table', {'class': 'type_5'})

    # Check if the second table exists
    if len(tables) > 1:
        # Get the second table
        second_table = tables[0]

        # Find all rows directly within the second table
        rows = second_table.find_all('tr')
        
        # Process each row
        for row in rows:
            # Extract columns from the row
            columns = row.find_all(['th', 'td'])

            tmp_column = []
            # Process each column
            for column in columns:
                tmp_column.append(column.get_text(strip=True))
                # print(column.get_text(strip=True), end='\t')
            ans.append(tmp_column); tmp_column = []
            # print()
    else:
        print("There is no second table with class 'type_5'.")
    print(ans)
    return(ans)
# KOSPI()