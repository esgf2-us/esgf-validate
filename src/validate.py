import logging

import deepdiff as dd
import pystac_client
import yaml
from tqdm import tqdm


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("esgf-validate")
    if not logger.handlers:
        file_handler = logging.FileHandler("errors.log", mode="w")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        file_handler.setLevel(logging.ERROR)
        logger.addHandler(file_handler)
    logger.setLevel(logging.ERROR)
    logger.parent.handlers = []
    return logger


def validate_stac_endpoints(
    ref_endpoint_url: str, com_endpoint_url: str, limit: int = 100
) -> bool:
    """Assymetrically validates the comparison STAC endpoint relative to a reference."""
    # Setup logger and print context for any errors if found
    logger = setup_logger()
    logger.error(f"ref = {ref_endpoint_url}")
    logger.error(f"com = {com_endpoint_url}")

    # Specify globally consistent search keywords to use when comparing.
    search = {"collections": "CMIP6", "max_items": limit, "limit": limit}

    # Setup clients
    ref_client = pystac_client.Client.open(ref_endpoint_url)
    com_client = pystac_client.Client.open(com_endpoint_url)

    # Loop over search results and validate item by item. Note this should be page by
    # page, but pages() is not currently working as the stac client documentation
    # indicates it should.
    endpoints_validated = True
    ref_items = list(ref_client.search(**search).items_as_dicts())
    for ref_item in tqdm(ref_items, desc=f"Checking {ref_endpoint_url}", unit="item"):

        # Search the comparison endpoint for these ids
        com_results = com_client.search(**search, ids=ref_item["id"])

        # There should only be a single comparison item
        com_item = list(com_results.items_as_dicts())
        if not com_item:
            logger.error(f"ref item does not exist in com!\nid={ref_item['id']}")
            endpoints_validated = False
            continue
        assert len(com_item) == 1
        com_item = com_item[0]

        difs = dd.DeepDiff(ref_item, com_item)
        if difs:
            endpoints_validated = False
            difs = (
                yaml.dump(difs.to_dict())
                .replace("new_", "com_")
                .replace("old_", "ref_")
            )
            logger.error(f"differences found!\nid={ref_item['id']}\n{difs}")

    return endpoints_validated


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        "validate.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-e",
        "--endpoints",
        nargs=2,
        default=["https://api.stac.esgf-west.org/", "https://api.stac.esgf-west.org/"],
    )
    parser.add_argument("-l", "--limit", type=int, default=100)
    args = parser.parse_args()

    # Check the symmetric difference between the endpoints
    if validate_stac_endpoints(
        *args.endpoints, limit=args.limit
    ) and validate_stac_endpoints(*(args.endpoints[::-1]), limit=args.limit):
        print("Endpoints are the same.")
    else:
        raise ValueError("Differences found, see 'errors.log' for details.")
