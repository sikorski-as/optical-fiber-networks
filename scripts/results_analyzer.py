import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import jsonpickle
import itertools
from functools import partial


class default_setup:
    results_path = 'C:\\users\\user\\Desktop\\optical-fiber-networks\\results\\{}\\'
    output_path = 'C:\\users\\user\\Desktop\\optical-fiber-networks\\output\\'
    # output_path = 'C:\\users\\user\\Desktop\\inzynierka\\wyniki-artykul\\'
    cumulative_output_name = 'cumulative'

    # funkcje, które mapują nazwa_folderu -> True/False
    # True - rysuj, False - pomiń
    filters = []

    cumulate_plots = False

    save = False
    pdf = True
    png = True
    legend = True
    grid = True
    grid_formatting = {
        'color': 'b',
        'alpha': 0.1,
        'axis': 'both',
        'which': 'major'
    }

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
        mean = 'Avg'
        min = 'Min'

    class axis:
        x_scale = 'log'
        y_scale = 'linear'

        x_label = 'number of evaluations'
        y_label = 'cost [cost units]'

    # get name of the algorithm from a folder name
    mapping_func = lambda folder_name: folder_name.split('_')[1]  # <nazwa_sieci>_<alg_name>_<whatever>

    # map name of the algorithm to a nice label
    mappings = {
        # 'bee': 'Bees',
        # 'har': 'Harmony',
        # 'hill': 'Hillclimbing',
        # 'hyb': 'Hybryd',
        # 'gen': 'Genetic',

        'bee': 'BA',
        'har': 'HS',
        'hill': 'HC',
        'hyb': 'HY',
        'gen': 'EA',
    }

    linewidth_default = 1.5
    linewidth_mappings = {
        # 'gen': 4
    }

    linestyle_mappings = {
        'bee': 'dashed',    # (5, 5),  # dashed
        'har': 'dotted',    # (1, 1),  # dotted
        'hill': 'dashdot',  # (3, 5, 1, 5),  # dashdot
        'hyb': 'dashed',    # (5, 5),  # dashed
        'gen': 'solid',     # ()  # solid
    }

    color_mappings = {
        'bee': 'red',
        'har': 'darkmagenta',
        'hill': 'black',
        'hyb': 'blue',
        'gen': 'green'
    }

    map_times_to_function_calls = True
    # ile wywołań funkcji celu na każdą iterację poszczególnego algorytmu
    @staticmethod
    def map_times_to_function_calls_func(timeline, name) -> list:
        timeline_length = len(timeline)
        if name == 'hyb':
            genetic_calls = itertools.repeat(200, 100)
            hill_calls = itertools.repeat(1, 10000)
            values = list(
                itertools.accumulate(
                    itertools.chain(genetic_calls, hill_calls)
                )
            )
            return values[:timeline_length] if len(values) > timeline_length else values

        else:
            # ile wywołań na iterację
            function_calls = {'bee': 108, 'har': 1, 'hill': 1, 'gen': 200}[name]
            return list(
                itertools.accumulate(itertools.repeat(function_calls, timeline_length))
            )


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
                partial_times.append(result['Partial times'])
                # partial_time.append(setup.map_times_to_function_calls_func(result['Partial times'], setup.mapping_func(folder_name)))

    # poniżej pokazuje ile średnio było wywołań danego algosa dla danej sieci
    alg_name = setup.mapping_func(folder_name)
    print('folder_name:', folder_name)
    print('alg name:', alg_name)
    summed = 0
    for ptime in partial_time:
        func_calls = setup.map_times_to_function_calls_func(ptime, alg_name)
        # print('func_calls len', len(func_calls))
        summed += func_calls[-1]
    print('mean objective func calls:', summed / len(partial_time), '\n')

    align_lengths(partial_scores)
    scores = np.array(partial_scores)

    timeline = create_timeline(partial_time)

    align_lengths(partial_time)
    times = np.array(partial_time)

    final_scores = [score[-1] for score in scores]
    # plt.boxplot(final_scores)
    # plt.show()

    mean = scores.mean(axis=0)
    max = scores.max(axis=0)
    min = scores.min(axis=0)
    std = scores.std(axis=0)

    mean_time = times.mean(axis=0)
    max_time = times.max(axis=0)
    min_time = times.min(axis=0)
    std_time = times.std(axis=0)

    # print(folder_name)
    print("Min score: {} Max score: {} Mean score: {} Std score: {}".format(min[-1], max[-1], mean[-1], std[-1]))
    # print("& {0:.1f} & {0:.1f} & {0:.1f} & {0:.1f}".format(min[-1], max[-1], mean[-1], std[-1]))

    # print(folder_name)
    print("Min time: {} Max time: {} Mean time: {} Std score: {}".format(min_time[-1], max_time[-1], mean_time[-1], std_time[-1]))

    print()
    print('%' * 65)
    print('%' * 65)
    print('%' * 65)
    print()

    with open(folder_path + 'summary.txt', mode='w') as f:
        f.write(jsonpickle.encode([mean, max, min, std, timeline]))


