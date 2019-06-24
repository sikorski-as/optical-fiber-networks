import networkx as nx


class Node:
	def __init__(self, name, long=0.0, lati=0.0):
		self.name = name
		self.long = long
		self.lati = lati
		self.x = 0
		self.y = 0


class Network(nx.Graph):
	def __init__(self, name='', *args, **kwargs):
		super(Network, self).__init__(*args, **kwargs)
		self.node_by_name = {}
		self.name = name

	@classmethod
	def load_native(cls, filename):
		network = cls(name=filename)
		with open(filename) as data_file:
			state = ''
			for line in data_file:
				if state == '':
					if line.startswith('NODES ('):
						state = 'NODES'
					elif line.startswith('LINKS ('):
						state = 'LINKS'
				else:
					if line.startswith(')'):
						state = ''
					elif state == 'NODES':
						name, _, long, lati, _, *_ = line.split()
						new_node = network.node_by_name[name] = Node(name, float(long), float(lati))
						network.add_node(new_node)
					elif state == 'LINKS':
						_, _, n1, n2, _, *_ = line.split()
						network.add_edge(network.node_by_name[n1], network.node_by_name[n2])
		return network

	def edge_middle_point(self, u, v, pixel_value=False):
		if self.has_edge(u, v):
			if pixel_value:
				return (u.x + v.x) / 2, (u.y + v.y) / 2
			else:
				return (u.long + v.long) / 2, (u.lati + v.lati) / 2
		else:
			raise ValueError(f'{u.name}-{v.name} edge does not exists')

	def add_pixel_coordinates(self, projection):
		for node in self.nodes:
			node.x = projection.get_x(node.long)
			node.y = projection.get_y(node.lati)
