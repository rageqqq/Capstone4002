All data is in the format Acc_x, Acc_y, Acc_z, Gyro_x, Gyro_y, Gyro_z

Import data in python using

```
data = pd.read_csv("file.csv").to_numpy(dtype=np.float32)
```
Files:<br />
"grenade.csv" - 43 samples of 60 timesteps<br />
"quit.csv" - 36 samples of 60 timesteps<br />
"reload.csv" - 36 samples of 60 timesteps<br />
"shield.csv" - 39 samples of 60 timesteps<br />
"walk.csv" - 1200 timeteps worth of non-action walking data<br />
"x_sim.csv" - 1 sample of 60 timesteps of each action spaced evenly with non-action walking data<br />
"x_test_real.csv" - 1836 derived samples of extracted feature data<br />
"y_test_real.csv" - 1836 derived samples of classification data<br />

0&4-Chester
1&5-Yikai
2&6-Alston
3&7-Bowen
8-Xinjia
