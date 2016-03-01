# Decorator function which asserts that passed, named, arguments are always iterable
# parameters:
#   - exception(boolean): define if function should throw exception or not.
#                         By default it will wrap input by simple arry
#   - args: parameter defines positional (array of positional) arguments that should be iterable
#   - kwargs: parameter defines keyword(array of keyword) arguments that should be iterable
# example:
#  @assert_kwarg_iterable(args=0, kwargs='x')
#  def some_function(x):
#       for v in x:
#           pass
#
#  some_function(1)        <-- now valid because args=0
#  some_function([1,2,3])  <-- valid without decorator
#  some_function(x=1)      <-- now valid because kwargs='x'
#  some_function(x=[1,2,3])<-- valid without decorator

# def single_element_itr(el):
#     yield el

def assert_arg_iterable(exception=False, **dec_kwargs):
    if 'kwargs' not in dec_kwargs and 'args' not in dec_kwargs:
        return lambda fun: fun

    if 'kwargs' in dec_kwargs and not hasattr(dec_kwargs['kwargs'], '__iter__'):
        dec_kwargs['kwargs'] = [dec_kwargs['kwargs']]

    if 'args' in dec_kwargs and not hasattr(dec_kwargs['args'], '__iter__'):
        dec_kwargs['args'] = [dec_kwargs['args']]

    def provider(fun):
        def wrap(*args, **kwargs):
            if 'kwargs' in dec_kwargs:
                for n in dec_kwargs['kwargs']:
                    if n in kwargs:
                        if not hasattr(kwargs[n], '__iter__'):
                            if not exception:
                                kwargs[n] = [kwargs[n]] #single_element_itr(kwargs[n])
                            else:
                                raise Exception("Argument %s should be iterable" % n)

            nargs = []*len(args)
            if 'args' in dec_kwargs:
                for i, val in enumerate(args):
                    if i in dec_kwargs['args']:
                        att = hasattr(val, '__iter__')
                        if not att and not exception:
                            nargs.append([kwargs[n]])#nargs.append(single_element_itr(kwargs[n]))
                        elif att:
                            nargs.append(val)
                        else:
                            raise Exception( "Argument %d should be iterable" % i)
                    else:
                        nargs.append(val)
            else:
                nargs = args

            return fun(*nargs, **kwargs)
        return wrap
    return provider

# Empty functin doing nothig. This can be used for some function replacement
# e. g. following line will stop displaying all plots:
#   plt.show = empty
#

def empty(*args, **kwargs):
    pass


# Function wich fixes named arguments in other function
# parameters:
#   - fun: function that should be wrapped
#   - override(boolean): switch defining if fixed arguments should be replaced if user will pass kwarg argument
#   - **dec_kwargs: keyword arguments which should be always passed to function
# example 1:
#   bluePlot = fixargument(plt.plot, color="b", linewidth=2)
#   x=range(0,10); y=sin(x)
#   bluePlot(x,y) <-- draw blue line plot with width equal to 2
#                 <-- under the hood it produces plt.plot(x, y, color="b", linewidth=2)
# example 2 (redefine existing function)
#   plt.figure = fixargument(plt.figure, figsize=(20,10))
#   after that any use of plt.figure will always add figsize=(20,10) to function call


def fixargument(fun, override=True, **dec_kwargs):
    def wrap(*args,**kwargs):
        for key, val in dec_kwargs.iteritems():
            if key not in kwargs or override:
                kwargs[key]=val
        # if len(args)==0 and not len(kwargs)==0:
        #     fun(**kwargs)
        # elif not len(args)==0 and len(kwargs)==0:
        #     fun(*args)
        # elif len(args)==0 and len(kwargs)==0:
        #     fun()
        # else:
        return fun(*args,**kwargs)
    wrap.__name__ = fun.__name__
    return wrap


# Helper classes for "join" function
class ToPositionedFunction:
    def __init__(self, pos):
        self.pos = pos

    def __call__(self, *args, **kwargs):
        fun = kwargs["fun"]
        kwargs.pop("fun")
        pos = kwargs.pop("pos")

        if pos in self.pos:
            return fun(*args, **kwargs)

        return fun()

    def clear(self):
        pass


class ToNamedFunction:
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        fun = kwargs["fun"]
        kwargs.pop("fun")
        kwargs.pop("pos")

        for n in self.name:
            if n == fun.__name__:
                return fun(*args, **kwargs)

        return fun()

    def clear(self):
        pass


