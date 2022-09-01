FROM ubuntu
ENV AP /data/app

# RUN curl -O https://bootstrap.pypa.io/get-pip.py
# RUN python3 get-pip.py --user

WORKDIR /src
ADD src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR $AP
CMD [ "python3", "-m", "bot.py" ]
