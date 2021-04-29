#!/bin/sh
export FLASK_APP=app.main
docker run -d -v "$1":/var/lib/mysql -e MYSQL_ROOT_PASSWORD=test -e MYSQL_DATABASE=FPL -e MYSQL_USER=fpltest -e MYSQL_PASSWORD=testpass -p 4000:3306 mysql:8.0
export DB_HOST=localhost:4000
export DB_USERNAME=fpltest
export DB_PASS=testpass
