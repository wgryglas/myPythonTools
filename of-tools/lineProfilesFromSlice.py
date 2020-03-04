#! /usr/bin/python

try:
    import numpy, matplotlib
except:
    print('The "numpy", "matplotlib" required. Install these python packages before usage')
    exit()


def loadData(path):
    import numpy as np
    pureData = np.loadtxt(path, skiprows=1, delimiter=',').T
    with open(path, 'r') as f:
        names = f.readline().replace('"', '').replace('\n', '').split(',')
    res = dict()
    for i, n in enumerate(names):
        res[n] = pureData[i]
    return res


def plot(data, dirX, dirY, var, precision, scale, pltDescription, useAutoscaling):
    """
    :param pltDescription: dictionary like object containing "type", "marker" and "linewidth" keys. Where type is
           matplotlib line style, marker is marker style
    """
    field = data[var]
    samplingDir = "Points:{}".format(dirY)
    spacingDir = "Points:{}".format(dirX)

    import numpy as np
    import matplotlib.pyplot as plt

    samplCoords = data[samplingDir]
    spacingCoords = data[spacingDir]

    # round spacing coords so that unique will be able to distinguish points collections with similar spacing coordinate
    if precision:
        spacingCoords = map(lambda d: np.round(d, precision), spacingCoords)

    spacingValues = sorted(np.unique(spacingCoords, return_index=True)[0])

    totalScale=scale

    if len(spacingValues) > 1 and useAutoscaling:
        # normalize data to make sure profiles will not overlap
        xdelta = spacingValues[1] - spacingValues[0]
        fmax = max(field)
        fmin = min(field)
        totalScale = (scale * xdelta / 2 / (fmax - fmin))
        field_scaled = field * totalScale
    else:
        field_scaled = field * scale

    for lineCoord in spacingValues:
        lineData = []
        fieldData = []
        for i, v in enumerate(spacingCoords):
            if v == lineCoord:
                lineData.append([samplCoords[i], field_scaled[i] + v])
                fieldData.append(field[i])

        lineData = np.array(lineData)
        fieldData = np.array(fieldData)

        sort = np.argsort(lineData[:, 0])
        lineData = lineData[sort, :]
        fieldData = fieldData[sort]


        plt.plot([lineCoord]*lineData.shape[0], lineData[:, 0], "--k")
        plt.plot(lineData[:, 1], lineData[:, 0], pltDescription['type'], marker=pltDescription['marker'], linewidth=pltDescription['linewidth'])

        #Add ref value labels
        if useAutoscaling:
            separtion = (lineData[-1,0]-lineData[0, 0]) / 20
            plt.text(lineCoord, lineData[-1,0] + separtion, "0")
            plt.text(lineData[-1, 1], lineData[-1, 0]+separtion, "{0:.1f}".format(fieldData[-1]))

    if pltDescription['grid']:
        plt.grid()

    plt.axis('equal')

    return totalScale



def showPlot():
    import matplotlib.pyplot as plt
    plt.show()


def saveFig(out):
    import matplotlib.pyplot as plt
    plt.savefig(out)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Plots multiple profiles of given field along defined direction. '
                                                 'As input accepts ParaView csv output of File/Save Data')
    parser.add_argument("path", type=str,
                        help='Path to *.csv file')
    parser.add_argument("field", type=str,
                        help='Choose what field should be plotted. Available fields according to *.csv file header')
    parser.add_argument("x", type=int, choices=[0, 1, 2],
                        help='Specify profiles spacing direction (direction along which subsequent sampling lines lie')
    parser.add_argument("y", type=int, choices=[0, 1, 2],
                        help='Specify profile sampling line direction')
    parser.add_argument("-o", "--output", type=str,
                        help='Specify file path where to store result image, if none image will appear only in window')
    parser.add_argument("-p", "--precision", type=int, default=3,
                        help="Specify coordinates precission. Algorithm will round points spacing coordinate to be able"
                             " to find subsequent lines with the equal coordinate value. If precission is to high "
                             "algorithm, might fail to group points in single sampling line. To high value (if damin "
                             "is very small) might group multiple lines")

    parser.add_argument("-t", "--type", type=str, default="-k",
                        help='''Matplotlib line type, default "-k" is black continuous line, ".k" is black dots,
                             " k"(space + k) is no line, see more
                             https://matplotlib.org/2.0.2/api/lines_api.html#matplotlib.lines.Line2D.set_linestyle)''')

    parser.add_argument("-m", "--marker", type=str, default=" ",
                        help='''Matplotlib marker type, default is none. Available types you can find here:
                                https://matplotlib.org/3.1.3/api/markers_api.html''')

    parser.add_argument("-l", "--linewidth", type=int, default=1,
                        help="Line width integer")

    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Tune parameter, scale factor for profiles. For example setting 2 would produce 2x wider "
                             "profiles. By default profiles will be scaled assert non overlpaing, but with this "
                             "parameter user might control it, as it might appear that profiles are not wide enough")

    parser.add_argument("-e", "--extra", type=str,
                        help="Specify additial file to add to the plot. For this data line properties are fixed, must use the same columns naming as original file, and the same dirs for spacing and line")

    parser.add_argument("-g", "--grid", action="store_true",
                        help="Adds grid to plot")

    args = parser.parse_args()

    d = loadData(args.path)
    pltSetup = {'type': args.type, 'marker': args.marker, 'linewidth': args.linewidth, 'grid':args.grid}
    pltScaling = plot(d, args.x, args.y, args.field, args.precision, args.scale, pltSetup, True)

    if args.extra:
        ed = loadData(args.extra)
        plot(ed, args.x, args.y, args.field, args.precision, pltScaling, {'type':' k', 'marker':'o', 'linewidth':1, 'grid':False}, False)

    if args.output:
        saveFig(args.output)
    else:
        showPlot()
