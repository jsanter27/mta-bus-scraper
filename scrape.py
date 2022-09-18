import argparse
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from os.path import exists
import requests
import schedule
from time import sleep, strftime

DEFAULT_URL = "https://bustime.mta.info/m/index;jsessionid=7849DFF3FC3ABE446945C864BF94AC3B?q=405220"
DEFAULT_OUTPUT = "data.csv"
DEFAULT_ROUTE = "BM3"


def create_csv_if_needed(filepath):
    if exists(filepath):
        return
    with open(filepath, "w", encoding="UTF8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Date", "Time", "Vehicle ID", "Time Remaining (Minutes)", "Estimated Arrival"])

    
def append_data(filepath, data):
    create_csv_if_needed(filepath)
    with open(filepath, "a", encoding="UTF8") as csv_file:
        writer = csv.writer(csv_file)
        for entry in data:
            writer.writerow([
                strftime("%m/%d/%Y"), 
                strftime("%I:%M %p"), 
                entry["vehicle_id"], 
                entry["time_remaining"],
                (datetime.now() + timedelta(minutes=entry["time_remaining"])).strftime("%I:%M %p")
            ])
        timestamp = strftime("%I:%M %p")
        print(f"{timestamp} data successfully logged to {filepath} :D\n")


def scrape(url, filepath, route):
    current_time = strftime("%m/%d/%Y %I:%M %p")
    timestamp = f"[{current_time}]"
    print(f"{timestamp} accessing MTA website...")
    try:
        result = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) " \
                "AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1"
        })
        soup = BeautifulSoup(result.content, features="xml")
        data = [
            {
                "time_remaining": int(div.ol.li.strong.text.split(" ")[0]),
                "vehicle_id": div.ol.li.small.text.split(" ")[1],
            } for div in soup.find_all(
                "div", 
                attrs={"class": "directionAtStop"}
            ) if route in div.p.a.strong.text
        ]
        if not data:
            print(f"{timestamp} no data found at this time :O\n")
            return
        append_data(filepath, data)
    except Exception as e:
        print(f"{timestamp} ERROR - something went wrong :(\n{e}\n")

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="scraper that calculates the estimated arrival time of buses :)")
    parser.add_argument("--url", "-u", type=str, help="url that the scraper will target")
    parser.add_argument("--output", "-o", type=str, help="desired file path of the output data")
    parser.add_argument("--route", "-r", type=str, help="desired bus route (ex. 'BM3')")
    args = parser.parse_args()
    
    url = args.url or DEFAULT_URL
    filepath = args.output or DEFAULT_OUTPUT
    route = args.route or DEFAULT_ROUTE
    
    schedule.every(10).seconds.do(scrape, url=url, filepath=filepath, route=route)
    print(f"Good luck, soldier! Remember to use CTRL+C to exit O_o\n")
    while True:
        schedule.run_pending()
        sleep(1)
