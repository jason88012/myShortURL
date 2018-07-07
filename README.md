# Short URL API Server
A short url API server application installation, configuration and usage tutorial.
## System Requirement
* [Python3](https://www.python.org/downloads/)
* virtualenv with Python3
* [Redis](https://redis.io/download)
* [Nginx](https://www.nginx.com/)

### System Setup
#### Redis
Use `wget` to install
```
$ wget http://download.redis.io/redis-stable.tar.gz
$ tar xvzf redis-stable.tar.gz
$ cd redis-stable
$ make
```
Modify the Redis configuration file with
```
$ sudo nano /etc/redis/redis.conf
```

#### Nginx
Use `apt-get` to install
```
$ sudo apt-get update
$ sudo apt-get install nginx
```
Modify the Nginx server configuration file with
```
$ sudo nano /etc/nginx/sites-available/default
```
Here is the configuration file `default` should looks like:
```
server { 
    listen 80 default;
    server_name [public IP or domain name];
    location / { 
        include uwsgi_params;
        uwsgi_pass unix:/tmp/short_url.sock;
        uwsgi_param UWSGI_PYHOME [directory to project's virtualenv]; 
        uwsgi_param UWSGI_CHDIR [directory to project];
        uwsgi_param UWSGI_SCRIPT uwsgi_server:app;
  }
}
```
Notice that every directory shoud use absolute path.


## Python Package Requirement
* [Redis](https://github.com/andymccurdy/redis-py)
* [Flask](http://flask.pocoo.org/)
* [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/)
* [pybase62](https://github.com/suminb/base62)

### Package Installation
Setup the virtualenv.
```
$ virtualenv env
```
Start the virtualenv.
```
$ source env/bin/activate
```
Install relative package.
```
$ pip install requirement.txt
```

## Start the Server
### 1. Start Redis Sever
Open another termial window, change directory to project and activate the redis server with:
```
$ redis-server
```
The database dump file will auto save to the current directory.

### 2. Start uWSGI Interface
In virtualenv, activate with:
```
$ uwsgi --ini uwsgi.ini
```
You can modify the uWSGI interface configuration with `uwsgi.ini`.
The `.ini` file should looks like this.
```
[uwsgi]

# uWSGI socket connect to nginx
socket=/tmp/short_url.sock
chmod-socket = 666

# project direction
chdir=[directory to project]

# virtual environment direction
home=[directory to project's virtualenv]

# Specify start script
wsgi-file=[directory to uwsgi_server.py]
callable=app

# uWSGI server parameter
master=true
processes=4
enable-threads = true
thunder-lock = true
die-on-term = true
```
Notice that every directory shoud use absolute path.

### 3. Activate Nginx Service
After finished the Nginx configuration, activate with:
```
$ sudo service nginx restart
```
Now Nginx server will start to listen port 80's request and forward to uWSGI interface.

## Usage
### Short a URL
```
$ curl http://[server_name]/shortURL -d "[url]"
```
This will give you a short url.

### Short a URL with Specific key
```
$ curl http://[server_name]/specify/[your key] -d "[url]"
```
This will give you a short which with your specify url key.

Example.
```
$ curl http://jason88012.ddns.net/shortURL -d "http://google.com"
{
  "State": "Sucess", 
  "short_url": "http://jason88012.ddns.net/3a7mo0O"
}

$ curl http://jason88012.ddns.net/specify/abcde -d "http://google.com"
{
  "State": "Sucess", 
  "short_url": "http://jason88012.ddns.net/abcde"
}
```

