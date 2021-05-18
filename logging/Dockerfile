FROM logstash:7.12.1

RUN logstash-plugin install logstash-input-google_pubsub

# Logstash config
COPY fpl-assistant-310814-a6001e5d9dd5.json /usr/share/logstash/config/gcloud-service-account-key.json
COPY pubsub-elastic.conf /usr/share/logstash/config/pubsub-elastic.conf
COPY logstash.yml /usr/share/logstash/config/logstash.yml
