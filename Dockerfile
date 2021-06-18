FROM python:3-alpine

WORKDIR mdv
COPY . .
RUN pip install -e .

ENTRYPOINT [ "mdv" ]
