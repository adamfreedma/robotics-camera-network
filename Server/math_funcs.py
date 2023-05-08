from typing import Union, Tuple
import math


def limit(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """
    returns a value within a limit of value
    :param value: value to be limited
    :param min_value: low limit
    :param max_value: high limit
    :return:
    """
    return min(max(value, min_value), max_value)


def point_and_slope(value: float, point: Tuple[float, float], slope: float) -> float:
    """
    finds the value y given x, in a y = m * x + b equation, given a point and the slope (m)
    :param value: x
    :param point: a point the fits the function y = m * x + b
    :param slope: m
    :return: the value y
    """
    return slope * (value - point[0]) + point[1]


def two_points(value: float, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    finds the value y given x, in a y = m * x + b equation, given two points the are on the function
    :param value: x
    :param point1: first point on the function
    :param point2: second point on the function
    :return: the value y
    """
    answer = math.inf
    if point1[0] != point2[0]:
        answer = point_and_slope(value, point1, (point1[1] - point2[1]) / (point1[0] - point2[0]))

    return answer


def dead_band(value: float, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    make a linear function between the two points, and a function parallel two the x axis outside, and returns y
     where x = value
    :param value: the value to dead band
    :param point1: first "point"
    :param point2: second "point"
    :return: the value y
    """
    min_value = min(point1[1], point2[1])
    max_value = max(point1[1], point2[1])

    return limit(two_points(value, point1, point2), min_value, max_value)
