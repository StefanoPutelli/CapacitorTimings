import pandas as pd
import os
import math
import matplotlib.pyplot as plt
from tqdm import tqdm

OUTPUT_PATH = 'out/'
DATA_PATH = 'data/'

LOW_TH = 2.0
HIGH_TH = 2.8

INCOMING_VOLTAGE = 3

def convert_to_scientific_notation(value_str):
    # Definire i fattori di conversione per i vari prefissi
    conversion_factors = {
        'p': 1e-12,  # pico
        'n': 1e-9,   # nano
        'u': 1e-6,   # micro
        'm': 1e-3,   # milli
        'c': 1e-2,   # centi
        'd': 1e-1,   # deci
        '': 1e0,     # unità base
        'k': 1e3,    # kilo
        'M': 1e6,    # mega
        'G': 1e9,    # giga
        'T': 1e12    # tera
    }

    # Estrai la parte numerica e il prefisso
    numeric_part = ''.join([char for char in value_str if char.isdigit() or char == '.'])
    prefix = ''.join([char for char in value_str if char.isalpha()])

    # Converti la parte numerica in float
    numeric_value = float(numeric_part)

    # Ottieni il fattore di conversione corrispondente al prefisso
    factor = conversion_factors.get(prefix, 1e0)  # Predefinito a 1e0 se il prefisso non è trovato

    # Calcola il valore in notazione scientifica
    scientific_value = numeric_value * factor

    return scientific_value

def calculate_V(Tl, Th, delta_t, R, C):
    exponent = -delta_t / (R * C)
    numerator = Tl * math.exp(exponent) - Th
    denominator = math.exp(exponent) - 1
    V = numerator / denominator
    return V

def load_data(file_path):
    # Load data from a CSV file using pandas
    with open(file_path, 'r') as f:
        lines = f.readlines()
        data = []
        for line in lines:
            line = line.strip().split(',')
            data.append([float(line[0]), int(line[1]), int(line[2])])
        return data

# #remove all lines with last column as 0
# def remove_zero(data):
#     # Remove all rows where the last column value is 0
#     data = data[data.iloc[:,-1] != 0]
#     return data

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
    smp_start_time = -9999
    smp_timings = []
    # main_time = abs(data.iloc[-1, 0] - data.iloc[0, 0])
    for i in range(0, len(data)):
        if(smp_start_time == -9999):
            if(data[i][2] == 0):
                smp_start_time = data[i][0]
        else:
            if(data[i][2] == 1):
                smp_timings.append(abs(smp_start_time - data[i][0]))
                smp_start_time = -9999

    return smp_timings #main_time

def start_analysis(file):
    # Perform analysis on a given file
    data = load_data(DATA_PATH + file)
    # data = remove_zero(data)
    # divdata = divide_data(data)
    timings = calculate_time(data)
    return timings # for i in range(0, len(data)):
    #     smp_timings, main_time = calculate_time(data)
    #     print("SMP timings: " + str(smp_timings))
    #     print("Main time: " + str(main_time))
    #     smp_average = sum(smp_timings) / len(smp_timings)
    # #write_data(divdata, file, OUTPUT_PATH + file[:-4] + "/")
    # return smp_average, main_time


if __name__ == '__main__':
    #iterate in all files inside data folder
    
    accuracies = []
    resistances = []
    capacitances = []
    actual_powers = []  # New list to store actual powers

    for file in tqdm(os.listdir(DATA_PATH)):
        smp_timings = start_analysis(file)
        smp_average = sum(smp_timings) / len(smp_timings)
        print("SMP average time: " + str(smp_average))
        #get C from filename example 1mF-2.2uF.csv -> 2.2uF -> 2.2e-6
        R = convert_to_scientific_notation(file.split("-")[2][:-6])
        C = convert_to_scientific_notation(file.split("-")[1][:-1])
        V = calculate_V(LOW_TH, HIGH_TH, smp_average, R, C)
        print("V: " + str(V))
        print("R: " + str(R))
        print("C: " + str(C))
        power_predicted = pow(V, 2) / R
        actual_power = pow(INCOMING_VOLTAGE, 2) / R  # Calculate actual power
        print("P predicted: " + str(power_predicted))
        print("P actual: " + str(actual_power))
        accuracy = (actual_power - abs(power_predicted - actual_power)) / actual_power * 100
        accuracies.append(power_predicted)  # Append power_predicted instead of accuracy
        resistances.append(R)
        capacitances.append(C)
        actual_powers.append(actual_power)  # Append actual_power to the list
        print("Accuracy: " + str(accuracy) + "%")
        print(file + " done")

        # #DEBUG
        # break

    # Plotting the efficiency vs resistance
    plt.figure()
    plt.scatter(resistances, accuracies, c=capacitances)
    plt.scatter(resistances, actual_powers, color='red', label='Actual Power')  # Add a line for actual powers
    plt.xlabel('Resistance')
    plt.ylabel('Power Predicted')
    plt.title('Power Predicted vs Resistance')
    plt.colorbar(label='Capacitance')
    plt.legend()  # Add a legend for the line
    plt.ylim(bottom=0)  # Set the y-axis minimum value to 0
    plt.show()


    print("All files done")

