from collections import defaultdict
from pprint import pprint
from jsonmanip import save_to_file

excel_raw_datafile = 'data/slices_usage_excel_raw.txt'


def main():
    loaded_data = defaultdict(lambda: defaultdict(dict))
    with open(excel_raw_datafile) as raw_datafile:
        table_name, years = None, []
        for line in raw_datafile:
            if line.startswith('BEGIN_TABLE'):
                header = line.split()
                table_name = header[1]
                years = [int(year) for year in header[2:]]
                # for year in years:
                #     loaded_data[table_name][year] = {}
            else:
                dataline = line.split()  # EDGE EDGE_ID USAGE USAGE | EDGE EDGE_ID USAGE USAGE | ...
                if len(dataline) == 0:
                    continue
                for column_id in range(len(dataline) // 4):
                    year = years[column_id]
                    edge_id = dataline[column_id * 4 + 1]
                    if edge_id == 'x':
                        continue
                    usage = int(dataline[column_id * 4 + 2])
                    edge_id_string = 'Edge {}'.format(edge_id)
                    loaded_data[table_name][year][edge_id_string] = {'Band 1': usage}

    save_to_file('data/slices_usage_from_preprocessed_excel.json', loaded_data)


if __name__ == '__main__':
    main()
