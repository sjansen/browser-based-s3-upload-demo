#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# vim: set fenc=utf-8 ai et sw=4 ts=8 sts=4 :

import hashlib, hmac, json, os

from base64 import b64encode
from datetime import datetime, timedelta
from uuid import uuid4

from flask import Flask, render_template

REGION  = os.environ.get('S3_REGION')
BUCKET  = os.environ.get('S3_BUCKET')

ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/form/")
def form_based():
    key  = str(uuid4())
    form = s3_upload_form(ACCESS_KEY, SECRET_KEY, REGION, BUCKET, key=key)
    ctx  = {'region': REGION, 'bucket': BUCKET, 'form': form}
    return render_template('form_based.html', **ctx)

def hmac_sha256(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def sign(key, date, region, service, msg):
    date  = date.strftime('%Y%m%d')
    hash1 = hmac_sha256('AWS4'+key, date)
    hash2 = hmac_sha256(hash1, region)
    hash3 = hmac_sha256(hash2, service)
    key   = hmac_sha256(hash3, 'aws4_request')
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).hexdigest()

def s3_upload_form(access_key, secret_key, region, bucket, key):
    now = datetime.utcnow()
    form = {
      'acl': 'private',
      'key': key,
      'success_action_status': '201',
      'x-amz-algorithm': 'AWS4-HMAC-SHA256',
      'x-amz-credential':
        '{}/{}/{}/s3/aws4_request'.format(
          access_key, now.strftime('%Y%m%d'), region
        ),
      'x-amz-date': now.strftime('%Y%m%dT000000Z'),
    }
    expiration = now + timedelta(minutes=30)
    policy = {
      'expiration': expiration.strftime('%Y-%m-%dT%H:%M:%SZ'),
      'conditions': [
        {'bucket': bucket},
        {'key':    key},
        {'acl': 'private'},
        ['content-length-range', 32, 10485760],
        {'success_action_status': form['success_action_status']},
        {'x-amz-algorithm':       form['x-amz-algorithm']},
        {'x-amz-credential':      form['x-amz-credential']},
        {'x-amz-date':            form['x-amz-date']},
      ]
    }
    if region == 'us-east-1':
        form['action'] = 'https://{}.s3.amazonaws.com/'.format(bucket)
    else:
        form['action'] = 'https://{}.s3-{}.amazonaws.com/'.format(bucket, region)
    form['policy'] = b64encode(json.dumps(policy))
    form['x-amz-signature'] = sign(secret_key, now, region, 's3', form['policy'])
    return form

def main():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()
