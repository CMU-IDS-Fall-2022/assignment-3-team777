import pyreadr
import pandas as pd

result = pyreadr.read_r('storms.rda')['storms']

print(result)