import paho.mqtt.client as mqtt
import structlog
import asyncio
from py_wifi_helper import yy_wifi_helper
from py_wifi_helper.yy_wifi_helper import WIFIAP

log = structlog.get_logger()


class MqttClient:
    def __init__(self):
        self.log = structlog.get_logger().bind()

    def start(self, event_loop=None):
        log = self.log.bind(action="start")
        try:
            self.event_loop = event_loop or asyncio.get_event_loop()
            self.client = mqtt.Client(
                client_id="release2mqtt_%s" % self.node_cfg.name, clean_session=True
            )
            self.client.username_pw_set(self.cfg.user, password=self.cfg.password)
            self.client.connect(host=self.cfg.host, port=self.cfg.port, keepalive=60)

            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            self.client.loop_start()

            log.info("Connected to broker at %s:%s" % (self.cfg.host, self.cfg.port))
        except Exception as e:
            log.error(
                "Failed to connect to broker %s:%s - %s",
                self.cfg.host,
                self.cfg.port,
                e,
                exc_info=1,
            )
            raise EnvironmentError(
                "Connection Failure to %s:%s as %s -- %s"
                % (self.cfg.host, self.cfg.port, self.cfg.user, e)
            )

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, _client, _userdata, _flags, rc):
        self.log.info("Connected to broker", result_code=rc)

    def on_disconnect(self, _client, _userdata, rc):
        self.log.info("Disconnected from broker", result_code=rc)

    def on_message(self, _client, _userdata, msg):
        self.log.info("Message received", msg=msg)


def scan(device="en0"):
    obj = yy_wifi_helper.YYWIFIHelper()
    query = obj.getAPList(device)

    if "status" in query and query["status"]:
        for item in query["list"]:
            print(item[WIFIAP.SSID],item[WIFIAP.CHANNEL_BAND],item[WIFIAP.CHANNEL_NUMBER])


if __name__ == "__main__":
    scan()
