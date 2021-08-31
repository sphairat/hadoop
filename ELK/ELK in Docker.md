ELK разворачивался в Docker на VM поднятом на PVE. Сервер *swift.* Для удобства отладки поднят контейнер Portainer на порту 9000

## Создание рабочих папок для каждого из компонентов ELK

```bash
user@swift:~$ mkdir elk #cоздаём папку проекта
user@swift:~$ cd elk #переходим в папку и создаём там подпапки для компонентов ELK
user@swift:~/elk$ mkdir -p elasticsearch/{config,storage}
user@swift:~/elk$ mkdir -p logstash/{config,pipeline,logfile}
user@swift:~/elk$ mkdir -p kibana/config
```

## Использование переменных

Для использования переменной ELK_VERSION cоздать в корне папки *ELK* файл .env c переменной и её значением, в моём случае версия 7.14.0

```bash
user@swift:~/elk$ vi .env
user@swift:~/elk$
user@swift:~/elk$ cat .env
ELK_VERSION=7.14.0
user@swift:~/elk$
```

## Настройка Elasticsearch

Dockerfile для Elasticsearch в папке ./elk/elasticsearch/

```bash
ARG ELK_VERSION
FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_VERSIO33N}
```

elasticsearch.yml для Elasticsearch в папке ./elk/elasticsearch/config/

```yaml
[cluster.name](http://cluster.name/): "elk-cluster"
network.host: 0.0.0.0
discovery.zen.minimum_master_nodes: 1
discovery.type: single-node
logger.level: DEBUG
```

## Настройка Logstash

Dockerfile для Logstash ./elk/logstash/

```bash
ARG ELK_VERSION
FROM docker.elastic.co/logstash/logstash-oss:${ELK_VERSION}
RUN logstash-plugin install logstash-input-beats
USER root
RUN mkdir -p /home/logstash/logfile
RUN chown -R logstash:logstash /home/logstash/logfile/
```

logstash.yml для Logstash в папке ./elk/logstash/config/

```yaml
http.host: "0.0.0.0"
path.config: /usr/share/logstash/pipeline
```

cоздаём файл конвейра (pipeline) ./logstash/pipeline/01.apache.conf

```bash
input {
beats {
port => 5000
type => apache
}
}
filter {
if [type] == "apache" {
grok {
match => { "message" => "%{COMBINEDAPACHELOG}" }
}
}
}
output {
if [type] == "apache" {
elasticsearch {
hosts => ["[http://elasticsearch:9200](http://elasticsearch:9200/)"]
index => "apache-combined-%{+YYYY.MM.dd}"
}
stdout { codec => rubydebug }
}
}
```

## Настройка Kibana

Dockerfile для Kibana ./elk/kibana/

```bash
ARG ELK_VERSION
FROM docker.elastic.co/kibana/kibana:${ELK_VERSION}
```

kibana.yml по пути ./elk/kibana/config

```bash
[server.name](http://server.name/): kibana
server.host: "0.0.0.0"
server.basePath: "/kibana"
elasticsearch.hosts: [http://elasticsearch:9200](http://elasticsearch:9200/)
apm_oss.enabled: true
xpack.apm.enabled: true
xpack.apm.ui.enabled: true
logging.dest: stdout
```

## Создание контейнеров для компонентов через docker-compose

Создать файл docker-compose.yml 

```yaml
version: '3'
services:
  elasticsearch:
     container_name: elasticsearch
     build:
        context: elasticsearch
        args:
           ELK_VERSION: ${ELK_VERSION}
     volumes:
       - ./elasticsearch/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
       - ./elasticsearch/storage:/usr/share/elasticsearch/data:rw

     ports:
       - "9200:9200"
       - "9300:9300"

     environment:
       - ELASTIC_PASSWORD="password"
       - ES_JAVA_OPTS=-Xmx256m -Xms256m
       - discovery.type=single-node
       - bootstrap.memory_lock=true
       - http.cors.allow-origin=*

     ulimits:
       memlock:
         soft:  -1
         hard:  -1
     networks:
       - elk

  logstash:
     container_name: logstash
     build:
        context: logstash
        args:
          ELK_VERSION: $ELK_VERSION
     volumes:
       - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml
       - ./logstash/pipeline:/usr/share/logstash/pipeline
     ports:
       - "5000:5000"
     networks:
       - elk
     depends_on:
       - elasticsearch
  kibana:
     container_name: kibana
     build:
        context: kibana/
        args:
          ELK_VERSION: ${ELK_VERSION}
     volumes:
       - ./kibana/config/:/usr/share/kibana/config
     ports:
       - "5601:5601"
     environment:
       - ELASTICSEARCH_PASSWORD="password"
     networks:
       - elk
     depends_on:
       - elasticsearch

networks:
   elk:
     driver: bridge
```

собрать/запустить контейнеры

```bash
user@swift:~/elk$ docker-compose up -d elasticsearch
user@swift:~/elk$ docker-compose up -d logstash
user@swift:~/elk$ docker-compose up -d kibana
```

## Nginx как реверс-прокси для подключения к elasticsearch и kibana

