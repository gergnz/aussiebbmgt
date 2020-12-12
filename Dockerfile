FROM abb-speedtest:latest
USER 0
RUN apk update && \
    apk add python3 py3-pip bash supervisor && \
    mkdir -p /srv
COPY . /srv
WORKDIR /srv
RUN pip install -r requirements.txt

RUN apk add tzdata && \
	LOCALEZONE=Australia/Sydney && \
	ln -snf /usr/share/zoneinfo/$LOCALEZONE /etc/localtime && \
	echo $LOCALEZONE > /etc/timezone

USER 1000

ENV FLASK_APP=aussiebbmgt.py
ENV TZ=Australia/Sydney

EXPOSE 5000/tcp

ENTRYPOINT []
CMD ["supervisord","-c","/srv/supervisor.conf"]