class Chain:
    @assert_arg_iterable(args=1, kwargs='noUnbind')
    def __init__(self, noUnbind=[]):
        self.prev = None
        self.firstDone = False
        self.noUnbind = noUnbind

    def __call__(self, *args, **kwargs):
        fun = kwargs["fun"]
        kwargs.pop("fun")
        pos = kwargs.pop("pos")
        if not self.firstDone:
            self.prev = fun(*args, **kwargs)
            self.firstDone = True
        elif self.prev:
            if pos not in self.noUnbind:
                try:
                    self.prev = fun(*self.prev)
                except TypeError:
                    self.prev = fun(self.prev)
            else:
                self.prev = fun(self.prev)
        else:
            self.prev = fun()

        return self.prev

    def clear(self):
        self.prev = None
        self.firstDone = False


# Function which joins passed function. Depending on "argsFor" parameter or "evaluator"
# different approach is applied for functions call.
# arguments:
#   - variable number of functions
#   - "argsFor" keyword argument defines to which functions should arguments be passed
#   - "evaluator" - explicit selection of evaluator class (on of ToPositionedFunction,ToNamedFunction or Chain)
# result:
#   - new composed function
#
# example 1 (pass argument to selected function):
#       makePlot = join(plt.figure, plt.plot, plt.show, argsFor="plot")
#   or
#       makePlot = join(plt.figure, plt.plot, plt.show, argsFor=1)
#   and usage:
#       x=range(0,10); y=sin(x)
#       makePlot(x,y) <-- calls plt.figure, plt.plot(x,y), plt.show()
#
# example 2(chain function call-result from one is passed to next):
#       def sumab(a,b):
#           return a+b
#
#       def pow2(c):
#           return c**2
#
#       sumPow2 = join(sumab,pow2)
#
#       print sumPow2(1,2)
#
# example 3 (chain call without unbinding list to multiple arguments - explicit evaluator selection)
#
#   define some helper function
#       def minmax(some_list):
#           return min(some_list), max(some_list)
#
#   define joined function (result from minmax is not unbind and tuple, not multiple args, is passed to sum):
#       minmaxSum = join(minmax, sum, evaluator=Chain(noUnbind=1))
#   or (input can be list of function where arguments should not be bind):
#       minmaxSum = join(minmax, sum, evaluator=Chain(noUnbind=[1]))
#   or (shortly)
#       minmaxSum = join(minmax, sum, evaluator=Chain(1))
#
#   usage:
#       print minmaxSum([sin(i) for i in range(0,10)])
#
#   Note: Chain by default tries to unbind all arguments, however if there will raise exception then this
#         function will try to execute function without unbinding. So your first shot in case of chain execution
#         should be just: minmaxSum = join(minmax,sum)


#from itertools import islice

@assert_arg_iterable(kwargs='argsFor')
def join(*functions, **j_kwargs):

    evaluator = None
    if "argsFor" in j_kwargs and "evaluator" in j_kwargs:
        raise Exception("You can't use argsFor and evaluator parameters together")

    if "argsFor" in j_kwargs:
        argsFor = j_kwargs['argsFor']
        argsFirstVal = next( iter(argsFor) )
        if isinstance(argsFirstVal, int):
            evaluator = ToPositionedFunction(argsFor)
        elif isinstance(argsFirstVal, str):
            evaluator = ToNamedFunction(argsFor)
        # elif hasattr(argsFirstVal, '__call__'):
        #     fnames=[]
        #     for f in argsFor:
        #         fnames.append( f.__name__ )
        #     evaluator = ToNamedFunction(fnames)
        else:
            raise Exception("Not known conversion from",type(argsFirstVal), " to function evaluator, allowed int and string")
    elif 'evaluator' in j_kwargs:
        evaluator = j_kwargs['evaluator']
    else:
        evaluator = Chain()

    def wrap(*args, **kwargs):
        res = None

        for f_id, f in enumerate(functions):
            kwargs["fun"] = f
            kwargs["pos"] = f_id
            res = evaluator(*args, **kwargs)
        evaluator.clear()
        return res
    return wrap


# Function joining provided function in the way that
# provided arguments are passed to all functions and
# result is stored in the list.
#
# example:
#   zipped = fzip(min,max)
#   print zipped( [sin(x) for x in np.linspace(0,20,0.1)] )
# or shortly:
#   print fzip(min,max)([sin(x) for x in np.linspace(0,20,0.1)])
def fzip(*functions):
    def wrap(*args, **kwargs):
        res=list()
        for f in functions:
            res.append(f(*args,**kwargs))
        return res
    return wrap


def substract(a,b):
    return a - b