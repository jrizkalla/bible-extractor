all: lxx vulgate kj2000 merged log

lxx:
	cd .. && python3 -m bible_extractor 0:check -o extracted_data/lxx.json -s extracted_data/lxx-stat.json --force > extracted_data/log/lxx.log 2>&1

vulgate:
	cd .. && python3 -m bible_extractor 1:check -o extracted_data/vulgate.json -s extracted_data/vulgate-stat.json --force > extracted_data/log/vulgate.log 2>&1

kj2000:
	cd .. && python3 -m bible_extractor 3:check -o extracted_data/kj2000.json -s extracted_data/kj2000-stat.json --force > extracted_data/log/kj2000.log 2>&1

merged:
	cd .. && python3 -m bible_extractor\
		extracted_data/lxx.json:remove_ranges:remove_new\
		extracted_data/vulgate.json:remove_new\
		extracted_data/kj2000.json:remove_old\
		-o extracted_data/merged.json -s extracted_data/merged-stat.json --force\
		> extracted_data/log/merged.log 2>&1
	# check the merge
	cd .. && python3 -m bible_extractor extracted_data/merged.json:check -o /dev/null >> extracted_data/log/merged.log 2>&1


.PHONY: all lxx
