import pandas as pd
import time

from pygbif import occurrences as gbif_occurrences, species as gbif_species


def get_gbif_data(scientific_names, area_bbox=None, limit_per_species=1000):
    """
    scientific_names: list of taxon scientific names
    area_bbox: [min_lon, min_lat, max_lon, max_lat]
    Returns combined pandas DataFrame with columns lat, lon, time
    """
    frames = []
    for name in scientific_names:
        print(f'fetching taxa "{name}"...')

        params = {
            'scientificName': name,
            'limit': limit_per_species,
            'hasCoordinate': True,
        }
        if area_bbox:
            params['decimalLatitude'] = f"{area_bbox[1]},{area_bbox[3]}"
            params['decimalLongitude'] = f"{area_bbox[0]},{area_bbox[2]}"
        results = gbif_occurrences.search(**params)
        data = results['results']
        if data:
            print(f'{length(data)} occurrences found.')
            df = pd.DataFrame(data)
        else:
            print('no occurrences found.')
        time.sleep(1)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame(columns=['decimalLongitude', 'decimalLatitude', 'eventDate'])
