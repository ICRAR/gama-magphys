DROP SCHEMA IF EXISTS gama_sed;
CREATE SCHEMA gama_sed;
USE gama_sed;

CREATE TABLE parameter_name (
  parameter_name_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
  name              VARCHAR(100) NOT NULL,
  create_time       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  INDEX (name)
) CHARACTER SET utf8 ENGINE=InnoDB;

CREATE TABLE run (
  run_id      BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  description VARCHAR(1000) NOT NULL,
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8 ENGINE=InnoDB;

CREATE TABLE galaxy (
  galaxy_id   BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  run_id      BIGINT UNSIGNED NOT NULL,
  gama_id     VARCHAR(128) NOT NULL,
  redshift    DECIMAL(10, 7) NOT NULL,
  i_sfh       DOUBLE,
  i_ir        DOUBLE,
  chi2        DOUBLE,
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (run_id) REFERENCES run(run_id),

  INDEX (redshift),
  INDEX (gama_id)
) CHARACTER SET utf8 ENGINE=InnoDB;

CREATE TABLE filter (
  filter_id     BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  run_id        BIGINT UNSIGNED NOT NULL,
  name          VARCHAR(30) NOT NULL,
  eff_lambda    DECIMAL(10, 4) NOT NULL,
  filter_number SMALLINT NOT NULL,
  create_time   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (run_id) REFERENCES run(run_id),

  INDEX (filter_number),
  INDEX (name)
) CHARACTER SET utf8 ENGINE=InnoDB;

CREATE TABLE filter_value (
  filter_values_id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  filter_id        BIGINT UNSIGNED NOT NULL,
  galaxy_id        BIGINT UNSIGNED NOT NULL,
  flux             DOUBLE NOT NULL,
  sigma            DOUBLE NOT NULL,
  flux_bfm         DOUBLE NOT NULL,
  create_time      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (filter_id) REFERENCES filter(filter_id),
  FOREIGN KEY (galaxy_id) REFERENCES galaxy(galaxy_id),

  INDEX (galaxy_id, filter_id)
) CHARACTER SET utf8 ENGINE=InnoDB;

CREATE TABLE result (
  parameter_result_id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  galaxy_id           BIGINT UNSIGNED NOT NULL,
  parameter_name_id   BIGINT UNSIGNED NOT NULL,
  best_fit            DOUBLE,
  percentile2_5       DOUBLE NOT NULL,
  percentile16        DOUBLE NOT NULL,
  percentile50        DOUBLE NOT NULL,
  percentile84        DOUBLE NOT NULL,
  percentile97_5      DOUBLE NOT NULL,
  create_time         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (galaxy_id) REFERENCES galaxy(galaxy_id),
  FOREIGN KEY (parameter_name_id) REFERENCES parameter_name(parameter_name_id),

  INDEX (galaxy_id, parameter_name_id),
  INDEX (best_fit),
  INDEX (percentile50)
) CHARACTER SET utf8 ENGINE=InnoDB;

INSERT INTO parameter_name (parameter_name_id, name) VALUES (0,  'f_mu (SFH)');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (1,  'f_mu (IR)');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (2,  'mu parameter');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (3,  'tau_V');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (4,  'sSFR_0.1Gyr');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (5,  'M(stars)');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (6,  'Ldust');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (7,  'T_C^ISM');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (8,  'T_W^BC');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (9,  'xi_C^tot');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (10, 'xi_PAH^tot');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (11, 'xi_MIR^tot');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (12, 'xi_W^tot');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (13, 'tau_V^ISM');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (14, 'M(dust)');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (15, 'SFR_0.1Gyr');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (16, 'metalicity Z/Zo');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (17, 'tform');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (18, 'gamma');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (19, 'tlastb');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (20, 'agem');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (21, 'ager');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (22, 'sfr16');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (23, 'sfr17');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (24, 'sfr18');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (25, 'sfr19');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (26, 'sfr29');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (27, 'fb16');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (28, 'fb17');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (29, 'fb18');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (30, 'fb19');
INSERT INTO parameter_name (parameter_name_id, name) VALUES (31, 'fb29');

