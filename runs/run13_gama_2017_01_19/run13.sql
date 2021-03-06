USE gama_sed;
INSERT INTO run (run_id, description) VALUES (13, 'Run based on the file GAMA and bc03 2017-01-19');

INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'fuv'     , 0.1535, 123 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'nuv'     , 0.2301, 124 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'u'       , 0.3557, 115 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'g'       , 0.4702, 116 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'r'       , 0.6175, 117 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'i'       , 0.7491, 118 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'z'       , 0.8946, 119 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'Z'       , 0.8800, 318 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'Y'       , 1.0213, 319 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'J'       , 1.2525, 320 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'H'       , 1.6433, 321 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'K'       , 2.1503, 322 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'WISEW1'  , 3.4   , 280 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'WISEW2'  , 4.6   , 281 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'WISEW3'  , 12.0  , 282 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'WISEW4'  , 22.0  , 283 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'PACS100' , 100.0 , 442 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'PACS160' , 160.0 , 443 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'SPIRE250', 250.0 , 444 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'SPIRE350', 350.0 , 445 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (13, 'SPIRE500', 500.0 , 446 );
