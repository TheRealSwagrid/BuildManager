#!/usr/bin/env python
import json
import os.path
import signal
import sys
from copy import deepcopy

import numpy as np
import quaternion
from time import sleep
from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint


class BuildManager(AbstractVirtualCapability):

    def __init__(self, server):
        super().__init__(server)
        self.build_plan = {}
        self.fitted_blocks = []
        self.max_key = -1
        self.factor = 100

    def LoadBuildPlan(self, params: dict):
        file_location = params["SimpleStringParameter"]
        formatPrint(self, f"Loading Build Plan: {file_location}")
        if os.path.exists(file_location):
            with open(file_location, mode='r') as file:
                self.build_plan = json.loads(file.read())
                self.max_key = max([int(k) for k in self.build_plan.keys()])
        else:
            raise FileNotFoundError("This file does not exist")
        formatPrint(self, f"New BuildPlan: {self.build_plan}")
        return {}

    def GetNextBlockPosition(self, params: dict):
        for i in range(1, self.max_key):
            key = str(i)
            if key not in self.fitted_blocks:
                dependency_resolved = True
                for dependency in self.build_plan[key]["depends_on"]:
                    dependency_resolved &= str(dependency) in self.fitted_blocks
                if not dependency_resolved:
                    continue
                pos = np.round(np.array(self.build_plan[key]["position"]), decimals=5)
                rot = np.round(np.array(self.build_plan[key]["rotation"]), decimals=7)

                ret = {"Position3D": pos.tolist(), "Quaternion": rot.tolist(),
                       "Vector3": self.build_plan[key]["shape"]}
                self.fitted_blocks += [key]
                return ret
        raise ValueError("No Block avaiable")

    def GetAvailableBlocks(self, params: dict):
        blocks = []
        for i in range(1, self.max_key):
            key = str(i)
            if key not in self.fitted_blocks:
                dependency_resolved = True
                for dependency in self.build_plan[key]["depends_on"]:
                    dependency_resolved &= str(dependency) in self.fitted_blocks
                if not dependency_resolved:
                    continue
                pos = np.round(np.array(self.build_plan[key]["position"]), decimals=5) * self.factor
                rot = np.round(np.array(self.build_plan[key]["rotation"]), decimals=7)

                ret = {"Position3D": pos.tolist(), "Quaternion": rot.tolist(),
                       "Vector3": (np.array(self.build_plan[key]["shape"])*self.factor).tolist(), "int": key}
                blocks.append(ret)
        for b in blocks:
            self.fitted_blocks += [b["int"]]
        return {"ParameterList": blocks}

    # noinspection PyUnreachableCode
    def GetWalls(self, params: dict) -> dict:
        walls = list()
        for i in range(1, self.max_key):
            key = str(i)
            block = self.build_plan[key]
            pos = np.array(block["position"]) * self.factor
            rotation = block["rotation"]

            quat = quaternion.as_quat_array(rotation)
            x = quaternion.rotate_vectors(quat, np.array([1., 0., 0.]))
            y = quaternion.rotate_vectors(quat, np.array([0., 1., 0.]))
            z = quaternion.rotate_vectors(quat, np.array([0., 0., 1.]))
            norm = np.cross(x, z)

            d = np.dot(np.array(pos), norm)
            norm_0 = norm / np.sum(np.sqrt(norm ** 2))
            norm_0 *= -1 if d < 0 else 1
            norm_0 = np.round(norm_0, decimals=5)
            d = np.round(np.dot(np.array(pos), norm_0), decimals=5)
            object = norm_0.tolist()
            # print(ls)
            object.append(d)
            if object not in walls:
                walls.append(object)
        return {"ListOfPoints": walls}

    def GetStartingPoints(self, params: dict):
        walls = self.GetWalls(params)
        points = []
        for wall in walls["ListOfPoints"]:
            """
            wall_norm = np.array(wall[:3])
            global_up = np.array([0, 0, 1])

            axis = np.cross(wall_norm, global_up)
            axis /= np.linalg.norm(axis)

            angle = np.arccos(np.dot(wall_norm, global_up))

            half_angle = angle / 2
            sin_half_angle = np.sin(half_angle)
            cos_half_angle = np.cos(half_angle)

            q = [sin_half_angle * axis[0], sin_half_angle * axis[1], sin_half_angle * axis[2], cos_half_angle]
            """
            points.append(
                (np.array(wall[:3]) * wall[3]).tolist() + (np.cross(wall[:3], [0, 0, 1]) != 0).astype(float).tolist())

        return {"ListOfPoints": points}

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
