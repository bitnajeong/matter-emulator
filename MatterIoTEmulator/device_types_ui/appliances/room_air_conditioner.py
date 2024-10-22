# Copyright (c) 2024 LG Electronics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0


from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from qtwidgets import Toggle
import logging
import threading
import os
import time
from rpc.roomairconditioner_client import Room_Air_Conditioner_Client
from ..stoppablethread import UpdateStatusThread
from ..constants_device import *
from constants import *
from ..device_base_ui import *

SOURCE_PATH = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__))))
DEVICE_RESOURCE_PATH = os.path.join(SOURCE_PATH, "res/Appliances/")


HEAT = 0
COOL = 1
OCCUPANCY = 2
SCHEDULE_CONFIG = 3
SET_BACK = 4
AUTO_MODE = 5
LOCAL_TEM = 6
ALLFEATURE_THER = 7

OFF_MODE = 0
LOW_MODE = 1
MEDIUM_MODE = 2
HIGH_MODE = 3
ON_MODE = 4
AUTO_MODE = 5
SMART_MODE = 6

INDEX_OFF = 0
INDEX_HEAT = 1
INDEX_COOL = 2
INDEX_AUTO = 3

MODE_OFF = 0
MODE_AUTO = 1
MODE_COOL = 3
MODE_HEAT = 4

FAN_OFF = 0
FAN_LOW = 1
FAN_MEDIUM = 2
FAN_HIGH = 3

MULTI_SPEED = 0
AUTO = 1
ROCKING = 2
WIND = 3
STEP = 4
AIR_FLOW_DIRECTION = 5
ALL_FEATURE = 6


