
CANnectivity_calls_ASM.json: /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_CANnectivity_14.yaml --export-function-call-to-file CANnectivity_calls_ASM.json

CANnectivity_calls_VCG.json:  /home/paul/git/cannecti/lpcxpresso55s16_1.4/zephyr/zephyr.elf
	python ../runner.py -c config_CANnectivity_14.yaml --export-function-call-to-file CANnectivity_calls_VCG.json --get-function-calls-from-build-dir-only

CANnectivity_calls_compare.tex: CANnectivity_calls_ASM.json CANnectivity_calls_VCG.json
	../scripts/compare_fn_call_files.py CANnectivity_calls_ASM.json CANnectivity_calls_VCG.json CANnectivity_calls_compare.tex

all: CANnectivity_calls_compare.tex
	@echo Generating all comparisons

.PHONY: all
