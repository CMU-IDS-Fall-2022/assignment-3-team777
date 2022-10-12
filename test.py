import pyreadr
import pandas as pd

result = pyreadr.read_r('storms.rda')
# df = pd.DataFrame.from_dict(result, orient='index')

print(result)