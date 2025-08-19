import os
from grpc_tools import protoc

PROTO_FOLDER = "proto"
PROTO_FILE = "object_detection.proto"
OUT_PATH = "src/services"

name, ext = os.path.splitext(PROTO_FILE)
print(f"Generating python code from proto file: {PROTO_FILE}")
python_out = os.path.join(OUT_PATH, name)

if not os.path.exists(python_out):
    os.makedirs(python_out)

protoc.main(
    (
        "",
        "-I.",
        f"--python_out={python_out}",
        f"--grpc_python_out={python_out}",
        os.path.join(PROTO_FOLDER, PROTO_FILE),
    )
)
