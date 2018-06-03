# Gnome
The code for the paper "Gnome: A Practical Approach to NLOS Mitigation for GPS Positioning in Smartphones".

## Requirement
- Python 2.7.x
- OS X or Ubuntu 
- Android 7+

## Code Structure 
- `cloud/`: Cloud part of Gnome. It downloads data from Google Street View in the specified area, and compute GPS path inflation. 
- `mobile/`: Mobile part of Gnome. It takes input from Android GPS metadata and the path inflation model from cloud, and computes the adjusted location. 

## Run Cloud
Go to `cloud/` dir and run `python run.py lat_bottom lon_left lat_top lon_right `. The last four parameters specifies the region where Gnome generates the path inflation model. The output is written in `inflation.pkl`

Sample command: `python run.py 34.045175 -118.260346 34.049438 -118.256356`

## Run Mobile
The mobile part of Gnome is running as a python library. Your code should include the `Gnome` class in `mobile/main.py` and `GPSmeta` in `mobile.meta.py`. Here is the example:

```
from mobile.main import Gnome
from mobile.meta import GPSmeta

gnome = Gnome(path_to_inflation_model)

while reading_gps:
	gps_meta = GPSmeta(your_gps_meta_data)
	position_adjusted = Gnome.update(gps_meta)
```

- `Gnome` is the main object to compute the new location. Use its `update` function to get new location reading
- `GPSmeta` contains raw GPS measurement like C/N0, Pseudorange rate, clock, etc. Please read `mobile/meta.py` to check how to initiate GPSmeta. You can get the raw GPS measurement data from Android APIs in your app. For API details please read the source code of [Android GNSS Logger](https://github.com/google/gps-measurement-tools/tree/master/GNSSLogger). `GPSmeta` also enables you to initiate the meta object with the output file of Android GNSS logger. 

