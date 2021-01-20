DROP TABLE IF EXISTS vacatures_relevant_keywords;
DROP TABLE IF EXISTS vacatures_lemma_relevant_keywords;
DROP TABLE IF EXISTS vacatures_single_relevant_keywords;
DROP TABLE IF EXISTS vacatures_lemma_single_relevant_keywords;
DROP TABLE IF EXISTS vacatures_keywords;
DROP TABLE IF EXISTS vacatures_lemma_Keywords;
DROP TABLE IF EXISTS vacatures_single_keywords;
DROP TABLE IF EXISTS vacatures_lemma_single_keyword;


DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS relevant_keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS lemma_relevant_keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS single_relevant_keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS lemma_single_relevant_keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS lemma_Keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS single_keywords;

DROP TABLE IF EXISTS vacatures;
DROP TABLE IF EXISTS lemma_single_keyword;


CREATE TABLE IF NOT EXISTS vacatures (
    vacature_id SERIAL NOT NULL,
    "vacature_tekst" VARCHAR(100000) NOT NULL,
    PRIMARY KEY (vacature_id)
);


CREATE TABLE relevant_keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_relevant_keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES relevant_keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE lemma_relevant_keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_lemma_relevant_keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES lemma_relevant_keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE single_relevant_keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_single_relevant_keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES single_relevant_keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE lemma_single_relevant_keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_lemma_single_relevant_keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES lemma_single_relevant_keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE lemma_Keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_lemma_Keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES lemma_Keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE single_keywords (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_single_keywords (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES single_keywords,
    PRIMARY KEY (vacature_id, woord_id)
);

CREATE TABLE lemma_single_keyword (;
    woord_id SERIAL NOT NULL,
    "woord" VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (woord_id)
);
CREATE TABLE vacatures_lemma_single_keyword (;
    vacature_id integer REFERENCES vacatures,
    woord_id integer REFERENCES lemma_single_keyword,
    PRIMARY KEY (vacature_id, woord_id)
);