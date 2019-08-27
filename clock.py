import time
import pycard10

if __name__ == "__main__":

    manager = None

    def connected(card10):
        manager.stop_discovery()
        card10.time_set(int(round(time.time() * 1000)))
        card10.vibra_vibrate(100)

    def failed(card10, error):
        manager.discover_card10s()

    def disconnected(card10):
        # just retry
        card10.connect(connected, disconnected, failed)

    def added(card10):
        card10.connect(connected, disconnected, failed)

    manager = pycard10.card10Manager(adapter_name='hci0', device_added=added)
    manager.is_adapter_powered = True

    if not manager.get_card10s():
        # no card10s, try to find some
        manager.discover_card10s()

    manager.run()

