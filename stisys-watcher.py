import requests
import getpass
from bs4 import BeautifulSoup


class StisysWatcher:

    loginData = {
        'username': None,
        'password': None
    }

    session = requests.Session()

    difffile_path = 'stisys-watcher.tmp'

    def __init__(self):
        self.read_logindata()
        self.login()

        fresh_results = self.get_all_results()
        if self.check_for_changes(fresh_results):
            print("ATTENTION: New results have been detected!\n\n")
            print(fresh_results)

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

    def check_for_changes(self, new_results: str) -> bool:
        self.create_difffile_if_nonexisting()

        with open(self.difffile_path, 'r+') as difffile:
            old_results = difffile.read()
            if new_results != old_results:
                difffile.write(new_results)
                return True

        return False

    def create_difffile_if_nonexisting(self):
        try:
            difffile = open(self.difffile_path, 'r')
        except FileNotFoundError:
            difffile = open(self.difffile_path, 'w+')
        difffile.close()


StisysWatcher()