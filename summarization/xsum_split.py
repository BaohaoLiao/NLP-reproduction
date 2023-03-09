import os
import sys
import json
from os.path import join
from multiprocessing import Pool


def read_file_and_split_into_doc_summary(file_name):
    with open(file_name, "r") as f:
        non_empty_lines = [l for l in (line.strip() for line in f) if l]
        concat = ' '.join(non_empty_lines)
        doc = concat.split("[SN]RESTBODY[SN] ")[1]
        summary = concat.split(" [SN]FIRST-SENTENCE[SN] ")[1].split(" [SN]RESTBODY[SN] ")[0]
    return doc, summary

if __name__ == '__main__':
    xsum_dir = sys.argv[1]
    split_file = sys.argv[2]
    output_dir = sys.argv[3]
    keys = ["test", "validation", "train"]
    types = ["src", "tgt"]

    with open(split_file, "r") as f:
        split_ids = json.load(f)
    split_file_names = {}
    for k in keys:
        split_file_names[k] = [join(xsum_dir, i + "summary") for i in split_ids[k]]

    results = {}
    for k in keys:
        with Pool(processes=5) as pool:
            result = pool.map(read_file_and_split_into_doc_summary, split_file_names[k])
        results[k] = result

    os.system("mkdir -p " + output_dir)
    for k in keys:
        doc_file = open(join(output_dir, k + ".src"), "w")
        summary_file = open(join(output_dir, k + ".tgt"), "w")
        for r in results[k]:
            doc_file.write(r[0] + "\n")
            summary_file.write(r[1] + "\n")
        doc_file.close()
        summary_file.close()


