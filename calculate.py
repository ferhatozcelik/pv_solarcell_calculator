import numpy as np
from numpy import arange
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy.optimize import root
import func as fc
import base64
from io import BytesIO


def calculate(uploaded_file, light_source):
    pickerList = uploaded_file[:, :]
    picker = list()

    for row in pickerList:
        # if float(row[0]) * float(row[1]) <= 0:
        if float(row[0]) >= 0 and float(row[1]) <= 0:
            picker.append([row[0], row[1]])

    picker = np.array(picker)
    x = picker[:, 0]
    y = picker[:, 1]
    n = len(picker)

    max_x_y = 0
    maximum_value = 0

    for line in picker:
        value = abs(line[0]) * abs(line[1])
        if value > maximum_value:
            maximum_value = value
            max_x_y = line

    Vmax = max_x_y[0]
    Jmax = max_x_y[1]

    results = []

    results.append([call_function(fc.sq, 2, x, y, n), fc.sq, 2])
    results.append([call_function(fc.tr, 3, x, y, n), fc.tr, 3])
    results.append([call_function(fc.fo, 4, x, y, n), fc.fo, 4])
    results.append([call_function(fc.fi, 5, x, y, n), fc.fi, 5])
    results.append([call_function(fc.si, 6, x, y, n), fc.si, 6])
    results.append([call_function(fc.se, 7, x, y, n), fc.se, 7])
    results.append([call_function(fc.ei, 8, x, y, n), fc.ei, 8])
    results.append([call_function(fc.ni, 9, x, y, n), fc.ni, 9])
    results.append([call_function(fc.te, 10, x, y, n), fc.te, 10])

    results.append([e0(x, y, n), function_e0, 0])

    results.append([e1(x, y, n), function_e1, 0])

    results.append([e2(x, y, n), function_e2, 0])

    ma = results[0]
    for i in results:
        if i[0] > ma[0]:
            ma = i

    chosen_function = ma[1]
    degree = ma[2]
    if chosen_function == function_e0:
        popt1, _ = curve_fit(function_e0, x, y)
        a, b = popt1
        res = root(function_e0, 0.1, args=(a, b)).x[0]
        x_line = arange(min(x), max(x), 0.001)
        y_line = function_e0(x_line, a, b)
        xt = np.linspace(0, res, n)
        f = a + np.exp(b * xt)
    elif chosen_function == function_e1:
        popt1, _ = curve_fit(function_e1, x, y)
        a, b, c = popt1
        res = root(function_e1, 0.1, args=(a, b, c)).x[0]
        x_line = arange(min(x), max(x), 0.001)
        y_line = function_e1(x_line, a, b, c)
        xt = np.linspace(0, res, n)
        f = a * xt + np.exp(b * xt) + c
    elif chosen_function == function_e2:
        popt1, _ = curve_fit(function_e2, x, y)
        a, b, c, d = popt1
        res = root(function_e2, 0.1, args=(a, b, c, d)).x[0]
        x_line = arange(min(x), max(x), 0.001)
        y_line = function_e2(x_line, a, b, c, d)
        xt = np.linspace(0, res, n)
        f = a * xt + np.exp(b * xt) + c * xt ** 2 + d
    else:
        popt1, _ = curve_fit(chosen_function, x, y)
        a, b, c, d, e, f, g, h, i, j, k = popt1
        coeffs = [a, b, c, d, e, f, g, h, i, j, k]

        res = root(chosen_function, 0.1, args=(a, b, c, d, e, f, g, h, i, j, k)).x[0]
        x_line = arange(min(x), max(x), 0.001)
        y_line = chosen_function(x_line, a, b, c, d, e, f, g, h, i, j, k)
        xt = np.linspace(0, res, n)
        f = coeffs[degree]

        for index in range(1, degree + 1):
            f += coeffs[index - 1] * xt ** index

    df = np.gradient(f) / np.gradient(xt)
    Rs = 1 / df[n - 1]
    Rsh = 1 / df[0]
    Voc = res
    Jsc = 1000 * y[0]
    FF = ((Vmax * Jmax) / (Voc * Jsc)) * 100
    Pin = light_source
    EF = abs((Voc * Jsc * FF / 1000) / (0.001 * light_source))

    fig = plt.figure()

    ax1 = fig.add_subplot(111)

    ax1.set_xlabel('V(V)')
    ax1.set_ylabel('J(mA/cm??)')
    plt.plot(x, 1000 * y, 'ko', label='Experimental', markevery=1)
    plt.plot(xt, 1000 * f, 'r-', label='Fit, R??={}'.format(ma[0]))
    ax1.legend()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    img_data = base64.b64encode(buf.getbuffer()).decode("ascii")

    return [Rs, Rsh, Voc, Jsc, FF, EF, Pin, img_data, picker]


def call_function(function, degree, x, y, n):
    popt1, _ = curve_fit(function, x, y)
    a, b, c, d, e, f, g, h, i, j, k = popt1
    coeffs = [a, b, c, d, e, f, g, h, i, j, k]

    res = root(function, 0.1, args=(a, b, c, d, e, f, g, h, i, j, k)).x[0]
    x_line = arange(min(x), max(x), 0.001)
    y_line = function(x_line, a, b, c, d, e, f, g, h, i, j, k)
    xt = np.linspace(0, res, n)
    f = coeffs[degree]
    for index in range(1, degree + 1):
        f += coeffs[index - 1] * xt ** index

    correlation_matrix = np.corrcoef(y, f)
    correlation_xy = correlation_matrix[0, 1]
    r2 = correlation_xy ** 2
    return r2


def function_e0(x, a, b):
    return a + np.exp(b * x)


def e0(x, y, n):
    popt1, _ = curve_fit(function_e0, x, y)
    a, b = popt1
    res = root(function_e0, 0.1, args=(a, b)).x[0]
    x_line = arange(min(x), max(x), 0.001)
    y_line = function_e0(x_line, a, b)
    xt = np.linspace(0, res, n)
    f = a + np.exp(b * xt)
    correlation_matrix = np.corrcoef(y, f)
    correlation_xy = correlation_matrix[0, 1]
    r2 = correlation_xy ** 2
    return r2


def function_e1(x, a, b, c):
    return a * x + np.exp(b * x) + c


def e1(x, y, n):
    popt1, _ = curve_fit(function_e1, x, y)
    a, b, c = popt1
    res = root(function_e1, 0.1, args=(a, b, c)).x[0]
    x_line = arange(min(x), max(x), 0.001)
    y_line = function_e1(x_line, a, b, c)
    xt = np.linspace(0, res, n)
    f = a * xt + np.exp(b * xt) + c
    correlation_matrix = np.corrcoef(y, f)
    correlation_xy = correlation_matrix[0, 1]
    r2 = correlation_xy ** 2
    return r2


def function_e2(x, a, b, c, d):
    return a * x + np.exp(b * x) + c * x ** 2 + d


def e2(x, y, n):
    popt1, _ = curve_fit(function_e2, x, y)
    a, b, c, d = popt1
    res = root(function_e2, 0.1, args=(a, b, c, d)).x[0]
    x_line = arange(min(x), max(x), 0.001)
    y_line = function_e2(x_line, a, b, c, d)
    xt = np.linspace(0, res, n)
    f = a * xt + np.exp(b * xt) + c * xt ** 2 + d
    correlation_matrix = np.corrcoef(y, f)
    correlation_xy = correlation_matrix[0, 1]
    r2 = correlation_xy ** 2
    return r2
