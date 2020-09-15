import os


def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def get_site_floors(data_dir: str) -> []:
    site_floors = []
    sites = [(f.name, f.path) for f in os.scandir(data_dir) if f.is_dir()]
    for site_name, site_dir in sites:
        site_floors.extend([(site_name, f.name) for f in os.scandir(site_dir) if f.is_dir()])

    return site_floors

