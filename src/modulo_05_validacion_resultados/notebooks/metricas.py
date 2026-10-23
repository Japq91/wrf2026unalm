# Metricas de validacion (Modulo 5)
import numpy as np


def calcular_mae(s, o):
    return float(np.mean(np.abs(s - o)))


def calcular_rmse(s, o):
    return float(np.sqrt(np.mean((s - o) ** 2)))


def calcular_bias(s, o):
    return float(np.mean(s - o))


def calcular_r(s, o):
    return float(np.corrcoef(s, o)[0, 1])


def calcular_kge(s, o):
    r = calcular_r(s, o)
    beta = np.mean(s) / np.mean(o)
    alpha = np.std(s) / np.std(o)
    kge = 1 - np.sqrt((r - 1) ** 2 + (beta - 1) ** 2 + (alpha - 1) ** 2)
    return kge, {"r": r, "beta": beta, "alpha": alpha}
