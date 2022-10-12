import pyreadr
import pandas as pd

result = pyreadr.read_r('storms.rda')
df = pd.DataFrame(result, columns=result.keys())

print(result)