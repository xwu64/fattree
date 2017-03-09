#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf, TCLink
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
import logging
import os
from time import sleep
import random

logging.basicConfig(filename='./fattree.log', level=logging.INFO)
logger = logging.getLogger(__name__)


class Fattree(Topo):
    logger.debug("Class Fattree")
    CoreSwitchList = []
    AggSwitchList = []
    EdgeSwitchList = []
    HostList = []

    def __init__(self, k, density):
        logger.debug("Class Fattree init")
        self.pod = k
        self.iCoreLayerSwitch = (k/2)**2-1
        self.iAggLayerSwitch = k*k/2
        self.iEdgeLayerSwitch = k*k/2
        self.density = density
        self.iHost = self.iEdgeLayerSwitch * density

        #Init Topo
        Topo.__init__(self)


    def createTopo(self):
        self.createCoreLayerSwitch(self.iCoreLayerSwitch)
        self.createAggLayerSwitch(self.iAggLayerSwitch)
        self.createEdgeLayerSwitch(self.iEdgeLayerSwitch)
        self.createHost(self.iHost)

    """
    Create Switch and Host
    """

    def _addSwitch(self, number, level, switch_list):
        for x in xrange(1, number+1):
            PREFIX = str(level)
            switch_list.append(self.addSwitch('s' + PREFIX + str(x), dpid=str(level)+str(x).zfill(15)))

    def createCoreLayerSwitch(self, NUMBER):
        logger.debug("Create Core Layer")
        self._addSwitch(NUMBER, 1, self.CoreSwitchList)

    def createAggLayerSwitch(self, NUMBER):
        logger.debug("Create Agg Layer")
        self._addSwitch(NUMBER, 2, self.AggSwitchList)

    def createEdgeLayerSwitch(self, NUMBER):
        logger.debug("Create Edge Layer")
        self._addSwitch(NUMBER, 3, self.EdgeSwitchList)

    def createHost(self, NUMBER):
        logger.debug("Create Host")
        for x in xrange(1, NUMBER+1):
            PREFIX = "h"
            self.HostList.append(self.addHost(PREFIX + str(x), ip=("10."+str((x-1)/self.pod+1)+"."+str(((x-1)%self.pod)/(self.pod/2)+1)+"."+str((x-1)%(self.pod/2)+1))))

    """
    Add Link
    """
    def createLink(self, bw_c2a=1, bw_a2e=1, bw_h2a=1):
        logger.debug("Add link Core to Agg.")
        end = self.pod/2
        for x in xrange(0, self.iAggLayerSwitch, end):
            for i in xrange(0, end):
                for j in xrange(0, end):
                    if i*end+j == self.pod-1:
                        self.addPort(self.AggSwitchList[x+i], self.AggSwitchList[x+i])
                        continue
                    self.addLink(
                        self.CoreSwitchList[i*end+j],
                        self.AggSwitchList[x+i],
                        bw=bw_c2a)

        logger.debug("Add link Agg to Edge.")
        for x in xrange(0, self.iAggLayerSwitch, end):
            for i in xrange(0, end):
                for j in xrange(0, end):
                    self.addLink(
                        self.AggSwitchList[x+i], self.EdgeSwitchList[x+j],
                        bw=bw_a2e)

        logger.debug("Add link Edge to Host.")
        for x in xrange(0, self.iEdgeLayerSwitch):
            for i in xrange(0, self.density):
                self.addLink(
                    self.EdgeSwitchList[x],
                    self.HostList[self.density * x + i],
                    bw=bw_h2a)

    def set_ovs_protocol_13(self,):
        self._set_ovs_protocol_13(self.CoreSwitchList)
        self._set_ovs_protocol_13(self.AggSwitchList)
        self._set_ovs_protocol_13(self.EdgeSwitchList)

    def _set_ovs_protocol_13(self, sw_list):
            for sw in sw_list:
                cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % sw
                os.system(cmd)


