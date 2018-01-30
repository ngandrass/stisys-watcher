import requests
import getpass
from bs4 import BeautifulSoup

print("Stisys-Watcher")
username = input("Username: ")
password = getpass.getpass("Password: ")

loginData = {
    'username': username,
    'password': password
}

session = requests.Session()
session.post("https://stisys.haw-hamburg.de/login.do", data=loginData)
result_html = session.get("https://stisys.haw-hamburg.de/viewExaminationData.do")

# Parse html result and find tables that contain the results
parsed_html = BeautifulSoup(result_html.text, 'lxml')
result_tables = parsed_html.body.find('div', attrs={'id': 'ergebnisuebersicht'}).find_all('table', attrs={'class': 'tablecontent'})

# Build pretty results
all_results = ""
for curTable in result_tables:
    resultRows = curTable.find('table').find_all('tr')
    for curResultRow in resultRows[1:]:
        cells = curResultRow.find_all('td')
        all_results += "{} - {} - {} - {}\n".format(" ".join(cells[1].text.split()), " ".join(cells[3].text.split()), " ".join(cells[5].text.split()), " ".join(cells[7].text.split()))

print(all_results)
