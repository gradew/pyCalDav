#!/usr/bin/env python

from datetime import datetime, timedelta
import caldav
from caldav.elements import dav, cdav
import re, pytz

class pyCalDav:
    """Fuck"""
    re_caldav_line=re.compile("^([^:]+):(.+)$")
    re_caldav_opts=re.compile("^([^;]+);(.+)$")
    re_date=re.compile("^([0-9]{4})([0-9]{2})([0-9]{2})$")
    re_datetime=re.compile("^([0-9]{4})([0-9]{2})([0-9]{2})(T([0-9]{2})([0-9]{2})([0-9]{2})(Z)?)?$")
    re_tzid=re.compile("^TZID=(.+)$")
    client=None
    pricipal=None
    calendars=None
    calendar=None

    def __init__(self):
        pass

    def connect(self, url):
        self.client = caldav.DAVClient(url)
        self.principal = self.client.principal()
        self.calendars = self.principal.calendars()
        if len(self.calendars)<1:
            return 1
        return 0

    def setCalendar(self, cName):
        bestguess=0
        bestguess_name=''
        cName=cName.lower()

        for i in range(0, len(self.calendars)-1):
            name=self.calendars[i].get_properties([dav.DisplayName(),])
            name=name['{DAV:}displayname']
            if name.lower().find(cName)!=-1:
                bestguess=i
                bestguess_name=name
        self.calendar = self.calendars[bestguess]
        return bestguess_name

    def getEvents(self):
        #return self.calendar.events()
        events=self.calendar.events()
        obj=[]
        for event in events:
            eventurl=str(event)
            eventurl_elements=eventurl.split("/")
            eventurl=eventurl_elements[len(eventurl_elements)-1]
            result=self.readEvent(event)
            summary=result['SUMMARY'][1]
            dtstart=self.parseDateTime(result['DTSTART'])
            dtend=self.parseDateTime(result['DTEND'])
            obj.append((eventurl, dtstart, dtend, summary))
        return obj

    def readEvent(self, event):
        output={}
        lines=event.data.split("\n")
        for line in lines:
            result=self.re_caldav_line.match(line)
            if result:
                key=result.group(1)
                val=result.group(2)
                opt_array=None
                res_opts=self.re_caldav_opts.match(key)
                if(res_opts):
                    key=res_opts.group(1)
                    opt=res_opts.group(2)
                    opt_array=opt.split(";")
                output[key]=(opt_array, val)
        return output

    def parseDateTime(self, iStr):
        val=str(iStr[1])
        m_datetime=self.re_datetime.match(val)
        opts=iStr[0]
        tzid='UTC'
        if opts is not None:
            for opt in opts:
                m_tzid=self.re_tzid.match(opt)
                if m_tzid:
                    tzid=m_tzid.group(1)
        obj_dt=None
        if m_datetime:
            m_year=m_datetime.group(1)
            m_month=m_datetime.group(2)
            m_day=m_datetime.group(3)
            m_hour=m_datetime.group(5)
            m_minute=m_datetime.group(6)
            m_second=m_datetime.group(7)
            m_zulu=m_datetime.group(8)
            if m_zulu is None:
                m_zulu=tzid
            else:
                m_zulu='UTC'
            tz=pytz.timezone(m_zulu)
            tz_utc=pytz.timezone('UTC')
            if m_hour is not None:
                obj_dt=datetime(int(m_year), int(m_month), int(m_day), int(m_hour), int(m_minute), int(m_second))
            else:
                obj_dt=datetime(int(m_year), int(m_month), int(m_day))
            obj_dt=tz.localize(obj_dt)
            obj_dt=obj_dt.astimezone(tz_utc)
            return obj_dt
        return None

