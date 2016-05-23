#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange, choice
from datetime import datetime, timedelta, time
import xmlrpclib

class MedicalDevice(object):
    patient_ids = []
    hospital_id = None
    device_id = None
    use_types = None
    dtime = None
    time_zone = None
    xmlrpc_server = None
    connection = None
    working_hours = None

    def __init__(self, hospital_id, device_id, use_types=None,
                 xmlrpc_server="", time_zone=8.0, start_time=datetime.utcnow(), 
                 working_hours=(8,17)):
        self.hospital_id = hospital_id
        self.device_id = device_id
        self.use_types = use_types
        self.dtime = start_time
        self.time_zone = time_zone
        self.xmlrpc_server = xmlrpc_server
        # process working hours int UTC (assumes integer time_zones)
        self.working_hours = (  int(( working_hours[0]+24-time_zone )%24), int(( working_hours[1]+24-time_zone )%24) )
        # set up xmlrpc connection
        if self.xmlrpc_server is not None:
            self.connection = xmlrpclib.ServerProxy(self.xmlrpc_server)
        # populate patients
        self.genPatients()
        # prime the first time step
        self.nextTime()

    def genPatients(self):
        """generate 20 random patient ids"""
        ids = []
        for i in range(20):
            ids.append(randrange(100,2000))
        self.patient_ids = list(set(ids))

    def pickPatient(self):
        return choice(self.patient_ids)

    def pickUseType(self):
        """pick random use type"""
        if self.use_types is None:
            return None
        return choice(self.use_types)

    def pickTimeStep(self):
        """pick semi-random step forward
           (treat length about 30,45,...,120, mins long)"""
        mins = choice([30,45,60,75,90,120]) + choice(range(-4,4))
        secs = choice(range(0,60))
        return timedelta(minutes=mins, seconds=secs)

    def nextTime(self):
        dt = self.pickTimeStep()
        self.dtime += dt
        begOfDay = time( self.working_hours[0] )
        endOfDay = time( self.working_hours[1] )
        t = self.dtime.time()
        if t > endOfDay:
            print "End of day: Going to beginning of next day."
            nextday = self.dtime + timedelta(hours=24)
            self.dtime = nextday.replace(hour=begOfDay.hour,
                                         minute=begOfDay.minute + choice(range(0,5)) )
        elif t < begOfDay:
            print "Going to begining of working day"
            self.dtime = self.dtime.replace(hour=begOfDay.hour,
                                            minute=begOfDay.minute + choice(range(0,5)) ) 
        return self.dtime

    def runStep(self):
        self.nextUsage()

    def runRealTimeStep(self):
        self.realTimeUsage()

    def nextUsage(self):
        patient = self.pickPatient()
        use_type = self.pickUseType()

        data = {'patient_id':patient,
                'site':self.hospital_id,
                'device':self.device_id,
                'time_used':self.dtime}
        if use_type is not None:
            data['use_type'] = use_type
        # push usage data to rpc server if connection is set up
        self.pushData(data)
        # iterate
        self.nextTime()
        return data

    def pushData(self, data):
        print "   pushing data"
        if self.connection is not None:
            try:
                self.connection.rpc_insert(data)
            except:
                print "Failed to send data"

    def sendHeartBeat(self):
        print "   heartbeat"
        if self.connection is not None:
            try:
                self.connection.rpc_heartbeat(self.device_id, self.hospital_id)
            except:
                print "Failed to send heart beat"
        
    def realTimeUsage(self):
        """ run simulation in realtime,
        pushing event data as the time hits simulated nextTime,
        then generate next time use."""
        utcnow = datetime.utcnow()
        next = self.dtime
        if utcnow > next:
            # execute usage if time is passed
            print "Executing device usage "+str(next)
            self.nextUsage()
            # Note: this conveniently also sets the next event time
        else:
            # send a heartbeat
            self.sendHeartBeat()
