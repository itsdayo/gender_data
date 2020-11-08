This project is written in python and it add columns to a csv file. If you specify -a or -auto, it will generate the gender, probability, and count column. Otherwise it will genereate a male and female column and binary values based off if the person is male or female.

The name column index needs to be specified in sections of the code. Look for the comments telling you where within the code.

### Usage:

**This code needs to be ran with python3 not python**

```sh
python3 genderize.py [-h] -i INPUT -o OUTPUT [-k KEY] [-c] [-ns] [-nh]
```

```
optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     API key
  -c, --catch           Try to handle errors gracefully
  -a, --auto            Automatically complete gender for identical names
  -nh, --noheader       Input has no header row

required arguments:
  -i INPUT, --input INPUT
                        Input file name
  -o OUTPUT, --output OUTPUT
                        Output file name
```

#### Flag details

- _key_: specify API key [required for 1000+ names]
- _catch_: try to gracefully catch and handle errors [recommended]
- _auto_: provides a binary based off if the person in the data is male or female. Does not include gender, probability, or count
- _noheader_: use if input file has no header row

### Test usage:

```
python3 genderize.py -i test/test.csv -o test/out.csv --catch
```

### Note:

- API key (https://store.genderize.io) is required when requesting more than 1000 names a month.

### Requires:

Required module can be found in "dep" folder or pypi link (see "Dependencies")

```
pip install Genderize-0.1.5-py3-none-any.whl
```

#### Dependencies:

- https://pypi.python.org/pypi/Genderize / https://github.com/SteelPangolin/genderize

### Features:

- Bulk processing (tested with 600,000+ names)
- Estimates remaining time
- Writes data after processing 10 names so little data is lost if an error occurs
- Support for genderize.io API key (allows processing of more than 1000 names /mo).
