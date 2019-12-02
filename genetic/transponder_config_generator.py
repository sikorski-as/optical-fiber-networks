from transponders import Transponder, find_configs_for_range, save_config
from transponders import ip, ea


def main():
    a, b, n = 1, 3001, 3
    tdata = [
        Transponder(transfer=40, width=4, cost=2),
        Transponder(transfer=100, width=4, cost=5),
        Transponder(transfer=200, width=8, cost=7),
        Transponder(transfer=400, width=12, cost=9),
    ]

    # print('generating with integer programming...')
    # ip_configs = find_configs_for_range(a, b, n, tdata, ip.create_config, stats=True)
    # save_config('data/transponder_config_ip.json', ip_configs)
    # print('finished with integer programming.')

    print('generating with genetic...')
    genetic_configs = find_configs_for_range(a, b, n, tdata, ea.create_config, stats=True)
    save_config('data/transponder_config_genetic.json', genetic_configs)
    print('finished with genetic programming.')


if __name__ == '__main__':
    main()