Необходимо поднять Nginx, который будет принимать подключения и проксировать их в kibana или elasticsearch

Создать папку для Nginx:

```bash
user@swift:~/elk$ mkdir -p nginx/{public,data,etc}
```

Создать файл ./elk/nginx/public/index.html 

```bash
user@swift:~/elk$ vi nginx/public/index.html
<html>
Follow to White Rabbit
</html>
```

Создать файл конфигурации nginx

```bash
user@swift:~/elk$ vi ~/docker-elk/nginx/etc/nginx.conf
worker_processes 4;   
events {
              worker_connections 1024;
}

http {

server {
       listen 80;
       server_name 172.17.17.33 ; *#IP-адрес swift*

       location / {
       root /usr/share/nginx/html;
       index index.html;
       }

       location /elastic/ {
       proxy_pass http://elasticsearch:9200/;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header Host $http_host;
       auth_basic "Restricted Content";
       auth_basic_user_file /etc/nginx/.htpasswd.user;
       }

       location /kibana/ {
       proxy_pass http://kibana:5601/;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header Host $http_host;
       rewrite ^/kibana/(.*)$ /$1 break;
       auth_basic "Restricted Content";
       auth_basic_user_file /etc/nginx/.htpasswd.user;
       }
     }
}
```

Для доступа в Kibana необходимо установить. Создание логин/пароля для авторизации в Kibana

```bash
sudo apt install apache2-utils
user@swift:~/elk/nginx/etc$ htpasswd -c .htpasswd.user admin
New password: #пароль будет использовать после при открытии страницы с Kibana
Re-type new password:
Adding password for user admin
user@swift:~/elk/nginx/etc$
```

Для создание контейнера с Nginx через docker-compose необходимо в файл ./elk/docker-compose.yml добавить **данные** для Nginx контейнера:

```yaml
version: '3'
services:
  elasticsearch:
     container_name: elasticsearch
     build:
        context: elasticsearch
        args:
           ELK_VERSION: 7.14.0
     volumes:
       - ./elasticsearch/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
       - ./elasticsearch/storage:/usr/share/elasticsearch/data:rw

     ports:
       - "9200:9200"
       - "9300:9300"

     environment:
       - ELASTIC_PASSWORD="password"
       - ES_JAVA_OPTS=-Xmx256m -Xms256m
       - discovery.type=single-node
       - bootstrap.memory_lock=true
       - http.cors.allow-origin=*

     ulimits:
       memlock:
         soft:  -1
         hard:  -1
     networks:
       - elk
  logstash:
     container_name: logstash
     build:
        context: logstash
        args:
          ELK_VERSION: $ELK_VERSION
     volumes:
       - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml
       - ./logstash/pipeline:/usr/share/logstash/pipeline
     ports:
       - "5000:5000"
     networks:
       - elk
     depends_on:
       - elasticsearch
  kibana:
     container_name: kibana
     build:
        context: kibana/
        args:
          ELK_VERSION: 7.14.0
     volumes:
       - ./kibana/config/:/usr/share/kibana/config
     ports:
       - "5601:5601"
     environment:
       - ELASTICSEARCH_PASSWORD="password"
     networks:
       - elk
     depends_on:
       - elasticsearch
  **nginx:
     image: nginx:alpine
     container_name: nginx
     volumes:
       - './nginx/etc/nginx.conf:/etc/nginx/nginx.conf:ro'
       - './nginx/public:/usr/share/nginx/html:ro'
       - './nginx/etc/.htpasswd.user:/etc/nginx/.htpasswd.user:ro'
     links:
       - elasticsearch
       - kibana
     depends_on:
       - elasticsearch
       - kibana
     ports:
       - '80:80'
     networks:
       - elk** 
networks:
   elk:
     driver: bridge
```

Создать/поднять контейнер с nginx:

```yaml
user@swift:~/elk$ docker-compose up -d nginx
```

Идём к Portainer и наблюдаем все поднятые контейры:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/a0d1fbd5-eac1-4bf6-bac3-63f716637c80/Untitled.png)

Открываем http://172.17.17.33/kibana. Вводим ранее созданные данные для nginx (admin/password). 

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/bc26fe8c-5c01-411b-a3e6-ee56d6c2ca3a/Untitled.png)

ELK стек готов к получению данных.

Можно при помощи клиента передачи логов Filebeat. Установка filebeat:

```
user@swift:~/elk$ curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.14.0-linux-x86_64.tar.gz
user@swift:~/elk$ tar xzvf filebeat-7.14.0-linux-x86_64.tar.gz
```

Правим конфиг

```yaml
$ vi /etc/filebeat/filebeat.yml

filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/apache2/*.log
...
...
output.logstash:
  # The Logstash hosts
  hosts: ["172.17.17.33:5000"] #IP-адрес сервера swift
```

Запускаем

```yaml
user@swift:~/docker-elk/filebeat-7.14.0-linux-x86_64$ ./filebeat -e -d "*"
```

Идем в Kibana, добавляем новый индекс **Stack Management -> -> Index Patterns.** Создаём Index pattern по маске **apache-combined-***

После идём в раздел Discover
