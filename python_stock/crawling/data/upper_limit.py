from bs4 import BeautifulSoup
import requests


def main():
    print('test_KOSPI.py is running...\n')
    ans = []; result_tables = []
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
        result_tables.append(tables[0])
        result_tables.append(tables[1])

        for idx, result_table in enumerate(result_tables):
        # Find all rows directly within the second table
            rows = result_table.find_all('tr')
            
            # Process each row
            for row in rows:
                # Extract columns from the row
                columns = row.find_all(['th', 'td'])

                tmp_column = []
                # Process each column
                for column in columns:
                    tmp_column.append(column.get_text(strip=True))
                    # print(column.get_text(strip=True), end='\t')
                if not (idx == 1 and tmp_column[0] == 'N'):
                    ans.append(tmp_column); 
                tmp_column = []
                # print()
        
    else:
        print("There is no second table with class 'type_5'.")
    return(ans)

if __name__ == "__main__":
    print(main())