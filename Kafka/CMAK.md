Cluster Manager for Apache Kafka от Yahoo – гибкое управление кластерами, топиками и пользователями, а также мониторинг рабочих показателей брокеров, продюсеров и потребителей. Ранее CMAK назывался Yahoo Kafka Manager, но в январе 2020 года был переименован. Сегодня проект находится под управлением Verizon Media и сообщества. Доступен для свободной загрузки с Github

**Установка CMAK в Docker**

1. Пуллим образ

```bash
docker pull hlebalbau/kafka-manager
```

1. Запускаем образ

```bash
docker run -d \
-p 29000:9000  \
-e ZK_HOSTS="IP:2181" \
hlebalbau/kafka-manager:latest
```

1. Поймал ошибку: 

    *Yikes! KeeperErrorCode = Unimplemented for /kafka-manager/mutex*

    [Решение](https://github.com/yahoo/CMAK/issues/731#issuecomment-643880544): на хосте zookeeper необходимо запустить скрипт *zkCli.sh*

    ```
    [root@sandbox-hdp bin]# ./bin/zkCli.sh
    [zk: localhost:2181(CONNECTED) 2] ls /kafka-manager
    [configs, deleteClusters, clusters]
    [zk: localhost:2181(CONNECTED) 3] create /kafka-manager/mutex ""
    Created /kafka-manager/mutex
    [zk: localhost:2181(CONNECTED) 5] create /kafka-manager/mutex/locks ""
    Created /kafka-manager/mutex/locks
    [zk: localhost:2181(CONNECTED) 6] create /kafka-manager/mutex/leases ""
    Created /kafka-manager/mutex/leases
    ```

2. Done!

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/69f76c48-ffef-4f0d-aafe-ec882df6e77c/Untitled.png)