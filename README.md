# SSKB - Super Simple Knowledge Base
A dead-simple KB with role-based access and full-text searching.

WARNING: Much broken. Very incomplete. Wow.

This application is still under heavy development. If you use it, please submit issues in GitHub (https://github.com/mambojuice/sskb)

## Project layout

Path | Description
-----|------------
sskb/ | Root
sskb/sskb/ | Root folder for holding Django project files
sskb/sskb/KnowledgeBase/ | Django project folder ('KnowledgeBase' is the name of the project in Django)
sskb/sskb/kb/ | Django app folder ('kb' is the name of the app within the Django project)
sskb/sskb/db.sqlite3 | SQLite3 database file located **OUTSIDE** the application root. Created when running `python manage.py migrate`
sskb/sskb/kb/static/ | Static files (CSS, JS, etc)
sskb/sskb/kb/wsgi.py | Python WSGI script for Apache integration

## Run with Docker
Dockerfile provided uses the standard Python3 docker image. Build your image with the following command:
`docker build -t sskb .`

Now run your image:
`docker run -d -p 8000:8000 sskb`

You should be able to browse to http://localhost:8000 and be directed to the login screen.

The Docker image will create a superuser 'admin' with password 'password'.

## Manual deployment

### Requirements
* pip (to install python packages)
* django

### Basic Installation
* This guide assumes Debian/Ubuntu is the running OS. Administrative rights are obtained using `sudo`
* RPM-based systems should be similar. Windows is theoretically possible but untested.
* The application will be installed to `/opt/sskb`
* Basic installation will get the application up and running using the Python development web server. It is not suitable for production use

1. Install pip
```bash
$ sudo apt-get install python3-pip
```

2. Update pip to latest version
```bash
$ sudo pip install --upgrade pip
```

3. Install Django
```bash
$ pip install django
```

4. Download InvoiceManager from Github repo. Optionally, download the Zip file from https://github.com/mambojuice/sskb/archive/master.zip
```bash
$ git clone https://github.com/mambojuice/sskb --branch master
$ sudo cp -r sskb/sskb /opt
$ cd /opt/sskb
```

5. Edit the following lines of KnowledgeBase/settings.py
```python
#  Put a random string at least 50 characters long here. This will keep hashed passwords safe.
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()<>{}'

# Set to match system time
TIME_ZONE = 'UTC'
```

6. Create the application database
```bash
/opt/sskb$ sudo python manage.py migrate
```

7. Create an admin user
```bash
/opt/sskb$ sudo python manage.py create superuser
Username (leave blank to use 'root'): admin
Email address: admin@home.local
Password:
Password (again):
Superuser created successfully.
```

8. At this point, you should have enough configured to run the app using Python's development server. Run the following command and browse to http://localhost:8000
```bash
/opt/invoicemanager$ sudo python manage.py runserver 0.0.0.0:8000
```
