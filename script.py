import csv
import requests
import sgp4
from sgp4 import io
from sgp4.earth_gravity import wgs72

from config import config
from satellite import Satellite
from space_track import LOGIN_URL, QUERY_URL


def main() -> None:
    if not validate_config():
        return

    login = dict(identity=config['SPACE_TRACK_USER'], password=config['SPACE_TRACK_PASSWORD'])
    session = requests.session()
    response = session.post(LOGIN_URL, data=login)

    if response.status_code == 200:
        print(f'Login to space-track: OK')
        for satellite in config['SATELLITES']:
            filename = f'{config["OUTPUT_FOLDER"]}/{satellite[1]}_TLE.tle'
            save_tle(session, satellite, filename)
            compute_and_save_csv(satellite, filename)
    else:
        print(f'Login to space-track: STATUS {response.status_code}, {response.content}')


def save_tle(session, satellite, filename):
    data = download_tle(session, satellite[0])

    with open(filename, 'wb') as outfile:
        outfile.write(data)

    print(f'Saved TLE file: OK')


def compute_and_save_csv(satellite, filename):
    all_tles = []
    with open(filename, 'r') as f:
        tle = []
        for line in f:
            tle.append(line)
            if len(tle) == 3:
                all_tles.append(tle)
                tle = []

    heights = []

    for tle in all_tles:
        satellite_sgp4 = sgp4.io.twoline2rv(tle[1], tle[2], wgs72)
        sat = Satellite(satellite_sgp4)

        heights.append([sat.epoch.astimezone().isoformat(), str(sat.mean_height).replace('.', ',')])  # needed for CSV

    height_filename = f'{config["OUTPUT_FOLDER"]}/{satellite[1]}_height.csv'

    with open(height_filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=";")
        writer.writerows(heights)

    print(f'Saved heights file: OK')


def download_tle(session: requests.Session, norad_id: int) -> bytes:
    url = QUERY_URL.format(config['START_DATE'], config['END_DATE'], norad_id)
    response = session.get(url)
    return response.content


def validate_config() -> bool:
    if config['SPACE_TRACK_USER'] == '' or config['SPACE_TRACK_USER'] == '':
        print('Fill space-track credentials in config.py.')
        return False
    if len(config['SATELLITES']) == 0:
        print('Specify satellites to download TLE for them.')
        return False

    return True


main()
