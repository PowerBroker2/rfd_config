import sys
import rfd900x
from time import sleep
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from pySerialTransfer import pySerialTransfer as txfer
from gui import Ui_MainWindow


class PortThread(QThread):
    def __init__(self, parent=None):
        super(PortThread, self).__init__(parent)
        self.parent = parent
    
    def run(self):
        while(True):
            self.parent.update_port()
            sleep(0.5)


class AppWindow(QMainWindow):
    '''
    Description:
    ------------
    Main GUI window class
    '''
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        
        self.setup_signals()
        self.setup_other()
    
    def setup_signals(self):
        self.setup_buttons()
        self.setup_comboboxes()
    
    def setup_buttons(self):
        self.ui.load_settings.clicked.connect(self.load)
        self.ui.save_settings.clicked.connect(self.save)
        self.ui.reset_to_defaults.clicked.connect(self.reset_to_defaults)
        self.ui.random_key.clicked.connect(self.random_key)
        self.ui.standard_mavlink.clicked.connect(self.standard_mavlink)
        self.ui.low_latency.clicked.connect(self.low_latency)
        self.ui.copy_req_to_remote.clicked.connect(self.copy_req_to_remote)
        self.ui.save_to_remote.clicked.connect(self.save_to_remote)
        
    def setup_comboboxes(self):
        self.update_port()
        self.ui.baud.addItems(map(str, [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 1000000]))
        self.ui.baud.setCurrentIndex(6)
       
        self.ui.baud_setting.addItems(map(str, [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 1000000]))
        self.ui.baud_setting.setCurrentIndex(6)
        self.ui.air_speed.addItems(map(str, rfd900x.AIR_SPEEDS))
        self.ui.net_id.addItems(map(str, rfd900x.NET_IDS))
        self.ui.tx_pwr.addItems(map(str, rfd900x.TX_PWRS))
        self.ui.mavlink.addItems(['Raw Data', 'Mavlink', 'Low Latency'])
        self.ui.min_freq.addItems(map(str, rfd900x.MIN_FREQS))
        self.ui.max_freq.addItems(map(str, rfd900x.MAX_FREQS))
        self.ui.max_freq.setCurrentIndex(len(rfd900x.MAX_FREQS) - 1)
        self.ui.num_channels.addItems(map(str, rfd900x.NUM_CHANNELS))
        self.ui.duty_cycle.addItems(map(str, rfd900x.DUTY_CYCLES))
        self.ui.lbt_rssi.addItems(map(str, rfd900x.LBT_RSSIS))
        self.ui.max_window.addItems(map(str, rfd900x.MAX_WINDOWS))
        self.ui.ant_mode.addItems(map(str, list(range(4))))
        self.ui.rate_and_freq_bands.addItems(map(str, list(range(4))))
        self.ui.target_rssi.addItems(map(str, list(range(50, 256))))
        self.ui.hysteresis_rssi.addItems(map(str, list(range(20, 51))))
        
        self.ui.baud_setting_remote.addItems(map(str, [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 1000000]))
        self.ui.baud_setting_remote.setCurrentIndex(6)
        self.ui.air_speed_remote.addItems(map(str, rfd900x.AIR_SPEEDS))
        self.ui.net_id_remote.addItems(map(str, rfd900x.NET_IDS))
        self.ui.tx_pwr_remote.addItems(map(str, rfd900x.TX_PWRS))
        self.ui.mavlink_remote.addItems(['Raw Data', 'Mavlink', 'Low Latency'])
        self.ui.min_freq_remote.addItems(map(str, rfd900x.MIN_FREQS))
        self.ui.max_freq_remote.addItems(map(str, rfd900x.MAX_FREQS))
        self.ui.max_freq_remote.setCurrentIndex(len(rfd900x.MAX_FREQS) - 1)
        self.ui.num_channels_remote.addItems(map(str, rfd900x.NUM_CHANNELS))
        self.ui.duty_cycle_remote.addItems(map(str, rfd900x.DUTY_CYCLES))
        self.ui.lbt_rssi_remote.addItems(map(str, rfd900x.LBT_RSSIS))
        self.ui.max_window_remote.addItems(map(str, rfd900x.MAX_WINDOWS))
        self.ui.ant_mode_remote.addItems(map(str, list(range(4))))
        self.ui.rate_and_freq_bands_remote.addItems(map(str, list(range(4))))
        self.ui.target_rssi_remote.addItems(map(str, list(range(50, 256))))
        self.ui.hysteresis_rssi_remote.addItems(map(str, list(range(20, 51))))
    
    def setup_other(self):
        self.rfd = rfd900x.RFDConfig()
        self.port_th = PortThread(self)
        self.port_th.start()
    
    def update_port(self):
        items = [self.ui.port.itemText(i) for i in range(self.ui.port.count())]
        
        if not txfer.serial_ports() == items:
            self.ui.port.clear()
            self.ui.port.addItems(txfer.serial_ports())
    
    def load(self):
        try:
            if self.rfd.open(self.ui.port.currentText(), int(self.ui.baud.currentText())):
                self.rfd.loadAll()
                import pprint
                pprint.pprint(self.rfd.params)
                self.ui.local.setEnabled(True)
                self.ui.save_settings.setEnabled(True)
                self.ui.reset_to_defaults.setEnabled(True)
                
                if self.rfd.hasRemote():
                    self.ui.remote.setEnabled(True)
                    self.ui.copy_req_to_remote.setEnabled(True)
                    self.ui.save_to_remote.setEnabled(True)
                else:
                    self.ui.remote.setEnabled(False)
                    self.ui.copy_req_to_remote.setEnabled(False)
                    self.ui.save_to_remote.setEnabled(False)
                
                self.rfd.close()
            
            else:
                print('Could not enter AT mode with modem on {} at {}'.format(self.ui.port.currentText(), self.ui.baud.currentText()))
                self.ui.local.setEnabled(False)
                self.ui.remote.setEnabled(False)
                self.ui.save_settings.setEnabled(False)
                self.ui.reset_to_defaults.setEnabled(False)
                self.ui.copy_req_to_remote.setEnabled(False)
                self.ui.save_to_remote.setEnabled(False)
        except:
            import traceback
            traceback.print_exc()
        
        self.rfd.close()
    
    def save(self):
        pass
    
    def reset_to_defaults(self):
        pass
    
    def random_key(self):
        pass
    
    def standard_mavlink(self):
        pass
    
    def low_latency(self):
        pass
    
    def copy_req_to_remote(self):
        pass
    
    def save_to_remote(self):
        pass


def main():
    '''
    Description:
    ------------
    Main program to run
    '''
    
    try:
        app = QApplication(sys.argv)
        w   = AppWindow()
        w.show()
        sys.exit(app.exec_())
        
    except (KeyboardInterrupt, SystemExit):
        pass
    
    try:
        w.port_th.terminate()
        
    except AttributeError:
        pass


if __name__ == '__main__':
    main()
    
    