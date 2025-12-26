# WRK


## Installation

```
sudo apt-get install build-essential libssl-dev git -y
git clone https://github.com/wg/wrk.git wrk 
cd wrk 
sudo make
sudo cp wrk /usr/local/bin 
```

## Run

```
./run-all.sh --duration 30 --server http://localhost
```


### Alternatives
1. Meshery: wrk2 is one of the 3 default load generators that it supports out of the box. Good for non-cli users
