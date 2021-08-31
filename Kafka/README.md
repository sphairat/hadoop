### Открытие консоли в контейнере с Sandbox-hdp. Перемещение в папку с Kafka.

```bash
[user@falcon ~]$ docker exec -it sandbox-hdp /bin/bash
[root@sandbox-hdp /]#
[root@sandbox-hdp /]#
[root@sandbox-hdp /]# cd usr
[root@sandbox-hdp usr]# cd hdp/current/kafka-broker/bin
```

### Cоздание топика *message* c фактором репликации 1 и тримя партициями

```bash
[root@sandbox-hdp bin]# ./kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 3 --topic messages
```

### Проверка создания топика

```bash
[root@sandbox-hdp bin]# ./kafka-topics.sh --list --zookeeper localhost:2181
ATLAS_ENTITIES
ATLAS_HOOK
__consumer_offsets
messages
```

### Открытие в одной консоли продюсера и запись сообщений в топик *message*

```bash
[root@sandbox-hdp bin]# ./kafka-console-producer.sh --broker-list [sandbox-hdp.hortonworks.com:6667](http://sandbox-hdp.hortonworks.com:6667/) --topic messages
>OneMessage
>TwoMessage
>ThreeMessage
```

### Открытие в другой консоли потребителя и чтение сообщений от продюсера в топике *message*

```bash
[root@sandbox-hdp bin]# ./kafka-console-consumer.sh --zookeeper [sandbox-hdp.hortonworks.com:2181](http://sandbox-hdp.hortonworks.com:2181/) --topic messages --from-beginning
>OneMessage
>TwoMessage
>ThreeMessage
```

### Запуск файла [message.py] и чтение результата в топике message

```bash
[root@sandbox-hdp kafka]# cat message.py
#!/usr/bin/python2.7

from time import sleep
from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['sandbox-hdp.hortonworks.com:6667'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

for e in range(10):
    data = {'number' : e}
    producer.send('message', value=data)
    sleep(5)

[root@sandbox-hdp bin]# ./kafka-console-consumer.sh --zookeeper [sandbox-hdp.hortonworks.com:2181](http://sandbox-hdp.hortonworks.com:2181/) --topic message --from-beginning
Using the ConsoleConsumer with old consumer is deprecated and will be removed in a future major release. Consider using the new consumer by passing [bootstrap-server] instead of [zookeeper].
{"number": 0}
{"number": 1}
{"number": 5}
{"number": 6}
{"number": 7}
{"number": 9}
```
