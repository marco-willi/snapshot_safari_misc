""" Generate an extracted subjects.csv based on the classifications
    Output:
        capture,created_at,retired_at,retirement_reason,roll,season,
        site,subject_id,zooniverse_url_0,zooniverse_url_1,zooniverse_url_2
"""
import os
import pandas as pd
import csv
import logging
import argparse
from collections import OrderedDict

from utils.logger import set_logging
from utils.utils import set_file_permission
from zooniverse_exports.legacy.legacy_extractor import build_img_path

from config.cfg import cfg


flags = cfg['add_subject_info_flags_legacy']

# args = dict()
# args['annotations'] = '/home/packerc/shared/zooniverse/Exports/SER/SER_S1_annotations.csv'
# args['output_csv'] = '/home/packerc/shared/zooniverse/Exports/SER/SER_S1_subjects_extracted.csv'

if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=str, required=True)
    parser.add_argument("--output_csv", type=str, required=True)
    parser.add_argument("--log_dir", type=str, default=None)
    parser.add_argument("--log_filename", type=str, default='extract_subjects_legacy')
    parser.add_argument("--exclude_colums", nargs='+', type=str, default=[])

    args = vars(parser.parse_args())

    ######################################
    # Check Input
    ######################################

    if not os.path.isfile(args['annotations']):
        raise FileNotFoundError(
            "annotations: {} not found".format(
             args['annotations']))

    flags.sort()

    # logging
    set_logging(args['log_dir'], args['log_filename'])
    logger = logging.getLogger(__name__)

    ######################################
    # Read Classifications
    ######################################

    # Read Subject CSV
    class_dict = OrderedDict()
    with open(args['annotations'], "r") as ins:
        csv_reader = csv.reader(ins, delimiter=',', quotechar='"')
        header = next(csv_reader)
        row_name_to_id_mapper = {x: i for i, x in enumerate(header)}
        for line_no, line in enumerate(csv_reader):
            subject_id = line[row_name_to_id_mapper['subject_id']]
            record = {k: line[v] for k, v in row_name_to_id_mapper.items()}
            class_dict[subject_id] = record

    logger.info("Read {} classifications".format(len(class_dict.keys())))

    ######################################
    # Create subject data
    ######################################

    # Create one row per subject
    subjects = OrderedDict()
    for cl in class_dict.values():
        subject_id = cl['subject_id']
        record = dict()
        for flag in flags:
            try:
                record[flag] = cl[flag]
            except:
                record[flag] = ''
        # correct image paths
        if "filenames" in record:
            try:
                filenames = record['filenames'].split(';')
                roll = record['roll']
                season = record['season']
                site = record['site']
                filenames = [
                    build_img_path(season, site, roll, x)
                    for x in filenames if x != '']
                record['filenames'] = ';'.join(filenames)
            except:
                pass
        record['subject_id'] = subject_id
        subjects[subject_id] = record

    ######################################
    # Export as CSV
    ######################################

    df = pd.DataFrame.from_dict(subjects, orient='index')

    # sort rows
    df.sort_values(
        by=['season', 'site', 'roll', 'capture', 'subject_id'], inplace=True)

    # re-arrange columns
    cols = df.columns.tolist()
    first_cols = [
        'capture_id', 'season', 'site', 'roll',
        'capture', 'subject_id']
    first_cols = [x for x in first_cols if x in cols]
    cols_rearranged = first_cols + [x for x in cols if x not in first_cols]

    # exclude cols if specified
    cols_final = [x for x in cols_rearranged if x not in args['exclude_colums']]

    df = df[cols_final]

    # export
    df.to_csv(args['output_csv'], index=False)

    # change permmissions to read/write for group
    set_file_permission(args['output_csv'])
