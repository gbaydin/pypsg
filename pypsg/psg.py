import pypsg
import os
import requests


class PSG():
    def __init__(self, server_url='https://psg.gsfc.nasa.gov/api.php', timeout_seconds=10):
        self._server_url = server_url
        self._timeout_seconds = timeout_seconds
        default_config_file_name = os.path.join(pypsg.__resource_path__, 'default.config')
        self._default_config = None
        with open(default_config_file_name) as f:
            self._default_config = f.read()

        print('Testing connection to PSG at {} ...'.format(self._server_url))
        reply = self.run(self._default_config)
        print('Connected to PSG with success.')

    def run(self, config):
        r = requests.post(self._server_url, data={'file':config}, timeout=self._timeout_seconds)
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            raise RuntimeError('Unexpected HTTP status code received from PSG: {}'.format(r.status_code))
