import os
import numpy as np
import matplotlib.pyplot as plt
import jsonpickle
import itertools
from functools import partial


class default_setup:
    results_path = 'C:\\users\\user\\Desktop\\optical-fiber-networks\\results\\{}\\'
    output_path = 'C:\\users\\user\\Desktop\\inzynierka-wyniki\\'
    cumulative_output_name = 'cumulative'
    filters = []

    cumulate_plots = False

    save = False
    pdf = True
    png = True
    legend = True

    class linestyle:
        max = 'dotted'
        mean = 'solid'
        min = 'dashed'

    class color:
        max = 'red'
        mean = 'green'
        min = 'blue'

    class legend_labels:
        max = 'Max'
        mean = 'Średnia'
        min = 'Min'

    class axis:
        x_scale = 'log'
        y_scale = 'linear'

        x_label = 'Czas [s]'
        y_label = 'Funkcja kosztu'

    # get name of the algorithm from a folder name
    mapping_func = lambda folder_name: folder_name.split('_')[-2]

    # map name of the algorithm to a nice label
    mappings = {
        'bee': 'Pszczeli',
        'har': 'Harmony',
        'hill': 'Wspinaczkowy',
        'hyb': 'Hybryda',
        'gen': 'Genetyczny',

        # 'bee': 'BA',
        # 'har': 'HS',
        # 'hill': 'HC',
        # 'hyb': 'HEA',
        # 'gen': 'GA',
    }

    linestyle_mappings = {
        'bee': 'solid',
        'har': 'solid',
        'hill': 'solid',
        'hyb': 'solid',
        'gen': 'solid'
    }

    color_mappings = {
        'bee': 'yellow',
        'har': 'orange',
        'hill': 'black',
        'hyb': 'blue',
        'gen': 'green'
    }


def align_lengths(scores: list):
    max_len = max([len(row) for row in scores])

    for i, row in enumerate(scores):
        size = len(row)
        if size < max_len:
            for _ in range(max_len - size):
                row.append(row[-1])


def create_timeline(scores: list):
    max_len = max([len(row) for row in scores])

    longest_attempts = [row for row in scores if len(row) == max_len]
    time = [np.mean([row[i] for row in longest_attempts]) for i in range(max_len)]
    return time


def load_results_data(folder_name, setup=default_setup):
    folder_path = setup.results_path.format(folder_name)

    partial_scores = []
    partial_time = []

    for i, file in enumerate(os.listdir(folder_path)):
        if not file.endswith('.txt') and i > 2:
            with open(folder_path + file, mode='r') as f:
                result = jsonpickle.decode(f.read())
                partial_scores.append(result['Partial scores'])
                partial_time.append(result['Partial times'])

    align_lengths(partial_scores)
    scores = np.array(partial_scores)

    timeline = create_timeline(partial_time)

    align_lengths(partial_time)
    times = np.array(partial_time)

    mean = scores.mean(axis=0)
    max = scores.max(axis=0)
    min = scores.min(axis=0)
    std = scores.std(axis=0)

    mean_time = times.mean(axis=0)
    max_time = times.max(axis=0)
    min_time = times.min(axis=0)
    std_time = times.std(axis=0)

    print(folder_name)
    print("Min: {} Max: {} Mean: {} Std: {}".format(min[-1], max[-1], mean[-1], std[-1]))
    print("& {0:.1f} & {0:.1f} & {0:.1f} & {0:.1f}".format(min[-1], max[-1], mean[-1], std[-1]))

    print(folder_name)
    print("Min: {} Max: {} Mean: {} Std: {}".format(min_time[-1], max_time[-1], mean_time[-1], std_time[-1]))

    with open(folder_path + 'summary.txt', mode='w') as f:
        f.write(jsonpickle.encode([mean, max, min, std, timeline]))


def data_loading(main_folder, setup=default_setup):
    folder_path = setup.results_path.format(main_folder)

    for i, folder in enumerate(os.listdir(folder_path)):
        folder_name = '{}\\{}'.format(main_folder, folder)
        load_results_data(folder_name)


