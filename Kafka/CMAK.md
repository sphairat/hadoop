Cluster Manager for Apache Kafka �� Yahoo � ������ ���������� ����������, �������� � ��������������, � ����� ���������� ������� ����������� ��������, ���������� � ������������. ����� CMAK ��������� Yahoo Kafka Manager, �� � ������ 2020 ���� ��� ������������. ������� ������ ��������� ��� ����������� Verizon Media � ����������. �������� ��� ��������� �������� � Github

**��������� CMAK � Docker**

1. ������ �����

```bash
docker pull hlebalbau/kafka-manager
```

1. ��������� �����

```bash
docker run -d \
-p 29000:9000  \
-e ZK_HOSTS="IP:2181" \
hlebalbau/kafka-manager:latest
```

1. ������ ������: 

    *Yikes! KeeperErrorCode = Unimplemented for /kafka-manager/mutex*

    [�������](https://github.com/yahoo/CMAK/issues/731#issuecomment-643880544): �� ����� zookeeper ���������� ��������� ������ *zkCli.sh*

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