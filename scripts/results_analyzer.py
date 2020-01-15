import os
import numpy as np
import matplotlib.pyplot as plt
import jsonpickle

results_path = 'C:\\users\\user\\Desktop\\optical-fiber-networks\\results\\{}\\'
desktop_path = 'C:\\users\\user\\Desktop\\abilene-wyniki\\'
# results_path = 'results\\{}\\'


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


def load_results_data(folder_name):
    folder_path = results_path.format(folder_name)

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
    # print(mean_time[-1])
    # print(max_time[-1])
    # print(min_time[-1])
    # print(std_time[-1])

    with open(folder_path + 'summary.txt', mode='w') as f:
        f.write(jsonpickle.encode([mean, max, min, std, timeline]))


def plot_data(folder_name: str):
    folder_path = results_path.format(folder_name)
    plt.figure()

    with open(folder_path + 'summary.txt') as f:
        mean, max, min, std, timeline = jsonpickle.decode(f.read())
        print(folder_name)
        print("Min: {} Max: {} Mean: {} Std: {}".format(min[-1], max[-1], mean[-1], std[-1]))
        # print(min[-1])
        # print(max[-1])
        # print(mean[-1])
        # print(std[-1])
        print(timeline)

        # plt.annotate(s='Min ({},{}) '.format(round(timeline[-1]), round(min[-1])), xy=(timeline[-1], round(min[-1])))
        plt.title(folder_name + ', min ({},{}) '.format(round(timeline[-1]), round(min[-1])))
        plt.plot(timeline, max, 'r')
        plt.plot(timeline, min, 'b')
        plt.plot(timeline, mean, 'g')
        plt.yscale('log')
        plt.xscale('log')
        # plt.show()
        plt.savefig(desktop_path + folder_name.replace('\\', '_') + '.png')


def data_loading(main_folder):
    folder_path = results_path.format(main_folder)

    for i, folder in enumerate(os.listdir(folder_path)):
        folder_name = '{}\\{}'.format(main_folder, folder)
        load_results_data(folder_name)


def data_ploting(main_folder):
    folder_path = results_path.format(main_folder)

    for i, folder in enumerate(os.listdir(folder_path)):
        folder_name = '{}\\{}'.format(main_folder, folder)
        plot_data(folder_name)


if __name__ == '__main__':
    data_loading("abilene")
    data_ploting("abilene")
