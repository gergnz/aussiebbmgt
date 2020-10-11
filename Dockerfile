FROM python:3-alpine3.12
#ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
#ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
## Chrome's sandboxing doesn't work in a Docker container - but that probably doesn't matter,
## since the Docker container is itself a kind of sandbox.
#ENV CHROME_EXTRA_FLAG="--no-sandbox"
RUN apk update && \
    apk add chromium chromium-chromedriver nodejs npm curl && \
    adduser -D -u 1000 aussiebb && \
    mkdir -p /app && \
    mkdir -p /srv
#COPY . /app/
COPY . /srv
WORKDIR /srv
RUN apk --no-cache add grep && \
	curl --silent "http://worldtimeapi.org/api/ip" --stderr - | grep -oP '(?<=timezone":").*(?=","unixtime)' > /app/timezone
RUN apk add tzdata && \
	LOCALEZONE=$(cat /app/timezone) && \
	ln -snf /usr/share/zoneinfo/$LOCALEZONE /etc/localtime && \
	echo $LOCALEZONE > /etc/timezone
#RUN npm install --unsafe-perm -g && chown -R 1000 /app
RUN pip install -r requirements.txt
USER 1000

ENV FLASK_APP=aussiebbmgt.py
ENV FLASK_ENV=development

EXPOSE 5000/tcp

CMD flask run --host 0.0.0.0
