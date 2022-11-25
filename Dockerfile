FROM python:3.8.3-slim-buster
ENV AP /data/app

ADD . $AP/
WORKDIR $AP

# install requirements
RUN pip3 install --no-cache-dir -r src/requirements.txt

# install module
RUN pip3 install -e .

RUN ["chmod", "+x", "scripts/my_wrapper_script.sh"]
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/scripts/my_wrapper_script.sh"]