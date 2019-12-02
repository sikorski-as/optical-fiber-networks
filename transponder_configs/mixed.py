from .ea import create_config as create_config_with_ea
from .ip import create_config as create_config_with_ip


def create_config(demand, transponders, n):
    optimal = create_config_with_ip(
        demanded_value=demand,
        tdata=transponders,
        n=1
    )
    configuration = create_config_with_ea(
        demand=demand,
        transponders=transponders,
        n=n,
        initial=optimal
    )
    return configuration
