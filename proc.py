#load csv file
import pandas as pd
import os

OUTPUT_PATH = 'out/'
DATA_PATH = 'data/'

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

#remove all lines with last column as 0
def remove_zero(data):
    data = data[data.iloc[:,-1] != 0]
    return data

#write data to csv file
def write_data(data, file_path, output_path):
    if(not os.path.exists(output_path)):
        os.makedirs(output_path)
    for d in range(0, len(data)):
        data[d].to_csv(output_path + str(d) + "_" + file_path, index=False, header=False)

#divide data when fisrt comunn of next line delta is greater than 0.1
def divide_data(data):
    div_data = []
    last_index = 0
    for i in range(1, len(data)):
        if abs(data.iloc[i, 0] - data.iloc[i-1, 0]) > 0.01:
            div_data.append(data.iloc[last_index:i-1, :])
            last_index = i
    div_data.append(data.iloc[last_index:, :])
    return div_data


def start(file):
    data = load_data(DATA_PATH + file)
    data = remove_zero(data)
    divdata = divide_data(data)
    write_data(divdata, file, OUTPUT_PATH + file[:-4] + "/")

if __name__ == '__main__':
    #iterate in all files inside data folder
    for file in os.listdir(DATA_PATH):
        start(file)
        print(file + " done")
    print("All files done")

