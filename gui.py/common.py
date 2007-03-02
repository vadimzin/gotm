#$Id: common.py,v 1.20 2007-03-02 12:33:45 jorn Exp $

import datetime,time,sys
import matplotlib.numerix

# ------------------------------------------------------------------------------------------
# Date-time parsing variables and functions
# ------------------------------------------------------------------------------------------

# datetime_displayformat: date format used to display datetime objects in the GUI.
datetime_displayformat = '%Y-%m-%d %H:%M:%S'

# parsedatetime: Convert string to Python datetime object, using specified format.
#   Counterpart of datetime.strftime.
def parsedatetime(str,fmt):
    t1tmp = time.strptime(str,fmt) 
    return datetime.datetime(*t1tmp[0:6])

# ------------------------------------------------------------------------------------------
# Command line argument utility functions
# ------------------------------------------------------------------------------------------

# getNamedArgument: Get the value of a named command line argument, and removes both name
#   and value from the global list of command line arguments. Returns None if the command
#   line argument was not specified. If the script was called with 'script.py -d hello',
#   getNamedArgument('-d') will return 'hello'.
def getNamedArgument(name):
    try:
        iarg = sys.argv.index(name)
    except ValueError:
        return None
    val = sys.argv[iarg+1]
    del sys.argv[iarg+1]
    del sys.argv[iarg]
    return val

# ------------------------------------------------------------------------------------------
# XML helper functions
# ------------------------------------------------------------------------------------------

# findDescendantNode: Return the first child XML DOM node with the specified location
#   (location = array of path components) below the specified XML DOM node (root).
#   If create = True, the node will be created if it does not exist yet.
def findDescendantNode(root,location,create=False):
    assert root!=None,'findDescendantNode called on non-existent parent node (parent = None).'
    node = root
    for childname in location:
        if childname=='': continue
        foundchild = None
        for ch in node.childNodes:
            if ch.nodeType==ch.ELEMENT_NODE and ch.localName==childname:
                foundchild = ch
                break
        else:
            if create:
                doc = root
                while doc.parentNode!=None: doc=doc.parentNode
                foundchild = doc.createElementNS(node.namespaceURI,childname)
                node.appendChild(foundchild)
            else:
                return None
        node = foundchild
    return node

# findDescendantNodes: Return a list of all child XML DOM nodes with the specified location
#   (location = array of path components) below the specified XML DOM node (root).
def findDescendantNodes(root,location):
    parentloc = location[:]
    name = parentloc.pop()
    parent = findDescendantNode(root,parentloc,create=False)
    children = []
    if parent!=None:
        for ch in parent.childNodes:
            if ch.nodeType==ch.ELEMENT_NODE and ch.localName==name:
                children.append(ch)
    return children

def addDescendantNode(root,location):
    parentloc = location[:]
    name = parentloc.pop()
    parent = findDescendantNode(root,parentloc,create=True)
    assert parent!=None,'Unable to locate or create parent node for "%s".' % str(location)
    doc = root
    while doc.parentNode!=None: doc=doc.parentNode
    node = doc.createElementNS(parent.namespaceURI,name)
    parent.appendChild(node)
    return node

def getNodeText(node):
    rc = ''
    for ch in node.childNodes:
        if ch.nodeType == ch.TEXT_NODE: rc += ch.data
    return rc

def setNodeText(node,text,xmldocument=None):
    if xmldocument==None:
        xmldocument = node
        while xmldocument.parentNode!=None: xmldocument=xmldocument.parentNode
    for ch in node.childNodes:
        if ch.nodeType == ch.TEXT_NODE:
            node.removeChild(ch)
            ch.unlink()
    val = xmldocument.createTextNode(text)
    node.insertBefore(val,node.firstChild)

# ------------------------------------------------------------------------------------------
# Numerical helper utilities
# ------------------------------------------------------------------------------------------

# Look for boundary indices of array based on desired value range.
def findindices(bounds,data):
    # Zero-based indices!
    start = 0
    stop = len(data)-1
    if bounds!=None:
        if bounds[0]!=None:
            while start<len(data) and data[start]<bounds[0]: start+=1
        if bounds[1]!=None:
            while stop>=0         and data[stop] >bounds[1]: stop-=1

        # Greedy: we want take the interval that fully encompasses the specified range.
        # (note that this also corrects for a start beyond the available range, or a stop before it)
        if start>0:          start-=1
        if stop<len(data)-1: stop +=1
        
    return (start,stop)

# 1D linear inter- and extrapolation.
def interp1(x,y,X):
    assert len(x.shape)==1, 'Original coordinates must be supplied as 1D array.'
    assert len(X.shape)==1, 'New coordinates must be supplied as 1D array.'
    newshape = [X.shape[0]]
    for i in y.shape[1:]: newshape.append(i)
    Y = matplotlib.numerix.zeros(newshape,matplotlib.numerix.typecode(y))
    icurx = 0
    for i in range(X.shape[0]):
        while icurx<x.shape[0] and x[icurx]<X[i]: icurx+=1
        if icurx==0:
            Y[i,:] = y[0,:]
        elif icurx>=x.shape[0]:
            Y[i,:] = y[-1,:]
        else:
            rc = (y[icurx,:]-y[icurx-1,:])/(x[icurx]-x[icurx-1])
            Y[i,:] = y[icurx-1,:] + rc*(X[i]-x[icurx-1])
    return Y
