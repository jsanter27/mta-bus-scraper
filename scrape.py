import argparse
from bs4 import BeautifulSoup
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from os.path import exists
import requests
import schedule
from time import sleep, strftime
from typing import List

DEFAULT_URL = "https://bustime.mta.info/m/index?q=405220"
DEFAULT_OUTPUT = "bus_data.csv"
DEFAULT_ROUTE = "BM3"
DEFAULT_INTERVAL = 10

@dataclass
class BusData:
    """Data structure to hold scraped data"""
    vehicle_id: str
    time_remaining: int


def create_csv_if_needed(filepath: str) -> None:
    if exists(filepath):
        return
    with open(filepath, "w", encoding="UTF8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "Date", 
            "Time", 
            "Vehicle ID", 
            "Time Remaining (Minutes)", 
            "Estimated Arrival"
        ])

    
def append_data(filepath: str, data: List[BusData]) -> None:
    create_csv_if_needed(filepath)
    with open(filepath, "a", encoding="UTF8") as csv_file:
        writer = csv.writer(csv_file)
        for bus in data:
            writer.writerow([
                strftime("%m/%d/%Y"), 
                strftime("%I:%M %p"), 
                bus.vehicle_id, 
                bus.time_remaining,
                (datetime.now() + timedelta(minutes=bus.time_remaining)).strftime("%I:%M %p")
            ])
        timestamp = "[" + strftime("%I:%M %p") + "]"
        print(f"{timestamp} data successfully logged to {filepath} :D\n")


def scrape(url: str, filepath: str, route: str) -> None:
    current_time = strftime("%m/%d/%Y %I:%M %p")
    timestamp = f"[{current_time}]"
    print(f"{timestamp} accessing MTA website...")
    try:
        result = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) " \
                "AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1"
        })
        soup = BeautifulSoup(result.content, features="xml")
        direction_at_stop = list(filter(
            lambda das: route in das.p.a.strong.text, 
            soup.find_all("div", attrs={"class": "directionAtStop"})
        ))
        if not direction_at_stop:
            print(f"{timestamp} no data found at this time :O\n")
            return
        div = direction_at_stop[0]
        data = [
            BusData(
                time_remaining=int(ol.li.strong.text.split(" ")[0]),
                vehicle_id=ol.li.small.text.split(" ")[1],
            ) for ol in div.find_all("ol")
        ]
        if not data:
            print(f"{timestamp} no data found at this time :O\n")
            return
        append_data(filepath, data)
    except Exception as e:
        print(f"{timestamp} ERROR - something went wrong :(\n{e}\n")

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="scraper that calculates the estimated arrival time of buses :)"
    )
    parser.add_argument(
        "--interval", 
        "-i", 
        type=int, 
        help="time interval, in minutes, that the web scraper will run"
    )
    parser.add_argument("--output", "-o", type=str, help="desired file path of the output data")
    parser.add_argument("--route", "-r", type=str, help="desired bus route (ex. 'BM3')")
    parser.add_argument(
        "--stop", 
        "-s", 
        type=int, 
        help="code number for the bus stop (ex. '405220' for WATER ST / PINE ST)"
    )
    parser.add_argument("--url", "-u", type=str, help="url that the scraper will target")
    args = parser.parse_args()
    
    url = args.url or f"https://bustime.mta.info/m/index?q={args.stop}" or DEFAULT_URL
    output = args.output or DEFAULT_OUTPUT
    route = args.route or DEFAULT_ROUTE
    interval = args.interval or DEFAULT_INTERVAL
    
    schedule.every(interval).minutes.do(scrape, url=url, filepath=output, route=route)
    print(f"Good luck, soldier! Remember to use CTRL+C to exit O_o\n")
    print(f"URL: {url}")
    print(f"OUTPUT: {output}")
    print(f"BUS ROUTE: {route}")
    print(f"INTERVAL: {interval} minute(s)\n")
    while True:
        schedule.run_pending()
        sleep(30)
