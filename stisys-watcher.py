import requests
import getpass
from bs4 import BeautifulSoup


class StisysWatcher:

    loginData = {
        'username': None,
        'password': None
    }

    session = requests.Session()

    def __init__(self):
        self.read_logindata()
        self.login()
        print(self.get_all_results())

    def read_logindata(self):
        print('Stisys-Watcher')
        self.loginData['username'] = input('Username: ')
        self.loginData['password'] = getpass.getpass('Password: ')

    def login(self):
        self.session.post('https://stisys.haw-hamburg.de/login.do', data=self.loginData)

    def get_all_results(self) -> str:
        result_html = self.session.get('https://stisys.haw-hamburg.de/viewExaminationData.do')

        # Parse html result and find tables that contain the results
        parsed_html = BeautifulSoup(result_html.text, 'lxml')
        result_tables = parsed_html.body.find('div', attrs={'id': 'ergebnisuebersicht'}).find_all('table', attrs={'class': 'tablecontent'})

        # Build pretty results
        all_results = ''
        for cur_table in result_tables:
            result_rows = cur_table.find('table').find_all('tr')
            for cur_result_row in result_rows[1:]:
                cells = cur_result_row.find_all('td')
                all_results += '{} - {} - {} - {}\n'.format(' '.join(cells[1].text.split()), ' '.join(cells[3].text.split()), ' '.join(cells[5].text.split()), ' '.join(cells[7].text.split()))

        return all_results


StisysWatcher()
