import glob
import sys
import numpy as np
import matplotlib.pyplot as plt


# k-point convergence
def get_gamma_eigv(scf_out_path):
    gamma_eigv = []
    with open(scf_out_path, mode='r', encoding='ascii') as f:
        line = f.readline()
        while "k = 0.0000 0.0000 0.0000" not in line:
            line = f.readline()

        line = f.readline()
        line = f.readline()
        while "\n" != line:
            tokens = list(map(float, filter(None, line.rstrip().split(" "))))
            gamma_eigv += tokens
            line = f.readline()

        gamma_eigv.sort()
        return np.array(gamma_eigv)


def get_efermi(scf_out_path):
    with open(scf_out_path, mode='r', encoding='ascii') as f:
        for line in f:
            if "the Fermi energy is" in line:
                return float(line.strip().split()[4])


def get_gamma_gap(gamma_eigv, efermi):
    vbi = np.sum(gamma_eigv < efermi) - 1
    cbi = vbi + 1

    return gamma_eigv[cbi] - gamma_eigv[vbi]


recip_nks = []
gamma_gaps = []
k_grids = []
for path in glob.glob(sys.argv[1]):
    nk = np.prod(np.array(list(map(int, path.split(".")[1:4]))))
    recip_nks.append(1/nk)

    k_grids.append("x".join(path.split(".")[1:4]))

    gamma_eigv = get_gamma_eigv(path)
    efermi = get_efermi(path)
    gamma_gap = get_gamma_gap(gamma_eigv, efermi)
    gamma_gaps.append(gamma_gap)

bg_ax, fig = plt.gca(), plt.gcf()
fig.set_size_inches(4, 3)
for i, nks in enumerate(recip_nks):
    plt.plot(nks, gamma_gaps[i], 'o', label=k_grids[i])

plt.legend()
bg_ax.set_xlabel(r"$1/n_k$")
bg_ax.set_ylabel(r"$E_g$ at $\Gamma$ Point")

# ecut_wfc convergence
recip_ecuts = []
ecuts = []
gamma_gaps = []
for path in glob.glob("Pb_FR/ecut_wfc_tests/SMBA2PbI4_151_157.ecut_wfc.*.scf.out"):
    ecut = float(".".join(path.split(".")[2:4]))
    recip_ecuts.append(1 / ecut)
    ecuts.append(ecut)

    gamma_eigv = get_gamma_eigv(path)
    efermi = get_efermi(path)
    gamma_gap = get_gamma_gap(gamma_eigv, efermi)
    gamma_gaps.append(gamma_gap)

bg_ax, fig = plt.gca(), plt.gcf()
fig.set_size_inches(5, 3)
for i in range(len(recip_ecuts)):
    plt.plot(recip_ecuts[i], gamma_gaps[i], 'o', label=ecuts[i])

plt.legend()
bg_ax.set_xlabel(r"$1/\mathrm{ecut\_wfc}$")
bg_ax.set_ylabel(r"$E_g$ at $\Gamma$ Point")

bg_ax, fig = plt.gca(), plt.gcf()
fig.set_size_inches(5, 3)
for i in range(len(recip_ecuts)):
    if ecuts[i] >= 40.0:
        plt.plot(recip_ecuts[i], gamma_gaps[i], 'o', label=ecuts[i])

plt.legend()
bg_ax.set_xlabel(r"$1/\mathrm{ecut\_wfc}$")
bg_ax.set_ylabel(r"$E_g$ at $\Gamma$ Point")
