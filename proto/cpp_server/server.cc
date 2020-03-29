#include <iostream>
#include <string>
#include <vector>

#include <grpcpp/grpcpp.h>
#include "server.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

using test::Test;
using test::HelloRequest;
using test::HelloReply;
using test::Numbers;
using test::Sum;

class TestServiceImpl final : public Test::Service {
  Status SayHello(ServerContext* context,
		  const HelloRequest* request,
		  HelloReply* reply) override {
    std::string prefix("Hello ");
    reply->set_message(prefix + request->name());
    return Status::OK;
  }

  Status Add(ServerContext* context,
  	     const Numbers* request,
  	     Sum* reply) override {
    int sum;
    sum = 0;

    for (auto num : request->numbers()){
      sum = sum+num;
    }

    reply->set_sum(sum);
    return Status::OK;
  }
};

void RunServer(){
  std::string server_address("0.0.0.0:50051");
  TestServiceImpl service;

  ServerBuilder builder;
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);  
  std::unique_ptr<Server> server(builder.BuildAndStart());
  
  std::cout << "Server listening on " << server_address << std::endl;

  server->Wait();
}

int main(int agrc, char** argv) {
  RunServer();

  return 0;
}
  
