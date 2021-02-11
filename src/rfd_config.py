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
            sleep(1)


class AppWindow(QMainWindow):
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
        self.ui.standard_mavlink_remote.clicked.connect(self.standard_mavlink_remote)
        self.ui.low_latency.clicked.connect(self.low_latency)
        self.ui.low_latency_remote.clicked.connect(self.low_latency_remote)
        self.ui.copy_req_to_remote.clicked.connect(self.copy_req_to_remote)
        
    def setup_comboboxes(self):
        self.update_port()
        self.ui.baud.addItems(map(str, rfd900x.SERIAL_SPEEDS_TRUE))
        self.ui.baud.setCurrentIndex(rfd900x.SERIAL_SPEEDS.index(57))
       
        self.ui.baud_setting.addItems(map(str, rfd900x.SERIAL_SPEEDS_TRUE))
        self.ui.baud_setting.setCurrentIndex(rfd900x.SERIAL_SPEEDS.index(57))
        self.ui.air_speed.addItems(map(str, rfd900x.AIR_SPEEDS))
        self.ui.net_id.addItems(map(str, rfd900x.NET_IDS))
        self.ui.tx_pwr.addItems(map(str, rfd900x.TX_PWRS))
        self.ui.mavlink.addItems(rfd900x.MAVLINK_MODES_TRUE)
        self.ui.min_freq.addItems(map(str, rfd900x.MIN_FREQS))
        self.ui.max_freq.addItems(map(str, rfd900x.MAX_FREQS))
        self.ui.max_freq.setCurrentIndex(len(rfd900x.MAX_FREQS) - 1)
        self.ui.num_channels.addItems(map(str, rfd900x.NUM_CHANNELS))
        self.ui.duty_cycle.addItems(map(str, rfd900x.DUTY_CYCLES))
        self.ui.lbt_rssi.addItems(map(str, rfd900x.LBT_RSSIS))
        self.ui.max_window.addItems(map(str, rfd900x.MAX_WINDOWS))
        self.ui.ant_mode.addItems(map(str, rfd900x.ANT_MODES))
        self.ui.rate_and_freq_bands.addItems(map(str, rfd900x.RATE_AND_FREQ_BANDS))
        self.ui.target_rssi.addItems(map(str, rfd900x.TARGET_RSSIS))
        self.ui.hysteresis_rssi.addItems(map(str, rfd900x.HYSTERESIS_RSSIS))
        
        self.ui.baud_setting_remote.addItems(map(str, rfd900x.SERIAL_SPEEDS_TRUE))
        self.ui.baud_setting_remote.setCurrentIndex(rfd900x.SERIAL_SPEEDS.index(57))
        self.ui.air_speed_remote.addItems(map(str, rfd900x.AIR_SPEEDS))
        self.ui.net_id_remote.addItems(map(str, rfd900x.NET_IDS))
        self.ui.tx_pwr_remote.addItems(map(str, rfd900x.TX_PWRS))
        self.ui.mavlink_remote.addItems(rfd900x.MAVLINK_MODES_TRUE)
        self.ui.min_freq_remote.addItems(map(str, rfd900x.MIN_FREQS))
        self.ui.max_freq_remote.addItems(map(str, rfd900x.MAX_FREQS))
        self.ui.max_freq_remote.setCurrentIndex(len(rfd900x.MAX_FREQS) - 1)
        self.ui.num_channels_remote.addItems(map(str, rfd900x.NUM_CHANNELS))
        self.ui.duty_cycle_remote.addItems(map(str, rfd900x.DUTY_CYCLES))
        self.ui.lbt_rssi_remote.addItems(map(str, rfd900x.LBT_RSSIS))
        self.ui.max_window_remote.addItems(map(str, rfd900x.MAX_WINDOWS))
        self.ui.ant_mode_remote.addItems(map(str, rfd900x.ANT_MODES))
        self.ui.rate_and_freq_bands_remote.addItems(map(str, rfd900x.RATE_AND_FREQ_BANDS))
        self.ui.target_rssi_remote.addItems(map(str, rfd900x.TARGET_RSSIS))
        self.ui.hysteresis_rssi_remote.addItems(map(str, rfd900x.HYSTERESIS_RSSIS))
    
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
                
                self.ui.local.setEnabled(True)
                self.ui.save_settings.setEnabled(True)
                self.ui.reset_to_defaults.setEnabled(True)
                
                if self.rfd.hasRemote():
                    self.rfd.loadAll(False)
                    self.rfd.close(False)
                    
                    self.ui.remote.setEnabled(True)
                    self.ui.copy_req_to_remote.setEnabled(True)
                else:
                    self.ui.remote.setEnabled(False)
                    self.ui.copy_req_to_remote.setEnabled(False)
                
                self.rfd.close()
                self.update_ui()
            
            else:
                print('Could not enter AT mode with modem on {} at {}'.format(self.ui.port.currentText(), self.ui.baud.currentText()))
                self.ui.local.setEnabled(False)
                self.ui.remote.setEnabled(False)
                self.ui.save_settings.setEnabled(False)
                self.ui.reset_to_defaults.setEnabled(False)
                self.ui.copy_req_to_remote.setEnabled(False)
        except:
            import traceback
            traceback.print_exc()
        
        self.rfd.close()
    
    def save(self):
        try:
            if self.rfd.open(self.ui.port.currentText(), int(self.ui.baud.currentText())):
                
                if self.ui.local.isEnabled():
                    if self.ui.baud_setting.isEnabled():
                        self.rfd.params['SERIAL_SPEED']['desVal'] = rfd900x.SERIAL_SPEEDS[self.ui.baud_setting.currentIndex()]
                        self.rfd.writeOutParam('SERIAL_SPEED')
                    
                    if self.ui.air_speed.isEnabled():
                        self.rfd.params['AIR_SPEED']['desVal'] = int(self.ui.air_speed.currentText())
                        self.rfd.writeOutParam('AIR_SPEED')
                    
                    if self.ui.net_id.isEnabled():
                        self.rfd.params['NETID']['desVal'] = int(self.ui.net_id.currentText())
                        self.rfd.writeOutParam('NETID')
                    
                    if self.ui.tx_pwr.isEnabled():
                        self.rfd.params['TXPOWER']['desVal'] = int(self.ui.tx_pwr.currentText())
                        self.rfd.writeOutParam('TXPOWER')
                    
                    if self.ui.ecc.isEnabled():
                        self.rfd.params['ECC']['desVal'] = int(self.ui.ecc.isChecked())
                        self.rfd.writeOutParam('ECC')
                    
                    if self.ui.mavlink.isEnabled():
                        self.rfd.params['MAVLINK']['desVal'] = self.ui.mavlink.currentIndex()
                        self.rfd.writeOutParam('MAVLINK')
                    
                    if self.ui.op_resend.isEnabled():
                        self.rfd.params['OPPRESEND']['desVal'] = int(self.ui.op_resend.isChecked())
                        self.rfd.writeOutParam('OPPRESEND')
                    
                    if self.ui.min_freq.isEnabled():
                        self.rfd.params['MIN_FREQ']['desVal'] = int(self.ui.min_freq.currentText())
                        self.rfd.writeOutParam('MIN_FREQ')
                    
                    if self.ui.max_freq.isEnabled():
                        self.rfd.params['MAX_FREQ']['desVal'] = int(self.ui.max_freq.currentText())
                        self.rfd.writeOutParam('MAX_FREQ')
                    
                    if self.ui.num_channels.isEnabled():
                        self.rfd.params['NUM_CHANNELS']['desVal'] = int(self.ui.num_channels.currentText())
                        self.rfd.writeOutParam('NUM_CHANNELS')
                    
                    if self.ui.duty_cycle.isEnabled():
                        self.rfd.params['DUTY_CYCLE']['desVal'] = int(self.ui.duty_cycle.currentText())
                        self.rfd.writeOutParam('DUTY_CYCLE')
                    
                    if self.ui.lbt_rssi.isEnabled():
                        self.rfd.params['LBT_RSSI']['desVal'] = int(self.ui.lbt_rssi.currentText())
                        self.rfd.writeOutParam('LBT_RSSI')
                    
                    if self.ui.flow_control.isEnabled():
                        self.rfd.params['RTSCTS']['desVal'] = int(self.ui.flow_control.isChecked())
                        self.rfd.writeOutParam('RTSCTS')
                    
                    if self.ui.max_window.isEnabled():
                        self.rfd.params['MAX_WINDOW']['desVal'] = int(self.ui.max_window.currentText())
                        self.rfd.writeOutParam('MAX_WINDOW')
                    
                    if self.ui.aes_encrypt.isEnabled():
                        self.rfd.params['ENCRYPTION_LEVEL']['desVal'] = int(self.ui.aes_encrypt.isChecked())
                        self.rfd.writeOutParam('ENCRYPTION_LEVEL')
                    
                    if self.ui.aes_key.isEnabled():
                        self.rfd.params['EncryptionKey']['desVal'] = self.ui.aes_key.text()
                        self.rfd.writeOutParam('EncryptionKey')
                    
                    if self.ui.ant_mode.isEnabled():
                        self.rfd.params['ANT_MODE']['desVal'] = self.ui.ant_mode.currentIndex()
                        self.rfd.writeOutParam('ANT_MODE')
        except:
            import traceback
            traceback.print_exc()
        
        self.rfd.save()
        self.rfd.close()
    
    def reset_to_defaults(self):
        pass
    
    def random_key(self):
        self.ui.aes_key.setText(rfd900x.gen_key())
    
    def standard_mavlink(self):
        self.ui.mavlink.setCurrentIndex(rfd900x.MAVLINK_MODES_TRUE.index('Mavlink'))
        self.ui.max_window.setCurrentIndex(rfd900x.MAX_WINDOWS.index(131))
    
    def standard_mavlink_remote(self):
        self.ui.mavlink_remote.setCurrentIndex(rfd900x.MAVLINK_MODES_TRUE.index('Mavlink'))
        self.ui.max_window_remote.setCurrentIndex(rfd900x.MAX_WINDOWS.index(131))
    
    def low_latency(self):
        self.ui.mavlink.setCurrentIndex(rfd900x.MAVLINK_MODES_TRUE.index('Low Latency'))
        self.ui.max_window.setCurrentIndex(rfd900x.MAX_WINDOWS.index(33))
    
    def low_latency_remote(self):
        self.ui.mavlink_remote.setCurrentIndex(rfd900x.MAVLINK_MODES_TRUE.index('Low Latency'))
        self.ui.max_window_remote.setCurrentIndex(rfd900x.MAX_WINDOWS.index(33))
    
    def copy_req_to_remote(self):
        if self.ui.air_speed.isEnabled() and self.ui.air_speed_remote.isEnabled():
            self.ui.air_speed_remote.setCurrentIndex(self.ui.air_speed.currentIndex())
        
        if self.ui.net_id.isEnabled() and self.ui.net_id_remote.isEnabled():
            self.ui.net_id_remote.setCurrentIndex(self.ui.net_id.currentIndex())
        
        if self.ui.ecc.isEnabled() and self.ui.ecc_remote.isEnabled():
            if not self.ui.ecc.isChecked() == self.ui.ecc_remote.isChecked():
                self.ui.ecc_remote.click()
        
        if self.ui.min_freq.isEnabled() and self.ui.min_freq_remote.isEnabled():
            self.ui.min_freq_remote.setCurrentIndex(self.ui.min_freq.currentIndex())
        
        if self.ui.max_freq.isEnabled() and self.ui.max_freq_remote.isEnabled():
            self.ui.max_freq_remote.setCurrentIndex(self.ui.max_freq.currentIndex())
        
        if self.ui.num_channels.isEnabled() and self.ui.num_channels_remote.isEnabled():
            self.ui.num_channels_remote.setCurrentIndex(self.ui.num_channels.currentIndex())
        
        if self.ui.lbt_rssi.isEnabled() and self.ui.lbt_rssi_remote.isEnabled():
            self.ui.lbt_rssi_remote.setCurrentIndex(self.ui.lbt_rssi.currentIndex())
        
        if self.ui.aes_encrypt.isEnabled() and self.ui.aes_encrypt_remote.isEnabled():
            if not self.ui.aes_encrypt.isChecked() == self.ui.aes_encrypt_remote.isChecked():
                self.ui.aes_encrypt_remote.click()
        
        if self.ui.rate_and_freq_bands.isEnabled() and self.ui.rate_and_freq_bands_remote.isEnabled():
            self.ui.rate_and_freq_bands_remote.setCurrentIndex(self.ui.rate_and_freq_bands.currentIndex())
        
        if self.ui.aes_key.isEnabled() and self.ui.aes_key_remote.isEnabled():
            self.ui.aes_key_remote.setText(self.ui.aes_key.text())
            
    def update_ui(self):
        if self.ui.local.isEnabled():
            if self.rfd.params['radioVersion']['curVal'] == None:
                self.ui.radio_version.clear()
                self.ui.radio_version.setEnabled(False)
            else:
                self.ui.radio_version.setEnabled(True)
                self.ui.radio_version.setText(self.rfd.params['radioVersion']['curVal'])
    
            if self.rfd.params['rssiSignalReport']['curVal'] == None:
                self.ui.rssi.clear()
                self.ui.rssi.setEnabled(False)
            else:
                self.ui.rssi.setEnabled(True)
                self.ui.rssi.setText(self.rfd.params['rssiSignalReport']['curVal'])
    
            if self.rfd.params['SERIAL_SPEED']['curVal'] == None:
                self.ui.baud_setting.setEnabled(False)
            else:
                self.ui.baud_setting.setEnabled(True)
                self.ui.baud_setting.setCurrentIndex(rfd900x.SERIAL_SPEEDS.index(self.rfd.params['SERIAL_SPEED']['curVal']))
    
            if self.rfd.params['AIR_SPEED']['curVal'] == None:
                self.ui.air_speed.setEnabled(False)
            else:
                self.ui.air_speed.setEnabled(True)
                self.ui.air_speed.setCurrentIndex(rfd900x.AIR_SPEEDS.index(self.rfd.params['AIR_SPEED']['curVal']))
    
            if self.rfd.params['NETID']['curVal'] == None:
                self.ui.net_id.setEnabled(False)
            else:
                self.ui.net_id.setEnabled(True)
                self.ui.net_id.setCurrentIndex(rfd900x.NET_IDS.index(self.rfd.params['NETID']['curVal']))
    
            if self.rfd.params['TXPOWER']['curVal'] == None:
                self.ui.tx_pwr.setEnabled(False)
            else:
                self.ui.tx_pwr.setEnabled(True)
                self.ui.tx_pwr.setCurrentIndex(rfd900x.NET_IDS.index(self.rfd.params['TXPOWER']['curVal']))
    
            if self.rfd.params['ECC']['curVal'] == None:
                if self.ui.ecc.isChecked():
                    self.ui.ecc.click()
                self.ui.ecc.setEnabled(False)
            else:
                self.ui.ecc.setEnabled(True)
                if self.rfd.params['ECC']['curVal'] and not self.ui.ecc.isChecked():
                    self.ui.ecc.click()
    
            if self.rfd.params['MAVLINK']['curVal'] == None:
                self.ui.mavlink.setEnabled(False)
            else:
                self.ui.mavlink.setEnabled(True)
                self.ui.mavlink.setCurrentIndex(rfd900x.MAVLINK_MODES.index(self.rfd.params['MAVLINK']['curVal']))
    
            if self.rfd.params['OPPRESEND']['curVal'] == None:
                if self.ui.op_resend.isChecked():
                    self.ui.op_resend.click()
                self.ui.op_resend.setEnabled(False)
            else:
                self.ui.op_resend.setEnabled(True)
                if self.rfd.params['OPPRESEND']['curVal'] and not self.ui.op_resend.isChecked():
                    self.ui.op_resend.click()
    
            if self.rfd.params['MIN_FREQ']['curVal'] == None:
                self.ui.min_freq.setEnabled(False)
            else:
                self.ui.min_freq.setEnabled(True)
                self.ui.min_freq.setCurrentIndex(rfd900x.MIN_FREQS.index(self.rfd.params['MIN_FREQ']['curVal']))
    
            if self.rfd.params['MAX_FREQ']['curVal'] == None:
                self.ui.max_freq.setEnabled(False)
            else:
                self.ui.max_freq.setEnabled(True)
                self.ui.max_freq.setCurrentIndex(rfd900x.MAX_FREQS.index(self.rfd.params['MAX_FREQ']['curVal']))
    
            if self.rfd.params['NUM_CHANNELS']['curVal'] == None:
                self.ui.num_channels.setEnabled(False)
            else:
                self.ui.num_channels.setEnabled(True)
                self.ui.num_channels.setCurrentIndex(rfd900x.NUM_CHANNELS.index(self.rfd.params['NUM_CHANNELS']['curVal']))
    
            if self.rfd.params['DUTY_CYCLE']['curVal'] == None:
                self.ui.duty_cycle.setEnabled(False)
            else:
                self.ui.duty_cycle.setEnabled(True)
                self.ui.duty_cycle.setCurrentIndex(rfd900x.DUTY_CYCLES.index(self.rfd.params['DUTY_CYCLE']['curVal']))
    
            if self.rfd.params['LBT_RSSI']['curVal'] == None:
                self.ui.lbt_rssi.setEnabled(False)
            else:
                self.ui.lbt_rssi.setEnabled(True)
                self.ui.lbt_rssi.setCurrentIndex(rfd900x.LBT_RSSIS.index(self.rfd.params['LBT_RSSI']['curVal']))
    
            if self.rfd.params['RTSCTS']['curVal'] == None:
                if self.ui.flow_control.isChecked():
                    self.ui.flow_control.click()
                self.ui.flow_control.setEnabled(False)
            else:
                self.ui.flow_control.setEnabled(True)
                if self.rfd.params['RTSCTS']['curVal'] and not self.ui.flow_control.isChecked():
                    self.ui.flow_control.click()
    
            if self.rfd.params['MAX_WINDOW']['curVal'] == None:
                self.ui.max_window.setEnabled(False)
            else:
                self.ui.max_window.setEnabled(True)
                self.ui.max_window.setCurrentIndex(rfd900x.MAX_WINDOWS.index(self.rfd.params['MAX_WINDOW']['curVal']))
    
            if self.rfd.params['ENCRYPTION_LEVEL']['curVal'] == None:
                if self.ui.aes_encrypt.isChecked():
                    self.ui.aes_encrypt.click()
                self.ui.aes_encrypt.setEnabled(False)
            else:
                self.ui.aes_encrypt.setEnabled(True)
                if self.rfd.params['ENCRYPTION_LEVEL']['curVal'] and not self.ui.aes_encrypt.isChecked():
                    self.ui.aes_encrypt.click()
    
            if self.rfd.params['EncryptionKey']['curVal'] == None:
                self.ui.aes_key.clear()
                self.ui.aes_key.setEnabled(False)
                self.ui.random_key.setEnabled(False)
            else:
                self.ui.aes_key.setEnabled(True)
                self.ui.random_key.setEnabled(True)
                self.ui.aes_key.setText(self.rfd.params['EncryptionKey']['curVal'])
    
            if self.rfd.params['ANT_MODE']['curVal'] == None:
                self.ui.ant_mode.setEnabled(False)
            else:
                self.ui.ant_mode.setEnabled(True)
                self.ui.ant_mode.setCurrentIndex(rfd900x.ANT_MODES.index(self.rfd.params['ANT_MODE']['curVal']))
    
            if self.rfd.params['RATE/FREQBAND']['curVal'] == None:
                self.ui.rate_and_freq_bands.setEnabled(False)
            else:
                self.ui.rate_and_freq_bands.setEnabled(True)
                self.ui.rate_and_freq_bands.setCurrentIndex(rfd900x.RATE_AND_FREQ_BANDS.index(self.rfd.params['RATE/FREQBAND']['curVal']))
    
            if self.rfd.params['TARGET_RSSI']['curVal'] == None:
                self.ui.target_rssi.setEnabled(False)
            else:
                self.ui.target_rssi.setEnabled(True)
                self.ui.target_rssi.setCurrentIndex(rfd900x.TARGET_RSSIS.index(self.rfd.params['TARGET_RSSI']['curVal']))
    
            if self.rfd.params['HYSTERESIS_RSSI']['curVal'] == None:
                self.ui.hysteresis_rssi.setEnabled(False)
            else:
                self.ui.hysteresis_rssi.setEnabled(True)
                self.ui.hysteresis_rssi.setCurrentIndex(rfd900x.HYSTERESIS_RSSIS.index(self.rfd.params['HYSTERESIS_RSSI']['curVal']))
                
        if self.ui.remote.isEnabled():
            try:
                if self.rfd.params['radioVersion']['curValRemote'] == None:
                    self.ui.radio_version_remote.clear()
                    self.ui.radio_version_remote.setEnabled(False)
                else:
                    self.ui.radio_version_remote.setEnabled(True)
                    self.ui.radio_version_remote.setText(self.rfd.params['radioVersion']['curValRemote'])
            except ValueError:
                pass
    
            try:
                if self.rfd.params['rssiSignalReport']['curValRemote'] == None:
                    self.ui.rssi_remote.clear()
                    self.ui.rssi_remote.setEnabled(False)
                else:
                    self.ui.rssi_remote.setEnabled(True)
                    self.ui.rssi_remote.setText(self.rfd.params['rssiSignalReport']['curValRemote'])
            except ValueError:
                pass
    
            try:
                if self.rfd.params['SERIAL_SPEED']['curValRemote'] == None:
                    self.ui.baud_setting_remote.setEnabled(False)
                else:
                    self.ui.baud_setting_remote.setEnabled(True)
                    self.ui.baud_setting_remote.setCurrentIndex(rfd900x.SERIAL_SPEEDS.index(self.rfd.params['SERIAL_SPEED']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['AIR_SPEED']['curValRemote'] == None:
                    self.ui.air_speed_remote.setEnabled(False)
                else:
                    self.ui.air_speed_remote.setEnabled(True)
                    self.ui.air_speed_remote.setCurrentIndex(rfd900x.AIR_SPEEDS.index(self.rfd.params['AIR_SPEED']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['NETID']['curValRemote'] == None:
                    self.ui.net_id_remote.setEnabled(False)
                else:
                    self.ui.net_id_remote.setEnabled(True)
                    self.ui.net_id_remote.setCurrentIndex(rfd900x.NET_IDS.index(self.rfd.params['NETID']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['TXPOWER']['curValRemote'] == None:
                    self.ui.tx_pwr_remote.setEnabled(False)
                else:
                    self.ui.tx_pwr_remote.setEnabled(True)
                    self.ui.tx_pwr_remote.setCurrentIndex(rfd900x.NET_IDS.index(self.rfd.params['TXPOWER']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['ECC']['curValRemote'] == None:
                    if self.ui.ecc_remote.isChecked():
                        self.ui.ecc_remote.click()
                    self.ui.ecc_remote.setEnabled(False)
                else:
                    self.ui.ecc_remote.setEnabled(True)
                    if self.rfd.params['ECC']['curValRemote'] and not self.ui.ecc_remote.isChecked():
                        self.ui.ecc_remote.click()
            except ValueError:
                pass
            
            try:
                if self.rfd.params['MAVLINK']['curValRemote'] == None:
                    self.ui.mavlink_remote.setEnabled(False)
                else:
                    self.ui.mavlink_remote.setEnabled(True)
                    self.ui.mavlink_remote.setCurrentIndex(rfd900x.MAVLINK_MODES.index(self.rfd.params['MAVLINK']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['OPPRESEND']['curValRemote'] == None:
                    if self.ui.op_resend_remote.isChecked():
                        self.ui.op_resend_remote.click()
                    self.ui.op_resend_remote.setEnabled(False)
                else:
                    self.ui.op_resend_remote.setEnabled(True)
                    if self.rfd.params['OPPRESEND']['curValRemote'] and not self.ui.op_resend_remote.isChecked():
                        self.ui.op_resend_remote.click()
            except ValueError:
                pass
    
            try:
                if self.rfd.params['MIN_FREQ']['curValRemote'] == None:
                    self.ui.min_freq_remote.setEnabled(False)
                else:
                    self.ui.min_freq_remote.setEnabled(True)
                    self.ui.min_freq_remote.setCurrentIndex(rfd900x.MIN_FREQS.index(self.rfd.params['MIN_FREQ']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['MAX_FREQ']['curValRemote'] == None:
                    self.ui.max_freq_remote.setEnabled(False)
                else:
                    self.ui.max_freq_remote.setEnabled(True)
                    self.ui.max_freq_remote.setCurrentIndex(rfd900x.MAX_FREQS.index(self.rfd.params['MAX_FREQ']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['NUM_CHANNELS']['curValRemote'] == None:
                    self.ui.num_channels_remote.setEnabled(False)
                else:
                    self.ui.num_channels_remote.setEnabled(True)
                    self.ui.num_channels_remote.setCurrentIndex(rfd900x.NUM_CHANNELS.index(self.rfd.params['NUM_CHANNELS']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['DUTY_CYCLE']['curValRemote'] == None:
                    self.ui.duty_cycle_remote.setEnabled(False)
                else:
                    self.ui.duty_cycle_remote.setEnabled(True)
                    self.ui.duty_cycle_remote.setCurrentIndex(rfd900x.DUTY_CYCLES.index(self.rfd.params['DUTY_CYCLE']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['LBT_RSSI']['curValRemote'] == None:
                    self.ui.lbt_rssi_remote.setEnabled(False)
                else:
                    self.ui.lbt_rssi_remote.setEnabled(True)
                    self.ui.lbt_rssi_remote.setCurrentIndex(rfd900x.LBT_RSSIS.index(self.rfd.params['LBT_RSSI']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['RTSCTS']['curValRemote'] == None:
                    if self.ui.flow_control_remote.isChecked():
                        self.ui.flow_control_remote.click()
                    self.ui.flow_control_remote.setEnabled(False)
                else:
                    self.ui.flow_control_remote.setEnabled(True)
                    if self.rfd.params['RTSCTS']['curValRemote'] and not self.ui.flow_control_remote.isChecked():
                        self.ui.flow_control_remote.click()
            except ValueError:
                pass
    
            try:
                if self.rfd.params['MAX_WINDOW']['curValRemote'] == None:
                    self.ui.max_window_remote.setEnabled(False)
                else:
                    self.ui.max_window_remote.setEnabled(True)
                    self.ui.max_window_remote.setCurrentIndex(rfd900x.MAX_WINDOWS.index(self.rfd.params['MAX_WINDOW']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['ENCRYPTION_LEVEL']['curValRemote'] == None:
                    if self.ui.aes_encrypt_remote.isChecked():
                        self.ui.aes_encrypt_remote.click()
                    self.ui.aes_encrypt_remote.setEnabled(False)
                else:
                    self.ui.aes_encrypt_remote.setEnabled(True)
                    if self.rfd.params['ENCRYPTION_LEVEL']['curValRemote'] and not self.ui.aes_encrypt_remote.isChecked():
                        self.ui.aes_encrypt_remote.click()
            except ValueError:
                pass
    
            try:
                if self.rfd.params['EncryptionKey']['curValRemote'] == None:
                    self.ui.aes_key_remote.clear()
                    self.ui.aes_key_remote.setEnabled(False)
                else:
                    self.ui.aes_key_remote.setEnabled(True)
                    self.ui.aes_key_remote.setText(self.rfd.params['EncryptionKey']['curValRemote'])
            except ValueError:
                pass
    
            try:
                if self.rfd.params['ANT_MODE']['curValRemote'] == None:
                    self.ui.ant_mode_remote.setEnabled(False)
                else:
                    self.ui.ant_mode_remote.setEnabled(True)
                    self.ui.ant_mode_remote.setCurrentIndex(rfd900x.ANT_MODES.index(self.rfd.params['ANT_MODE']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['RATE/FREQBAND']['curValRemote'] == None:
                    self.ui.rate_and_freq_bands_remote.setEnabled(False)
                else:
                    self.ui.rate_and_freq_bands_remote.setEnabled(True)
                    self.ui.rate_and_freq_bands_remote.setCurrentIndex(rfd900x.RATE_AND_FREQ_BANDS.index(self.rfd.params['RATE/FREQBAND']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['TARGET_RSSI']['curValRemote'] == None:
                    self.ui.target_rssi_remote.setEnabled(False)
                else:
                    self.ui.target_rssi_remote.setEnabled(True)
                    self.ui.target_rssi_remote.setCurrentIndex(rfd900x.TARGET_RSSIS.index(self.rfd.params['TARGET_RSSI']['curValRemote']))
            except ValueError:
                pass
    
            try:
                if self.rfd.params['HYSTERESIS_RSSI']['curValRemote'] == None:
                    self.ui.hysteresis_rssi_remote.setEnabled(False)
                else:
                    self.ui.hysteresis_rssi_remote.setEnabled(True)
                    self.ui.hysteresis_rssi_remote.setCurrentIndex(rfd900x.HYSTERESIS_RSSIS.index(self.rfd.params['HYSTERESIS_RSSI']['curValRemote']))
            except ValueError:
                pass
        

def main():
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
    
    