def iperfTest(net, topo):
    logger.debug("Start iperfTEST")
    h1000, h1015, h1016 = net.get(
        topo.HostList[0], topo.HostList[14], topo.HostList[15])

    #iperf Server
    h1000.popen(
        'iperf -s -u -i 1 > iperf_server_differentPod_result', shell=True)

    #iperf Server
    h1015.popen(
        'iperf -s -u -i 1 > iperf_server_samePod_result', shell=True)

    #iperf Client
    h1016.cmdPrint('iperf -c ' + h1000.IP() + ' -u -t 10 -i 1 -b 100m')
    h1016.cmdPrint('iperf -c ' + h1015.IP() + ' -u -t 10 -i 1 -b 100m')


def pingTest(net):
    logger.debug("Start Test all network")
    net.pingAll()


def createTopo(pod, density, ip="192.168.33.101", port=6623, bw_c2a=1, bw_a2e=1, bw_h2a=1):
    logging.debug("LV1 Create Fattree")
    topo = Fattree(pod, density)
    topo.createTopo()

    topo.createLink(bw_c2a=bw_c2a, bw_a2e=bw_a2e, bw_h2a=bw_h2a)
    net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True,autoStaticArp=True)

    logging.debug("LV1 Start Mininet")
    CONTROLLER_IP = ip
    CONTROLLER_PORT = port
    net.addController(
        'controller', controller=RemoteController,
        ip=CONTROLLER_IP, port=CONTROLLER_PORT)

    s22 = net.getNodeByName('s22')
    s24 = net.getNodeByName('s24')
    s26 = net.getNodeByName('s26')
    s28 = net.getNodeByName('s28')

    Intf("ens1f1", s22, port = 2)
    Intf("ens1f0", s24, port = 2)
    Intf("ens2f1", s26, port = 2)
    Intf("ens2f0", s28, port = 2)
    net.start()

    '''
        Set OVS's protocol as OF13
    '''
    topo.set_ovs_protocol_13()

    logger.debug("LV1 dumpNode")

    #dumpNodeConnections(net.hosts)
    pingTest(net)
    #iperfTest(net, topo)

    """
    h7 = net.getNodeByName("h7")
    h1 = net.getNodeByName("h1")
    h3 = net.getNodeByName("h3")
    h5 = net.getNodeByName("h5")
    h9 = net.getNodeByName("h9")
    h11 = net.getNodeByName("h11")
    h13 = net.getNodeByName("h13")
    h15 = net.getNodeByName("h15")
    h7.cmd("iperf -s > log7&")
    h11.cmd("iperf -s > log11&")
    h13.cmd("iperf -s > log13&")
    h15.cmd("iperf -s > log15&")
    h1.cmd("iperf -c 10.2.2.1 -t 100 &")
    h3.cmd("iperf -c 10.3.2.1 -t 100 &")
    h5.cmd("iperf -c 10.4.1.1 -t 100 &")
    h9.cmd("iperf -c 10.4.2.1 -t 100 ")
    print "go"
    sleep(10)
    """
    startServer(net,topo, 16)
    sleep(10)
    print 'start'
    startClient(net,topo,6)
    sleep(100)

    net.stop()

def startServer(net,topo, serverNum):
    for i, each in enumerate(topo.HostList) :
        host = net.getNodeByName(each)
        command = 'iperf -s -i 1 > /home/security/fattree/log/mixLog/hedera/10/log{} &'.format(i+1)
        host.cmd(command)

def startClient(net, topo, clientNum):
    fh = open("flow", "r")

    for line in fh:
        client, server = line.split(' ')
        client = int(client)
        server = int(server)
        print client+1, server+1
        client = topo.HostList[client]
        client = net.getNodeByName(client)
        server = topo.HostList[server]
        serverIP = net.getNodeByName(server).IP()
        command = 'iperf -c {} -t 100 &'.format(serverIP)
        client.cmd(command)
        sleep(0.1)

if __name__ == '__main__':
    setLogLevel('info')
    if os.getuid() != 0:
        logger.debug("You are NOT root")
    elif os.getuid() == 0:
        createTopo(4, 2)
