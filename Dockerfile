FROM python:2-alpine

WORKDIR mdv
COPY . .
RUN ./setup.py install

ENTRYPOINT [ "mdv" ]
