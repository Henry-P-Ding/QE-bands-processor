import copy
import numpy as np
from perovskite_utils.file_read_write import FileReader, FileReaderState


class PWscfBandsOutputState(FileReaderState):
    def enter(self):
        pass

    def execute(self):
        tokens = list(filter(None, self._file_reader.current_str.strip().split(" ")))
        if len(tokens) > 0 and tokens[0] == "high-symmetry":
            self._file_reader.add_k_point(float(tokens[-1]))

    def exit(self):
        pass


class PWscfBandsOutputReader(FileReader):
    def __init__(self, read_path):
        super().__init__(
            reader_states={"state": PWscfBandsOutputState(self)},
            start_state_name="state",
            read_path=read_path,
        )
        self._k_points_x = None

    @property
    def k_points_x(self):
        if self._k_points_x is None:
            self.read_file()

        if self._k_points_x is None:
            raise RuntimeError("_k_points_x is still None after file read.")
        return self._k_points_x

    def add_k_point(self, k_point):
        self._k_points_x.append(k_point)

    def read_file(self):
        with open(self.read_path, "r", encoding="ascii") as bands_file:
            for line in bands_file:
                self.feed(line)

    def feed(self, str_data):
        self._current_str = str_data
        self.execute_state()


class EnergyBand:
    def __init__(self, k_points_x, eigv, spins):
        self.eigv = np.array(eigv)
        self.k_points_x = np.array(k_points_x)
        self.spins = np.array(spins)
        if self.eigv.ndim != 1:
            raise ValueError(
                f"eigv must be one-dimensional, but has {self.eigv.ndim} dimensions instead."
            )
        if self.k_points_x.ndim != 1:
            raise ValueError(
                f"k_points_x must be one-dimensional, but has {self.k_points_x.ndim} dimensions instead."
            )
        if self.spins.ndim != 1:
            raise ValueError(
                f"spins must be one-dimensional, but has {self.spins.ndim} dimensions instead."
            )
        if not (
            np.array([self.eigv.size, self.k_points_x.size, self.spins.size])
            == self.eigv.size
        ).all():
            raise ValueError(
                f"Input shape of eigv, k_points_x, spins are not same: {self.eigv.shape}, {self.k_points_x.shape}, {self.spins.shape}"
            )

        self.k_count = self.eigv.size

    @property
    def max_eigv(self):
        return np.max(self.eigv)

    @property
    def max_k_points_x(self):
        return self.k_points_x[self.eigv == np.max(self.eigv)]

    @property
    def max_k_index(self):
        return np.arange(self.k_count)[self.eigv == np.max(self.eigv)]

    @property
    def min_eigv(self):
        return np.min(self.eigv)

    @property
    def min_k_points_x(self):
        return self.k_points_x[self.eigv == np.min(self.eigv)]

    @property
    def min_k_index(self):
        return np.arange(self.k_count)[self.eigv == np.min(self.eigv)]


class BandStructure:
    def __init__(self, bands, n_electrons):
        if not all(map(lambda band: isinstance(band, EnergyBand), bands)):
            raise ValueError("Not all bands are instances of EnergyBand")
        self.bands = bands
        if not n_electrons % 2 == 0:
            raise ValueError("Number of electrons is not even.")
        self.n_electrons = n_electrons
        self.valence_band = bands[n_electrons - 1]
        self.conduction_band = bands[n_electrons]
        self.band_gap = self.conduction_band.min_eigv - self.valence_band.max_eigv


class BandsDataState(FileReaderState):
    def __init__(self, file_reader):
        super().__init__(file_reader)
        self._current_k_points = []
        self._current_eigv = []
        self._bands = []

    def enter(self):
        self._current_k_points = []
        self._current_eigv = []
        self._bands = []

    def execute(self):
        tokens = list(filter(None, self._file_reader.current_str.strip().split(" ")))
        if len(tokens) == 0:
            self._bands.append(
                EnergyBand(
                    self._current_k_points,
                    self._current_eigv,
                    [None] * len(self._current_eigv),
                )
            )
            self._current_k_points = []
            self._current_eigv = []
        else:
            self._current_k_points.append(float(tokens[0]))
            self._current_eigv.append(float(tokens[1]))

    def exit(self):
        self._file_reader.band_structure = BandStructure(
            self._bands, self._file_reader.n_electrons
        )


class BandsDataReader(FileReader):
    def __init__(self, read_path, n_electrons):
        super().__init__(
            reader_states={"state": BandsDataState(self)},
            start_state_name="state",
            read_path=read_path,
        )
        self.n_electrons = int(n_electrons)
        self.band_structure = None

    def read_file(self):
        with open(self.read_path, "r", encoding="ascii") as bands_file:
            for line in bands_file:
                self.feed(line)

            self.current_state.exit()

    def feed(self, str_data):
        self._current_str = str_data
        self.execute_state()
