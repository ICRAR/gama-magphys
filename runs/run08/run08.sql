USE gama_sed;
INSERT INTO run (run_id, description) VALUES (8, 'Run based on the file 24 bands using LAMBAR and bc03');

INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'FUV'		   , 0.152	, 46  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'NUV'		   , 0.231	, 47  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'u'		     , 0.3798	, 75  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'B'		     , 0.445	, 76  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'V'		     , 0.551	, 77  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'g'		     , 0.4780	, 78  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'r'		     , 0.6295	, 79  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'i'		     , 0.7641	, 80  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'z'		     , 0.9037	, 81  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'Y'		     , 1.02		, 158 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'J'		     , 1.25		, 159 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'H'		     , 1.64		, 160 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'K'		     , 2.15		, 161 );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'IRAC1'		 , 3.56		, 28  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'IRAC2'		 , 4.51		, 29  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'IRAC3'		 , 5.76		, 30  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'IRAC4'		 , 8.00		, 31  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'MIPS24'	 , 24.	  , 32  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'MIPS70'	 , 70.	  , 33  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'PACS100'	 , 100.		, 51  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'PACS160'	 , 160.		, 52  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'SPIRE250' , 250.		, 42  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'SPIRE350' , 350.		, 43  );
INSERT INTO filter (run_id, name, eff_lambda, filter_number) VALUES (8, 'SPIRE500' , 500.		, 44  );



