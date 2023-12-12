# Dockerfile

FROM grafana/grafana-oss:latest as grafana

# Đặt thư mục làm việc
WORKDIR /app

USER root

# Sao chép mã nguồn vào thư mục làm việc
COPY . /app
RUN rm /etc/grafana/grafana.ini && ln -s /app/grafana.ini /etc/grafana/grafana.ini
RUN chmod +x /app/entrypoint.sh
RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing python3 py3-pip

RUN pip install -r /app/requirements.txt

USER grafana

# Expose port cho Grafana
EXPOSE 3000

# Expose port cho FastAPI
EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
