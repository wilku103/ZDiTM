#!/usr/bin/env python3

import requests
from thefuzz import process

import click
from prettytable import PrettyTable

ZDITM_URL = "https://www.zditm.szczecin.pl/api/v1/"


def get_stop_numbers(stop_name: str) -> list[int]:
	response = requests.get(f"{ZDITM_URL}stops")
	stops = response.json()["data"]

	to_match = [stop["name"].lower() for stop in stops]

	matched = process.extract(stop_name.lower(), to_match, limit=10)

	matched = set([match[0] for match in matched if match[1] > 80])
	return [stop["number"] for stop in stops if stop["name"].lower() in matched]


@click.command()
@click.argument("stop_name")
def print_tables(stop_name: str):
	numbers = get_stop_numbers(stop_name)
	for number in numbers:
		table = PrettyTable()
		table.field_names = ["Linia", "Kierunek", "Przyjazd rzeczywisty"]

		stop = requests.get(f"{ZDITM_URL}displays/{number}").json()
		tablica = stop["departures"]

		for departure in tablica:
			if departure["time_real"] is None:
				continue
			table.add_row([departure["line_number"], departure["direction"], f"{departure["time_real"]} min"])
		print(stop["stop_name"])
		print(table)


def main():
	print_tables()


if __name__ == "__main__":
	main()
