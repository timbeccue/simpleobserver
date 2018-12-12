import time
import csv
import sys
import json

print("test")
print(sys.version_info[1])
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    raise Exception("Python 3.6 or a more recent version is required. Try running 'py [file] -3.6'.")

infile = 'messier.csv'
outfile = 'messier.js'
data = {}

def readCSV(infile): 
    with open(infile) as f:
        data = csv.DictReader(f, delimiter=',')
        line_count = 0
        for row in data:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                line_count += 1
        print(f'Processed {line_count} lines.')

def writeJSON(outfile):
    with open(outfile, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    readCSV(infile)
    print(data(size))
    writeJSON(outfile)

if __name__ == '__main__':
    main()