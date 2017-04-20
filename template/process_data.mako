#!/bin/bash
# Use MagPhys to process one pixel
#
OVERALL_START=$(date +%s)
echo task,actual,expected,redshift > timings.csv

export magphys=${ dir_magphys }/magphys
export scratch=${ XX }
cd $scratch

export FILTERS=${ dir_magphys }/runs/${ run_name }/FILTERBIN.RES
export OPTILIB=$magphys/OptiLIB_${ magphys_model }.bin
export OPTILIBIS=$magphys/OptiLIBis_${ magphys_model }.bin
export IRLIB=$magphys/InfraredLIB.bin
export USER_FILTERS=${ dir_magphys }/runs/${ run_name }/filters.dat
export USER_OBS=$scratch/mygals.dat

/bin/rm -f *.lbr

% for redshift_group in ${ redshift_groups }:

# Timing information
NOW=$(date +%s)
DIFF=$(echo "$NOW - $OVERALL_START" | bc)
echo '----'
echo Wall time actual $DIFF seconds
echo Wall time expected ${ 2 } seconds
echo '----'
echo way_get_optic_colors,$DIFF,${ 2 },${ XX } >> timings.csv

# Create the models
echo "{0}
70.0,0.3,0.7" > redshift

echo N | $magphys/make_zgrid

START=$(date +%s)

cat redshift | $magphys/get_optic_colors

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo get_optic_colors took $DIFF seconds
echo get_optic_colors,$DIFF,${4},${XX} >> timings.csv

# Timing information
NOW=$(date +%s)
DIFF=$(echo "$NOW - $OVERALL_START" | bc)
echo '----'
echo Wall time actual $DIFF seconds
echo Wall time expected ${ 3 } seconds
echo '----'
echo way_${ 1 },$DIFF,${ 3 },${ XX } >> timings.csv

START=$(date +%s)

cat redshift | $magphys/${1}

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo ${ 1 } took $DIFF seconds
echo ${ 1 },$DIFF,${ 5 },${ AA } >> timings.csv

# Next galaxies
echo "# Header" > mygals.dat
% for galaxy in ${ redshift_group.galaxies }:
echo ${ galaxy.line } >> mygals.dat
% endfor

% endfor

END=$(date +%s)
DIFF=$(echo "$END - $OVERALL_START" | bc)
echo '------------'
echo Total wall time actual $DIFF seconds
echo Total wall time expected ${ 0 } seconds
echo '------------'
echo total,$DIFF,${ 0 },NaN >> timings.csv
