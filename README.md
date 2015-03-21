Convert SVN XML logs to iCalendar .ics files. Written in Python. Uses vObject and Beautiful Soup.

    $ svn --verbose --xml log project > project.log
    $ python pysvnlog2ics.py -x "project.log" -i "project.ics" -p "My Project"
