import logging

import requests

logger = logging.getLogger(__name__)


def fetch_ace_metadata(url, headers):
    """Fetch paginated ACE metadata from API."""
    all_results = []
    while url:
        logger.info("Fetching data from URL: %s", url)
        response = requests.get(
            url, headers=headers)
        if response.status_code != 200:
            logger.error('Failed to fetch data from %s: %s',
                         url, response.status_code)
            break
        data = response.json()
        all_results.extend(data.get('results', []))
        url = data.get('next')
    return all_results


def extract_fields(data):
    """Extract required fields from ACE metadata."""
    military_course = [
        item['metadata']['Metadata_Ledger']['military_course']
        for item in data
        if 'metadata' in item and
           'Metadata_Ledger' in item['metadata'] and
           'military_course' in item['metadata']['Metadata_Ledger']
    ]
    ace_identifier = [
        item['metadata']['Metadata_Ledger']['ace_identifier']
        for item in data
        if 'metadata' in item and
           'Metadata_Ledger' in item['metadata'] and
           'ace_identifier' in item['metadata']['Metadata_Ledger']
    ]
    area_hours_list = [
        area_hour
        for item in data
        if 'metadata' in item and
           'Metadata_Ledger' in item['metadata']
        for area_hour in item['metadata']['Metadata_Ledger'].
        get('areaandhour', {}).get('areaandhour', [])
    ]
    return military_course, ace_identifier, area_hours_list


def save_serialized(serializer_class, data, label):
    """Validate and save serializer data, log errors if any."""
    serializer = serializer_class(data=data, many=True)
    if serializer.is_valid():
        serializer.save()
        logger.info('Created %s: %s', label, serializer.data)
    else:
        logger.error('%s errors: %s', label, serializer.errors)
