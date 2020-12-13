import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import draw

years_2010_2019 = list(range(2010, 2020))
years_2020_2024 = list(range(2020, 2025))

data_series = {
    'WYN_EMPIR': {
        'time': years_2010_2019,
        'slices': [984, 1038, 1086, 1170, 1192, 1156, 1240, 1234, 1290, 1278],
        'Gbs': [75100, 80800, 86900, 89100, 91800, 91500, 97800, 100100, 102000, 105700]
    },
    'WYN_PROGN_0': {
        'time': years_2020_2024,
        'slices': [1248, 1304, 1282, 1472, 1478],
        'Gbs': [108900, 111700, 115300, 118700, 122100]
    },
    'WYN_PROGN_L': {
        'time': years_2020_2024,
        'slices': [1232, 1276, 1284, 1324, 1424],
        'Gbs': [107300, 110700, 113800, 117500, 119500]
    },
    'WYN_PROGN_LS': {
        'time': years_2020_2024,
        'slices': [1204, 1250, 1278, 1288, 1436],
        'Gbs': [105500, 108400, 111800, 114600, 118200]
    },
    'WYN_PROGN_P': {
        'time': years_2020_2024,
        'slices': [1288, 1274, 1294, 1434, 1435],
        'Gbs': [110100, 112800, 116400, 119000, 122800]
    },
    'WYN_PROGN_PS': {
        'time': years_2020_2024,
        'slices': [1284, 1418, 1392, 1466, 1527],
        'Gbs': [112000, 115600, 118900, 121800, 124600]
    },
}

settings = {
    'colors': {
        'slices': 'blue',
        'Gbs': 'orange'
    },
    'labels': {
        'time': 'years',
        'slices': 'slices utilization',
        'Gbs': 'Gbps'
    },
    'ylims': {
        'slices': (1_000, 1_500),
        'Gbs': (75_000, 125_000)
    }
}

def main():
    slices_color = settings['colors']['slices']
    gbs_color = settings['colors']['Gbs']
    slices_ylims = settings['ylims']['slices']
    gbs_ylims = settings['ylims']['Gbs']

    for table_name, table_data in data_series.items():
        fig, ax1 = plt.subplots()
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax1.set_xlabel(settings['labels']['time'])
        ax1.set_ylabel(settings['labels']['slices'], color=slices_color)

        ax1.plot(table_data['time'], table_data['slices'], color=slices_color)
        ax1.tick_params(axis='y', labelcolor=slices_color)
        if slices_ylims:
            ax1.set_ylim(*slices_ylims)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        ax2.set_ylabel(settings['labels']['Gbs'], color=gbs_color)  # we already handled the x-label with ax1
        ax2.plot(table_data['time'], table_data['Gbs'], color=gbs_color)
        ax2.tick_params(axis='y', labelcolor=gbs_color)
        if gbs_ylims:
            ax2.set_ylim(*gbs_ylims)

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        draw.save_as('output/wykres-{}.pdf'.format(table_name))


if __name__ == '__main__':
    main()
