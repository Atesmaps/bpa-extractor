/* SQL script for create table with BPA reports history */
CREATE TABLE bpa_history (
	id serial PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
	zone_name VARCHAR (80) NOT NULL,
	zone_id VARCHAR (10) NOT NULL,
    danger_level INT NOT NULL,
    bpa_date DATE NOT NULL
);
