#!/bin/sh
export FLASK_APP=app.main
docker run -d -v "$1":/var/lib/mysql -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=FPL -e MYSQL_USER=fpluser -e MYSQL_PASSWORD=fplpass -p 4000:3306 mysql:8.0
export DB_HOST=localhost:4000
export DB_USERNAME=fpluser
export DB_PASS=fplpass
