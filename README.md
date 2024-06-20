# solana_rpc

### Description

Here's the implementation of suggested task.
All code is written on python. Base libraries I used is aiohttp and asyncio to be able to execute event handling and
processing concurrently. All code is working through asyncio event loop, making event handling process become
non-blocking.

For simplicity of demonstration all events (INVOKE, NOTHING, ERROR) are being consumed through websocket connection,
which can be easily replaced with Kafka brokers, HTTP endpoints or RPC calls. To simulate event queue I wrote simple
event [producer](websocker_server.py), which sends one of listed events once every random time interval.

The code resembles high level of abstraction, which makes it easy to write custom event handlers or be able to accept
different types of responses.

I have chosen [getSupply](https://solana.com/docs/rpc/http/getsupply) RPC method to test my application. After INVOKE
event appears, the response is being serialized to dataclass model and stored in local
thread-safe [priority queue](app/priority_queue.py) with timestamp as sorting key, which allows to retrieve the latest
processed event in O(1). Note, that priority queue has limited size, which could be set through environment variables of
application. After the limit is achieved, queue drops all the results except the last one. This is done in order to
avoid overflowing CPU memory of the process.

To save all processed requests, I suggest using MongoDB as most convenient way to store JSON's. Although it might be
replaced with any other relational or nosql DB.

In order to track latencies and performance main application exposes */metric* endpoint for sending Prometheus logs.
Which then can be used as metric to build monitoring through Grafana. To be honest, I didn't find any convenience of
tracking standard deviation of latencies, because it's never shows the performance of application. Instead of it, I
provide Grafana monitoring for 50% and 95% quantile of latency.

On my local computer, I gained this results:
![latency](docs/latency.png)

### How to run

First of you should set all environment variables before running application, in particular:

```
MONGO_URI=mongodb://root:root@mongodb:27017
MONGO_DB=test
MAX_QUEUE_SIZE=10000
WEBSOCKET_URI=ws://websocket_server:9000
```

and store them into .env file

Next, to run the application you simply should run Docker containers via:

```bash
docker compose up --build -d
```

Main application will export metrics on
```localhost:8080/metrics```

Prometheus
```localhost:9090```

Grafana will run on
```localhost:3030/metrics```

MongoDB on
```mongodb://root:root@localhost:27017```

### MongoDB setup

```
use test;
db.createCollection("getSupply");
```

### Grafana setup

Add new Prometheus source:
```http://prometheus:9090```

Build new dashboard and create to quires

1. 95% quantile latency:
    ```
    histogram_quantile(
        0.95,
        sum(
          rate(
            getSupply_latency_ms_bucket[1m]
          )
        ) by (le)
    )
    ```
2. 50% quantile latency:
    ```
    histogram_quantile(
        0.5,
        sum(
          rate(
            getSupply_latency_ms_bucket[1m]
          )
        ) by (le)
    )
    ```
   

Be happy!
