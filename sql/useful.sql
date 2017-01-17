delete from filter_value
where galaxy_id in (select galaxy_id from galaxy where run_id <= 10);

delete from result
where galaxy_id in (select galaxy_id from galaxy where run_id <= 10);

delete from galaxy where run_id <= 10;

optimize table filter_value, result, galaxy;
