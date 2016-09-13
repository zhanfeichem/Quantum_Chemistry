import itertools


class SinglesDoublesAmplitudes:

    def __init__(self, spin_molecular_integral, orbital_energies, occupied_orbitals, unoccupied_orbitals):
        self.integrals = spin_molecular_integral
        self.orbital_energies = orbital_energies
        self.occupied = range(occupied_orbitals)
        self.unoccupied = range(occupied_orbitals, occupied_orbitals + unoccupied_orbitals)
        self.singles, self.doubles = self.indexes()
        self.denominator = self.denominator_arrays()

    def indexes(self):
        singles = []
        doubles = []
        for i in self.occupied:
            for a in self.unoccupied:
                singles.append((i, a))
        for i, j in itertools.permutations(self.occupied, 2):
            for a, b in itertools.permutations(self.unoccupied, 2):
                doubles.append((i, j, a, b))
        return singles, doubles

    def mp2_initial_guess(self):
        t = {}
        for i, a in self.singles:
            t[i, a] = 0
        for i, j, a, b in self.doubles:
            t[i, j, a, b] = self.integrals.item(i, j, a, b) / self.denominator[i, j, a, b]
        return t

    def calculate_amplitudes(self, t_prev):
        t = {}
        tau_1, tau_2 = self.tau(t_prev)
        inter = self.intermediates(t_prev, tau_1, tau_2)

        for i, a in self.singles:
            t[i, a] = self.singles_amplitudes(i, a, t_prev, inter)
        for i, j, a, b in self.doubles:
            t[i, j, a, b] = self.doubles_amplitudes(i, j, a, b, t_prev, tau_1, inter)

        return t

    def singles_amplitudes(self, i, a, t, inter):
        t_ia = 0

        for e in self.unoccupied:
            t_ia += t[i, e] * inter[a, e]

        for m in self.occupied:
            t_ia -= t[m, a] * inter[m, i]
            for e in self.unoccupied:
                if i != m and a != e:
                    t_ia += t[i, m, a, e] * inter[m, e]

        for n, f in self.singles:
            t_ia -= t[n, f] * self.integrals.item(n, a, i, f)

        for m, e in self.singles:
            for f in self.unoccupied:
                if i != m and e != f:
                    t_ia -= 0.5 * t[i, m, e, f] * self.integrals.item(m, a, e, f)
            for n in self.occupied:
                if m != n and a != e:
                    t_ia -= 0.5 * t[m, n, a, e] * self.integrals.item(n, m, e, i)

        return t_ia / self.denominator[i, a]

    def doubles_amplitudes(self, i, j, a, b, t, tau, inter):
        t_ijab = self.integrals.item(i, j, a, b)

        for e in self.unoccupied:
            out = 0
            for m in self.occupied:
                out += t[m, b] * inter[m, e]
            if a != e:
                t_ijab += t[i, j, a, e] * (inter[b, e] - 0.5 * out)
            out = 0
            for m in self.occupied:
                out += t[m, a] * inter[m, e]
            if b != e:
                t_ijab -= t[i, j, b, e] * (inter[a, e] - 0.5 * out)

        for m in self.occupied:
            out = 0
            for e in self.unoccupied:
                out += t[j, e] * inter[m, e]
            if i != m:
                t_ijab -= t[i, m, a, b] * (inter[m, j] + 0.5 * out)
            out = 0
            for e in self.unoccupied:
                out += t[i, e] * inter[m, e]
            if j != m:
                t_ijab += t[j, m, a, b] * (inter[m, i] + 0.5 * out)

        for m, n in itertools.permutations(self.occupied, 2):
            t_ijab += 0.5 * tau[m, n, a, b] * inter[m, n, i, j]

        for e, f in itertools.permutations(self.unoccupied, 2):
            t_ijab += 0.5 * tau[i, j, e, f] * inter[a, b, e, f]

        for m, e in self.singles:
            if i != m and a != e:
                t_ijab += t[i, m, a, e] * inter[m, b, e, j]
            t_ijab -= t[i, e] * t[m, a] * self.integrals.item(m, b, e, j)
            if i != m and b != e:
                t_ijab -= t[i, m, b, e] * inter[m, a, e, j]
            t_ijab += t[i, e] * t[m, b] * self.integrals.item(m, a, e, j)
            if j != m and a != e:
                t_ijab -= t[j, m, a, e] * inter[m, b, e, i]
            t_ijab += t[j, e] * t[m, a] * self.integrals.item(m, b, e, i)
            if j != m and b != e:
                t_ijab += t[j, m, b, e] * inter[m, a, e, i]
            t_ijab -= t[j, e] * t[m, b] * self.integrals.item(m, a, e, i)

        for e in self.unoccupied:
            t_ijab += t[i, e] * self.integrals.item(a, b, e, j) - t[j, e] * self.integrals.item(a, b, e, i)

        for m in self.occupied:
            t_ijab -= t[m, a] * self.integrals.item(m, b, i, j) - t[m, b] * self.integrals.item(m, a, i, j)

        return t_ijab / self.denominator[i, j, a, b]

    def intermediates(self, t, tau_1, tau_2):
        intermediates = {}

        for a, e in itertools.product(self.unoccupied, repeat=2):
            f_ae = 0
            for m, f in self.singles:
                f_ae += t[m, f] * self.integrals.item(m, a, f, e)
                for n in self.occupied:
                    if m != n and a != f:
                        f_ae -= 0.5 * tau_2[m, n, a, f] * self.integrals.item(m, n, e, f)
            intermediates[a, e] = f_ae

        for m, i in itertools.product(self.occupied, repeat=2):
            f_mi = 0
            for n, e in self.singles:
                f_mi += t[n, e] * self.integrals.item(m, n, i, e)
                for f in self.unoccupied:
                    if i != n and e != f:
                        f_mi += 0.5 * tau_2[i, n, e, f] * self.integrals.item(m, n, e, f)
            intermediates[m, i] = f_mi

        for m, e in itertools.product(self.occupied, self.unoccupied):
            f_me = 0
            for n, f in self.singles:
                f_me += t[n, f] * self.integrals.item(m, n, e, f)
            intermediates[m, e] = f_me

        for m, n, i, j in itertools.product(self.occupied, repeat=4):
            w_mnij = self.integrals.item(m, n, i, j)
            for e in self.unoccupied:
                w_mnij += t[j, e] * self.integrals.item(m, n, i, e) - t[i, e] * self.integrals.item(m, n, j, e)
                for f in self.unoccupied:
                    if i != j and e != f:
                        w_mnij += 0.25 * tau_1[i, j, e, f] * self.integrals.item(m, n, e, f)
            intermediates[m, n, i, j] = w_mnij

        for a, b, e, f in itertools.product(self.unoccupied, repeat=4):
            w_abef = self.integrals.item(a, b, e, f)
            for m in self.occupied:
                w_abef -= t[m, b] * self.integrals.item(a, m, e, f) - t[m, a] * self.integrals.item(b, m, e, f)
                for n in self.occupied:
                    if m != n and a != b:
                        w_abef += 0.25 * tau_1[m, n, a, b] * self.integrals.item(m, n, e, f)
            intermediates[a, b, e, f] = w_abef

        for m, b, e, j in itertools.product(self.occupied, self.unoccupied, self.unoccupied, self.occupied):
            w_mbej = self.integrals.item(m, b, e, j)
            for f in self.unoccupied:
                w_mbej += t[j, f] * self.integrals.item(m, b, e, f)
            for n in self.occupied:
                w_mbej -= t[n, b] * self.integrals.item(m, n, e, j)
                for f in self.unoccupied:
                    if j != n and f != b:
                        w_mbej -= 0.5 * t[j, n, f, b] * self.integrals.item(m, n, e, f)
                    w_mbej -= t[j, f] * t[n, b] * self.integrals.item(m, n, e, f)
            intermediates[m, b, e, j] = w_mbej

        return intermediates

    def tau(self, t):
        tau_1 = {}
        tau_2 = {}
        for i, j, a, b in self.doubles:
            tau_1[i, j, a, b] = t[i, j, a, b] + t[i, a] * t[j, b] - t[i, b] * t[j, a]
            tau_2[i, j, a, b] = t[i, j, a, b] + 0.5 * (t[i, a] * t[j, b] - t[i, b] * t[j, a])
        return tau_1, tau_2

    def denominator_arrays(self):
        denominator = {}
        for i, a in self.singles:
            denominator[i, a] = self.orbital_energies[i] - self.orbital_energies[a]
        for i, j, a, b in self.doubles:
            denominator[i, j, a, b] = self.orbital_energies[i] + self.orbital_energies[j] - self.orbital_energies[a] \
            - self.orbital_energies[b]
        return denominator

    def calculate_correlation(self, t):
        correlation = 0
        for i, j, a, b in self.doubles:
            correlation += self.integrals.item(i, j, a, b) * (0.25 * t[i, j, a, b] + 0.5 * t[i, a] * t[j, b])
        return correlation