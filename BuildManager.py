#!/usr/bin/env python
import json
import os.path
import signal
import sys
from time import sleep
from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint


class BuildManager(AbstractVirtualCapability):

    def __init__(self, server):
        super().__init__(server)
        self.build_plan = {}
        self.fitted_blocks = {}
        self.keys = []
        self.current_key = 0

    def LoadBuildPlan(self, params: dict):
        file_location = params["SimpleStringParameter"]
        formatPrint(self, f"Loading Build Plan: {file_location}")
        if os.path.exists(file_location):
            with open(file_location, mode='r') as file:
                self.build_plan = json.loads(file.read())
                self.keys = list(self.build_plan.keys())
        else:
            raise FileNotFoundError("This file does not exist")
        formatPrint(self, f"New BuildPlan: {self.build_plan}")
        return {}

    def GetNextBlockPosition(self, params: dict):
        key = self.keys[self.current_key]
        ret = {"Position3D": self.build_plan[key]["position"], "Quaternion": self.build_plan[key]["rotation"]}
        ret["Vector3"] = self.build_plan[key]["shape"]
        self.current_key += 1
        return ret

    def loop(self):

        sleep(.0001)

if __name__ == '__main__':
    # Needed for properly closing when process is being stopped with SIGTERM signal
    def handler(signum, frame):
        print("[Main] Received SIGTERM signal")
        listener.kill()
        quit(1)


    try:
        port = None
        if len(sys.argv[1:]) > 0:
            port = int(sys.argv[1])
        server = VirtualCapabilityServer(port)
        listener = BuildManager(server)
        listener.start()
        signal.signal(signal.SIGTERM, handler)
        listener.join()
    # Needed for properly closing, when program is being stopped wit a Keyboard Interrupt
    except KeyboardInterrupt:
        print("[Main] Received KeyboardInterrupt")
        server.kill()
        listener.kill()
