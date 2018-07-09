# Short URL API Server
A short url API server application installation, configuration and usage tutorial.
In this project, use Ubuntu16.04 as a test OS.
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
(env)$ pip install -r requirement.txt
```

## Start the Server
### 1. Change Server Prefix
Edit the `conf.py`, add your `server_name` in it.
```
$ nano util/conf.py
```

Ex. Assume your public ip is `1.2.3.4`
```
SERVER_URL_PREFIX = os.getenv("SERVER_URL_PREFIX", "http://1.2.3.4/")
```

### 2. Start Redis Sever
Open another termial window, change directory to project and activate the redis server with:
```
$ redis-server
```
The database dump file will auto save to the current directory.

### 3. Start uWSGI Interface
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

Activate uWSGI in virtualenv with:
```
(env)$ uwsgi --ini uwsgi.ini
```

### 4. Activate Nginx Service
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

After configuration, activate Nginx with:
```
$ sudo service nginx restart
```
Now Nginx server will start to listen port 80 and forward request to uWSGI interface.

### 5. Check Firewall
Don't forget to allow your firewall to accept port 80 request.
```
$ sudo ufw allow http
```

## Usage
### Short a URL
```
$ curl http://[server_name]/shortURL -d "[url]"
```
This will give you a short url.

### Short a URL with Specific key
```
$ curl http://[server_name]/specify/[your_key] -d "[url]"
```
This will give you a short which with your specify url key.

### Example
```
$ curl http://1.2.3.4/shortURL -d "http://google.com"
{
  "State": "Sucess", 
  "short_url": "http://1.2.3.4/3a7mo0O"
}

$ curl http://1.2.3.4/specify/abcde -d "http://yahoo.com"
{
  "State": "Sucess", 
  "short_url": "http://1.2.3.4/abcde"
}
```

### Precautions
* A too long url will return error (over 2000 character).
* In general mode, If collision occured, It will replace old one.
* In specify key mode, If use an existed key, It will check the key first and it will give you another usable key if the key is not available.
* In specify key mode, If the input url and specified key will cause [loop condition](http://xuv.be/Looping-url-shortening.html), It will return error.
* Please **DO NOT** use short url service to save your important website. The safety issue please check [this page](https://blog.trendmicro.com/are-shortened-urls-safe/).
