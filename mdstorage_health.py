#!/usr/bin/python

import datetime
import sys
import subprocess
import boto.ses
from slacker import Slacker

sns_conn = boto.ses.connect_to_region('<AWS_REGION>', aws_access_key_id='<AWS_ACCESS_KEY>', aws_secret_access_key='<AWS_SECRET_KEY>')
now = datetime.datetime.today().strftime('%Y-%m-%d')
slack_token = '<SLACK_API_TOKEN>'
slack_channel = '<SLACK_CHANNEL>'
smcli_bin = '/opt/dell/mdstoragemanager/client/SMcli'
arguments = ["<MDSTORAGE_IP_ADDRESS>", "-S", "-quick", "-c", "show storageArray healthStatus;"]
slack = Slacker(slack_token)

command = [smcli_bin]
command.extend(arguments)

def send_mail(subject, email):
    sns_conn.send_email('<FROM_EMAIL>', subject, email, ['<TO_EMAIL>'])

try:
    smcli = subprocess.Popen(command, stdout=subprocess.PIPE)
except:
    subject = "There was a problem getting storage status."
    email = "Couldn't get storage status, sorry."
    send_mail(subject, email)
    slack.chat.post_message(slack_channel, subject)
else:
    health_status = smcli.communicate()[0].rstrip()
    if 'optimal' in health_status:
        subject = 'Storage health status %s' % health_status
        slack.chat.post_message(slack_channel, subject)
    else:
        subject = "Storage status " + health_status
        email_subject = "Storage check problem"
        slack.chat.post_message(slack_channel, subject)
        send_mail(email_subject, subject)
