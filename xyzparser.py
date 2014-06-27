def isAtom(line):
	if len(line.split()) == 1:
		return True
	return line[0].isalpha()

def convertAtom(xyzAtom):
	xyzVals = xyzAtom.split()
	if len(xyzVals) == 1:
		return " "
	resultList = ["atom"]
	resultList.extend(xyzVals[1:3])
	resultList.append(xyzVals[0])
	return "\t".join(resultList)

def geometryFromXyz(xyz):
	xyzAtoms = filter(isAtom, xyz.splitlines())
	return "\n".join(map(convertAtom, xyzAtoms)[1:])