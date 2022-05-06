# Identifying Possible Winners in Ranked Choice Voting Elections with Outstanding Ballots

# Data

Testing is performed using the dataset below:

[New York City Democratic Mayor Citywide](https://www.vote.nyc/page/election-results-summary-2021)

The `data` folder which should be placed in the root directory can be found [here](https://drive.google.com/file/d/1LsR0-M8Ho-2oqpFcY-UdXkT1p1CpWc-q/view?usp=sharing) 


# Installing Dependecies

The Python dependecies can be installed through the `requirements.txt` file provided. Run:

    pip install -r requirements.txt

Additionally, [Graphviz](https://graphviz.org/download/) should nanually be installed and added to the system PATH.

# What to run

## `src/autorun.py`
This script will run each election in the `src/elections.csv` file. The output contains the data we present in Table 1 along with the minimum bound ballots for each possible winnner.


## `src/gen_graphs.py` - Generate elimination order DAGs

Be default, we have this set to produce the compressed DAG for the New York Democratic Member of the City
Council 16th Council District election.

Set the election file path variable `file` as desired. Set the number of candidates in the election `num_cands` and number of missing ballots `missing` as desired. Choose if you want to use DAG compression in `compress_graph`. If you want to remove certain candidates from the election, add their candidate id's to the `remove` list. Running the script will produce the graph in `output.eps` and also opens a window to see the graph. Note: You almost always have to play around with the node sizing and font parameters to achieve a good fit in the window. 


## `plots/plot_data.py`

This script will generate the plot in Figure 2.

# Other files

## `src/make_tree.py`

This contains the core of our algorithms. Algorithm 1 from the paper is implemented in `_verify()`. Algorithm 2 is implemented in `_make_tree()`.
