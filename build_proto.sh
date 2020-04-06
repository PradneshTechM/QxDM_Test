#!/bin/bash

python3.7 -m grpc_tools.protoc -I src/ --python_out=src/ --grpc_python_out=src/ src/qxdm.proto