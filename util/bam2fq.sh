#!/bin/bash

#
# Author: Xiao Jianfeng
#
# last modified: 2014.08.11
# Date:          2014.08.05

if [ $# -eq 0 -o "$1" == "-h" -o "$1" == "--help" ]
then
        echo "Usage: $0 bam_file [output_prefix]" >&2
        exit
fi

# $# must be -ge 1 as previous test will exit otherwise
bam_file=$1

if [ $# -ge 2 ]
then
        prefix=$2
else
        prefix=${1%.bam}
fi

# bam_file=WGC021367D.mapped.bam

left_file=${prefix}_1.fq.gz
right_file=${prefix}_2.fq.gz
left_file_tmp=tmp.left.$$
right_file_tmp=tmp.right.$$

mkfifo ${left_file_tmp}
mkfifo ${right_file_tmp}
gzip -c < ${left_file_tmp} > ${left_file} &
gzip -c < ${right_file_tmp} > ${right_file} &

tmp_file=tmp.$$
mkfifo ${tmp_file}

# for test, use 'head -n 10000' to limit the input
# samtools view ${bam_file} | cut -f 1,2,10,11 | head -n 2000000 > ${tmp_file} &
samtools view ${bam_file} | cut -f 1,2,10,11 > ${tmp_file} &

# the primary alignment should have flag & 0x900 == 0, first read has flag & 0x40 == 0x40, and second read has flag & 0x80 == 0x80
# so primary alignment of first read should be flag & 0x940 (ie. 2368) == 0x40, and for second read flag & 0x980 (ie. 2432) == 0x80
# CREATE TABLE left as select qname from fastq where flag & 2368 == 64;
# CREATE TABLE right as select qname from fastq where flag & 2432 == 128;

sqlite3 <<-EOF
.output stderr
PRAGMA journal_mode = memory;
PRAGMA cache_size   = 1000000;

select datetime('now', 'localtime')||" begin";
CREATE TABLE fastq (qname, flag, seq, qual);

select datetime('now', 'localtime')||" import begin";
.separator "\t"
.import tmp.$$ fastq
CREATE INDEX qname_idx on fastq (qname);

select datetime('now', 'localtime')||" import done";

CREATE TABLE left as select qname from fastq where flag & 2368 == 64;
CREATE TABLE right as select qname from fastq where flag & 2432 == 128;

select datetime('now', 'localtime')||" create left right done";

CREATE INDEX left_idx on left (qname);
CREATE INDEX right_idx on right (qname);

select datetime('now', 'localtime')||" create left right index done";

.output ${left_file_tmp}
.separator "\n"
select distinct "@"||fastq.qname||"/1", seq, '+', qual from right join fastq on fastq.qname == right.qname where flag&2368 == 64 order by right.qname;

.output stderr
select datetime('now', 'localtime')||" create left reads done";

.output ${right_file_tmp}
.separator "\n"
select distinct "@"||fastq.qname||"/2", seq, '+', qual from left join fastq on fastq.qname == left.qname where flag&2432 == 128 order by left.qname;

.output stderr
select datetime('now', 'localtime')||" create right reads done";
.exit
EOF

wait
rm ${tmp_file} ${left_file_tmp} ${right_file_tmp}