def data_loading(main_folder, setup=default_setup):
    folder_path = setup.results_path.format(main_folder)

    for i, folder in enumerate(os.listdir(folder_path)):
        folder_name = '{}\\{}'.format(main_folder, folder)
        load_results_data(folder_name)


def boxplots(main_folder, action, setup=default_setup):
    folder_path = setup.results_path.format(main_folder)
    folders = os.listdir(folder_path)
    for f in setup.filters:
        folders = filter(f, folders)

    for folder in folders:
        folder_name = '{}\\{}'.format(main_folder, folder)
        times, scores, label = action(folder_name, setup=setup) # dodać appendowanie do listy

    plt.title(main_folder)
    plt.boxplot(scores)
    plt.show()


def boxplot(folder_name, setup=default_setup):
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


def plot_one(folder_name: str, setup=default_setup):
    folder_path = setup.results_path.format(folder_name)
    plt.figure()

    with open(folder_path + 'summary.txt') as f:
        mean, max, min, std, timeline = jsonpickle.decode(f.read())

        alg_name = setup.mapping_func(folder_name)
        if setup.map_times_to_function_calls:
            timeline = setup.map_times_to_function_calls_func(timeline, alg_name)

        max = list(itertools.chain([max[0]], max))
        mean = list(itertools.chain([mean[0]], mean))
        min = list(itertools.chain([min[0]], min))
        timeline = list(itertools.chain([0], timeline))

        print(folder_name)
        # plt.title(folder_name + ', min ({},{}) '.format(round(timeline[-1]), round(min[-1])))

        if setup.grid:
            plt.grid(**setup.grid_formatting)

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

    if setup.grid:
        plt.grid(**setup.grid_formatting)

    for folder in folders:
        dirname = '{}\\{}'.format(main_folder, folder)
        action(dirname, setup=setup)

    if setup.legend:
        plt.legend()

    if setup.axis.x_scale == 'log':
        plt.xlim(left=1)

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

        alg_name = setup.mapping_func(folder_name)
        if setup.map_times_to_function_calls:
            timeline = setup.map_times_to_function_calls_func(timeline, alg_name)

        mean = list(itertools.chain([mean[0]], mean))
        timeline = list(itertools.chain([0], timeline))

        print(folder_name)

        color = setup.color_mappings[setup.mapping_func(folder_name)]
        linestyle = setup.linestyle_mappings[setup.mapping_func(folder_name)]

        linewidth = setup.linewidth_mappings.get(setup.mapping_func(folder_name), setup.linewidth_default)
        if type(linestyle) == tuple:
            meanline, = plt.plot(timeline, mean, dashes=linestyle, color=color, linewidth=linewidth)
        else:
            meanline, = plt.plot(timeline, mean, linestyle=linestyle, color=color, linewidth=linewidth)

        if setup.legend:
            legend_label = setup.mappings[setup.mapping_func(folder_name)]
            meanline.set_label(legend_label)

        plt.xscale(setup.axis.x_scale)
        plt.yscale(setup.axis.y_scale)

        # plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)

        plt.gca().yaxis.set_major_formatter(tick.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
        plt.subplots_adjust(left=0.14, right=0.95)

        plt.xlabel(setup.axis.x_label, fontweight='bold')
        plt.ylabel(setup.axis.y_label, fontweight='bold')


if __name__ == '__main__':
    class cumulative_pol(default_setup):
        output_path = default_setup.output_path + '/'
        save = True
        cumulate_plots = True
        cumulative_output_name = 'pol5_cumulative'
        filters = [
            lambda folder_name: folder_name.endswith('_5'),
            lambda folder_name: 'hyb' not in folder_name
        ]

    class setup_pol(default_setup):
        output_path = default_setup.output_path + 'pol5/'
        save = True
        filters = [
            lambda folder_name: folder_name.endswith('_5'),
        ]

    class setup_ger(default_setup):
        output_path = default_setup.output_path + 'ger10/'
        save = True
        filters = [
            lambda folder_name: folder_name.endswith('_10')
        ]

    class cumulative_ger(default_setup):
        output_path = default_setup.output_path + '/'
        save = True
        cumulate_plots = True
        cumulative_output_name = 'ger_cumulative'
        filters = [
            lambda folder_name: folder_name.endswith('_10'),
            lambda folder_name: 'hyb' not in folder_name
        ]

    class cumulative_janos(default_setup):
        output_path = default_setup.output_path + '/'
        save = True
        cumulate_plots = True
        cumulative_output_name = 'janos1_cumulative'
        filters = [
            lambda folder_name: folder_name.endswith('_1'),
            lambda folder_name: 'hyb' not in folder_name
        ]

    class setup_janos(default_setup):
        output_path = default_setup.output_path + 'janos1/'
        save = True
        filters = [
            lambda folder_name: folder_name.endswith('_1'),
        ]

    class cumulative_usa_can(default_setup):
        output_path = default_setup.output_path + '/'
        save = True
        cumulate_plots = True
        cumulative_output_name = 'usa_can_01_cumulative'
        filters = [
            lambda folder_name: folder_name.endswith('_01'),
            lambda folder_name: 'hyb' not in folder_name
        ]

    # class cumulative_ger10(default_setup):
    #     save = True
    #     cumulate_plots = True
    #     cumulative_output_name = 'ger10_cumulative'
    #
    # class cumulative_ger15(default_setup):
    #     save = True
    #     cumulate_plots = True
    #     cumulative_output_name = 'ger15_cumulative'
    #
    # class cumulative_ger20(default_setup):
    #     save = True
    #     cumulate_plots = True
    #     cumulative_output_name = 'ger20_cumulative'

    # data_loading('pol')
    plot_cumulative('pol', plot_one_cumulative, cumulative_pol)
    # plot_many('pol', plot_one, setup_pol)

    # data_loading('ger')
    plot_cumulative('ger', plot_one_cumulative, cumulative_ger)
    # plot_many('ger', plot_one, setup_ger)

    # data_loading('janos')
    # plot_cumulative('janos', plot_one_cumulative, cumulative_janos)
    # plot_many('janos', plot_one, setup_janos)

    # data_loading('can')
    plot_cumulative('can', plot_one_cumulative, cumulative_usa_can)
    # plot_many('can', plot_one, ...)

    # data_loading('ger10')
    # plot_cumulative('ger10', plot_one_cumulative, cumulative_ger10)

    # data_loading('ger15')
    # plot_cumulative('ger15', plot_one_cumulative, cumulative_ger15)

    # data_loading('ger20')
    # plot_cumulative('ger20', plot_one_cumulative, cumulative_ger20)
