import sys
import os
import json
import pyfits

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = []
parset = None
for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if name == 'Parset' and value is not None:
        parset = value
        continue
    if name == 'Parset' and value is None:
        continue
    if name == 'Noise-Image' and value is None:
        continue

    if isinstance(value, list):
        arg = "{0}{1} {2}".format(cab['prefix'], name, ",".join(value))
    else:
        arg = '{0}{1} {2}'.format(cab['prefix'], name, value)

    args.append(arg)


removed = False
for item1 in args:
    if 'Noise-Image' in item1:
        noise_image = item1.split('{0}Noise-Image '.format(cab['prefix']))[-1]
        args.remove('{0}Noise-Image {1}'.format(cab['prefix'], noise_image))
        noise_hdu = pyfits.open(noise_image)
        noise_data = noise_hdu[0].data
        noise_std = noise_data.std()
        noise_hdu.close()
        for item2 in args:
            if 'Noise-Sigma' in item2:
                noise_sigma = item2.split('{0}Noise-Sigma '.format(cab['prefix']))[-1]
                args.remove('{0}Noise-Sigma {1}'.format(cab['prefix'], noise_sigma))
                removed = True
                threshold = float(noise_sigma)*noise_std
                for item3 in args:
                    if '{0}Deconv-FluxThreshold'.format(cab['prefix']) in item3:
                        args.remove(item3)
                args.append('{0}Deconv-FluxThreshold {1}'.format(cab['prefix'], threshold))
if not removed:
    args.remove('{0}Noise-Sigma 3.0'.format(cab['prefix']))

if parset is not None:
    args.insert(0, parset)
utils.xrun(cab['binary'], args)
