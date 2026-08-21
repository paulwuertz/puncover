
CANnectivity_calls_ASM.json: /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_CANnectivity_14.yaml --export-function-call-to-file CANnectivity_calls_ASM.json

CANnectivity_calls_VCG.json:  /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_CANnectivity_14.yaml --export-function-call-to-file CANnectivity_calls_VCG.json --get-function-calls-from-build-dir-only

CANnectivity_calls_compare.tex: CANnectivity_calls_ASM.json CANnectivity_calls_VCG.json ../scripts/compare_fn_call_files.py
	../scripts/compare_fn_call_files.py CANnectivity_calls_ASM.json CANnectivity_calls_VCG.json CANnectivity_calls_compare.tex
	@echo ../scripts/compare_fn_call_files.py CANnectivity_calls_ASM.json CANnectivity_calls_VCG.json CANnectivity_calls_compare.tex

prusa_coreone_calls_ASM.json: /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_prusa_coreone.yaml --export-function-call-to-file prusa_coreone_calls_ASM.json

prusa_coreone_calls_VCG.json:  /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_prusa_coreone.yaml --export-function-call-to-file prusa_coreone_calls_VCG.json --get-function-calls-from-build-dir-only

prusa_coreone_calls_compare.tex: prusa_coreone_calls_ASM.json prusa_coreone_calls_VCG.json ../scripts/compare_fn_call_files.py
	../scripts/compare_fn_call_files.py prusa_coreone_calls_ASM.json prusa_coreone_calls_VCG.json prusa_coreone_calls_compare.tex
	@echo ../scripts/compare_fn_call_files.py prusa_coreone_calls_ASM.json prusa_coreone_calls_VCG.json prusa_coreone_calls_compare.tex

libresolar_bms_calls_ASM.json: /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_libresolar_bms.yaml --export-function-call-to-file libresolar_bms_calls_ASM.json

libresolar_bms_calls_VCG.json:  /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_libresolar_bms.yaml --export-function-call-to-file libresolar_bms_calls_VCG.json --get-function-calls-from-build-dir-only

libresolar_bms_calls_compare.tex: libresolar_bms_calls_ASM.json libresolar_bms_calls_VCG.json ../scripts/compare_fn_call_files.py
	../scripts/compare_fn_call_files.py libresolar_bms_calls_ASM.json libresolar_bms_calls_VCG.json libresolar_bms_calls_compare.tex
	@echo ../scripts/compare_fn_call_files.py libresolar_bms_calls_ASM.json libresolar_bms_calls_VCG.json libresolar_bms_calls_compare.tex

one.tex: CANnectivity_calls_compare.tex prusa_coreone_calls_compare.tex libresolar_bms_calls_compare.tex
	cat CANnectivity_calls_compare.tex prusa_coreone_calls_compare.tex libresolar_bms_calls_compare.tex > one.tex

# ../scripts/compare_fn_call_files.py /home/paul/git/pexplorer/selfperf/tmp/zephyr_cannectivity_14_gcc_lpc55s16_functions.json CANnectivity_calls_VCG.json CANnectivity_calls_compare_pexVCG.tex
# ../scripts/compare_fn_call_files.py CANnectivity_calls_ASM.json /home/paul/git/pexplorer/selfperf/tmp/zephyr_cannectivity_14_gcc_lpc55s16_functions.json CANnectivity_calls_compare_pexASM.tex

all: one.tex
	@echo Generating all comparisons

.PHONY: all
