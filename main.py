import requests
from thefuzz import process

ZDITM_URL = "https://www.zditm.szczecin.pl/api/v1/"


def get_stop_numbers(stop_name: str) -> list[int]:
	response = requests.get(f"{ZDITM_URL}stops")
	stops = response.json()["data"]

	to_match = [stop["name"].lower() for stop in stops]

	matched = process.extract(stop_name.lower(), to_match, limit=10)

	matched = set([match[0] for match in matched if match[1] > 80])
	return [stop["number"] for stop in stops if stop["name"].lower() in matched]


def main():

	numbers = get_stop_numbers(input("Podaj nazwę przystanku: "))
	for number in numbers:
		stop = requests.get(f"{ZDITM_URL}displays/{number}").json()
		tablica = stop["departures"]
		print(stop["stop_name"])
		for departure in tablica:
			if departure["time_real"] is None:
				continue
			print(departure["line_number"], departure["direction"], departure["time_real"])
		print()


if __name__ == "__main__":
	main()
