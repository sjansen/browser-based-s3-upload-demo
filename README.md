# Browser-Based Direct To S3 Upload

Uploading files directly to S3, instead of an intermediate server,
is a great way to reduce server load. While this demo uses Python
and Flask, the code should be simple to translate to other languages
and frameworks.

http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html

## Features

### AWS Signature Version 4

When this demo was created, the majority of direct to S3 upload
examples used AWS Signature Version 2. However, only Signature v4
is supported in new AWS regions like Frankfurt (eu-central-1).

### Form-based Example

The form-based example requires only HTML, no JavaScript. Its
simplicity makes it a useful tool to explore API options.

### Dropzone-based Example

The Dropzone-based example demonstrates CORS compatibility and
dynamic S3 object keys. Hopefully it also demonstrates that, with
a little polishing, direct to S3 upload can provide an excellent
user experience.

http://www.dropzonejs.com/

## Configuring The Bucket

### CORS Policy

For JavaScript-based uploads, a CORS policy must be added to the
bucket. An example policy in included: `doc/cors.xml`

### IAM User

Using your root AWS credentials is not recommended. Instead, for
improved security, create a dedicated IAM user and attach a custom
inline policy. An example policy is included: `doc/iam.json`

### Lifecycle Rules

It is often desirable to automatically delete uploaded files after
a delay. One easy way to accomplish this is using S3 Lifecycle
rules. For example, if a dedicated bucket is used for uploads, the
bucket could be configured to delete all objects one day after
creation.

## Running The Server


### Linux / Mac

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    export AWS_ACCESS_KEY_ID=AKI0123456789ABCDEF
    export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    export S3_REGION=eu-central-1
    export S3_BUCKET=incoming-bucket
    
    ./application.py
    
    open http://localhost:5000


### Foreman

Alternatively, instead of exporting environment variables manually,
`foreman` can run the application using variables from a `.env`
file.  An example file is included: `doc/example.env`

http://ddollar.github.io/foreman/

### Heroku

    heroku create
    heroku config:set AWS_ACCESS_KEY_ID=AKI0123456789ABCDEF
    heroku config:set AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    heroku config:set S3_REGION=eu-central-1
    heroku config:set S3_BUCKET=incoming-bucket
    git push heroku master
    heroku open

## Gotchas

Only one file can be uploaded per POST request.

The `file` field must be the last field in the POST payload. For
JavaScript-based uploads, this means it may be necessary to pass
arguments or construct objects carefully in order to ensure the
`file` field gets sent last.

If your application allows anonymous file upload, you should not
allow anonymous download of the same file. Otherwise, your application
could be abused to share undesirable content. The included example
policy files demonstrate how to implement write only access.
