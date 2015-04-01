# -----------------------------------------------------------------------
# The information in this file is the property of Tableau Software and
# is confidential.
#
# Copyright (C) 2012  Tableau Software.
# Patents Pending.
# -----------------------------------------------------------------------
# externalapi/samples/csv2tde.py
# -----------------------------------------------------------------------
import sys
import csv
import time
import datetime
import locale
import array
import re
import ConfigParser

# Import Tableau module
from dataextract import *

# Define type maps
schemaIniTypeMap = {
    'boolean':  Type.BOOLEAN,
    'number':   Type.INTEGER,
    'decimal':  Type.DOUBLE,
    'date':     Type.DATE,
    'datetime': Type.DATETIME,
    'string':   Type.UNICODE_STRING,
}

def setDate(row, colNo, value) :
        d = datetime.datetime.strptime(value, "%Y-%m-%d")
        row.setDate( colNo, d.year, d.month, d.day )

def setDateTime(row, colNo, value) :
        if( value.find(".") != -1) :
                d = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        else :
                d = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        row.setDateTime( colNo, d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond/100 )

fieldSetterMap = {
  Type.BOOLEAN:        lambda row, colNo, value: row.setBoolean( colNo, value.lower() == "true" ),
  Type.INTEGER:        lambda row, colNo, value: row.setInteger( colNo, int(value) ),
  Type.DOUBLE:         lambda row, colNo, value: row.setDouble( colNo, float(value) ),
  Type.UNICODE_STRING: lambda row, colNo, value: row.setString( colNo, value ),
  Type.CHAR_STRING:    lambda row, colNo, value: row.setCharString( colNo, value ),
  Type.DATE:           lambda row, colNo, value: setDate(row, colNo, value),
  Type.DATETIME:       lambda row, colNo, value: setDateTime( row, colNo, value )
}
def convert(csvReader, tdeFile, typedefs) :
    # Start stopwatch
    #startTime = time.clock()
    #csvFile = sys.argv[1];

    hasHeader = True
    colNames = [] #typedefs.keys()
    colTypes = []
    locale.setlocale(locale.LC_ALL, '')

    def getColumnType(colName):
        if colName in typedefs:
            return schemaIniTypeMap[typedefs[colName]['type']]
        else:
            return Type.UNICODE_STRING


    # Open CSV file
    #csvReader = csv.reader(open(csvFile, 'rb'), delimiter=',', quotechar='"')

    # Create TDE output
    #tdeFile = csvFile.split('.')[0] + ".tde";
    print "Creating extract:", tdeFile
    with Extract(tdeFile) as extract:
        table = None  # set by createTable
        tableDef = None

        # Define createTable function
        def createTable(line):
            if line:
                # append with empty columns so we have the same number of columns as the header row
                while len(colNames) < len(line):
                    colNames.append(None)
                    colTypes.append(Type.UNICODE_STRING)
                # write in the column names from the header row
                colNo = 0
                for colName in line:
                    colNames[colNo] = colName
                    #print "coltype for ", colName, 'is ', getColumnType(colName)
                    colTypes[colNo] = getColumnType(colName)
                    colNo += 1

            # for any unnamed column, provide a default
            for i in range(0, len(colNames)):
                if colNames[i] is None:
                    colNames[i] = 'F' + str(i + 1)

            # create the schema and the table from it
            tableDef = TableDefinition()
            for i in range(0, len(colNames)):
                tableDef.addColumn( colNames[i], colTypes[i] )
            table = extract.addTable( "Extract", tableDef )
            return table, tableDef

        # Read the table
        rowNo = 0
        for line in csvReader:

            # Create the table upon first row (which may be a header)
            if table is None:
                table, tableDef = createTable( line if hasHeader else None )
                if hasHeader:
                    continue

            # We have a table, now write a row of values
            row = Row(tableDef)
            colNo = 0
            for field in line:
                if( colTypes[colNo] != Type.UNICODE_STRING and field == "" ) :
                    row.setNull( colNo )
                else :
                    fieldSetterMap[colTypes[colNo]](row, colNo, field);
                colNo += 1
            table.insert(row)

            # Output progress line
            rowNo += 1
            if rowNo % 100000 == 0:
                print "\b"*32 + locale.format("%d", rowNo, grouping=True), "rows inserted",

        # Terminate progress line
        if rowNo >= 100000:
            print  # terminate line


# Output elapsed time
#print "Elapsed:", locale.format("%.2f", time.clock() - startTime), "seconds"



# colParser = re.compile(r'(col)(\d+)', re.IGNORECASE)
# schemaIni = ConfigParser.ConfigParser()
# schemaIni.read("schema.ini")
# for item in schemaIni.items(csvFile):
#     name = item[0]
#     value = item[1]
#     if name == "colnameheader":
#         hasHeader = value == "True";
#     m = colParser.match(name)
#     if not m:
#         continue
#     colName = m.groups()[0]
#     colNo = int(m.groups()[1]) - 1;
#     parts = value.split(' ')
#     name = parts[0]
#     try:
#         type = schemaIniTypeMap[parts[1]]
#     except KeyError:
#         type = Type.UNICODE_STRING
#     while colNo >= len(colNames):
#         colNames.append(None)
#         colTypes.append(Type.UNICODE_STRING)
#     colNames[colNo] = name
#     colTypes[colNo] = type