def plot_one(folder_name: str, setup=default_setup):
    folder_path = setup.results_path.format(folder_name)
    plt.figure()

    with open(folder_path + 'summary.txt') as f:
        mean, max, min, std, timeline = jsonpickle.decode(f.read())

        max = list(itertools.chain([max[0]], max))
        mean = list(itertools.chain([mean[0]], mean))
        min = list(itertools.chain([min[0]], min))
        timeline = list(itertools.chain([0], timeline))

        print(folder_name)
        # plt.title(folder_name + ', min ({},{}) '.format(round(timeline[-1]), round(min[-1])))

        maxline, = plt.plot(timeline, max, linestyle=setup.linestyle.max, color=setup.color.max)
        maxline.set_label(setup.legend_labels.max)

        minline, = plt.plot(timeline, min, linestyle=setup.linestyle.min, color=setup.color.min)
        minline.set_label(setup.legend_labels.min)

        meanline, = plt.plot(timeline, mean, linestyle=setup.linestyle.mean, color=setup.color.mean)
        meanline.set_label(setup.legend_labels.mean)

        plt.xscale(setup.axis.x_scale)
        plt.yscale(setup.axis.y_scale)

        plt.xlabel(setup.axis.x_label, fontweight='bold')
        plt.ylabel(setup.axis.y_label, fontweight='bold')

        if setup.legend:
            plt.legend()

        if setup.save:
            if setup.png:
                plt.savefig(setup.output_path + folder_name.replace('\\', '_') + '.png')
            if setup.pdf:
                plt.savefig(setup.output_path + folder_name.replace('\\', '_') + '.pdf')
        else:
            plt.show()


def plot_many(main_folder, action, setup=default_setup):
    folder_path = setup.results_path.format(main_folder)
    folders = os.listdir(folder_path)
    for f in setup.filters:
        folders = filter(f, folders)

    for folder in folders:
        folder_name = '{}\\{}'.format(main_folder, folder)
        action(folder_name, setup=setup)


def plot_cumulative(main_folder, action, setup=default_setup):
    folder_path = setup.results_path.format(main_folder)
    folders = os.listdir(folder_path)
    for f in setup.filters:
        folders = filter(f, folders)

    plt.figure()
    for folder in folders:
        dirname = '{}\\{}'.format(main_folder, folder)
        action(dirname, setup=setup)

    if setup.legend:
        plt.legend()

    if setup.save:
        if setup.png:
            plt.savefig(setup.output_path + '{}.png'.format(setup.cumulative_output_name))
        if setup.pdf:
            plt.savefig(setup.output_path + '{}.pdf'.format(setup.cumulative_output_name))
    else:
        plt.show()


def plot_one_cumulative(folder_name, setup=default_setup):
    folder_path = setup.results_path.format(folder_name)

    with open(folder_path + 'summary.txt') as f:
        mean, max, min, std, timeline = jsonpickle.decode(f.read())

        mean = list(itertools.chain([mean[0]], mean))
        timeline = list(itertools.chain([0], timeline))

        print(folder_name)

        color = setup.color_mappings[setup.mapping_func(folder_name)]
        linestyle = setup.linestyle_mappings[setup.mapping_func(folder_name)]
        meanline, = plt.plot(timeline, mean, linestyle=linestyle, color=color)

        if setup.legend:
            legend_label = setup.mappings[setup.mapping_func(folder_name)]
            meanline.set_label(legend_label)

        plt.xscale(setup.axis.x_scale)
        plt.yscale(setup.axis.y_scale)

        plt.xlabel(setup.axis.x_label, fontweight='bold')
        plt.ylabel(setup.axis.y_label, fontweight='bold')


if __name__ == '__main__':
    class cumulative_pol(default_setup):
        output_path = default_setup.output_path + '/'
        save = True
        cumulate_plots = True
        cumulative_output_name = 'pol5_cumulative'
        filters = [
            lambda folder_name: folder_name.endswith('_5')
        ]


    class cumulative_ger(default_setup):
        output_path = default_setup.output_path + '/'
        save = True
        cumulate_plots = True
        cumulative_output_name = 'ger10_cumulative'
        filters = [
            lambda folder_name: folder_name.endswith('_10')
        ]


    class setup_pol(default_setup):
        output_path = default_setup.output_path + 'pol5/'
        save = True
        filters = [
            lambda folder_name: folder_name.endswith('_5')
        ]


    class setup_ger(default_setup):
        output_path = default_setup.output_path + 'ger10/'
        save = True
        filters = [
            lambda folder_name: folder_name.endswith('_10')
        ]

    data_loading('pol')
    data_loading('ger')
    plot_cumulative('pol', plot_one_cumulative, cumulative_pol)
    plot_cumulative('ger', plot_one_cumulative, cumulative_ger)
    plot_many('pol', plot_one, setup_pol)
    plot_many('ger', plot_one, setup_ger)
