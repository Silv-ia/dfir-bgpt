import math
import os
import random
import re
import sys

### Create the dict structure under /dataset
# /image0001
# - header.bin
# - tail.bin 
# /body
# - chunk1
# - chunk2
# ...
# - meta.json

# meta.json: len of body, #chunks, ch size, last chunk len