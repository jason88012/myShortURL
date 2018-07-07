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
$ make test
$ sudo make install
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
Assume your public IP is `1.2.3.4` and the project is in `/home/myShortUrl`, Here is the configuration file `default` should looks like.
```
server { 
    listen 80 default;
    server_name 1.2.3.4;
    location / { 
        include uwsgi_params;
        uwsgi_pass unix:/tmp/short_url.sock;
        uwsgi_param UWSGI_PYHOME /home/myShortUrl/env; 
        uwsgi_param UWSGI_CHDIR /home/myShortUrl;
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
$ virtualenv -p python3 env
```
Start the virtualenv.
```
$ source env/bin/activate
```
Install relative package.
```
$ pip install -r requirement.txt
```

## Start the Server
### 1. Change Server Prefix
Chane the `conf.py`, add your `server_name` in it.
```
$ nano util/conf.py
```

Ex. Assume your public ip is `1.2.3.4`
```
SERVER_URL_PREFIX = os.getenv("SERVER_URL_PREFIX", "1.2.3.4")
```

### 2. Start Redis Sever
Open another termial window, change directory to project and activate the redis server with:
```
$ redis-server
```
The database dump file will auto save to the current directory.

### 3. Start uWSGI Interface
In virtualenv, activate with:
```
$ uwsgi --ini uwsgi.ini
```
You can modify the uWSGI interface configuration with `uwsgi.ini`.
Assume your project is in `/home/myShortUrl`, the file should looks like this:
```
[uwsgi]

# uWSGI socket connect to nginx
socket=/tmp/short_url.sock
chmod-socket = 666

# project direction
chdir=/home/myShortUrl

# virtual environment direction
home=/home/myShortUrl/env

# Specify start script
wsgi-file=/home/myShortUrl/uwsgi_server.py
callable=app

# uWSGI server parameter
master=true
processes=4
enable-threads = true
thunder-lock = true
die-on-term = true
```
Notice that every directory shoud use absolute path.

### 4. Activate Nginx Service
Activate Nginx with:
```
$ sudo service nginx restart
```
Now Nginx server will start to listen port 80 and forward request to uWSGI interface.

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
$ curl http://1.2.3.4/shortURL -d "http://google.com"
{
  "State": "Sucess", 
  "short_url": "http://1.2.3.4/3a7mo0O"
}

$ curl http://1.2.3.4/specify/abcde -d "http://google.com"
{
  "State": "Sucess", 
  "short_url": "http://1.2.3.4/abcde"
}
```

