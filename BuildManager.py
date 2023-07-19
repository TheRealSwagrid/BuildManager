#!/usr/bin/env python
import signal
import sys

from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint


class BuildManager(AbstractVirtualCapability):

    def __init__(self, server):
        super().__init__(server)
        self.build_plan = {
            "block_1": {
                "position": [0., 0., 0.]
            },
            "block_2" : {

            }
        }

    def LoadBuildPlan(self, params: dict):
        file_location = params["SimpleStringParameter"]
        formatPrint(self, f"Loading Build Plan: {file_location}")
        return {}

    def GetNextBlockPosition(self, params: dict):
        return params
