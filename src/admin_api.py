import logging
import random
import string
import sys

from client import send_post_request, send_put_request


class AdminAPI:
    def __init__(self, server_url='http://127.0.0.1:8081'):
        self.server_url = server_url

    def add_team_and_get_token(self, team_name=None):
        if team_name is None:
            team_name = 'anton-and-dima-' + ''.join(random.choices(string.ascii_lowercase
                                                                   + string.ascii_uppercase
                                                                   + string.digits, k=10))
        body = send_post_request(self.team_base_url, {'team_name': team_name})

        team_name = body.json()['name']
        token = body.json()['token']

        logging.info('Added team %s', team_name)

        return team_name, token

    def start_game(self):
        send_put_request(self.game_start_url)
        logging.info('Started game')

    def stop_game(self):
        send_put_request(self.game_stop_url)
        logging.info('Stopped game')


    @property
    def admin_url(self):
        return self.server_url + '/admin'

    @property
    def game_start_url(self):
        return self.admin_url + '/start'

    @property
    def game_stop_url(self):
        return self.admin_url + '/stop'

    @property
    def team_base_url(self):
        return self.admin_url + '/team'


if __name__ == '__main__':
    # Usage: python admin_api.py http://api.citysimulation.eu/moore TEAM_NAME

    SERVER_URL = 'http://localhost:8081'
    if len(sys.argv) >= 2:
        SERVER_URL = sys.argv[1]

    admin_api = AdminAPI(server_url=SERVER_URL)

    if len(sys.argv) >= 3:
        team_name = sys.argv[2]
        _, token = admin_api.add_team_and_get_token(team_name)
        print(team_name + ' ' + token)
    admin_api.start_game()
