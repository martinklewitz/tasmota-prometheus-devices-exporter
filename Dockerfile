FROM python:alpine
RUN apk add --no-cache tini

ADD exporter.py /app/exporter.py
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
  rm -rf /tmp/requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python" , "/app/exporter.py"]