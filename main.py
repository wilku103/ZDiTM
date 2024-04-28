#!/usr/bin/env python3

import click
import requests
from prettytable import PrettyTable
from thefuzz import process

ZDITM_URL = "https://www.zditm.szczecin.pl/api/v1/"


def get_stop_numbers(stop_name: str) -> list[int]:
	# Get all stops
	response = requests.get(f"{ZDITM_URL}stops")
	stops = response.json()["data"]
	to_match = [stop["name"].lower() for stop in stops]

	# Get the best matches
	matched = process.extract(stop_name.lower(), to_match, limit=10)

	# Filter out the matches with low score
	matched = set([match[0] for match in matched if match[1] > 80])
	# Return the stop numbers
	return [stop["number"] for stop in stops if stop["name"].lower() in matched]


@click.command()
@click.argument("stop_name")
@click.option("-l", "--line", help="Filter by line number")
def print_tables(stop_name: str, line: str):
	numbers = get_stop_numbers(stop_name)
	for number in numbers:
		# Get the stop data
		stop = requests.get(f"{ZDITM_URL}displays/{number}").json()
		# Create the table
		table = PrettyTable(
			["Linia", "Kierunek", "Przyjazd rzeczywisty"],
			title=f"{stop['stop_name']} ({stop['stop_number']})",
		)

		# Add departures with real time to the table
		for departure in stop["departures"]:
			if departure["time_real"] is None:
				continue
			table.add_row(
				[
					departure["line_number"],
					departure["direction"],
					f"{departure['time_real']} min",
				]
			)

		# If line to filter by is provided, remove the rows with different line number
		if line:
			for row in table.rows:
				if row[0] != line:
					table.del_row(table.rows.index(row))

		# Print the table if there are any rows
		if len(table.rows) > 0:
			print(table)


def main():
	print_tables()


if __name__ == "__main__":
	main()
