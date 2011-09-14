#!/usr/bin/python

import roslib;
roslib.load_manifest('executive_usarsim')

from usarsim_gui import Ui_usar_main_gui as UsarsimUi
#from PyQt4 import QtGui,  QtCore
from PyQt4 import *
import rospy
import sys
import socket

from std_msgs.msg import String

'''
UsarsimManager, interface to USARSIM simulator
'''
class UsarsimManager(QtGui.QWidget, UsarsimUi):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        UsarsimUi.__init__(self)
        
        self.ui = UsarsimUi()
        self.ui.setupUi(self)
        
        ''' Local variables, publishers and subscribers'''
        self.initialize()
        
        '''
        Connect Buttons
        '''
        self.connect(self.ui.btn_connect,  QtCore.SIGNAL("clicked()"), self.connect_to_sim)
        self.connect(self.ui.btn_disconnect,  QtCore.SIGNAL("clicked()"), self.disconnect_sim)
        self.connect(self.ui.btn_spawn,  QtCore.SIGNAL("clicked()"), self.spawn_robot)
        self.connect(self.ui.btn_send_command,  QtCore.SIGNAL("clicked()"), self.send_custom_command)
    
    def initialize(self):
        self.pub_status = rospy.Publisher('/executive_usarsim/status', String)
        self.sub_status = rospy.Subscriber('/executive_usarsim/status', String, self.status_callback)
        self.ui.btn_disconnect.setEnabled(False)
        self.ui.btn_spawn.setEnabled(False)
        self.ui.btn_send_command.setEnabled(False)
    
    def connect_to_sim(self):
        rospy.loginfo("button clicked")
        
        host = self.ui.line_edit_hostip.text()
        port = int( self.ui.line_edit_port.text() )
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            sys.stderr.write("[ERROR] %s\n" % msg)
            sys.exit(1)

        try:
            self.sock.connect((host, port))
        except socket.error as msg: 
            sys.stderr.write("[ERROR] %s\n" % msg)
            sys.exit(2)
        
        self.pub_status.publish('Connected to Simulator, sending spawn message...')
        self.ui.btn_connect.setEnabled(False)
        self.ui.btn_disconnect.setEnabled(True)
        self.ui.btn_spawn.setEnabled(True)
        self.ui.btn_send_command.setEnabled(True)
    
    def disconnect_sim(self):
        self.sock.close()
        self.ui.btn_connect.setEnabled(True)
        self.ui.btn_disconnect.setEnabled(False)
        self.ui.btn_spawn.setEnabled(False)
        self.ui.btn_send_command.setEnabled(False)
    
    ''' Spawn a robot in the simulation '''
    def spawn_robot(self):
        robot_name = str(self.ui.le_robot_name.text())
        x = str(self.ui.loc_x.text())
        y = str(self.ui.loc_y.text())
        z = str(self.ui.loc_z.text())
        spawn_str = 'INIT {ClassName USARBot.'+robot_name+'} {Location '+x+','+y+','+z+'}'
        print spawn_str
        self.sock.send(spawn_str+'\r\n')
        self.pub_status.publish('Spawned the Robot '+robot_name+ ' at '+x+','+y+','+z)
    
    def send_custom_command(self):
        command = str(self.ui.line_edit_command.text())
        self.sock.send(command+'\r\n')
        data = self.sock.recv(128)
        self.pub_status.publish('Command Response:'+str(data))
    
    ''' Log STATUS messages as they arrive'''
    def status_callback(self, status):
        msg = '[STATUS] '+str(status.data)
        self.ui.text_status.append(msg)


def run():
    app = QtGui.QApplication(sys.argv)
    window = UsarsimManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    rospy.init_node('executive_usarsim',  log_level=rospy.DEBUG)
    run()
