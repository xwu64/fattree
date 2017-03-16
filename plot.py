from numpy import arange
import matplotlib.pyplot as plt
import numpy

def getData(filename):
    """TODO: Docstring for plot.
    :returns: TODO

    """

    f = open(filename, 'r')

    result = []
    for line in f:
        segments = line.split(' ')
        if segments[-1] == "Kbits/sec\n":
            result.append(float(segments[-2]))
        elif segments[-1] == "bits/sec\n" :
            result.append(float(segments[-2])/1000000)
        elif segments[-1] == "Mbits/sec\n":
            result.append(1000)
    return result


def getColumn(datas):
    """TODO: Docstring for getColumn.
    :returns: TODO

    """
    minLen = 1000

    for each in datas:
        minLen = min(minLen, len(each))

    for i in range(16):
        datas[i] = datas[i][:minLen]

    xData = []

    for _ in range(minLen):
        xData.append(0)

    for i in range(minLen):
        for j in range(16):
            xData[i] += datas[j][i]

    return xData[10:]

ecmpMininet = []
hederaMininet = []
ecmpMix = []
hederaMix = []

def p(version):
    """TODO: Docstring for main.
    :returns: TODO

    """
    plt.figure(figsize=(10,6))
    plt.ylabel("Network Bisection Bandwidth (Kbps)",fontsize=20)
    plt.xlabel("Seconds", fontsize=20)
    line = []
    legend = []

    datas = []
    prefix = './log/oneMininetLog/ecmp/{}/log'.format(version)
    for i in range(1,17):
        filename = prefix+str(i)
        data = getData(filename)
        datas.append(data)

        row = arange(10,60, 1)
    xData = getColumn(datas)

    xData = xData[:min(len(xData), len(row))]
    ecmpMininet.append(sum(xData)/len(xData))
    row = row[:min(len(xData), len(row))]

    seg, =plt.plot(row, xData, 'k', c='r')
    line.append(seg)
    legend.append("ECMP-oneMininet")

    datas = []
    prefix = './log/oneMininetLog/hedera/{}/log'.format(version)
    for i in range(1,17):
        filename = prefix+str(i)
        data = getData(filename)
        datas.append(data)

        row = arange(10,60, 1)
    xData = getColumn(datas)
    xData = xData[:min(len(xData), len(row))]
    hederaMininet.append(sum(xData)/len(xData))
    row = row[:min(len(xData), len(row))]

    seg, =plt.plot(row, xData, '--', c='b')
    line.append(seg)
    legend.append("Hedera-oneMininet")

    datas = []
    prefix = './log/mixLog/hedera/{}/log'.format(version)
    for i in range(1,17):
        filename = prefix+str(i)
        data = getData(filename)
        datas.append(data)

    row = arange(10,60, 1)
    xData = getColumn(datas)
    xData = xData[:min(len(xData), len(row))]
    hederaMix.append(sum(xData)/len(xData))
    row = row[:min(len(xData), len(row))]

    seg, =plt.plot(row, xData, '-.', c='g')
    line.append(seg)
    legend.append("Hedera-mix")

    datas = []
    prefix = './log/mixLog/ecmp/{}/log'.format(version)
    for i in range(1,17):
        filename = prefix+str(i)
        data = getData(filename)

        datas.append(data)

    row = arange(10,60, 1)
    xData = getColumn(datas)
    xData = xData[:min(len(xData), len(row))]
    ecmpMix.append(sum(xData)/len(xData))
    row = row[:min(len(xData), len(row))]

    seg, =plt.plot(row, xData, ':', c='k')
    line.append(seg)
    legend.append("ecmp-mix")

    plt.axis([10,50,0,16000])
    plt.legend(line,legend, loc=3, mode='expand', bbox_to_anchor=(0.,1.02,1.,.102), ncol=4, borderaxespad=0.)
    plt.grid()
    #plt.show()


def getStdDev(datas):
    result = []
    avg = sum(datas)/len(datas)
    variance = 0
    for data in datas:
        variance+=(avg-data)**2
    return (variance/len(datas))**0.5

def plotAllversion():
    """TODO: Docstring for plotAllversion.

    :returns: TODO

    """
    plt.figure(figsize=(10,6))
    plt.ylabel("Network Bisection Bandwidth (Kbps)",fontsize=20)
    routing = ('hedera', 'ecmp')
    scenarios = ('one Mininet', 'mix mode')
    result = ((sum(hederaMininet)/len(hederaMininet), (sum(hederaMix)/len(hederaMix))), ((sum(ecmpMininet)/len(ecmpMininet)), (sum(ecmpMix)/len(ecmpMix))))
    hederaStd = []
    ecmpStd = []
    hederaStd.append(getStdDev(hederaMininet))
    hederaStd.append(getStdDev(hederaMix))
    ecmpStd.append(getStdDev(ecmpMininet))
    ecmpStd.append(getStdDev(ecmpMix))

    index = numpy.arange(len(result[0]))

    bar_width = 0.3
    plt.grid(axis='y')
    plt.bar(index, result[0], bar_width, color='r', label=routing[0], alpha=1, yerr=hederaStd)
    plt.bar(index+bar_width, result[1], bar_width, color='b', label=routing[1], alpha=1, yerr=ecmpStd)
    plt.legend()
    plt.xticks(index + bar_width, scenarios)
    plt.savefig("./all.png")

    pass

if __name__ == "__main__":
    for i in range(1, 11): p(i)
    plt.show()
    plotAllversion()
    p(9)
    plt.savefig("./one.png")
