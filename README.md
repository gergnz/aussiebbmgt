# Setup
```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Run the flask app
```
flask run
```

# Pull data about DPU and Speed test results and store it in the local database
```
./dpuportstatuspopulate.py; ./speedtestpopulate.py
```

# Run a DPU Port Status
```
./rundpuportstatus.py
```

# Speed Test
```
docker run --rm -e TZ=Australia/Sydney abb-speedtest
```
Project: https://github.com/lukealford/abb-speedtest-cli
