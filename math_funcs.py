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
    return slope * (value - point[0]) + point[1]


def two_points(value: float, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    answer = math.inf
    if point1[0] != point2[0]:
        answer = point_and_slope(value, point1, (point1[1] - point2[1]) / (point1[0] - point2[0]))

    return answer


def dead_band(value: float, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:

    min_value = min(point1[1], point2[1])
    max_value = max(point1[1], point2[1])

    # print(two_points(value, point1, point2))

    return limit(two_points(value, point1, point2), min_value, max_value)


