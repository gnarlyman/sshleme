# sshleme

## Installation

```commandline
pip install sshleme
```


## Usage

### hosts list

create a list of ips
```text
10.1.1.1
10.2.2.2

```

#### create a tasks module
```python
# tasks.py
from sshleme.lib import async_task

@async_task
async def uptime(client):
    result, error = await client.run('uptime')
    if error:
        print(client.output(error))
    else:
        print(client.output(result.stdout))

```

run the following
```commandline
sshleme -r uptime hosts -f ~/path/to/iplist
```

### csv rows

#### create a csv file
```text
ipaddress,name
10.1.1.1,hostA
10.2.2.2,hostB

```

#### create a tasks module
```python
# tasks.py
from sshleme.lib import async_task

@async_task
async def uptime(client):
    result, error = await client.run('uptime')
    if error:
        print(client.output(error, fields=['name']))
    else:
        print(client.output(result.stdout, fields=['name']))

```

```commandline
sshleme -r uptime csv -f ~/path/to/csv -c ipaddress
```

### Importing into another project

using sshleme as a module in project

```python
# project.py
import asyncio
from sshleme.lib import ConcurrentExecutor, async_task

@async_task
async def get_uptime(client):
    command = 'uptime'
    result, error = await client.run(command)
    # return result and error to the executor
    return result, error

list_of_hosts = ['127.0.0.1', '127.0.0.2', '127.0.0.3']


loop = asyncio.get_event_loop()
executor = ConcurrentExecutor(concurrent=50)
loop.run_until_complete(
    executor.run_func_on_hosts(list_of_hosts, get_uptime)
)

# returns [tuple(results, error)]
print(executor.results)

```
