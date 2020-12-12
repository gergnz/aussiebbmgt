#!/usr/bin/env bash
if [ ! -f /srv/aussiebbmgt.db ]
then
  cp /srv/empty.db /srv/aussiebbmgt.db
fi

/srv/runforever.py
