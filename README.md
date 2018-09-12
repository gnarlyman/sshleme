# sshleme

## Installation

- install into virtual env


## Usage

### hosts list

create a list of ips
```text
10.1.1.1
10.2.2.2

```

create a tasks module
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

create a csv file
```text
ipaddress,name
10.1.1.1,hostA
10.2.2.2,hostB

```

create a tasks module
```python
# tasks.py
from sshleme.lib import async_task

@async_task
async def uptime(client):
    result, error = await client.run('uptime', fields=['name'])
    if error:
        print(client.output(error, fields=['name']))
    else:
        print(client.output(result.stdout, fields=['name']))

```

```commandline
sshleme -r uptime csv -f ~/path/to/csv -c ipaddress
```
