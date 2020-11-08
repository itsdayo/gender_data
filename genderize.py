from genderize import Genderize, GenderizeException
import csv
import sys
import os.path
import time
import argparse
import logging

import jpyhelper as jpyh


def genderize(args):
    print(args)

    # File initialization
    dir_path = os.path.dirname(os.path.realpath(__file__))

    logging.basicConfig(filename=dir_path + os.sep + "log.txt", level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    ofilename, ofile_extension = os.path.splitext(args.output)

    ofile = ofilename + "_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
    ifile = args.input

    if os.path.isabs(ifile):
        print("\n--- Input file: " + ifile)
    else:
        print("\n--- Input file: " + dir_path + os.sep + ifile)

    if os.path.isabs(ofile):
        print("--- Output file: " + ofile)
    else:
        print("--- Output file: " + dir_path + os.sep + ofile + "\n")

    # File integrity checking
    if not os.path.exists(ifile):
        print("--- Input file does not exist. Exiting.\n")
        sys.exit()

    if not os.path.exists(os.path.dirname(ofile)):
        print("--- Error! Invalid output file path. Exiting.\n")
        sys.exit()

    # Some set up stuff
    # csv.field_size_limit(sys.maxsize)

    # Initialize API key
    if not args.key == "NO_API":
        print("--- API key: " + args.key + "\n")
        genderize = Genderize(
            user_agent='GenderizeDocs/0.0',
            api_key=args.key)
        key_present = True
    else:
        print("--- No API key provided.\n")
        key_present = False

    # Open ifile
    with open(ifile, 'r', encoding="utf8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',', skipinitialspace=True)

        i = next(readCSV)  # set i to the headers as an array
        first_name = []
        allData = []

        if args.auto == False:  # add columns based off auto
            i.append('male')
            i.append('female')
        if args.auto == True:
            i.append('gender')
            i.append('probability')
            i.append('count')

        for row in readCSV:  # Read CSV into first_name list
            allData.append(row)
            first_name.append(row[1])  # specify the name column index here

        if args.noheader == False:
            first_name.pop(0)  # Remove header

        o_first_name = list()

        # Deleted this part of the code because it substrings the name column
        # for l in first_name:
        #     for b in l:
        #         o_first_name.append(b)
        # print(o_first_name)

        if args.auto == True:

            chunks = list(jpyh.splitlist(first_name, 10))

            print("--- Read CSV with " + str(len(first_name)) +
                  " first_name. " + str(len(first_name)) + " unique.")
        else:
            chunks = list(jpyh.splitlist(first_name, 10))
            print("--- Read CSV with " + str(len(first_name)) + " first_name")

        print("--- Processed into " + str(len(chunks)) + " chunks")

        if jpyh.query_yes_no("\n---! Ready to send to Genderdize. Proceed?") == False:
            print("Exiting...\n")
            sys.exit()

        if os.path.isfile(ofile):
            if jpyh.query_yes_no("---! Output file exists, overwrite?") == False:
                print("Exiting...\n")
                sys.exit()
            print("\n")

        if args.auto == True:
            ofile = ofile + ".tmp"

        response_time = []
        gender_responses = list()
        with open(ofile, 'w', newline='', encoding="utf8") as f:
            writer = csv.writer(f)
            writer.writerow(i)  # write row header based off input file header
            chunks_len = len(chunks)
            stopped = False
            for index, chunk in enumerate(chunks):
                if stopped:
                    break
                success = False
                while not success:
                    try:
                        start = time.time()

                        if key_present:
                            dataset = genderize.get(chunk)
                        else:
                            dataset = Genderize().get(chunk)

                        gender_responses.append(dataset)
                        success = True
                    except GenderizeException as e:
                        #print("\n" + str(e))
                        logger.error(e)

                        # zzError handling
                        if "response not in JSON format" in str(e) and args.catch == True:
                            if jpyh.query_yes_no("\n---!! 502 detected, try again?") == True:
                                success = False
                                continue
                        elif "Invalid API key" in str(e) and args.catch == True:
                            print(
                                "\n---!! Error, invalid API key! Check log file for details.\n")
                        else:
                            print(
                                "\n---!! GenderizeException - You probably exceeded the request limit, please add or purchase a API key. Check log file for details.\n")
                        stopped = True
                        break

                    response_time.append(time.time() - start)
                    print("Processed chunk " + str(index + 1) + " of " + str(chunks_len) + " -- Time remaining (est.): " +
                          str(round((sum(response_time) / len(response_time) * (chunks_len - index - 1)), 3)) + "s")

                    singleDataDict1 = dict()
                    newSingleDataDict = dict()
                    singleDataDictGen = dict()
                    singleDataDictData = dict()
                    newDataListWithGen = list()
                    allDataList = list()
                    addDataDict = {}
                    newDataList = list()
                    newArry = list()

                    # get each row and make a new dictionatry
                    for l in allData:
                        for n in range(0, len(l)):
                            singleDataDict1[n] = l[n]

                        dictionary_copy = singleDataDict1.copy()
                        allDataList.append(dictionary_copy)

                    # Combined the input file data with the gender api data
                    for m in allDataList:
                        for n in dataset:

                            if n['name'] == m[1]:  # specify name column here
                                singleDataDictGen = n
                                singleDataDictData = m
                                singleDataDictData.update(singleDataDictGen)

                                # delete the name key because of duplication
                                del singleDataDictData['name']

                                newDataListWithGen.append(
                                    singleDataDictData)

                    for newData in newDataListWithGen:
                        # add gender binary at the end of the data dictionary
                        if newData['gender'] == 'female' and newData['probability'] > 0.5:
                            newData.update({'male': 0, 'female': 1})
                        elif newData['gender'] == 'male'and newData['probability'] > 0.5:
                            newData.update({'male': 1, 'female': 0})
                        # since this is without argument auto delete gender, probability, and count
                        del newData['gender']
                        del newData['probability']
                        del newData['count']
                        # write the data column
                        writer.writerow(newData.values())
                    break

            if args.auto == True:
                print("\nCompleting identical first_name...\n")
                # AUTOCOMPLETE first_name

                # Create master dict
                gender_dict = dict()
                singleDataDict = dict()
                singleDataDict1 = dict()
                newSingleDataDict = dict()
                singleDataDictGen = dict()
                singleDataDictData = dict()
                newDataListWithGen = list()
                allDataList = list()
                addDataDict = {}
                newDataList = list()
                newArry = list()

                # get each row and make a new dictionatry
                for l in allData:
                    for n in range(0, len(l)):

                        singleDataDict1[n] = l[n]

                    dictionary_copy = singleDataDict1.copy()
                    allDataList.append(dictionary_copy)

                # Combined the input file data rows with the gender api data rows
                for m in allDataList:
                    for n in dataset:

                        if n['name'] == m[1]:  # specify name column here
                            singleDataDictGen = n
                            singleDataDictData = m
                            singleDataDictData.update(singleDataDictGen)

                            del singleDataDictData['name']

                            newDataListWithGen.append(singleDataDictData)

                filename, file_extension = os.path.splitext(ofile)
                with open(filename, 'w', newline='', encoding="utf8") as f:
                    writer = csv.writer(f)

                    writer.writerow(i)  # write the header column

                    for newData in newDataListWithGen:
                        # write the data column
                        writer.writerow(newData.values())

            print("Done!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bulk genderize.io script')
    required = parser.add_argument_group('required arguments')

    required.add_argument(
        '-i', '--input', help='Input file name', required=True)
    required.add_argument(
        '-o', '--output', help='Output file name', required=True)
    parser.add_argument('-k', '--key', help='API key',
                        required=False, default="NO_API")
    parser.add_argument('-c', '--catch', help='Try to handle errors gracefully',
                        required=False, action='store_true', default=True)
    parser.add_argument('-a', '--auto', help='Automatically complete gender for identical first_name',
                        required=False, action='store_true', default=False)
    parser.add_argument('-nh', '--noheader', help='Input has no header row',
                        required=False, action='store_true', default=False)

    genderize(parser.parse_args())
