#!/usr/bin/env python3

# TODO implement a description for the entire file

__author__ = "Scott Teresi"

import logging
import coloredlogs
from configparser import ConfigParser

from load_data.import_image_data import image_data, extract_dsm
from load_data.import_ground_data import ground_data, extract_canopy_ht
from load_data.import_obs_data import obs_data
from load_data.import_obs_data import geno_plot_dict
from replace_names import replace_names
from height_correlation.quantile_optimize import quantile_optimize


if __name__ == '__main__':
    # TODO implement a main description
    """
    Test
    """
    log_level = logging.INFO
    logger = logging.getLogger(__name__)
    coloredlogs.install(level=log_level)
    logger.info("Setting config file...")
    config = ConfigParser()
    # Code in the parser objects, hard coded
    config['Filenames'] = {'HumanData': 'ground_data_2019.csv',
                           'DroneData': 'point_data_6in_2019obs.csv',
                           'ObservationKey': 'obs_2019_key.csv'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    logger.info("Reading config file...")
    parser = ConfigParser()
    parser.read('config.ini')
    # Set the objects from the parser
    HumanData = parser.get('Filenames', 'HumanData')
    DroneData = parser.get('Filenames', 'DroneData')
    ObservationKey = parser.get('Filenames', 'ObservationKey')
    logger.info("Config file objects have been set...")

    logger.info("Load and clean the data...")
    DroneData = image_data(DroneData)

    logger.info('Importing the ground data...')
    HumanData = ground_data(HumanData)

    logger.info('Importing the ground data...')
    ObsData = obs_data(ObservationKey)

    logger.info('Creating plotID vs. genotype dictionary...')
    GenoPlotDict = geno_plot_dict(ObsData)

    logger.info('Replacing plotID with genotype for HumanData...')
    ReplacedHumanData = replace_names(HumanData, GenoPlotDict, 'plot')

    logger.info('Replacing plotID with genotype for DroneData...')
    ReplacedDroneData = replace_names(DroneData, GenoPlotDict, 'plot_id')

    # extract data from columns for soil
    soil, soil_size = extract_dsm(
        DroneData,
        colname = "DSM_7_2_19",
        groupcol = "plot_id",
        grouprow = HumanData["plot"].values
    )
    # extract data from columns for canopy
    canopy, canopy_size = extract_dsm(
        DroneData,
        colname = "DSM_10_7_19", # this is the last date (caution: dead plants?)
        groupcol = "plot_id",
        grouprow = HumanData["plot"].values
    )

    # extract canopy manually taken heights from pandas.DataFrame
    manual_ht = extract_canopy_ht(
        HumanData
    )

    # identify optimal quantile settings
    cost, pos = quantile_optimize(
        z_soil = soil,
        z_soil_size = soil_size,
        z_canopy = canopy,
        z_canopy_size = canopy_size,
        manual_ht = manual_ht,
        n_particles = 100,
        iters = 20
    )

    print("Objfn cost:", cost)
    print("Soil quantile:", pos[0])
    print("Canopy quantile:", pos[1])