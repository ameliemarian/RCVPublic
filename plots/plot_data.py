from matplotlib import pyplot as plt
import csv

with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    data = list(reader)

candidates = []
dp_time = []
bf_time = []

for election in data:
    candidates.append(int(election["candidates"]))
    dp_time.append(float(election["dp_time"]))
    bf_time.append(float(election["bf_time"]))

fig1, ax1 = plt.subplots()
ax1.set_yscale("log")
#ax1.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

#ax1.set_yticks(np.arange(0,7200,100))

ax1.set_xlabel("Number of Candidates")
ax1.set_ylabel("Runtime (S)")
ax1.scatter(candidates,dp_time, label = "calculatePossibleOutcomes",marker='x',color="blue")
ax1.scatter(candidates,bf_time,label="Brute Force",marker='.',color="red")
ax1.legend()
ax1.tick_params(axis=u'both', which=u'both',length=3)
ax1.set_title("calculatePossibleOutcomes versus Brute Force Runtimes")

plt.savefig('data_plot.eps', format='eps')
plt.savefig('data_plot.png', format='png')
plt.show()