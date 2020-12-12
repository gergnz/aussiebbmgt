#!/usr/bin/env bash
if [ ! -f /data/aussiebbmgt.db ]
then
  cp /srv/empty.db /data/aussiebbmgt.db
fi

/srv/runforever.py
