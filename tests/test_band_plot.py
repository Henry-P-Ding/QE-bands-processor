import unittest
import sys
sys.path.insert(0, "../perovskite_utils")
import matplotlib.pyplot as plt
from perovskite_utils.file_read_write import PWscfSCFOutputReader
from QE_bands_processor.bands_data import BandsDataReader
from QE_bands_processor.band_plot import BandStructureArtist

class TestBandPlots(unittest.TestCase):
    def test_plot_band(self):
        scf_reader = PWscfSCFOutputReader("tests/SMBA2PbI4_151_157.scf.out")
        scf_reader.read_file()
        self.assertEqual(scf_reader.num_electrons, 560.0)
        bands_reader = BandsDataReader(
            "tests/SMBA2PbI4_151_157_band_structure.dat.gnu", scf_reader.num_electrons
        )
        bands_reader.read_file()
        self.assertEqual(bands_reader.band_structure.band_gap, 1.1718000000000002)
        
        fig, ax = plt.gcf(), plt.gca()
        artist = BandStructureArtist(ax)
        artist.draw_plot(bands_reader.band_structure, [-2, 4])
        plt.show()

if __name__ == "__main__":
    unittest.main()
