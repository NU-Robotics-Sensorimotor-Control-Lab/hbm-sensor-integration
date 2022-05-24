import os
import csv
import matplotlib.pyplot as plt
import numpy as np


class data_saver(object):
    """
    data_saver encapsulates a cache of data to be saved as well as the underlying code to save the data
    """

    def __init__(self, save_directory):
        """
        Construct a new 'data_saver' object.

        :param save_directory: The name of the directory within the /data/ folder to be saved to
        :return: returns new datasaver object
        """
        self.data_cache = []
        self.save_dir = os.getcwd() + "/data/" + save_directory
        self.save_directory = save_directory
        
        self.header = None

    def update_save_dir(self, save_directory):
        self.save_dir = os.getcwd() + "/data/" + save_directory

    def add_data(self, line):
        """Add a list to be appended

        Args:
            line list[any]: List that will be saved as it's own row
        """
        self.data_cache.append(line)

    def clear(self):
        """
        Clear the data cache

        :return: returns nothing
        """
        self.data_cache.clear()

    def add_header(self, header_list):
        """Adds a header. Care should be taken S.T. the header has the proper order

        Args:
            header_list list[any]: Ordered list of desired header
        """

        self.header = header_list

    def save_data(self, mode):
        """
        Command that creates and writes a new file based on the cache

        :param mode: tell the object the mode, which informs the directory to
        be saved in

        :return: returns nothing
        """
        path = f"{self.save_dir}/{mode}/"

        try:
            os.makedirs(path)
        except OSError:
            # print("Creation of the directory %s failed" % path)
            pass
        else:
            print("Successfully created the directory %s" % path)

        i = 0
        while os.path.exists(f"{path}Set1_trial{i}.csv"):
            i += 1

        with open(f"{path}{mode}_data{i}.csv", "w") as file:
            if self.header:
                file.write(",".join([str(x) for x in self.header]) + "\n")

            for line in self.data_cache:
                file.write(",".join([str(x) for x in line]) + "\n")

        print(f"Successfully wrote to file {path}Set1_trial{i}.csv")
        return

    def save_and_plot_data(self, mode):
        """
        Command that creates and writes a new file based on the cache

        :param mode: tell the object the mode, which informs the directory to
        be saved in

        :return: returns nothing
        """
        path = f"{self.save_dir}/{mode}/"

        try:
            os.makedirs(path)
        except OSError:
            # print("Creation of the directory %s failed" % path)
            pass
        else:
            print("Successfully created the directory %s" % path)

        i = 0
        while os.path.exists(f"{path}Set1_trial{i}.csv"):
            i += 1

        with open(f"{path}Set1_trial{i}.csv", "w") as file:
            if self.header:
                file.write(",".join([str(x) for x in self.header]) + "\n")

            for line in self.data_cache:
                file.write(",".join([str(x) for x in line]) + "\n")

        print(f"Successfully wrote to file {path}Set1_trial{i}.csv")
        Open_path = os.getcwd() + "/data/" + self.save_directory + "/" + f"{mode}/Set1_trial{i}.csv"
        self.plot(Open_path)
        return self.max_torque

    def plot(self, open_path):
        File = open(open_path)
        Reader = csv.reader(File)
        Data = list(Reader)

        x = []
        y = []

        for i in range(1, len(Data)):
            x.append(float(Data[i][0]) - float(Data[1][0]))
            y.append(float(Data[i][2])) 

        plt.plot(x,y, label='original')

        # add MAF filter
        F = 250
        i = 1
        value = []
        time = []
        while i < len(y) - F +1:
            B = y[i:i+F]
            B_ave = sum(B)/F
            value.append(B_ave)

            C = x[i:i+F]
            C_ave = sum(C)/F
            time.append(C_ave)
            i +=1

        plt.annotate('Max torque : '+ str(max(value)), xy=(x[value.index(max(value))], max(value)), xytext=(x[value.index(max(value))], max(value)+6),
                    xycoords='data',
                    arrowprops=dict(facecolor='black', shrink=0.01)
                    )

        plt.plot(time,value, label='Filterd plot')
        plt.legend()
        plt.xlabel("Time (s)")
        plt.ylabel("Torque (Nm)")
        plt.show()
        self.max_torque = max(value)


if __name__ == "__main__":
    save = data_saver("test_test", "Testing")

    save.add_data([1, 2, 3, 4])
    save.add_data([2, 5, 1, 5])
    save.add_data([3, 7, 7, 7])
    save.add_data([4, 8, 8, 8])

    save.add_header(["Index", "Round", "Par1", "Par2"])

    save.save_data("MVT_L")
