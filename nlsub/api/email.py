import json
from datetime import timedelta

import requests
from django.conf import settings
from django.core.signing import TimestampSigner
from django.utils.http import urlquote
from rest_framework.exceptions import APIException

from api.models import Subscriber


def generate_url(action, email, list_id):
    signable = [email, list_id]
    signer = TimestampSigner(salt=action)
    signable_s = json.dumps(signable)
    signed_s = signer.sign(signable_s)
    return "{}/{}?signature={}".format(settings.NL['URL_PREFIX'], action, urlquote(signed_s))

def validate_confirm(action, signed_s, max_age=timedelta(days=3)):
    signer = TimestampSigner(salt=action)
    return json.loads(signer.unsign(signed_s, max_age=max_age))

def send_subscription_email(email, list):
    try:
        Subscriber.objects.get(email=email, list=list)
        # TODO Already subscribed exception
        raise APIException("subscriber {} already on list: {}".format(email, list.name))
    except Subscriber.DoesNotExist:
        pass
    url = generate_url("subscribe", email, list.pk)
    return requests.post(
        "https://api.mailgun.net/v3/{0}/messages".format(settings.NL['HOST']),
        auth=("api", settings.NL['API_KEY']),
        data={"from": "{} <hn@niels-ole.com>".format(list.name),
              "to": [email],
              "subject": "Please confirm your subscription",
              "html": "Someone has entered your email address for the newsletter: {}<br>To confirm this subscription please click the following link: <a href=\"{}\">Confirm subcription</a><br>The link will be valid for the next 72 hours.".format(list.name, url)})

def generate_unsubscribe_url(email, list_id):
    return generate_url(action="unsubscribe", email=email, list_id=list_id)


def send_email(subscriber, elist, html, subject):
    url = generate_unsubscribe_url(subscriber.email, elist.id)
    html += "<br />Fed up with this newsletter? <a href=\"{}\">Unsubscribe</a>".format(url)
    host_ = settings.NL['HOST']
    return requests.post(
        "https://api.mailgun.net/v3/" + host_ + "/messages",
        auth=("api", settings.NL['API_KEY']),
        data={"from": u'"{}"<newsletter@{}>'.format(elist.name, host_),
              "to": u'<{}>'.format(subscriber.email),
              "subject": subject,
              "html": html})

