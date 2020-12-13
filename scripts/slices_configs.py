class polska:
    sndlib_file = 'data/sndlib/native/polska/polska.txt'
    size = (512, 512)
    padding = 60
    data_file = 'data/pol1.dat'
    usage_file = 'data/usage.json'
    npaths = 3
    nslices = 192
    download_map = False
    draw_map = False
    map_file = 'data/polska.png'
    draw_border = True
    country = 'pol'
    name_mapping = {
        'Lodz': 'Łódź',
        'Bialystok': 'Białystok',
        'Kolobrzeg': 'Kołobrzeg',
        'Poznan': 'Poznań',
        'Krakow': 'Kraków',
        'Wroclaw': 'Wrocław',
        'Warsaw': 'Warszawa',
        'Rzeszow': 'Rzeszów',
        'Gdansk': 'Gdańsk',
        'Bydgoszcz': 'Bydgoszcz',
        'Katowice': 'Katowice',
        'Szczecin': 'Szczecin',
    }
    draw_usage = True
    draw_topology = True

    save_output = True
    output_image_file = 'results/polska_case4_tags.pdf'
