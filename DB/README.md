# Database Container Setup

Run mysql base image container in the background.
```
docker run --name ["container_name"] -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:8.0
```

Move the ```schema.sql``` file to the container.
```
docker cp hoge.sql [cotaier-id]:/schema.sql
```

Login into docker
```
docker ps
docker exec -it [container-id] /bin/bash
```

Login into  mysql
```
mysql -u root -p
```

Run sql script
```
source schema.sql
```