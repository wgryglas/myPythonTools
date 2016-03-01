from function import fixargument
from function import join
from matplotlib.pyplot import xticks
from matplotlib.pyplot import yticks
from matplotlib.pyplot import figure
from matplotlib.pyplot import plot
from matplotlib.pyplot import show

# Function fixing figure size and returning new function

# example:
# plt.figure = fix_figure_size(plt.figure, w=20, h=10)
# ...
# plt.figure() <-- opens window with width=20 and height=10


def fix_figure_size(figureFunction, **d_kwargs):
    w = 5
    h = 5
    if 'w' in d_kwargs:
        w = d_kwargs['w']

    if 'h' in d_kwargs:
        h = d_kwargs['h']

    return fixargument(figureFunction, figsize=(w, h))


# Function computing spacing and latex formatting for some array of values.
# parameters:
#   constant_latex - define latex constant format, e.g. "pi", "alpha"
#   constant_value - assign numerical value to constant
#   num - array of values or just range [ -10, 10 ]
#   den - define fraction of constant which should be included (e.g. den=0.5 will produce 0,1/2pi,pi,3/2pi ...)
# return values:
#   values - array of numbers corresponding to its latex string representation
#   strings - array of latex format for specified numbers
#
# example (x is array of float values x=[0, 0.5, 1, ..., 6 ]):
#   tickVal, tickStrings = latex_range("pi", numpy.pi, num=x, den=0.5)
#   where: tickVal = [0, 0.5*pi, 1*pi ] (result is numbers array)
#          tickStrings=[0, $\frac{1}{2}\pi$, $\pi$]
#
# Usage example for pyplot:
#   x = [0.1*i for i in range(0,10)]
#   y = numpy.sin(x)
#   plt.figure()
#   plt.plot(x,y)
#   plt.xticks( *latex_range("pi", numpy.pi, num=x, den=2)
#   plt.show()


def latex_range(constant_latex, constant_value, num, den=1):

    if hasattr(den, '__iter__'):
            raise Exception("Denominator have to be single integer")

    num = range(int(round(float(min(num))/(constant_value*den), 0)), int(round(float(max(num))/(constant_value*den),0)+1))

    strings = ['']*len(num)
    values = [0.]*len(num)
    deninv = int(1./den)

    for i, n in enumerate(num):

        values[i] = float(n)*den

        if values[i] == 0.:
            strings[i] = "$0$"
        elif values[i] == 1.:
            strings[i] = r'$\%s$' % constant_latex
        elif values[i].is_integer():
            strings[i] = r'$%d\%s$' % (values[i], constant_latex)
        else:
            strings[i] = r'$\frac{%d}{%d}\%s$' % (num[i], deninv, constant_latex)

        values[i] *= constant_value

    return values, strings

latex_xticks = join(latex_range, xticks)
latex_yticks = join(latex_range, yticks)


show_plot = join(figure, plot, show, argsFor=1)