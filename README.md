# About

This is a web scraper to be used for collecting estimated arrival times for MTA buses. By default, it collects arrival time for BM3 routes at WATER ST / PINE ST.

# Installation

This program uses Python 3.8.10.

After cloning or downloading the repo, navigate to its root and install the programs dependencies with the command:
```bash
pip install -r requirements.txt
```

# Usage

To run the scraper after installing the dependencies, use the following command:
```bash
python scrape.py
```

# Custom Parameters

To find out more about using the scraper using custom parameters, such as `url`, `output`, and `route`, use the command:
```bash
python scrape.py -h
```
or
```bash
python scrape.py --help
```
to find out more.