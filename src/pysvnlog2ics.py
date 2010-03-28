#!/bin/env/python
# -*- coding: utf8 -*-
# Convert Subversion XML Log to iCalendar format
# $Id$
# uses:
# http://vobject.skyhouseconsulting.com/
# http://www.crummy.com/software/BeautifulSoup/


import os
import sys
import traceback
import datetime

from ConfigParser import ConfigParser
from optparse import OptionParser, Option, OptionGroup

# 3rd party libs
import BeautifulSoup
import vobject


__AUTHOR__ = u"Pekka Järvinen"
__YEAR__ = "2010"
__VERSION__ = "0.0.1"


if __name__ == "__main__":
    banner  = u" %s" % (__VERSION__)
    banner += u" (c) %s %s" % (__AUTHOR__, __YEAR__)

    examples = []
    examples.append("")

    usage = "\n".join(examples)

    parser = OptionParser(version="%prog " + __VERSION__, usage=usage, description=banner)

    parser.add_option("--xml", "-x", action="store", type="string", dest="xmlfile", help="Subversion XML file")
    parser.add_option("--ical", "-i", action="store", type="string", dest="icalfile", help="iCalendar file")
    parser.add_option("--author", "-a", action="store", type="string", dest="author", help="Author is only (not required)")
    parser.add_option("--project", "-p", action="store", type="string", dest="project", help="Project name")

    (options, args) = parser.parse_args()


    if options.author == "":
        options.author = None

    if options.xmlfile == "":
        options.xmlfile = None

    if options.icalfile == "":
        options.icalfile = None

    if options.project == "":
        options.project = None

    if options.project is None:
        print "Project name not given"
        sys.exit(1)

    if options.xmlfile != None and options.icalfile != None:
        options.xmlfile = os.path.realpath(options.xmlfile)
        options.icalfile = os.path.realpath(options.icalfile)

        if os.path.isdir(options.icalfile):
            print "iCal file '%s' is directory" % options.icalfile
            sys.exit(1)

        if os.path.isfile(options.xmlfile):
            print "Opening '%s'.." % options.xmlfile
            f = open(options.xmlfile, 'rb')

            print "Reading '%s'.." % options.xmlfile
            contents = f.read()
            f.close()

            soup = BeautifulSoup.BeautifulSoup(contents, fromEncoding="utf-8")

            calendar = vobject.iCalendar()

            print "Finding entries.."

            entry_num = 1

            for i in soup.findAll('logentry'):
                date = datetime.datetime.strptime(str(i.date.decodeContents()).split('.')[0], '%Y-%m-%dT%H:%M:%S')

                revision = int(i['revision'])

                try:
                  author = i.author.decodeContents()
                except:
                  author = u'UNKNOWN'

                try:
                    message = i.msg.decodeContents()
                except:
                    message = u''

                if message == '':
                    message = u''

                if type(message) != unicode:
                    print "Message is not unicode!!"
                    print type(message)
                    print message
                    sys.exit(1)

                add_entry = True
                
                if options.author is not None:
                    if author != options.author:
                        add_entry = False

                if add_entry:
                    print "Adding entry #%d.." % entry_num

                    entry = vobject.newFromBehavior('vevent')
                    entry.add('description').value = message
                    entry.add('summary').value = u"%s: rev. %s -%s" % (options.project, revision, author)
                    start = date - datetime.timedelta(seconds=1)
                    entry.add('dtstart').value = start
                    entry.add('dtend').value = date
                    entry.add('dtstamp').value = date
                    entry.add('uid').value = u"%s#%d#%s" % (author, revision, i.date.decodeContents())

                    calendar.add(entry)

                    entry_num += 1

            # Write iCal file
            print "Writing iCalendar file '%s'.." % options.icalfile
            f = open(options.icalfile, 'wb')
            f.write(calendar.serialize())
            f.close()

            print "Done."
            sys.exit(0)

    sys.exit(1)