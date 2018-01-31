#!/usr/bin/env python3

import argparse
import getpass
import json

from os import path
from typing import Union, List
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup


STISYS_BASE_URL = 'https://stisys.haw-hamburg.de'
STISYS_LOGIN_URL = urljoin(STISYS_BASE_URL, 'login.do')
STISYS_RESULTS_URL = urljoin(STISYS_BASE_URL, 'viewExaminationData.do')


class StisysWatcher:
    def __init__(self):
        # Create Empty dict
        self.login_data = {}

        self.silent_mode = False

        self.session = requests.Session()

        self.difffile_path = None

        self.parse_cli_arguments()
        self.read_logindata()
        self.login()

        diff = self.check_for_changes(self.get_all_results())
        if diff:
            print("ATTENTION: New results have been detected!\n")
            for result in diff:
                print(result)

    def parse_cli_arguments(self):
        parser = argparse.ArgumentParser(
                description=(
                    'Stisys Watcher. '
                    'Automatically pull new results from Stisys (HAW Hamburg).'
                    )
                )

        parser.add_argument(
            '-u',
            type=str,
            help='Your HAW username (a-idenfitier)',
            dest='username')

        parser.add_argument(
            '-p',
            type=str,
            help='Your HAW password',
            dest='password')

        parser.add_argument(
            '-s',
            action='store_true',
            help='Silent mode. Suppresses output apart from result.',
            dest='silent_mode')

        parser.add_argument(
            '-f',
            type=str,
            default='stisys-watcher.state',
            help='Use custom file to store last query state.',
            dest='difffile_path'
        )
        parser.add_argument(
            '-c',
            type=open,
            help='Load credentials from file.',
            dest='credfile'
        )

        cli_args = parser.parse_args()
        if cli_args.credfile:
            self.login_data = json.load(cli_args.credfile)

            if (
                    'username' not in self.login_data or
                    'password' not in self.login_data
                    ):
                raise Exception('Cred file invalid')

        else:
            self.login_data = {
                'username': cli_args.username,
                'password': cli_args.password
            }
        self.silent_mode = cli_args.silent_mode
        self.difffile_path = cli_args.difffile_path

    def read_logindata(self):
        if not self.silent_mode:
            print('Stisys-Watcher')

        if self.login_data['username'] is None:
            self.login_data['username'] = input('Username: ')
        else:
            if not self.silent_mode:
                print('Username: ' + str(self.login_data['username']))

        if self.login_data['password'] is None:
            self.login_data['password'] = getpass.getpass('Password: ')
        else:
            if not self.silent_mode:
                print('Password: Set via CLI argument.')

    def login(self):
        resp = self.session.post(STISYS_LOGIN_URL, data=self.login_data)

        # Check HTTP status code
        resp.raise_for_status()

        # Check if login failed
        if 'Login' in resp.text and 'fehlgeschlagen' in resp.text:
            raise Exception('Login Failed')

    def get_all_results(self) -> str:
        result_html = self.session.get(STISYS_RESULTS_URL)

        # Parse html result and find tables that contain the results
        parsed_html = BeautifulSoup(result_html.text, 'lxml')
        div_container = parsed_html.body.find(
                'div',
                attrs={'id': 'ergebnisuebersicht'}
            )
        result_tables = div_container.find_all(
                'table',
                attrs={'class': 'tablecontent'}
            )

        # Build pretty results
        all_results = ''
        for cur_table in result_tables:
            result_rows = cur_table.find('table').find_all('tr')
            for cur_result_row in result_rows[1:]:
                cells = cur_result_row.find_all('td')
                all_results += '{} - {} - {} - {}\n'.format(
                        cl_text(cells[1]),
                        cl_text(cells[3]),
                        cl_text(cells[5]),
                        cl_text(cells[7])
                    )

        return all_results

    def check_for_changes(self, new_results: str) -> Union[None, List[str]]:
        # Read all lines from file
        if path.isfile(self.difffile_path):
            with open(self.difffile_path, 'r') as difffile:
                old_results_lines = [line.strip() for line in difffile.readlines()]
        else:
            old_results_lines = []

        # Compare new results and look for differences
        new_results_lines = new_results.splitlines()
        if new_results_lines is not old_results_lines:
            different_lines = []

            # Find new results
            for cur_result in new_results_lines:
                if cur_result not in old_results_lines:
                    different_lines.append(cur_result)

            # Update difffile
            with open(self.difffile_path, 'w') as difffile:
                difffile.write(new_results)

            return different_lines
        else:
            return None


def cl_text(element):
    """
    Converts tree element to text and collapse Whitespaces

    Yes the name is not exactly good,
    but a longer one would partially betray the purpose of this function.

    :type element: str
    :rtype: str
    """
    return ' '.join(element.text.split())


# simulate main function to allow import of this file
if __name__ == '__main__':
    StisysWatcher()
