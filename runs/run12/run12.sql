USE gama_sed;
INSERT INTO run (run_id, description) VALUES (12, 'Run based on the file 26 bands using g10 zCosmos and bc03');

INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'FUV'      , 0.152   , 46  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'NUV'      , 0.231   , 47  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'u'        , 0.3798  , 75  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'B'        , 0.445   , 76  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'V'        , 0.551   , 77  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'g'        , 0.4780  , 78  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'r'        , 0.6295  , 79  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'i'        , 0.7641  , 80  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'z'        , 0.9037  , 81  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'Y'        , 1.02    , 158 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'J'        , 1.25    , 159 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'H'        , 1.64    , 160 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'K'        , 2.15    , 161 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'IRAC1'    , 3.56    , 28  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'IRAC2'    , 4.51    , 29  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'IRAC3'    , 5.76    , 30  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'IRAC4'    , 8.00    , 31  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'MIPS24'   , 24.0    , 32  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'MIPS70'   , 70.0    , 33  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'PACS100'  , 100.0   , 51  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'PACS160'  , 160.0   , 52  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'SPIRE250' , 250.0   , 42  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'SPIRE350' , 350.0   , 43  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (12, 'SPIRE500' , 500.0   , 44  );
