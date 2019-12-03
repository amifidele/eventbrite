from __future__ import unicode_literals

import hmac
import hashlib
import json
import requests

BASE_URL = 'https://api.mailgun.net/v3'


class Mailgun(object):
    def __init__(self, domain, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key
        self.auth = ('api', private_key)
        self.base_url = '{0}/{1}'.format(BASE_URL, domain)

    def post(self, path, data, auth=None, files=None, include_domain=True):
        url = self.base_url if include_domain else BASE_URL
        return requests.post(url + path, auth=auth or self.auth, data=data, files=files)

    def get(self, path, params=None, auth=None, include_domain=True):
        url = self.base_url if include_domain else BASE_URL
        return requests.get(url + path, auth=auth or self.auth, params=params)

    def send_message(self, from_email, to, cc=None, bcc=None,
                     subject=None, text=None, html=None, user_variables=None,
                     reply_to=None, headers=None, inlines=None, attachments=None, campaign_id=None):
        # sanity checks
        assert (text or html)

        data = {
            'from': from_email,
            'to': to,
            'cc': cc or [],
            'bcc': bcc or [],
            'subject': subject or '',
            'text': text or '',
            'html': html or '',
        }

        if reply_to:
            data['h:Reply-To'] = reply_to

        if headers:
            for k, v in headers.items():
                data["h:%s" % k] = v

        if campaign_id:
            data['o:campaign'] = campaign_id

        if user_variables:
            for k, v in user_variables.items():
                data['v:%s' % k] = v

        files = []

        if inlines:
            for filename in inlines:
                files.append(('inline', open(filename)))

        if attachments:
            for filename, content_type, content in attachments:
                files.append(('attachment', (filename, content, content_type)))

        return self.post('/messages', data, files=files)

    def get_events(self, begin=None, end=None, ascending=None, limit=None, filters=None):
        params = dict()

        if begin:
            params['begin'] = begin

        if end:
            params['end'] = end

        if ascending:
            params['ascending'] = ascending

        if limit:
            params['limit'] = limit

        if filters is None:
            filters = dict()

        params.update(filters)

        return self.get('/events', params=params)

    def create_list(self, address, name=None, description=None, access_level=None):
        data = {'address': address}
        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if access_level and access_level in ['readonly', 'members', 'everyone']:
            data['access_level'] = access_level

        return self.post('/lists', data, include_domain=False)

    def add_list_member(self, list_name, address, name=None, params=None,
                        subscribed=True, upsert=False):
        data = {'address': address}
        if name:
            data['name'] = name

        if params:
            data['vars'] = json.dumps(params) if isinstance(params, dict) else params

        if not subscribed:
            data['subscribed'] = 'no'

        if upsert:
            data['upsert'] = 'yes'

        return self.post('/lists/%s/members' % list_name, data, include_domain=False)

    def verify_authenticity(self, token, timestamp, signature):
        return signature == hmac.new(
            key=self.private_key, msg='{}{}'.format(timestamp, token),
            digestmod=hashlib.sha256).hexdigest()

    def validate(self, address):
        params = dict(address=address)
        auth = ('api', self.public_key)
        return self.get('/address/validate', params=params, auth=auth, include_domain=False)
