CREATE TABLE words (
	word_id SERIAL NOT NULL,
	"word" VARCHAR(255) NOT NULL,
	PRIMARY KEY (word_id)
);

CREATE TABLE dates (
	date_id SMALLSERIAL NOT NULL,
	"date" DATE NOT NULL,
	PRIMARY KEY (date_id)
);

CREATE TABLE institutes (
	institute_id SMALLSERIAL NOT NULL,
	"institute" VARCHAR(255) NOT NULL,
	PRIMARY KEY (institute_id)
);

CREATE TABLE entries (
	entry_id SERIAL NOT NULL,
	word_id integer REFERENCES words,
	word_count INTEGER NOT NULL,
	date_id SMALLINT REFERENCES dates,
	institute_id SMALLINT REFERENCES institutes,
	PRIMARY KEY (entry_id)
);
