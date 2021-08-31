# Sandbox HDP & Free IPA
**Sandbox HDP
Поднятие FREE-IPA Server в Docker**

скачивание образа ipa-server с [hub.docker.com](http://hub.docker.com/)

```bash
docker pull freeipa/freeipa-server:centos-8
```

создаем папку для хранилища контейнера с free ipa

```bash
[user@falcon ~]$ sudo mkdir -p /opt/dockers/freeipa-data
```

запуск контейнера ipa-server в той же сети что и sandbox-hdp (cde)

```bash
[user@falcon ~]$ sudo docker run --name ipa-server -ti \
-h ipa.test.local \
--sysctl net.ipv6.conf.all.disable_ipv6=0 \
-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
-v /opt/dockers/freeipa-data:/data \
--publish "443:443" \
--publish "389:389" \
--publish "636:636" \
--publish "88:88" \
--publish "88:88/udp" \
--publish "464:464" \
--publish "464:464/udp" \
--network=cda \
freeipa/freeipa-server:centos-8
```

Автозапуск контейнера

```bash
docker update --restart unless-stopped ipa-server
```

идем в запущенный контейнер с IPA-Server и проверяем создание пользователей

```bash
[user@falcon ~]$ docker exec -it ipa-server /bin/bash
```

получаем билет для admin'a, создаём пользователя hadoopadmin и добавляем его в группу admins

```
kinit admin
ipa user-add hadoopadmin --first=Hadoop --last=Admin
ipa group-add-member admins --users=hadoopadmin
ipa passwd hadoopadmin
```

Конфигурим файл krb5.conf на сервере с Sandbox-HDP.  Правим /etc/krb5.conf :

```
default_ccache_name = KEYRING:persistent:%{uid}
```

на

```
default_ccache_name = FILE:/tmp/krb5cc_%{uid}
```

Для созданного пользователя hadoopadmin создаем группу ambari-managed-principal

```
[root@ipa /]# ipa group-add ambari-managed-princinal
--------------------------------------
Added group "ambari-managed-princinal"
--------------------------------------
  Group name: ambari-managed-princinal
  GID: 503600005
[root@ipa /]# ipa group-add-member admins --users=hadoopadmin
  Group name: admins
  Description: Account administrators group
  GID: 503600000
  Member users: admin, hadoopadmin
-------------------------
Number of members added 1
-------------------------

```

Логинимся под пользователем и меняем ему пароль, как того просит система

```
[root@ipa /]# kinit hadoopadmin
Password for hadoopadmin@TEST.LOCAL:
Password expired.  You must change it now.
Enter new password:
Enter it again:
```

**Установка JCE на сервер с Sandbox-HDP**

cкачиваем архив, выясняем где установлен Java, распаковываем в ту папку архив, рестартуем Ambari

```bash
[root@sandbox-hdp /]# wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip"
[root@sandbox-hdp /]# whereis java
java: /usr/bin/java /usr/lib/java /etc/java /usr/share/java /usr/share/man/man1/java.1.gz
[root@sandbox-hdp /]# ls -l /usr/bin/java
lrwxrwxrwx. 1 root root 22 Nov 29  2018 /usr/bin/java -> /etc/alternatives/java
[root@sandbox-hdp /]# ls -l /etc/alternatives/java
lrwxrwxrwx. 1 root root 73 Nov 29  2018 /etc/alternatives/java -> /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-0.el7_5.x86_64/jre/bin/java
[root@sandbox-hdp /]# unzip -o -j -q jce_policy-8.zip -d /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-0.el7_5.x86_64/jrelib/security/
[root@sandbox-hdp /]# sudo ambari-server restart
```

На сервер с Ambari, в нашем случае контейнер с Sandbox-HDP ставим ipa-admintools:

```
[root@falcon user]# docker exec -it sandbox-hdp /bin/bash
[root@sandbox-hdp /]# yum -y install rng-tools
[root@sandbox-hdp /]# yum -y install ipa-admintools
```

На сервере с Sandbox-HDP устанавливаем ipa-client. Предварительно проверим что резолвится ipa.test.local в нужный IP-адрес

```bash
[root@sandbox-hdp /]# yum -y install ipa-client
[root@sandbox-hdp /]# ipa-client-install --domain=test.local \
     --server=ipa.test.local\
     --realm=TEST.LOCAL \
     --principal=hadoopadmin@TEST.LOCAL
```

После этого в веб-интерфейсе можно проверить появление в HOST хоста с именем sandbox'a. 

![image](https://user-images.githubusercontent.com/40624766/131553286-43ace8cc-a3c5-4f8e-91bd-83f81e67d1ff.png)

Идем в веб Амбари, Kerberos

![image](https://user-images.githubusercontent.com/40624766/131553356-b646cd2c-50f2-4ecb-9372-97e803517ae4.png)

Cледуем написанному, вводим данные от FREE IPA.
-----------








[https://www.dmosk.ru/miniinstruktions.php?mini=freeipa-centos](https://www.dmosk.ru/miniinstruktions.php?mini=freeipa-centos)

[https://docs.arenadata.io/adh/v1.6.1/SecurityAmbari/config.html](https://docs.arenadata.io/adh/v1.6.1/SecurityAmbari/config.html)

[https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/ambari-authentication-ldap-ad/content/amb_freeIPA_ladap_setup_example.html](https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/ambari-authentication-ldap-ad/content/amb_freeIPA_ladap_setup_example.html)

[https://community.cloudera.com/t5/Community-Articles/Ambari-2-4-Kerberos-with-FreeIPA/ta-p/247653](https://community.cloudera.com/t5/Community-Articles/Ambari-2-4-Kerberos-with-FreeIPA/ta-p/247653)

[https://docs.cloudera.com/HDPDocuments/HDP2/HDP-2.6.1/bk_security/content/_distribute_and_install_the_jce.html](https://docs.cloudera.com/HDPDocuments/HDP2/HDP-2.6.1/bk_security/content/_distribute_and_install_the_jce.html)
