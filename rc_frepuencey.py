import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from scipy.interpolate import interp1d

def ba_driver_impedance_resistive(frequencies, freq_points, R_values):
    """
    Simulates the impedance of a BA driver at different frequencies, using linear interpolation.

    Parameters:
    frequencies (array-like): Array of frequencies (in Hz) at which to calculate the impedance.
    freq_points (array-like): Frequencies at which the resistive impedance values are given.
    R_values (array-like): Resistive impedance values (in ohms) at the given freq_points.

    Returns:
    np.ndarray: Array of impedance values (in ohms) corresponding to the input frequencies.
    """
    # Linear interpolation of resistive impedance
    impedance_interpolator = interp1d(freq_points, R_values, kind='linear', fill_value='extrapolate')
    impedance = impedance_interpolator(frequencies)
    
    return impedance

def ba_driver_db_response(frequencies, freq_points, dB_values):
    """
    Simulates the dB level of a BA driver at different frequencies, using linear interpolation.

    Parameters:
    frequencies (array-like): Array of frequencies (in Hz) at which to calculate the dB response.
    freq_points (array-like): Frequencies at which the dB values are given.
    dB_values (array-like): dB levels at the given freq_points.

    Returns:
    np.ndarray: Array of dB levels corresponding to the input frequencies.
    """
    # Linear interpolation of dB response
    db_interpolator = interp1d(freq_points, dB_values, kind='linear', fill_value='extrapolate')
    dB_response = db_interpolator(frequencies)
    
    return dB_response

def rc_cutoff_frequency(R, C_uF):
    """
    Calculates the cutoff frequency of an RC circuit.

    Parameters:
    R (float): Resistance in ohms.
    C_uF (float): Capacitance in microfarads.

    Returns:
    float: Cutoff frequency in Hz.
    """
    C = C_uF * 1e-6  # Convert microfarads to farads
    return 1 / (2 * np.pi * R * C)

class PlotWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.plot_impedance = self.addPlot(title="Impedance Magnitude (Frequency-Dependent Resistive)")
        self.plot_impedance.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_impedance.setLabel('left', 'Impedance', units='Ohms')
    
        self.nextRow()
        
        self.plot_db = self.addPlot(title="dB Response (Frequency-Dependent)")
        self.plot_db.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_db.setLabel('left', 'dB Level')
        
        self.nextRow()

        self.label_cutoff = self.addLabel(text="RC Circuit Cutoff Frequency:", row=2, col=0)
        
        self.update_plots()
    
    def update_plots(self):
        frequencies = np.linspace(20, 20000, 500)  # Frequency range from 20 Hz to 20 kHz
        
        # Specific frequencies and their corresponding resistive impedance and dB values
        freq_points = np.array([20, 100, 1000, 5000, 10000, 20000])
        R_values = np.array([20, 15, 20, 25, 30, 35])  # Resistive impedance values in ohms
        dB_values = np.array([1, 65, 70, 75, 80, 85])  # dB levels
        
        impedance = ba_driver_impedance_resistive(frequencies, freq_points, R_values)
        dB_response = ba_driver_db_response(frequencies, freq_points, dB_values)
        
        # Update impedance plot
        self.plot_impedance.clear()
        self.plot_impedance.plot(frequencies, impedance, pen=pg.mkPen({'color': "#0080FF", "width": 2}))
        
        # Update dB response plot
        self.plot_db.clear()
        self.plot_db.plot(frequencies, dB_response, pen='g')

        # Calculate and display RC circuit cutoff frequency
        R = 1000  # Example resistance in ohms
        C_uF = 1  # Example capacitance in microfarads
        cutoff_freq = rc_cutoff_frequency(R, C_uF)
        self.label_cutoff.setText(f"RC Circuit Cutoff Frequency: {cutoff_freq:.2f} Hz")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BA Driver Impedance and dB Response')
        self.setGeometry(100, 100, 1200, 900)
        
        self.plot_widget = PlotWidget(self)
        self.setCentralWidget(self.plot_widget)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())