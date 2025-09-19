FROM grafana/grafana:9.5.2

ENV GF_AUTH_ANONYMOUS_ENABLED="true"
ENV GF_AUTH_ANONYMOUS_ORG_ROLE="Admin"
ENV GF_AUTH_DISABLE_LOGIN_FORM="true"

COPY docker/devops/grafana/datasources/datasources.yaml /etc/grafana/provisioning/datasources
