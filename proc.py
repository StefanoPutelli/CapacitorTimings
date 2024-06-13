import pandas as pd
import os

#load csv file

OUTPUT_PATH = 'out/'
DATA_PATH = 'data/'

def load_data(file_path):
    # Load data from a CSV file using pandas
    data = pd.read_csv(file_path)
    return data

#remove all lines with last column as 0
def remove_zero(data):
    # Remove all rows where the last column value is 0
    data = data[data.iloc[:,-1] != 0]
    return data

#write data to csv file
def write_data(data, file_path, output_path):
    # Write data to a CSV file
    # If the output path doesn't exist, create it
    if(not os.path.exists(output_path)):
        os.makedirs(output_path)
    for d in range(0, len(data)):
        # Set header as timestamp, SMP, MAIN
        data[d].columns = ['timestamp', 'SMP', 'MAIN']
        data[d].to_csv(output_path + str(d) + "_" + file_path, index=False)

#divide data when fisrt comunn of next line delta is greater than 0.1
def divide_data(data):
    # Divide the data into separate chunks based on a condition
    div_data = []
    last_index = 0
    for i in range(1, len(data)):
        if abs(data.iloc[i, 0] - data.iloc[i-1, 0]) > 0.01:
            div_data.append(data.iloc[last_index:i-1, :])
            last_index = i
    div_data.append(data.iloc[last_index:, :])
    return div_data

def calculate_time(data):
    # Calculate SMP timings and main time from the data
    smp_start_time = 0
    smp_timings = []
    main_time = abs(data.iloc[-1, 0] - data.iloc[0, 0])
    for i in range(0, len(data)):
        if(smp_start_time == 0):
            if(data.iloc[i, 1] == 1):
                smp_start_time = data.iloc[i, 0]
        else:
            if(data.iloc[i, 1] == 0):
                smp_timings.append(abs(smp_start_time - data.iloc[i, 0]))
                smp_start_time = 0

    return smp_timings, main_time

def start_analysis(file):
    # Perform analysis on a given file
    data = load_data(DATA_PATH + file)
    data = remove_zero(data)
    divdata = divide_data(data)
    for i in range(0, len(divdata)):
        smp_timings, main_time = calculate_time(divdata[i])
        smp_average = sum(smp_timings) / len(smp_timings)
    write_data(divdata, file, OUTPUT_PATH + file[:-4] + "/")
    return smp_average, main_time

if __name__ == '__main__':
    #iterate in all files inside data folder
    for file in os.listdir(DATA_PATH):
        smp_average, main_time = start_analysis(file)
        print("SMP average time: " + str(smp_average))
        print("Main time: " + str(main_time))
        print(file + " done")

    print("All files done")

