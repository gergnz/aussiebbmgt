create table dpuportstatusresults(
	id INT,
	result varchar(10),
	syncState varchar(10),
	operationalState varchar(10),
	reversePowerState varchar(10),
	linerateup NUMERIC,
	lineratedown NUMERIC,
	completed_at TEXT
);

create table speedtestresults(
	id INT,
	server varchar(10),
	latencyMs NUMERIC,
	downloadSpeedKbps NUMERIC,
	uploadSpeedKbps NUMERIC,
	date TEXT
);

create table settings(
  key varchar(256) PRIMARY KEY,
  value varchar(256)
)
