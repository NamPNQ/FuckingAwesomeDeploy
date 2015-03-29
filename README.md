## FuckingAwesomeDeploy



### What?

A web interface for deployments.

**Login:**

![](http://i.imgur.com/JdcJfP9.png)

**View the current status of all your projects:**

![](http://i.imgur.com/Jn57FQB.png)

**Allow anyone to watch deploys as they happen:**

![](http://i.imgur.com/VRAZoeJ.png)

**Deploy project:**

![](http://i.imgur.com/6jUwMIB.png)


### How?

FuckingAwesomeDeploy works by ensuring a git repository for a project is up-to-date, and then executes the commands associated with a stage.

Streaming is done through a that uses [server-sent events](https://en.wikipedia.org/wiki/Server-sent_events) to display to the client.

#### Requirements

* MySQL or Postgresql or SQLite
* Redis
* Python 2.7

#### Setup

First clone this project, go to working dir and...

If u using virtualenv

```bash
virtualenv env
. env/bin/active
```

Install requirements

```bash
pip install -r requirments.txt
```

Remove file settings.py and fab_db.db, coppy settings.example.py and rename to settings.py, see `Config in the settings.py file` for config

After config, run migrate

```bash
python manage.py db upgrade
```

Run server

```bash
python wsgi.py
```

Go to http://localhost:5000

Config in the settings.py file:

##### General app 

*SECRET_KEY* for Flask.

*PROJECT_NAME* Change to what u want.

*APPLICATION_ROOT* prefix your url


##### Google OAuth 

*GOOGLE_CLIENT_ID* and *GOOGLE_CLIENT_SECRET*

* Navigate to https://console.developers.google.com/project and create a new project
* Enter a name and a unique project id
* Once the project is provisioned, click APIs & auth
* Turn on Contacts API and Google+ API (they are needed by Samson to get email and avatar)
* Click the Credentials link and then create a new Client ID
* Set the Authorized JavaScript Origins to http://localhost:3000
* Set the Authorized Redirect URI to http://localhost:3000/auth/google/callback
* Create the Client ID
* You should now have Client ID and Client secret values to populate the .env file with

##### Sentry

*SENTRY_DSN* sentry dsn

##### DATBASE

*SQLALCHEMY_DATABASE_URI* i using sqlachemy, that mean u can using what u want your database, ex: postgresql, mysql, sqllite

#### User roles

Role | Description
--- | ---
Viewer | Can view all deploys.
Deployer | Viewer + ability to deploy projects.
Admin | Deployer + can setup and configure projects + management of user roles.

The first user that logs into FuckingAwesomeDeploy will automatically become a admin.

##### For real use

I had make supervisor.conf and nginx.conf for real use.

##### Process

-> Suggesst me :D


### Note

I using frontend of project [Samson](https://github.com/zendesk/samson) and some code in [freight](https://github.com/zendesk/samson/raw/master/README.md)


## Help needed
If you are a Python developer or a web designer you can help us improve FuckingAwesomeDeploy. Feel free to take a look at the bug tracker for some tasks to do.
