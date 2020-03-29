import grpc
import time
import server_pb2
import server_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = server_pb2_grpc.TestStub(channel)
        response = stub.SayHello(server_pb2.HelloRequest(name='Harv')).message
    print(f'SayHello response: {response}')

    start = time.time()
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = server_pb2_grpc.TestStub(channel)
        response = stub.Add(server_pb2.Numbers(numbers=[1, 2, 3])).sum
    exec_time = time.time() - start
    print(f'Add response: {response}')
    print(f'C++ gPRC: {exec_time}')

    print('')
    start = time.time()
    print(sum([1, 2, 3]))
    exec_time = time.time() - start
    print(f'python: {exec_time}')


if __name__ == '__main__':
    run()
