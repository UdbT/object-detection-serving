# proto folder
This folder is for proto files. These proto files must not be included in docker container when deployed.
In order to build python files from a specific proto file, you will need to
1. Create your own .proto file. (The name of your proto file will be the folder name under `src/services`)
2. Install grpc dependencies `pip install grpcio-tools==1.64.1`
3. Change your PROTO_FILE in `proto/run_codegen.py` to be your proto file
4. Run `python -m proto.run_codegen`
5. `src/services/xxx/proto` folder will be created along with 2 python files `xxx_pb2_grpc.py` and `xxx_pb2.py`
6. Go to `src/services/xxx/proto/xxx_pb2_grpc.py` and change `from proto import ...` to `from . import ...`