from django.template import Template
from django.template import Context
from django.conf import settings
import os
import json
import itertools
from collections import namedtuple
import time
import math
from functools import partial

settings.configure() #ignoring django bullshit

variables = json.load(open("variables.json"))
template = Template(open("control.template").read())

class Variable:
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __str__(self):
		return self.name + "=" + str(self.value)

combinations = []
for var in variables["iterables"]:
	values = []
	for value in var["values"]:
		values.append(Variable(var["name"], value))
	combinations.append(values)

def nextOddInteger(num):
	ceil = math.ceil(num)
	return ceil if ceil % 2 == 1 else ceil +1

def atomLine(arr):
	return "atom\t" + "\t".join(map(str, arr[0:3])) + " " + arr[3]

def cordByPos(pos, atoms):
	return atoms[pos]

def average(atoms, cordNum):
	return mean(map(partial(cordByPos, cordNum), atoms))

def origin(atoms):
	return map(partial(average, atoms), [0, 1, 2])

def mean(arr):
	l = len(arr)
	return float(sum(arr)) / l if  l > 0 else float('nan')

def subtract(pair):
	return pair[0] - pair[1]

def square(x):
	return x * x

def distance(originCords, atomCords):
	diffs = map(subtract, zip(atomCords, originCords))
	return math.sqrt(sum(map(square, diffs)))

def maxDistance(origin, atoms):
	return max(map(partial(distance, origin), atoms))

def constant(name):
	return next(const["value"] for const in variables["constants"] if const["name"] == name)

def cubeOutput(num):
	return "output cube eigenstate {0}\ncube filename eigen{0}.cube".format(num)

def cubeOutputs(num):
	return "\n".join(map(cubeOutput, range(1, num + 1)))

atoms = variables["atoms"]
originCords = map(lambda x: round(x, 3), origin(atoms))
cube_origin = " ".join(map(str, originCords))
voxel_size = constant("voxel_size")
cube_edge = nextOddInteger(maxDistance(originCords, atoms) * 2 / voxel_size)
cube_outputs = cubeOutputs(constant("eigen_cubes_number"))

geometry = "\n".join(map(atomLine, atoms))
 
for comb in itertools.product(*combinations):
	directory = "-".join(map(str, comb))
	if not os.path.exists(directory):
		os.makedirs(directory)
		
		# create a context for a template
		dic = dict([(str(x.name), x.value) for x in comb])
		for constant in variables["constants"]:
			dic[constant["name"]] = constant["value"]
		dic["cube_origin"] = cube_origin
		dic["cube_edge"] = cube_edge
		dic["cube_outputs"] = cube_outputs

		context = Context(dic)

		# render a template in a control file
		open(directory + "/control.in", "w").write(template.render(context))

		# output a generated geometry into a geometry file
		open(directory + "/geometry.in", "w").write(geometry)

		os.chdir(directory)

		start = time.time()
		print "Executing FHI-AIMS on " + directory + "..."
		os.system("/home/john/Desktop/FHI-AIMS/aims_110113/bin/aims.110113.mpi.x > output.out")
		print "Executed FHI-AIMS on " + directory + " in " + str(time.time() - start) + " secs"

		os.chdir("..")