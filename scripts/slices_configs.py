class polska:
    out_file = 'data/polska4400.out'
    data_file = 'data/polska4400.dat'
    sndlib_file = 'data/polska.txt'
    nslices = 384
    npaths = 3

    download_map = False
    draw_map = False
    map_file = 'data/polska.png'
    save_output = True
    output_image_file = 'output/polska4400.pdf'
    padding = 125
    size = (1024, 1024)

    country = 'pol'
    draw_border = True

    name_mapping = dict()


class nobel_germany:
    out_file = 'data/ger.out'
    data_file = 'data/ger.dat'
    sndlib_file = 'data/nobel-germany.txt'
    nslices = 384
    npaths = 3

    download_map = False
    draw_map = False
    map_file = 'data/nobel-germany.png'
    save_output = True
    output_image_file = 'output/ger.pdf'
    padding = 145
    size = (768, 1024)

    country = 'deu'
    draw_border = True

    name_mapping = dict()


class abilene:
    out_file = 'data/abilene2000.out'
    data_file = 'data/abilene2000.dat'
    sndlib_file = 'data/abilene.txt'
    nslices = 384
    npaths = 3

    download_map = False
    draw_map = False
    map_file = 'data/abilene.png'
    save_output = True
    output_image_file = 'output/abilene.pdf'
    padding = 135
    size = (1024, 768)

    country = 'usa'
    draw_border = True

    name_mapping = dict(
        ATLAM5='Atlanta1',
        ATLAng='Atlanta',
        CHINng='Chicago',
        DNVRng='Denver',
        HSTNng='Huston',
        IPLSng='Indianapolis',
        KSCYng='Kansas',
        LOSAng='Los Angeles',
        NYCMng='New York',
        SNVAng='San Francisco',
        STTLng='Seattle',
        WASHng='Washington'
    )
