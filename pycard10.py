import gatt

# TODO: proper error handling

class card10(gatt.Device):
    def connect(self, connected=None, disconnected=None, failed=None):
        self._connected_cb = connected
        self._disconnected_cb = disconnected
        self._failed_cb = failed
        if self.is_connected():
            if self.is_services_resolved():
                self.services_resolved()
            return
        print("[%s] Connecting..." % (self.mac_address))
        # TODO: make it async
        super().connect()

    def _connected(self):
        print("[%s] Connected" % (self.mac_address))
        self._connect_signals()
        if self.is_services_resolved():
            self.services_resolved()
        elif not self.is_bonded():
            self._object.Pair()

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        if self._failed_cb:
            self._failed_cb(self, error)

    def _disconnected(self):
        print("[%s] Disconnected" % (self.mac_address))
        self._disconnect_signals()
        if self._disconnected_cb:
            self._disconnected_cb(self)

    def services_resolved(self):
        super().services_resolved()
        print("[%s] Let's roll!" % (self.mac_address))
        if self._connected_cb:
            self._connected_cb(self)

    def _get_characteristic(self, uuid):
        if not self.is_services_resolved():
            return

        device_information_service = next(
            s for s in self.services
            if s.uuid == '42230200-2342-2342-2342-234223422342')

        return next(
            c for c in device_information_service.characteristics
            if c.uuid == uuid)

    def time_get(self):
        characteristic = self._get_characteristic('42230201-2342-2342-2342-234223422342')
        if not characteristic:
            return
        values = characteristic.read_value()
        time = 0
        for i in range(8):
            time += values[7-i] * 256**i
        return time

    def time_set(self, time):
        characteristic = self._get_characteristic('42230201-2342-2342-2342-234223422342')
        if not characteristic:
            return
        values = []
        for i in range(8):
            r = time % 256
            time = (time - r) // 256
            values.append(r)
        values.reverse()
        characteristic.write_value(values)

    def rockets_set(self, blue, orange, green):
        characteristic = self._get_characteristic('42230210-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([blue, orange, green])

    def vibra_vibrate(self, time):
        characteristic = self._get_characteristic('4223020f-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([time % 256, time // 256])

    def leds_bottom_left_set(self, r, g, b):
        characteristic = self._get_characteristic('42230211-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([r, g, b])

    def leds_bottom_right_set(self, r, g, b):
        characteristic = self._get_characteristic('42230212-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([r, g, b])

    def leds_top_right_set(self, r, g, b):
        characteristic = self._get_characteristic('42230213-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([r, g, b])

    def leds_top_left_set(self, r, g, b):
        characteristic = self._get_characteristic('42230214-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([r, g, b])

    def leds_dim_bottom_set(self, val):
        characteristic = self._get_characteristic('42230215-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([val])

    def leds_dim_top_set(self, val):
        characteristic = self._get_characteristic('42230216-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([val])

    def leds_powersafe_set(self, val):
        characteristic = self._get_characteristic('42230217-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([val])

    def leds_flashlight_set(self, val):
        characteristic = self._get_characteristic('42230218-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([val])

    def personal_state_set(self, val):
        characteristic = self._get_characteristic('42230219-2342-2342-2342-234223422342')
        if not characteristic:
            return
        characteristic.write_value([val % 256, val // 256])

    def leds_set(self, vals):
        characteristic = self._get_characteristic('42230220-2342-2342-2342-234223422342')
        if not characteristic:
            return
        leds = []
        for val in vals:
            leds.append(val[0])
            leds.append(val[1])
            leds.append(val[2])
        for i in range(0, 11 - len(vals)):
            leds.append(0)
            leds.append(0)
            leds.append(0)
        characteristic.write_value(leds)

    def light_sensor_get(self):
        characteristic = self._get_characteristic('422302f0-2342-2342-2342-234223422342')
        if not characteristic:
            return
        values = characteristic.read_value()
        return values[0] + values[1] * 256

    # TODO: file transfer

    def characteristic_write_value_failed(self, *args, **kwargs):
        print("FAIL", args, kwargs)

    def is_card10(self):
        return self.mac_address.upper().startswith('CA:4D:10:')

    def is_bonded(self):
        return self._properties.Get('org.bluez.Device1', 'Paired') == 1

class card10Manager(gatt.DeviceManager):
    def __init__(self, adapter_name, device_added):
        self._device_added_cb = device_added
        super().__init__(adapter_name)

    def device_discovered(self, device):
        if not device.is_card10():
            return
        print("Discovered [%s] %s" % (device.mac_address, device.alias()))
        if self._device_added_cb:
            self._device_added_cb(device)

    def make_device(self, mac_address):
        return card10(mac_address=mac_address, manager=self)

    def discover_card10s(self):
        print("Looking for card10s...")
        manager.start_discovery(['42230100-2342-2342-2342-234223422342', '42230200-2342-2342-2342-234223422342'])

    def get_card10s(self):
        return [device for device in self.devices() if device.is_card10()]

    def _properties_changed(self, interface, changed, invalidated, path):
        mac_address = self._mac_address(path)
        if not mac_address:
            return
        device = self._devices.get(mac_address)
        if not device.is_card10():
            return
        #print("changed", interface, changed, invalidated, path)
        if device and changed.get("Connected") is not None:
            if changed["Connected"]:
                device._connected()
            else:
                device._disconnected()
        if device and changed.get("ServicesResolved"):
            device.services_resolved()

    def run(self, mainloop=None):
        if self._device_added_cb:
            for device in self.get_card10s():
                self._device_added_cb(device)
        super().run()
