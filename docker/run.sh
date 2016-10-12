#!/bin/bash
PORT=8080
if [ $TORNADO_PORT  ]; then
    PORT=$TORNADO_PORT
fi
sed -Ei 's/\$PORT/'$PORT'/' /etc/supervisord.d/tornado.ini
supervisord -n -c /etc/supervisord.conf
