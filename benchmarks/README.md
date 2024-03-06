# JSON5 Benchmarking data

This directory contains a simple command line program that compares the
speed of JSON5 with the builtin JSON decoder. 

On a 2018 Mac Mini with a 3 GHz 6 Core Intel Core i5 and 64 GB of memory
running MacOS 14.2.1, JSON5 is from 800-1200x slower than JSON.

The three datasets come from MIT-licensed data grabbed off the web on
Mar 3, 2024 around 21:30 GMT. Their accompanying licenses are contained
in the [LICENSE](../LICENSE) file.

[64KB-min.json](64KB-min.json) was retrieved from 
<https://raw.githubusercontent.com/MicrosoftEdge/Demos/e3b81daee151a225c1d8f24bf82d31c464b0f737/json-dummy-data/64KB-min.json>.
It looks like that is part of a set of sample data used to benchmark
Microsoft Edge's JSON viewer, and I'm guessing that the data was 
synthetically generated.

[bitly-usa-gov.json](bitly-usa-gov.json) was retrieved from 
<https://raw.githubusercontent.com/wesm/pydata-book/b992071876bb4324b0323170061c886760289d4d/datasets/bitly_usagov/example.txt>.
and is a data set that was part of the sample data for *Python Data Analysis,
3rd Edition*. Apparently this data came from bit.ly data for USA.gov, although
I have been unable to find either the original source data or a description
of the schema for it. The book only references the 'tz' field, which appears
to be a timezone, the 'a' field, which loooks like a web browser User-Agent
string. The data was originally a file of newline-separated JSON records,
but I merged them into a single array.

[twitter.json](twitter.json) was retrieved from 
<https://raw.githubusercontent.com/miloyip/nativejson-benchmark/5dbf5a933a850652bf059cde64cc1f0c8d2c5d6f/data/twitter.json>.
It comes from what appears to be a a repo used for benchmarking for various
Native C/C++ JSON parsers. I do not know where this file was retrieved from
or what the schema is, but this file has a more complicated schema and contains
data in multiple languages.
