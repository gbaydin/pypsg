import pypsg
import os
import requests
from pkg_resources import resource_string
from io import StringIO
from collections import OrderedDict
import re
import time
import numpy as np


class PSG():
    def __init__(self, server_url='https://psg.gsfc.nasa.gov/api.php', timeout_seconds=10, key=None):
        self._server_url = server_url
        self._timeout_seconds = timeout_seconds
        self._key = key
        default_config_file_name = os.path.join(pypsg.__resource_path__, 'default.config')
        self.default_config_str = str(resource_string(__name__, 'resources/default.config'))
        self.default_config = self.config_str_to_dict(self.default_config_str)

        print('Testing connection to PSG at {} ...'.format(self._server_url))
        reply = self.run(self.default_config)
        print('Connected to PSG with success.')

    @staticmethod
    def config_str_to_dict(config_str):
        psg_regex = r"<(.+?)>(.*)"
        matches = re.finditer(psg_regex, config_str, re.MULTILINE)

        ret = OrderedDict()
        for match in matches:
            key = match.group(1)
            value = match.group(2)
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    value = value
            ret[key] = value
        return ret

    @staticmethod
    def config_dict_to_str(config_dict):
        ret = []
        for key, value in config_dict.items():
            ret.append('<{}>{}'.format(key, str(value)))
        return '\n'.join(ret)

    def run(self, config=None, config_str=None):
        if config_str is None:
            if config is None:
                raise ArgumentError('Expecting either config or config_str.')
            else:
                config_str = self.config_dict_to_str(config)

        time_start = time.time()
        data = {'file':config_str}
        if self._key is not None:
            data['key'] = self._key
        reply = requests.post(self._server_url, data=data, timeout=self._timeout_seconds)
        time_duration = time.time() - time_start
        if reply.status_code == requests.codes.ok:
            reply_raw = reply.text
        else:
            raise RuntimeError('Unexpected HTTP status code received from PSG: {}'.format(r.status_code))

        reply_header = []
        reply_data = []
        for line in reply_raw.splitlines():
            if line.startswith('#'):
                reply_header.append(line)
            else:
                reply_data.append(line)

        reply_header_str = '\n'.join(reply_header)
        reply_data_np = np.loadtxt(StringIO('\n'.join(reply_data)))

        return {'header': reply_header_str, 'spectrum': reply_data_np, 'duration_seconds': time_duration}
