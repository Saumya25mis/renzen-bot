# context from docker compose up will be from root `src`

FROM python:3.8.3-slim-buster

ENV AP /data/app
ENV PYTHONUNBUFFERED=1

ADD . $AP/
WORKDIR $AP

# install requirements
RUN pip3 install --no-cache-dir -r global-requirements.txt
RUN pip3 install -e .

RUN ["chmod", "+x", "src/bot/bot_wrapper_script.sh"]

ENTRYPOINT ["src/bot/bot_wrapper_script.sh"]
