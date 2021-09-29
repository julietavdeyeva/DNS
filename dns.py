import dnslib
import pickle
import socket
import sys
import time


class DNS:
    def __init__(self):
        self.cache = {}
        self.request = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.request.bind(('localhost', 53))
        self.request.settimeout(1)
        self.response.settimeout(1)

    def run(self):
        try:
            data, address = self.request.recvfrom(512)
            if data:
                parse_data = dnslib.DNSRecord.parse(data)
                question = parse_data.questions[0]
                if question.qname in self.cache and question.qtype in self.cache[question.qname]:
                    info, _ = self.cache[question.qname][question.qtype]
                    print('Info from cache:\n' + str(info))
                    parse_data.questions.remove(question)
                else:
                    server = ("8.8.8.8", 53)
                    self.response.sendto(parse_data.pack(), server)

            time.sleep(0.25)

            data, address = self.response.recvfrom(512)
            if data:
                parse_data = dnslib.DNSRecord.parse(data)
                print(parse_data)
                for question in parse_data.rr:
                    self.cache[question.rname] = {question.rtype: (parse_data, int(time.time()) + question.ttl)}
        except OSError:
            pass
        time.sleep(0.25)
        self.update_cache()

    def update_cache(self):
        for i in self.cache:
            current_time = int(time.time())
            for j in self.cache[i]:
                _, ttl = self.cache[i][j]
                if ttl < current_time:
                    del self.cache[i][j]


if __name__ == '__main__':
    server = DNS()
    server.run()
    try:
        with open('cache.txt', 'rb') as f:
            server.cache = pickle.load(f)
            server.update_cache()
    except Exception:
        pass
    print("Server is running...")
    try:
        while True:
            command = input(
                "\nEnter command:\n 'stop' - to stop server \n 'get' - to get resource records\n")
            if command == "get":
                address = input("Enter address\n")
                type = input("Enter record type\n")
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(dnslib.DNSRecord.question(address, type).pack(), ("localhost", 53))
                s.close()
                server.run()
            elif command == "stop":
                break
            else:
                print("Enter right command")
    except Exception as e:
        print(e)
    finally:
        server.request.close()
        server.response.close()
        with open('cache.txt', 'wb') as f:
            pickle.dump(server.cache, f)
            time.sleep(1)
        sys.exit(0)
