# Mazta Bank Data "How To"

## First Deployment

First of all on your XAMPP or LARAGON must have databases name like :
- center
- sales
- human_resource
- master

Then just run ```bash deploy.sh``` if you're using linux, run ```.\deploy.ps1``` if you're using windows PowerShell

## Settings

### Domain
__*Use Staticfiles*__ for Media or folder static

On the master_data/master_data/settings.py there's some block code that i commented on it like :

#### This Will Allow the Server To Run At HTTPS
- CSRF_COOKIE_SECURE
- SESSION_COOKIE_SECURE
- SECURE_SSL_REDIRECT

#### This Will Force All Action to HTTPS
- SECURE_HSTS_SECONDS
- SECURE_HSTS_INCLUDE_SUBDOMAINS
- SECURE_HSTS_PRELOAD

#### This is Security for XSS and MIME
- SECURE_BROWSER_XSS_FILTER = True
- SECURE_CONTENT_TYPE_NOSNIFF = True

If you deploy this to a server that runs in __*Https*__ you must set all of that to __True__

And There's a __*DEBUG*__ and __*ALLOWED_HOSTS*__ on settings.py, 
set __*DEBUG*__ to __False__ if you don't wanna see the debug on your page, 
and __*ALLOWED_HOSTS*__ to set the project to just run on your domains
, for example :
- __DEBUG = TRUE__
- __ALLOWED_HOSTS = ['yourdomain.com', 'example.com']__

### Databases

On the Databases section you see the database settings, here's the explaination :
- __'default'__ is for the _Alias_ database that i call on the controller or views.py
- __'ENGINE'__ used for the engine of the database it can be __mysql__, __postgresql__, __sqlite3__, __etc__
- __'NAME'__ is the name of database you setup on your XAMPP
- __'USER'__ is user for your XAMPP
- __'PASSWORD'__ password your XAMPP for user
- __'HOST'__ is your host database
- __'POST'__ port database

for Example :

    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'core',
        'USER': 'root',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost,
        'PORT': '3306,
    }