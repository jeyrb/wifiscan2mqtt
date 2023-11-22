import paho.mqtt.client as mqtt
import subprocess
import structlog
import asyncio

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


def scan(device="wlan0",timeout=90):
    ret = subprocess.run(('/usr/bin/nmcli','-m','multiline','-c','no','--fields','all','device','wifi','list'),
			  capture_output=True,timeout=timeout,text=True)
    nets=[]
    net=None
    for l in ret.stdout.split('\n'):
      if l and ':' in l:
        tag,value=l.split(':',1)
        if tag == 'NAME':
            if net is not None:
                nets.append(net)
            net={}
        net[tag]=value.strip()
    if net:
        nets.append(net)
    for net in nets:
        print(net)


if __name__ == "__main__":
    scan()
