#!/bin/bash
# Slice plates of N identical Specimen 04 articles (N=1..9) plus the real
# 9-article Sobol batch split over two plates. Manual layout, no --arrange.
cd /tmp/slicing
for N in 1 2 3 4 5 6 7 8 9; do
  python3 build_plate.py $N single_$N.3mf
  mkdir -p out_$N
  timeout 1200 ./squashfs-root/AppRun --slice 0 --debug 1 --outputdir out_$N single_$N.3mf > log_$N.txt 2>&1
  echo "N=$N exit=$? gcodes: $(ls out_$N/*.gcode 2>/dev/null | tr '\n' ' ')"
done
# plate A: spec5, spec2, spec3 front row; spec1, spec8 second row
python3 build_group.py all9_plateA.3mf "18:78:64,9:192:64,12:286:64,6:105:178,27:215:178"
mkdir -p out_plateA
timeout 1800 ./squashfs-root/AppRun --slice 0 --debug 1 --outputdir out_plateA all9_plateA.3mf > log_plateA.txt 2>&1
echo "plateA exit=$? gcodes: $(ls out_plateA/*.gcode 2>/dev/null | tr '\n' ' ')"
# plate B: spec6, spec0, spec7 front row; spec4 second row
python3 build_group.py all9_plateB.3mf "21:75:64,3:170:64,24:263:64,15:160:178"
mkdir -p out_plateB
timeout 1800 ./squashfs-root/AppRun --slice 0 --debug 1 --outputdir out_plateB all9_plateB.3mf > log_plateB.txt 2>&1
echo "plateB exit=$? gcodes: $(ls out_plateB/*.gcode 2>/dev/null | tr '\n' ' ')"
echo DONE
