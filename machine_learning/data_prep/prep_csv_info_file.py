""" Create a CSV file with info about all images and labels to
    create dataset inventories from
"""
import csv
import datetime
from collections import Counter, OrderedDict

input_db_export = '/home/packerc/will5448/test_export_season_1.csv'
output_cleaned = '/home/packerc/will5448/test_export_season_1_cleaned.csv'
max_images = 3
# /home/packerc/shared/machine_learning/data/info_files/SER

def binarize(x):
    """ convert values between 0 and 1 to 1 (if 0.5 or larger), else to 0 """
    try:
        return int(float(x) + 0.5)
    except:
        return 0


def correct_image_name(name):
    """ change image name
    OLD: S1/G12/G12_R1/PICT3981.JPG
    NEW: S1/G12/G12_R1/S1_G12_R1_PICT3981.JPG

    OLD: S8/O09/O09_R3/S8_O09_R3_S8_O09_R3_IMAG9279.JPG
    NEW: S8/O09/O09_R3/S8_O09_R3_S8_O09_R3_IMAG9279.JPG
    """
    if '/' not in name:
        return name
    name_splits = name.split('/')
    if '_' in name_splits[-1]:
        return name
    path = '/'.join(name_splits[0:-1])
    file_name_new = '_'.join([name_splits[0], name_splits[2], name_splits[3]])
    return path + '/' + file_name_new


behaviors = ["Standing", "Resting", "Moving",
             "Eating", "Interacting", "Babies"]

# Read db export file
all_records = list()
counts = list()
with open(input_db_export, 'r') as f:
    csv_reader = csv.reader(f, delimiter=',')
    header = next(csv_reader)
    header.append("empty")
    header[header.index("idCaptureEvent")] = 'capture_id'
    header[header.index("CountMedian")] = 'Count'
    header[header.index("PathFilename")] = 'image'
    header_to_id = {h: i for i, h in enumerate(header)}
    for row in csv_reader:
        row.append('')
        try:
            ts = datetime.datetime.strptime(
                    row[header_to_id["CaptureTimestamp"]],
                    '%Y-%m-%d %H:%M:%S')
        except:
            ts = datetime.datetime.strptime('1900', '%Y')
        row[header_to_id["CaptureTimestamp"]] = \
            ts.strftime('%Y-%m-%d-%H-%M-%S')
        # change path
        row[header_to_id['image']] = 'SER/' + \
            correct_image_name(row[header_to_id["image"]])
        # convert behaviors to binary
        for behav in behaviors:
            row[header_to_id[behav]] = binarize(row[header_to_id[behav]])
        # convert empty non-empty
        if row[header_to_id["NumberOfSpecies"]] == '0':
            row[header_to_id["empty"]] = '1'
            row[header_to_id["Species"]] = 'empty'
            row[header_to_id["Count"]] = '0'
        else:
            row[header_to_id["empty"]] = '0'
            if row[header_to_id["Count"]] == '0':
                print("Wrong count for: %s" % row)
        counts.append(row[header_to_id["Count"]])
        # lower case for species
        row[header_to_id["Species"]] = row[header_to_id["Species"]].lower()
        # create capture id
        capture_id = '#'.join([row[header_to_id["Season"]],
                               row[header_to_id["GridCell"]],
                               row[header_to_id["RollNumber"]],
                               row[header_to_id["CaptureEventNum"]]])
        row[header_to_id['capture_id']] = capture_id
        all_records.append(row)

# check counts
Counter(counts)

# Convert and Clean data
data_clean = OrderedDict()
for row in all_records:
    capture_id = row[header_to_id['capture_id']]
    if capture_id not in data_clean:
        data_clean[capture_id] = {'images': list(), 'record': dict(), 'species': set()}
    dat = data_clean[capture_id]
    img = row[header_to_id['image']]
    if (img not in dat['images']) and (len(dat['images']) < max_images):
        dat['images'].append(img)
    dat['species'].add(row[header_to_id['Species']])
    dat['record'][row[header_to_id['Species']]] = row


# Create list for writing to disk
data_list_clean = list()
images = ['image%s' % (i + 1) for i in range(0, max_images)]
header_clean = ['capture_id', 'empty', 'Species', 'Count', 'Standing',
                'Resting', 'Moving', 'Eating', 'Interacting',
                'Babies', 'Season', 'CaptureTimestamp'] + images
record_clean = ['' for i in range(0, len(header_clean))]
record_mapper = {v: k for k, v in enumerate(header_clean)}
for k, v in data_clean.items():
    new_record = [x for x in record_clean]
    # fill in images
    for i, img in enumerate(v['images']):
        new_record[record_mapper['image%s' % (i + 1)]] = img
    # create a record per species
    for spec in v['species']:
        row = v['record'][spec]
        for col in header_clean:
            if 'image' in col:
                continue
            new_record[record_mapper[col]] = row[header_to_id[col]]
        to_append = [x for x in new_record]
        data_list_clean.append(to_append)

# write file
with open(output_cleaned, "w") as outs:
    csv_writer = csv.writer(outs, delimiter=',')
    print("Writing file to %s" % output_cleaned)
    csv_writer.writerow([x.lower() for x in header_clean])
    for i, line in enumerate(data_list_clean):
        csv_writer.writerow(line)











    for i in range(1, max_images):
        header.append("image%s" % (i + 1))
        if capture_id not in all_records:
            all_records[capture_id] = row
        else:
            old_row = all_records[capture_id]





# Counter({'0': 353793, '1': 44584, '2': 11435, '3': 5388, '4': 3092,
# '11-50': 2108, '5': 1995, '6': 1291, '7': 990, '8': 737, '10': 511,
# '9': 460, '51+': 6})


# Target output
# capture_id, image_path, empty, species, behaviors, season, site, location, timestamp

# meta data
#/home/packerc/shared/season_captures/SER/captures
# Season, Site, Roll, Capture, Image, PathFilename, TimestampJPG
# 1,B04,1,1,1,S1/B04/B04_R1/PICT0001.JPG,2010:07:18 16:26:14

# season_x.csv
# S9/B03/B03_R1/S9_B03_R1_IMAG0003.JPG,ASG001lfjx,21,1,1,0,0,0,0,0

# season exports
# idCaptureEvent,Season,GridCell,RollNumber,CaptureEventNum,SequenceNum,PathFilename
# 2424940,9,B03,1,1,1,S9/B03/B03_R1/S9_B03_R1_IMAG0001.JPG
