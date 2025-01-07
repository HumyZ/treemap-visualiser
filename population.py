from __future__ import annotations
import json
from typing import Optional, List, Dict

from tree_data import AbstractTree


# Constants for the World Bank population files
WORLD_BANK_POPULATIONS = 'populations.json'
WORLD_BANK_REGIONS = 'regions.json'


class PopulationTree(AbstractTree):
    """A tree representation of country population data.

    This tree always has three levels:
      - The root represents the entire world.
      - Each node in the second level is a region (defined by the World Bank).
      - Each node in the third level is a country.

    The data_size attribute corresponds to the 2019 population of the country,
    as reported by the World Bank.

    """

    def __init__(self: PopulationTree, world: bool,
                 root: Optional[object] = None,
                 subtrees: Optional[List[PopulationTree]] = None,
                 data_size: int = 0) -> None:
        """Initialize a new PopulationTree.

        If <world> is True, then this tree is the root of the population tree,
        and it should load data from the World Bank files.
        In this case, none of the other parameters are used.

        If <world> is False, pass the other arguments directly to the superclass
        constructor.
        """
        if world:
            region_trees = _load_data()
            AbstractTree.__init__(self, 'World', region_trees)
        else:
            if subtrees is None:
                subtrees = []
            AbstractTree.__init__(self, root, subtrees, data_size)

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.
        """
        return " -> "


def _load_data() -> List[PopulationTree]:
    """Create a list of trees corresponding to different world regions.

    Each tree consists of a root node -- the region -- attached to one or
    more leaves -- the countries in that region.
    """
    # Get data from World Bank files.
    country_populations = _get_population_data()
    regions = _get_region_data()

    region_lst = []
    for region in regions:
        country_lst = []
        for country in regions[region]:
            if country in country_populations:
                country_lst.append(PopulationTree(False, country, None,
                                                  country_populations[country]))
        region_lst.append(PopulationTree(False, region, country_lst))
    return region_lst


def _get_population_data() -> Dict[str, int]:
    """Return country population data from the World Bank.

    The return value is a dictionary, where the keys are country names,
    and the values are the corresponding populations of those countries.

    """
    _, population_data = _get_json_data(WORLD_BANK_POPULATIONS)
    population_data = population_data[47:]

    countries = {}
    for data in population_data:
        country = data['country']['value']
        value = data['value']
        if isinstance(value, int):
            countries[country] = value
    return countries


def _get_region_data() -> Dict[str, List[str]]:
    """Return country region data from the World Bank.

    The return value is a dictionary, where the keys are region names,
    and the values a list of country names contained in that region.

    """
    _, country_data = _get_json_data(WORLD_BANK_REGIONS)

    regions = {}
    for data in country_data:
        country = data['name']
        region = data['region']['value']
        identifier = data['region']['id']
        if identifier != 'NA':
            if region not in regions:
                regions[region] = [country]
            else:
                regions[region].append(country)
    return regions


def _get_json_data(fname: str) -> list:
    """Return a list representing the JSON data from file fname.

    """
    f = open(fname)
    return json.loads(f.read())