class RoomAirConditioner(BaseDeviceUI):
    """
    RoomAirConditioner device UI controller represent some attribues, clusters
    and endpoints corresspoding to Matter Specification v1.2
    """

    def __init__(self, parent) -> None:
        """
        Create a new `RoomAirConditioner` UI.
        :param parent: An UI object load RoomAirConditioner device UI controller.
        """
        super().__init__(parent)
        self.fan_mode = 0
        self.ther_mode = 0
        self.temperature = 0
        self.humidity = 0
        self.cooling = 0
        self.heating = 0
        self.feature_thermostat = 0
        self.feature_fan = 0
        self.on_off = False
        self.enable_update = True
        self.time_repeat = 10
        self.time_sleep = 0
        self.is_stop_clicked = False
        self.is_edit = True
        self.is_edit_hum = True
        self.is_on = True

        # Show icon
        self.lbl_main_icon = QLabel()
        pix = QPixmap(DEVICE_RESOURCE_PATH + 'room-air-conditioner.png')
        self.lbl_main_icon.setFixedSize(70, 70)
        pix = pix.scaled(
            self.lbl_main_icon.size(),
            aspectMode=Qt.KeepAspectRatio)
        self.lbl_main_icon.setPixmap(pix)
        self.lbl_main_icon.setAlignment(Qt.AlignCenter)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.lbl_main_icon)
        self.parent.ui.lo_controller.addLayout(h_layout)

        # Display on/off status
        self.lbl_main_status = QLabel()
        self.lbl_main_status.setText('Off')
        self.lbl_main_status.setAlignment(Qt.AlignCenter)
        self.parent.ui.lo_controller.addWidget(self.lbl_main_status)

        # Display local temperature
        self.lbl_temp_status = QLabel()
        self.lbl_temp_status.setText('Local Temperature:')
        self.lbl_temp_status.setAlignment(Qt.AlignCenter)
        self.parent.ui.lo_controller.addWidget(self.lbl_temp_status)

        self.line_edit_temp = QLineEdit()
        self.validator = QIntValidator()
        self.double_validator = QDoubleValidator()
        self.line_edit_temp.setValidator(self.validator)
        self.line_edit_temp.setValidator(self.double_validator)
        self.line_edit_temp.setMaximumSize(QSize(65, 20))
        self.lbl_measure = QLabel()
        self.lbl_measure.setText('°C')
        self.grid_layout_temp = QHBoxLayout()
        self.grid_layout_temp.setAlignment(Qt.AlignCenter)
        self.grid_layout_temp.addWidget(
            self.lbl_temp_status, alignment=Qt.AlignRight)
        self.grid_layout_temp.addWidget(
            self.line_edit_temp, alignment=Qt.AlignRight)
        self.grid_layout_temp.addWidget(
            self.lbl_measure, alignment=Qt.AlignRight)

        self.line_edit_temp.textEdited.connect(self.on_text_edited_temp)
        self.line_edit_temp.returnPressed.connect(self.on_return_pressed)
        self.parent.ui.lo_controller.addLayout(self.grid_layout_temp)

        # Display humidity
        self.lbl_hum_status = QLabel()
        self.lbl_hum_status.setText('Local Humidity:')
        self.lbl_hum_status.setAlignment(Qt.AlignCenter)
        self.parent.ui.lo_controller.addWidget(self.lbl_hum_status)

        self.line_edit_hum = QLineEdit()
        self.line_edit_hum.setValidator(self.validator)
        self.line_edit_hum.setValidator(self.double_validator)
        self.line_edit_hum.setMaximumSize(QSize(65, 20))
        self.lbl_measure_hum = QLabel()
        self.lbl_measure_hum.setText('%')
        self.grid_layout_hum = QHBoxLayout()
        self.grid_layout_hum.setAlignment(Qt.AlignCenter)
        self.grid_layout_hum.addWidget(
            self.lbl_hum_status, alignment=Qt.AlignRight)
        self.grid_layout_hum.addWidget(
            self.line_edit_hum, alignment=Qt.AlignRight)
        self.grid_layout_hum.addWidget(
            self.lbl_measure_hum, alignment=Qt.AlignRight)

        self.line_edit_hum.textEdited.connect(self.on_text_edited_hum)
        self.line_edit_hum.returnPressed.connect(self.on_return_pressed)
        self.parent.ui.lo_controller.addLayout(self.grid_layout_hum)

        # Show control button/switch
        self.sw_title = QLabel()
        self.sw_title.setText('Off/On')
        self.parent.ui.lo_controller.addWidget(self.sw_title)
        self.sw = Toggle()
        self.sw.setFixedSize(60, 40)
        self.sw.stateChanged.connect(self.handle_onoff_changed)
        self.parent.ui.lo_controller.addWidget(self.sw)

        # Fan feature
        self.lbl_feature = QLabel()
        self.lbl_feature.setText('Fan Feature')
        self.parent.ui.lo_controller.addWidget(self.lbl_feature)
        fan_feature_list = [
            "MultiSpeed",
            "Auto",
            "Rocking",
            "Wind",
            "Step",
            "AirflowDirection",
            "AllFeature"]
        self.fan_feature_box = QComboBox()
        self.fan_feature_box.addItems(fan_feature_list)
        # Connect the currentIndexChanged signal to a slot
        self.fan_feature_box.currentIndexChanged.connect(
            self.fan_feature_changed)
        self.parent.ui.lo_controller.addWidget(self.fan_feature_box)
        self.sl_fan_title = QLabel()
        self.sl_fan_title.setText('Fan Mode')
        self.parent.ui.lo_controller.addWidget(self.sl_fan_title)

        # Fan mode
        fan_mode_list = ["OFF", "LOW", "MEDIUM", "HIGH", "ON", "AUTO", "SMART"]
        self.fan_control_box = QComboBox()
        self.fan_control_box.addItems(fan_mode_list)
        self.fan_control_box.model().item(ON_MODE).setEnabled(False)
        self.fan_control_box.model().item(SMART_MODE).setEnabled(False)
        # Connect the currentIndexChanged signal to a slot
        self.fan_control_box.currentIndexChanged.connect(
            self.handle_fan_mode_changed)
        self.parent.ui.lo_controller.addWidget(self.fan_control_box)

        # Show heating dimmable slider
        self.sl_heat_title = QLabel()
        self.sl_heat_title.setText('Set Heating')
        self.parent.ui.lo_controller.addWidget(self.sl_heat_title)
        self.lb_heat_level = QLabel()
        self.lb_heat_level.setFixedSize(50, 30)
        self.lb_heat_level.setText('°C')
        self.lb_heat_level.setAlignment(Qt.AlignCenter)
        self.parent.ui.lo_controller.addWidget(self.lb_heat_level)

        self.sl_heat_level = QSlider()
        self.sl_heat_level.setRange(700, 3000)
        self.sl_heat_level.setOrientation(Qt.Horizontal)
        self.sl_heat_level.valueChanged.connect(self.update_heat_level)
        self.sl_heat_level.sliderReleased.connect(
            self.handle_level_heating_changed)
        self.sl_heat_level.sliderPressed.connect(self.on_pressed_event)
        self.parent.ui.lo_controller.addWidget(self.sl_heat_level)

        # Show cooling dimmable slider
        self.sl_cool_title = QLabel()
        self.sl_cool_title.setText('Set Cooling')
        self.parent.ui.lo_controller.addWidget(self.sl_cool_title)
        self.lb_cool_level = QLabel()
        self.lb_cool_level.setFixedSize(50, 30)
        self.lb_cool_level.setText('°C')
        self.lb_cool_level.setAlignment(Qt.AlignCenter)
        self.parent.ui.lo_controller.addWidget(self.lb_cool_level)

        self.sl_cool_level = QSlider()
        self.sl_cool_level.setRange(1600, 3200)
        self.sl_cool_level.setOrientation(Qt.Horizontal)
        self.sl_cool_level.valueChanged.connect(self.update_cool_level)
        self.sl_cool_level.sliderReleased.connect(
            self.handle_level_cooling_changed)
        self.sl_cool_level.sliderPressed.connect(self.on_pressed_event)
        self.parent.ui.lo_controller.addWidget(self.sl_cool_level)

        # Thermostat feature
        self.lbl_thermostat_feature = QLabel()
        self.lbl_thermostat_feature.setText('Thermostat Feature')
        self.parent.ui.lo_controller.addWidget(self.lbl_thermostat_feature)

        thermostat_feature_list = [
            "Heating",
            "Cooling",
            "Occupancy",
            "Schedule Configuration",
            "SetBback",
            "Auto Mode",
            "Local Tmeperature Not Exposed",
            "AllFeature"]
        self.thermostat_feature_box = QComboBox()
        self.thermostat_feature_box.addItems(thermostat_feature_list)
        self.thermostat_feature_box.model().item(OCCUPANCY).setEnabled(False)
        self.thermostat_feature_box.model().item(SCHEDULE_CONFIG).setEnabled(False)
        self.thermostat_feature_box.model().item(SET_BACK).setEnabled(False)
        self.thermostat_feature_box.model().item(LOCAL_TEM).setEnabled(False)
        # Connect the currentIndexChanged signal to a slot
        self.thermostat_feature_box.currentIndexChanged.connect(
            self.thermostat_feature_changed)
        self.parent.ui.lo_controller.addWidget(self.thermostat_feature_box)
        self.lbl_mod = QLabel()
        self.lbl_mod.setText('Thermostat System Mode')
        self.parent.ui.lo_controller.addWidget(self.lbl_mod)

        # Create a thermostat system mode
        mod_list = ["Off", "Heat", "Cool", "Auto"]
        self.mod_box = QComboBox()
        self.mod_box.addItems(mod_list)
        # Connect the currentIndexChanged signal to a slot
        self.mod_box.currentIndexChanged.connect(
            self.handle_thermostat_mode_changed)
        self.parent.ui.lo_controller.addWidget(self.mod_box)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.sl_heat_title, 0, 0)
        self.grid_layout.addWidget(self.lb_heat_level, 0, 1)
        self.grid_layout.addWidget(self.sl_heat_level, 1, 0)
        self.grid_layout.addWidget(self.sl_cool_title, 2, 0)
        self.grid_layout.addWidget(self.lb_cool_level, 2, 1)
        self.grid_layout.addWidget(self.sl_cool_level, 3, 0)
        self.parent.ui.lo_controller.addLayout(self.grid_layout)

        # Init rpc
        self.client = Room_Air_Conditioner_Client(self.config)
        self.set_initial_value()
        self.start_update_device_status_thread()
        logging.debug("Init Room Air Conditioner done")

    def fan_feature_changed(self, feature_type):
        """
        Handle display UI when fan control feature map change
        :param feature_type: Value feature map of fan control cluster
        """
        logging.info("RPC SET fan feature: " + str(feature_type))
        self.client.SetRoomAirConditionerSensor(
            {'FanFeatureMap': {'featureMap': feature_type}})
        self.mutex.acquire(timeout=1)
        self.mutex.release()

    def thermostat_feature_changed(self, feature_type):
        """
        Handle display UI when thermostat feature map change
        :param feature_type: Value feature map of thermostat cluster
        """
        logging.info("RPC SET thermostat feature: " + str(feature_type))
        self.client.SetRoomAirConditionerSensor(
            {'ThermostatFeatureMap': {'featureMap': feature_type}})
        self.client.SetRoomAirConditionerSensor(
            {
                'Thermostat': {
                    'systemMode': MODE_OFF,
                    'OccupiedCoolingSetpoint': self.cooling,
                    'OccupiedHeatingSetpoint': self.heating}})
        self.mutex.acquire(timeout=1)
        self.mutex.release()

    def enable_update_mode(self):
        """Enable attribute 'enable_update' for enable update value of combo box"""
        self.enable_update = True

    def on_text_edited_temp(self):
        """Enable 'is_edit' attribute when line edit temperature is editting"""
        self.is_edit = False

    def on_text_edited_hum(self):
        """Enable 'is_edit' attribute when line edit humidity is editting"""
        self.is_edit_hum = False

    def on_return_pressed(self):
        """
        Handle set temperature measurement or
        humidity measurement when set from line edit
        """
        try:
            value_temp = round(float(self.line_edit_temp.text()) * 100)
            value_hum = round(float(self.line_edit_hum.text()) * 100)
            if 0 <= value_temp <= 10000:
                data_temp = {
                    'TemperatureMeasurement': {
                        'MeasuredValue': value_temp}}
                self.client.SetMeasuredValue(data_temp)
                self.is_edit = True
            else:
                self.message_box(ER_TEMP)
                self.line_edit_temp.setText(str(self.temperature))

            if 0 <= value_hum <= 10000:
                data_hum = {
                    'RelativeHumidityMeasurement': {
                        'HumidityValue': value_hum}}
                self.client.SetHumiditySensorValue(data_hum)
                self.is_edit_hum = True
            else:
                self.message_box(ER_HUM)
                self.line_edit_hum.setText(str(self.humidity))
        except Exception as e:
            logging.error("Error: " + str(e))

    def message_box(self, message):
        """
        Message box to notify value out of range when set value to line edit
        :param message: The notify message to user
        """
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Air Quality SenSor")
        msgBox.setText("Value out of range")
        msgBox.setInformativeText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def on_pressed_event(self):
        """
        Enable 'is_on_control' attribute when occupied cooling slider or
        occupied heating slider of thermostat change
        """
        self.is_on_control = True

    def handle_fan_mode_changed(self, mode):
        """
        Handle fan mode change
        :param mode {int}: A new mode of fan mode
        """
        logging.info("RPC SET Fan Mode: " + str(mode))
        self.enable_update = False
        QTimer.singleShot(1, self.enable_update_mode)
        self.mutex.acquire(timeout=1)
        self.client.SetRoomAirConditionerSensor(
            {'Fancontrol': {'FanMode': mode}})
        self.mutex.release()

    def handle_thermostat_mode_changed(self, mode):
        """
        Handle thermostat system mode change
        :param mode {int}: A new mode of thermostat system mode
        """
        logging.info("RPC SET Thermostat System Mode: " + str(mode))
        index = self.mod_box.currentIndex()
        level_cool = self.sl_cool_level.value()
        level_heat = self.sl_heat_level.value()
        self.mutex.acquire(timeout=1)
        self.check_system_mode(index)
        if index == INDEX_OFF:
            self.ther_mode = MODE_OFF
        elif index == INDEX_HEAT:
            self.ther_mode = MODE_HEAT

        elif index == INDEX_COOL:
            self.ther_mode = MODE_COOL

        elif index == INDEX_AUTO:
            self.ther_mode = MODE_AUTO

        self.client.SetRoomAirConditionerSensor(
            {
                'Thermostat': {
                    'systemMode': self.ther_mode,
                    'OccupiedCoolingSetpoint': level_cool,
                    'OccupiedHeatingSetpoint': level_heat}})
        self.mutex.release()
        self.is_on_control = False

    def check_system_mode(self, index):
        """
        Check thermostat system mode change
        then enable or disable UI corressponding to each system mode value
        :param index {int}: A index of system mode combo box
        """
        if index == INDEX_OFF:
            self.sl_heat_level.setEnabled(False)
            self.sl_cool_level.setEnabled(False)

        elif index == INDEX_HEAT:
            self.sl_heat_level.setEnabled(True)
            self.sl_cool_level.setEnabled(False)

        elif index == INDEX_COOL:
            self.sl_cool_level.setEnabled(True)
            self.sl_heat_level.setEnabled(False)

        elif index == INDEX_AUTO:
            self.sl_heat_level.setEnabled(True)
            self.sl_cool_level.setEnabled(True)

    def set_initial_value(self):
        """
        Handle set initial value of all supported attributes
        to matter device(backend) through rpc service
        """
        try:
            data_hum = {'RelativeHumidityMeasurement': {'HumidityValue': 9611}}
            data_temp = {'TemperatureMeasurement': {'MeasuredValue': 2834}}
            data_room = {
                'OnOff': {
                    'OnOff': True},
                'Thermostat': {
                    'OccupiedHeatingSetpoint': 2125,
                    'OccupiedCoolingSetpoint': 2776,
                    'systemMode': MODE_OFF},
                'Fancontrol': {
                    'FanMode': FAN_MEDIUM,
                    'SpeedSetting': 100},
                'FanFeatureMap': {
                    'featureMap': 1},
                'ThermostatFeatureMap': {
                    'featureMap': ALLFEATURE_THER}}
            self.client.SetRoomAirConditionerSensor(data_room)
            self.client.SetHumiditySensorValue(data_hum)
            self.client.SetMeasuredValue(data_temp)
        except Exception as e:
            self.parent.wkr.connect_status.emit(STT_RPC_INIT_FAIL)
            logging.info("Can not set initial value: " + str(e))

    def update_cool_level(self, value):
        """
        Update OccupiedCooling value for OccupiedCooling label
        :param value: Value of OccupiedCooling slider
        """
        self.lb_cool_level.setText(str(round(value / 100.0, 2)) + "°C")

    def update_heat_level(self, value):
        """
        Update OccupiedHeating value for OccupiedHeating label
        :param value: Value of OccupiedHeating slider
        """
        self.lb_heat_level.setText(str(round(value / 100.0, 2)) + "°C")

    def check_onoff(self, is_On):
        """
        Handle disable or enable feature on UI
        when on/off attribute change
        :param is_On: Value of on-off attribute, 0: False, other True
        """
        if is_On:
            self.fan_control_box.setEnabled(True)
            self.mod_box.setEnabled(True)
            self.thermostat_feature_box.setEnabled(True)
            self.fan_feature_box.setEnabled(True)
        else:
            self.fan_control_box.setEnabled(False)
            self.mod_box.setEnabled(False)
            self.thermostat_feature_box.setEnabled(False)
            self.fan_feature_box.setEnabled(False)
            self.client.SetRoomAirConditionerSensor(
                {'Thermostat': {'systemMode': MODE_OFF}})

    def handle_onoff_changed(self, data):
        """
        Handle set on off attribute to matter device(backend)
        through rpc service when on/off toggle
        :param data: Value of on-off attribute, 0: False, other True
        """
        logging.info("RPC SET On/Off: " + str(data))
        self.mutex.acquire(timeout=1)
        if data == 0:
            self.client.SetRoomAirConditionerSensor(
                {'OnOff': {'OnOff': False}})
            self.is_stop_clicked = True
            self.check_onoff(False)
        else:
            self.client.SetRoomAirConditionerSensor({'OnOff': {'OnOff': True}})
            self.is_stop_clicked = False
            self.check_onoff(True)
        self.mutex.release()

    def handle_level_cooling_changed(self):
        """
        Handle set OccupiedCooling value to matter device(backend)
        through rpc service when OccupiedCooling slider change
        """
        level_cool = self.sl_cool_level.value()
        level_heat = self.sl_heat_level.value()
        logging.info("RPC SET Cool level: " + str(level_cool))
        self.mutex.acquire(timeout=1)
        if "On" in self.lbl_main_status.text():
            self.on_off = True
        else:
            self.on_off = False

        self.client.SetRoomAirConditionerSensor(
            {
                'OnOff': {
                    'OnOff': self.on_off},
                'Fancontrol': {
                    'FanMode': self.fan_mode},
                'Thermostat': {
                    'systemMode': self.ther_mode,
                    'OccupiedCoolingSetpoint': level_cool,
                    'OccupiedHeatingSetpoint': level_heat}})
        self.mutex.release()
        self.is_on_control = False

    def handle_level_heating_changed(self):
        """
        Handle set OccupiedHeating value to matter device(backend)
        through rpc service when OccupiedHeating slider change
        """
        level_heat = self.sl_heat_level.value()
        level_cool = self.sl_cool_level.value()
        logging.info("RPC SET Heat level: " + str(level_heat))
        self.mutex.acquire(timeout=1)
        if "On" in self.lbl_main_status.text():
            self.on_off = True
        else:
            self.on_off = False

        self.client.SetRoomAirConditionerSensor(
            {
                'OnOff': {
                    'OnOff': self.on_off},
                'Fancontrol': {
                    'FanMode': self.fan_mode},
                'Thermostat': {
                    'systemMode': self.ther_mode,
                    'OccupiedCoolingSetpoint': level_cool,
                    'OccupiedHeatingSetpoint': level_heat}})
        self.mutex.release()
        self.is_on_control = False

    def check_enable_fan_feature(self, feature_type):
        """
        Check fan feature map change
        then enable or disable UI corressponding to each fan feature map value
        :param feature_type {int}: A feature map value of fan feature map
        """
        self.fan_control_box.setEnabled(False)
        self.fan_control_box.model().item(AUTO_MODE).setEnabled(False)
        if ((feature_type == MULTI_SPEED) or (
                feature_type == AUTO) or (feature_type == STEP)):
            self.fan_control_box.setEnabled(True)
            if (feature_type == AUTO):
                self.fan_control_box.model().item(AUTO_MODE).setEnabled(True)
        elif (feature_type == ALL_FEATURE):
            self.fan_control_box.setEnabled(True)
            self.fan_control_box.model().item(AUTO_MODE).setEnabled(True)

    def check_enable_feature_thermostat(self, feature_type):
        """
        Check thermostat feature map change
        then enable or disable UI corressponding to each thermostat feature map value
        :param feature_type {int}: A feature map value of thermostat feature map
        """
        if (feature_type == HEAT):
            self.mod_box.model().item(INDEX_COOL).setEnabled(False)
            self.mod_box.model().item(INDEX_AUTO).setEnabled(False)
            self.mod_box.model().item(INDEX_HEAT).setEnabled(True)
        elif (feature_type == COOL):
            self.mod_box.model().item(INDEX_HEAT).setEnabled(False)
            self.mod_box.model().item(INDEX_AUTO).setEnabled(False)
            self.mod_box.model().item(INDEX_COOL).setEnabled(True)
        elif (feature_type == AUTO_MODE):
            self.mod_box.model().item(INDEX_HEAT).setEnabled(False)
            self.mod_box.model().item(INDEX_AUTO).setEnabled(True)
            self.mod_box.model().item(INDEX_COOL).setEnabled(False)
        elif (feature_type == ALLFEATURE_THER):
            self.mod_box.model().item(INDEX_HEAT).setEnabled(True)
            self.mod_box.model().item(INDEX_AUTO).setEnabled(True)
            self.mod_box.model().item(INDEX_COOL).setEnabled(True)

    def on_device_status_changed(self, result):
        """
        Interval update all attributes value
        to UI through rpc service
        :param result {dict}: Data get all attributes value
        from matter device(backend) from rpc service
        """
        # logging.info(f'on_device_status_changed {result}, RPC Port: {str(self.parent.rpcPort)}')
        try:
            device_hum_status = result['device_hum_status']
            device_tem_status = result['device_tem_status']
            device_room_status = result['device_room_status']
            device_state = result['device_state']
            self.parent.update_device_state(device_state)
            if device_room_status['status'] == 'OK':
                self.heating = device_room_status['reply']['Thermostat']['OccupiedHeatingSetpoint']
                self.sl_heat_level.setValue(self.heating)
                self.cooling = device_room_status['reply']['Thermostat']['OccupiedCoolingSetpoint']
                self.sl_cool_level.setValue(self.cooling)

                if self.feature_thermostat != device_room_status[
                        'reply']['ThermostatFeatureMap']['featureMap']:
                    self.feature_thermostat = device_room_status[
                        'reply']['ThermostatFeatureMap']['featureMap']
                    self.thermostat_feature_box.setCurrentIndex(
                        self.feature_thermostat)
                    self.check_enable_feature_thermostat(
                        self.feature_thermostat)

                if self.feature_fan != device_room_status['reply']['FanFeatureMap']['featureMap']:
                    self.feature_fan = device_room_status['reply']['FanFeatureMap']['featureMap']
                    self.fan_feature_box.setCurrentIndex(self.feature_fan)
                    self.check_enable_fan_feature(self.feature_fan)

                if (self.fan_mode !=
                        device_room_status['reply']['Fancontrol']['FanMode']):
                    self.fan_mode = device_room_status['reply']['Fancontrol']['FanMode']
                    if self.enable_update:
                        self.fan_control_box.setCurrentIndex(self.fan_mode)
                if self.on_off != device_room_status['reply']['OnOff']['OnOff']:
                    self.on_off = device_room_status['reply']['OnOff']['OnOff']
                    if self.on_off:
                        self.lbl_main_status.setText('On')
                        self.sw.setCheckState(Qt.Checked)
                    else:
                        self.lbl_main_status.setText('Off')
                        self.sw.setCheckState(Qt.Unchecked)

                if (self.ther_mode !=
                        device_room_status['reply']['Thermostat']['systemMode']):
                    self.ther_mode = device_room_status['reply']['Thermostat']['systemMode']
                    if self.ther_mode == MODE_OFF:
                        self.mod_box.setCurrentIndex(INDEX_OFF)
                    elif self.ther_mode == MODE_HEAT:
                        self.mod_box.setCurrentIndex(INDEX_HEAT)
                    elif self.ther_mode == MODE_COOL:
                        self.mod_box.setCurrentIndex(INDEX_COOL)
                    elif self.ther_mode == MODE_AUTO:
                        self.mod_box.setCurrentIndex(INDEX_AUTO)

                self.check_system_mode(self.mod_box.currentIndex())

            if device_tem_status['status'] == 'OK':
                self.temperature = round(
                    float(
                        device_tem_status['reply']['TemperatureMeasurement']['MeasuredValue'] /
                        100),
                    2)
                if self.is_edit:
                    self.line_edit_temp.setText(str(self.temperature))
            if device_hum_status['status'] == 'OK':
                self.humidity = round(
                    float(
                        device_hum_status['reply']['RelativeHumidityMeasurement']['HumidityValue'] /
                        100),
                    2)
                if self.is_edit_hum:
                    self.line_edit_hum.setText(str(self.humidity))

        except Exception as e:
            logging.error("Error: " + str(e))

    def update_device_status(self):
        """
        Update value for all attributes on UI
        when set timer for change random attribute value
        """
        try:
            while self.check_condition_update_status(
                    self.update_device_status_thread):
                try:
                    if not self.is_on_control:
                        self.mutex.acquire(timeout=1)
                        device_hum_status = self.client.GetHumiditySensorValue()
                        device_tem_status = self.client.GetMeasuredValue()
                        device_room_status = self.client.GetRoomAirConditionerSensor()
                        device_state = self.client.get_device_state()
                        self.mutex.release()
                        self.sig_device_status_changed.emit(
                            {
                                'device_hum_status': device_hum_status,
                                'device_tem_status': device_tem_status,
                                'device_room_status': device_room_status,
                                'device_state': device_state})
                    time.sleep(0.5)
                except Exception as e:
                    logging.error(
                        f'{str(e)} , RPC Port: {str(self.parent.rpcPort)}')
        except Exception as e:
            logging.error(str(e))

    def stop(self):
        """
        Stop thread update device state
        Stop rpc client
        """
        self.stop_update_state_thread()
        self.stop_client_rpc()
