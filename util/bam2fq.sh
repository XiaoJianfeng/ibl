#!/bin/bash

#
# Author: Xiao Jianfeng
#
# Date:   2014.08.05

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

left_file=${prefix}_1.fq
right_file=${prefix}_2.fq

temp_file=temp.$$
mkfifo ${temp_file}

# for test, use 'head -n 10000' to limit the input
# samtools view ${bam_file} | cut -f 1,2,10,11 | head -n 2000000 > ${temp_file} &
samtools view ${bam_file} | cut -f 1,2,10,11 > ${temp_file} &

sqlite3 <<-EOF
.output stderr
PRAGMA journal_mode = memory;
PRAGMA cache_size   = 1000000;

select date()||" "||time()||" begin";
CREATE TABLE fastq (qname, flag, seq, qual);

select date()||" "||time()||" import begin";
.separator "\t"
.import temp.$$ fastq
CREATE INDEX qname_idx on fastq (qname);

select date()||" "||time()||" import done";

CREATE TABLE left as select qname from fastq where flag & 64 == 64;
CREATE TABLE right as select qname from fastq where flag & 128 == 128;

select date()||" "||time()||" create left right done";

CREATE INDEX left_idx on left (qname);
CREATE INDEX right_idx on right (qname);

select date()||" "||time()||" create left right index done";

.output ${left_file}
.separator "\n"
select distinct "@"||right.qname||"/1", seq, '+', qual from right join fastq on fastq.qname == right.qname where flag&64 == 64 order by right.qname;

.output stderr
select date()||" "||time()||" create left reads done";

.output ${right_file}
.separator "\n"
select distinct "@"||left.qname||"/2", seq, '+', qual from left join fastq on fastq.qname == left.qname where flag&128 == 128 order by left.qname;

.output stderr
select date()||" "||time()||" create right reads done";
.exit
EOF
rm ${temp_file}
