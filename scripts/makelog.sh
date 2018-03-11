#!/usr/bin/env bash

# concat all log files into a temp file
# and tail -f that file

logfile=$(mktemp /tmp/bible-extractor.XXXXXX)


proc_ids=()

function cleanup() {
    echo "Cleaning up..."
    for proc in ${proc_ids[@]}; do
        kill $proc
    done


    rm "$logfile"
    exit
}

tail -f extracted_data/log/lxx.log >> "$logfile" &
proc_ids=(${proc_ids[@]} $!)
tail -f extracted_data/log/vulgate.log >> "$logfile" &
proc_ids=(${proc_ids[@]} $!)
tail -f extracted_data/log/kj2000.log >> "$logfile" &
proc_ids=(${proc_ids[@]} $!)
tail -f extracted_data/log/merged.log >> "$logfile" &
proc_ids=(${proc_ids[@]} $!)

trap cleanup INT

tail -f "$logfile"

cleanup
