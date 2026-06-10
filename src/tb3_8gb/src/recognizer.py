#!/usr/bin/env python

"""
recognizer.py is a wrapper for pocketsphinx.
  parameters:
    ~lm - filename of language model
    ~dict - filename of dictionary
    ~fsg - filename of finite state grammar
    ~mic_name - set the pulsesrc device name for the microphone input.
  publications:
    ~output (std_msgs/String) - text output
  services:
    ~start (std_srvs/Empty) - start speech recognition
    ~stop (std_srvs/Empty) - stop speech recognition
"""

import roslib; roslib.load_manifest('pocketsphinx')
import rospy

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

from std_msgs.msg import String
from std_srvs.srv import *
import os
import commands

class recognizer(object):
    def __init__(self):
        rospy.init_node("recognizer")

        self._device_name_param = "~mic_name"
        self._lm_param = "~lm"
        self._dic_param = "~dict"
        self._fsg_param = "~fsg"

        if rospy.has_param(self._device_name_param):
            self.device_name = rospy.get_param(self._device_name_param)
            self.device_index = self.pulse_index_from_name(self.device_name)
            self.launch_config = "pulsesrc device=" + str(self.device_index)
        elif rospy.has_param('~source'):
            self.launch_config = rospy.get_param('~source')
        else:
            self.launch_config = 'gconfaudiosrc'

        self.launch_config += " ! audioconvert ! audioresample " \
                            + '! vader name=vad auto-threshold=false threshold=0.05 ' \
                            + '! pocketsphinx name=asr ! fakesink'

        self.started = False
        rospy.on_shutdown(self.shutdown)
        self.pub = rospy.Publisher('~output', String, queue_size=10)
        rospy.Service("~start", Empty, self.start)
        rospy.Service("~stop", Empty, self.stop)

        if (rospy.has_param(self._lm_param) or rospy.has_param(self._fsg_param)) and rospy.has_param(self._dic_param):
            self.start_recognizer()
        else:
            rospy.logwarn("lm/fsg and dic parameters need to be set to start recognizer.")

    def start_recognizer(self):
        rospy.loginfo("Starting recognizer... ")
        self.pipeline = gst.parse_launch(self.launch_config)
        self.asr = self.pipeline.get_by_name('asr')
        self.asr.connect('partial_result', self.asr_partial_result)
        self.asr.connect('result', self.asr_result)
        self.asr.set_property('dsratio', 1)

        if rospy.has_param(self._lm_param):
            self.asr.set_property('lm', rospy.get_param(self._lm_param))
        elif rospy.has_param(self._fsg_param):
            self.asr.set_property('fsg', rospy.get_param(self._fsg_param))

        self.asr.set_property('dict', rospy.get_param(self._dic_param))

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::application', self.application_message)
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.started = True

    def pulse_index_from_name(self, name):
        output = commands.getstatusoutput("pacmd list-sources | grep -B 1 'name: <" + name + ">' | grep -o -P '(?<=index: )[0-9]*'")
        if len(output) == 2: return output[1]
        else: raise Exception("Error. pulse index doesn't exist for name: " + name)

    def stop_recognizer(self):
        if self.started:
            self.pipeline.set_state(gst.STATE_NULL)
            self.started = False

    def shutdown(self):
        self.loop.quit()

    def start(self, req):
        self.start_recognizer()
        return EmptyResponse()

    def stop(self, req):
        self.stop_recognizer()
        return EmptyResponse()

    def asr_partial_result(self, asr, text, uttid):
        struct = gst.Structure('partial_result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def asr_result(self, asr, text, uttid):
        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        msgtype = msg.structure.get_name()
        if msgtype == 'partial_result':
            rospy.logdebug("Partial: " + msg.structure['hyp'])
        if msgtype == 'result':
            msg_out = String()
            msg_out.data = str(msg.structure['hyp'].lower())
            if msg_out.data.strip():
                rospy.loginfo("Published result: " + msg_out.data)
                self.pub.publish(msg_out)

if __name__ == "__main__":
    rec = recognizer()
    rec.loop = gobject.MainLoop()
    rec.loop.run()
