def fit_coords(inCurveX, inCurveY, outCurveX, outCurveY, tolerance=1e-6, print_optim_output=False):
    """
    Function which computes transformation of  x, y coordinates from
    curve(inCurveX,inCurveY) to other curve (outCurveX, outCurveY)
    :param inCurveX: x coordinates to be fitted
    :param inCurveY: y coordinates to be fitted
    :param outCurveX: x coordinates of desired curve
    :param outCurveY: y coordinates of desired curve
    :return: transformed x, y, and transformation parameters (dx, dy, angle)
    """
    import numpy as np
    from scipy.optimize import minimize

    def transform(x, y, p):
        # dx, dy, alpha = p
        # return x*np.cos(alpha) - y*np.sin(alpha) + dx, x*np.sin(alpha) + y*np.cos(alpha) + dy
        # dx, dy = p
        # return x + dx, y + dy
        return x, y + p

    def distance(p):
        x, y = transform(inCurveX, inCurveY, p)
        return max([min( (outCurveX - x[i])**2 + (outCurveY - y[i])**2 ) for i in range(len(x))])

    res = minimize(distance, np.zeros(1), method="Nelder-Mead", options={'xtol':tolerance})

    if print_optim_output:
        print res

    outX, outY = transform(inCurveX, inCurveY, res.x)
    return outX, outY, res.x