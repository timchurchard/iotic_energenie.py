# iotic_energenie.py

Tim's Simple Energenie to Iotic Space share example

Using Iotic Labs marvellous IOT Infrastructure: https://iotic-labs.com/ | https://developer.iotic-labs.com/

And David Whale's wonderful pyenergenie code: https://github.com/whaleygeek/pyenergenie

And the exciting Energenie Monitor + Raspberry Pi board: https://energenie4u.co.uk/catalogue/product/MIHO004-RT


## Install

Download submodules
```shell
git submodule init
git submodule update
```

Install python deps
```shell
sudo pip3 install rdflib py-IoticAgent
```

Run the pyenergenie monitor script (I like screen)
```shell
# Apply the patch to stop the csv file growing forever
cd 3rd/pyenergenie/
git apply ../../monitor.py.patch

# Run (press ctrl+a then d to detach if the monitor starts successfully)
screen -S monitor sudo python 3rd/pyenergenie/src/monitor.py
```

- Create a file called share.ini with credentials from iotic-labs.com -

Run the share script
```shell
screen -S share python3 share.py
```

