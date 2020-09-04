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
