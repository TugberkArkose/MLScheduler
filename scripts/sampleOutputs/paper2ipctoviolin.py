import seaborn as sns
import sys

def main():

    if len(sys.argv) < 3:
        print "Use Paper2PerQuantumIPCExtractor.py <sim output in file name> <graph out name>"
        sys.exit(0)

    # quantum = index + 1
    ipc_per_quantum = []
    filename = sys.argv[1]
    graphname = sys.argv[2]
    with open(filename) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    for line in content:
        if line.startswith("System IPC"):
            ipc = float(line[13:])
            ipc_per_quantum.append(ipc)
    sns.set_style("whitegrid")
    ax = sns.violinplot(x=ipc_per_quantum)
    fig = ax.get_figure()
    fig.savefig(graphname)

if __name__ == "__main__":
    main()
