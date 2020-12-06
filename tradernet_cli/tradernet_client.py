# ########################################################### #
#           PublicApi-клиент TraderNet для Python 3           #
#    https://tradernet.com/tradernet-api/public-api-client    #
# ########################################################### #
# edited to support PEP8 code style
import time
import hmac
import hashlib
import requests


class TraderNetAPIError(Exception):
    pass


class PublicApiClient:
    V1 = 1
    V2 = 2

    def __init__(self, api_url, api_key, api_secret):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret

    def presign(self, d):
        s = ''
        for i in sorted(d):
            if type(d[i]) == dict:
                s += f'{i}={self.presign(d[i])}&'
            else:
                s += f'{i}={d[i]}&'
        return s[:-1]

    def http_encode(self, d, mode=1):
        s = ''
        for i in sorted(d):
            if type(d[i]) == dict:
                s += self.http_encode(d[i], i) + '&'
            else:
                if mode == 1:
                    s += f'{i}={d[i]}&'
                else:
                    s += f'{mode}[{i}]={d[i]}&'
        return s[:-1]

    def send_request(self, method, params=None, version=V2):
        req = dict()
        req['cmd'] = method
        if params:
            req['params'] = params
        if version == self.V1 and 'params' not in req:
            req['params'] = {}
        if version != self.V1 and self.api_key:
            req['apiKey'] = self.api_key
        req['nonce'] = int(time.time()*10000)

        pre_sig = self.presign(req)
        presig_enc = self.http_encode(req)

        if version == self.V1:
            # V1 version does not work at the moment, it at least requires a proper auth procedure
            raise NotImplemented
            # req['sig'] = hmac.new(key=self.api_secret.encode(), digestmod=hashlib.sha256).hexdigest()
            # res = requests.post(self.api_url, data={'q': json.dumps(req)})
        else:
            api_headers = {
                'X-NtApi-Sig': hmac.new(
                    key=self.api_secret.encode(),
                    msg=pre_sig.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).hexdigest(),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            url = self.api_url + '/v2/cmd/' + method
            res = requests.post(url, params=presig_enc, headers=api_headers, data=presig_enc)

        res.raise_for_status()

        # handle api error
        if 'application/json' in res.headers['Content-Type']:
            json_result = res.json()
            if type(json_result) is dict and 'code' in json_result.keys():
                raise TraderNetAPIError(json_result)

        return res

    def __str__(self):
        return f'<{self.__class__.__name__}>(' \
               f'api_url="{self.api_url}", ' \
               f'api_key="{self.api_key}", ' \
               f'api_secret="{self.api_secret}")'
