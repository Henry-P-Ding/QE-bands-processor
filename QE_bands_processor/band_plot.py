import numpy as np

class BandStructureArtist:
    def __init__(self, ax, band_colors=None):
        self._ax = ax
        if band_colors is None:
            self._band_colors = {
                "vb": "purple",
                "cb": "green"
            }
        else:
            self._band_colors = band_colors

    def draw_plot(self, band_structure, e_range, e_ref=None, k_points_labels=None):
        if e_ref == None:
            e_ref = band_structure.valence_band.max_eigv

        for band in band_structure.bands:
            if band == band_structure.valence_band:
                color = self._band_colors["vb"]
                lw = 0.8
            elif band == band_structure.conduction_band:
                color = self._band_colors["cb"]
                lw = 0.8
            else:
                color = 'black'
                lw = 0.4
            self._ax.plot(band.k_points_x, band.eigv - e_ref, '-', color=color, lw=lw)

        self._ax.set_ylim(e_range)
        self._ax.set_xlim(np.min(band_structure.bands[0].k_points_x), np.max(band_structure.bands[0].k_points_x))
        #self._ax.vlines(, e_range[0], e_range[1], linestyles='-', color='red', lw = 0.7)
        if k_points_labels is not None:
            self._ax.set_xticks(band_structure.bands[0].k_points_x, k_points_labels)
        self._ax.plot(band_structure.valence_band.max_k_points_x[0], np.mean(band_structure.valence_band.max_eigv) - e_ref, 'o', color='purple')
        self._ax.plot(band_structure.conduction_band.min_k_points_x[0], np.mean(band_structure.conduction_band.min_eigv) - e_ref, 'o', color='green')
        #self._ax.legend(loc="upper right")

