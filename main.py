import pandas as pd
import visualize as vz
import workwithdata as wd


if __name__ == '__main__':
    teacher = pd.read_csv("data\Building0teacher.csv", ';', nrows = 671)
    teacher = wd.correctdata(teacher)

    vz.visualize(teacher)
