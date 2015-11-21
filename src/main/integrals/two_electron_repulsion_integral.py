from src.main.objects import PrimitiveBasisFactory
from src.main.common import BinomialCoefficientsFunction
from src.main.common import Vector
from src.main.common import BoysFunction
from math import factorial, sqrt
import numpy as np


class ElectronRepulsionIntegral:

    @staticmethod
    def sigma_function(l, l_1, l_2, a, b, r, g):
        out = BinomialCoefficientsFunction.calculate_coefficient(l, l_1, l_2, a, b) * ((factorial(l) * g**(r - l)) / (factorial(r) * factorial(l - 2*r)))
        return out

    @staticmethod
    def gaussian_product_factor(a_1, a_2, a_3, a_4, a_p, a_q, r_a, r_b, r_c, r_d):
        r_ab = Vector.distance(r_a, r_b)
        r_cd = Vector.distance(r_c, r_d)
        out = ((2 * np.pi**2) / (a_p * a_q)) * sqrt(np.pi / (a_p + a_q)) * np.exp(- ((a_1 * a_2 * r_ab**2) / a_p) - ((a_3 * a_4 * r_cd**2) / a_q))
        return out

    @classmethod
    def b_function(cls, l, ll, r, rr, i, l_1, l_2, a_x, b_x, p_x, g_1, l_3, l_4, c_x, d_x, q_x, g_2):
        pa_x = p_x - a_x
        pb_x = p_x - b_x
        qc_x = q_x - c_x
        qd_x = q_x - d_x
        c_x = p_x - q_x
        delta = (1/(4*g_1)) + (1/(4*g_2))
        out1 = (-1)**l * cls.sigma_function(l, l_1, l_2, pa_x, pb_x, r, g_1) * cls.sigma_function(ll, l_3, l_4, qc_x, qd_x, rr, g_2)
        out2_num = (-1)**i * (2 * delta)**(2 * (r + rr)) * factorial(l + ll - 2*r - 2*rr) * delta**i * c_x**(l + ll - 2*(r + rr + i))
        out2_den = (4 * delta)**(l + ll) * factorial(i) * factorial(l + ll - 2*(r + rr + i))
        ans = out1 * (out2_num / out2_den)
        return ans

    @classmethod
    def integral(cls, g1, g2, g3, g4):
        g5 = PrimitiveBasisFactory.gaussian_product(g1, g2)
        g6 = PrimitiveBasisFactory.gaussian_product(g3, g4)

        a_1 = g1.exponent
        r_1 = g1.coordinates
        l_1 = g1.integral_exponents

        a_2 = g2.exponent
        r_2 = g2.coordinates
        l_2 = g2.integral_exponents

        a_3 = g3.exponent
        r_3 = g3.coordinates
        l_3 = g3.integral_exponents

        a_4 = g4.exponent
        r_4 = g4.coordinates
        l_4 = g4.integral_exponents

        a_5 = g5.exponent
        r_5 = g5.coordinates

        a_6 = g6.exponent
        r_6 = g6.coordinates

        r_56 = Vector.distance(r_5, r_6)
        delta = (1/(4*a_5)) + (1/(4*a_6))

        out1 = 0
        for l in range(l_1[0] + l_2[0] + 1):
            for r in range(int(l/2) + 1):
                for ll in range(l_3[0] + l_4[0] + 1):
                    for rr in range(int(ll/2) + 1):
                        for i in range(int((l + ll - 2*r - 2*rr) / 2) + 1):
                            out2 = cls.b_function(l, ll, r, rr, i, l_1[0], l_2[0], r_1[0], r_2[0], r_5[0], a_5, l_3[0], l_4[0], r_3[0], r_4[0], r_6[0], a_6)
                            for m in range(l_1[1] + l_2[1] + 1):
                                for s in range(int(m / 2) + 1):
                                    for mm in range(l_3[1] + l_4[1] + 1):
                                        for ss in range(int(mm/2) + 1):
                                            for j in range(int((m + mm - 2*s - 2*ss) / 2) + 1):
                                                out3 = cls.b_function(m, mm, s, ss, j, l_1[1], l_2[1], r_1[1], r_2[1], r_5[1], a_5, l_3[1], l_4[1], r_3[1], r_4[1], r_6[1], a_6)
                                                for n in range(l_1[2] + l_2[2] + 1):
                                                    for t in range(int(n/2) + 1):
                                                        for nn in range(l_3[2] + l_4[2] + 1):
                                                            for tt in range(int(nn/2) + 1):
                                                                for k in range(int((n + nn - 2*t - 2*tt) / 2) + 1):
                                                                    out4 = cls.b_function(n, nn, t, tt, k, l_1[2], l_2[2], r_1[2], r_2[2], r_5[2], a_5, l_3[2], l_4[2], r_3[2], r_4[2], r_6[2], a_6)
                                                                    v = l + ll + m + mm + n + nn - 2*(r + rr + s + ss + t + tt) - (i + j + k)
                                                                    out5 = BoysFunction.function(v, (r_56**2 / (4 * delta)))
                                                                    out1 += out2 * out3 * out4 * out5
        out1 *= cls.gaussian_product_factor(a_1, a_2, a_3, a_4, a_5, a_6, r_1, r_2, r_3, r_4)
        return out1

    @classmethod
    def symmetry_check(cls, g1, g2, g3, g4):
        pass
