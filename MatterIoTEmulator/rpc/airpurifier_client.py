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


from rpc.device_client import DeviceClient
from google.protobuf import json_format
from airpurifier_service import airpurifier_service_pb2
import time
import logging


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s"
)


class Air_Purifier_Client(DeviceClient):
    """
    AirPurifier Client class for creating a device.
    """

    def __init__(self, socket_addr=None):
        """
        Initialize a AirPurifier client instance.

        Arguments:
            socket_addr {str} -- configuration about ip address and port
        """
        super().__init__(socket_addr)

    def GetAirPurifierSensor(self):
        """
        Return Air Purifier state.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetAirPurifierSensor()
        # logging.info(result)
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.AirPurifierState())
        return {'status': result[0].name, 'reply': reply}

    def SetAirPurifierSensor(self, data):
        """
        Set AirPurifier state and return the result.

        Arguments:
            data {str} -- the AirPurifier state
        """
        arg = airpurifier_service_pb2.AirPurifierState()
        json_format.ParseDict(data, arg)
        # logging.info(arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetAirPurifierSensor(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}

    def getFanMode(self):
        """
        Return FAN mode.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetFanMode()
        # logging.info(result)
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.AirPurifierState())
        return {'status': result[0].name, 'reply': reply}

    def setFanMode(self, data):
        """
        Set FAN mode and return the result.

        Arguments:
            data {str} -- the FAN mode
        """
        arg = airpurifier_service_pb2.AirPurifierState()
        json_format.ParseDict(data, arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetFanMode(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}

    def getMeasuredValue(self):
        """
        Return measured value.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetMeasuredValue()
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.TemperatureSensor())
        return {'status': result[0].name, 'reply': reply}

    def setMeasuredValue(self, data):
        """
        Set measured value and return the result.

        Arguments:
            data {str} -- the measured value
        """
        arg = airpurifier_service_pb2.TemperatureSensor()
        json_format.ParseDict(data, arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetMeasuredValue(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}

    def getHumidityValue(self):
        """
        Return humidity value.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetHumidityValue()
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.HumiditySensor())
        return {'status': result[0].name, 'reply': reply}

    def setHumidityValue(self, data):
        """
        Set humidity value and return the result.

        Arguments:
            data {str} -- the humidity value
        """
        arg = airpurifier_service_pb2.HumiditySensor()
        json_format.ParseDict(data, arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetHumidityValue(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}

    def getAirQuality(self):
        """
        Return AirQuality value.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetAirQuality()
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.AirQuality())
        return {'status': result[0].name, 'reply': reply}

    def setAirQuality(self, data):
        """
        Set AirQuality value and return the result.

        Arguments:
            data {str} -- the AirQuality value
        """
        arg = airpurifier_service_pb2.AirQuality()
        json_format.ParseDict(data, arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetAirQuality(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}

    def getCondition(self):
        """
        Return AirCondition value.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetCondition()
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.HEPAFilter())
        return {'status': result[0].name, 'reply': reply}

    def setCondition(self, data):
        """
        Set AirCondition value and return the result.

        Arguments:
            data {str} -- the AirCondition value
        """
        arg = airpurifier_service_pb2.HEPAFilter()
        json_format.ParseDict(data, arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetCondition(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}

    # PM25
    def getPM25(self):
        """
        Return PM25 value.
        """
        result = self.rpcs.chip.rpc.AirPurifier.GetPM25()
        reply = json_format.MessageToDict(
            result[1], airpurifier_service_pb2.PM25())
        return {'status': result[0].name, 'reply': reply}

    def setPM25(self, data):
        """
        Set PM25 value and return the result.

        Arguments:
            data {str} -- the PM25 value
        """
        arg = airpurifier_service_pb2.PM25()
        json_format.ParseDict(data, arg)
        result = self.rpcs.chip.rpc.AirPurifier.SetPM25(arg)
        reply = json_format.MessageToDict(result[1])
        return {'status': result[0].name, 'reply': reply}


if __name__ == '__main__':
    # This is the sample only
    client = Air_Purifier_Client()
    print(client.getFanMode())
    time.sleep()
