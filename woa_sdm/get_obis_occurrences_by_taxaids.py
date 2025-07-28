def get_obis_occurrences_by_taxaids(taxa_ids, area_bbox=None, limit=10000):
    """
    Download occurrence data from OBIS by taxon ID list.
    Returns a dataframe with lat, lon, time columns.
    """
    frames = []
    for tid in taxa_ids:

        query = obis_occurrences.search(taxonid=tid, size=limit)
        if area_bbox:
            bbox = area_bbox
            geom = f"POLYGON(({bbox[0]} {bbox[1]},{bbox[2]} {bbox[1]},{bbox[2]} {bbox[3]},{bbox[0]} {bbox[3]},{bbox[0]} {bbox[1]}))"
            query = obis_occurrences.search(taxonid=tid, size=limit, geometry=geom)
        query.execute()

        try:
            df = query.to_pandas()
        except Exception:
            continue

        if set(['decimalLongitude', 'decimalLatitude', 'eventDate']).issubset(df.columns):
            frames.append(df[['decimalLongitude', 'decimalLatitude', 'eventDate']].rename(
                columns={'decimalLongitude': 'lon', 'decimalLatitude': 'lat', 'eventDate': 'time'}
            ))
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame(columns=['lon', 'lat', 'time'])
