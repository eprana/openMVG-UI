import maya.cmds as cmds
import pymel.core as pm
import os

'''
Export the current selection to an ABC archive, w/ the following options:
  - the worldSpace option
  - the uvWrite option
  - an entry in the export attribute list : 'imagePath'
'''
def exportSelectionAsABC():
    # check for AbcExport command
    if not 'AbcExport' in dir(pm):
        pm.error('AbcExport: command not found.')
        return
    # retrieve all selected node paths
    selection = pm.ls(sl=True, recursive=True, dagObjects=True)
    if not selection:
        return
    nodePathtoExport = []
    for n in selection:
        if n.type() != 'transform':
            nodePathtoExport.append(n.getParent().fullPath())
    # get out file path from user
    outfile = pm.fileDialog2(fileMode=0)
    if not outfile:
        return
    # ensure we use a '*.abc' file extension
    outfile = os.path.splitext(outfile[0])[0]+'.abc'
    # build the AbcExport command
    exportCmd = '-worldSpace -attr mvg_imageSourcePath -attr mvg_intrinsicParams -file %s -uvWrite'%outfile
    for p in nodePathtoExport:
        exportCmd += ' -root %s'%p
    exportCmd = '''
import pymel.core as pm
pm.AbcExport(j="%s")'''%exportCmd
    pm.evalDeferred(exportCmd)


def createLocator(locatorPosition):
    mvgRoot = 'mvgRoot'
    mvgLocator = 'mvgLocator'
    # Create or retrieve locator
    list = cmds.ls(mvgLocator)

    if not list:
        transformNode = cmds.createNode('transform', name=mvgLocator, parent=mvgRoot)
        cmds.createNode( 'MVGDummyLocator', parent=transformNode)
    cmds.xform(mvgLocator, ws=True, r=True, t=locatorPosition)


def createLocatorFromVertex():

    # Get selected vertex
    selection = cmds.ls('*.vtx[*]', selection=True, fl=True)
    if len(selection) != 1:
        print "You need to select one vertex (and one only)."
        return
    vertex = selection[0]
    vertexPosition = cmds.xform(vertex, q=True, ws=True, t=True)

    createLocator(vertexPosition)

def loadPCColor():
    pointCloud = 'mvgPointCloud'
    particleShape = 'particleShape1'
    colorR = cmds.getAttr('{}.mvg_R'.format(particleShape))
    colorG = cmds.getAttr('{}.mvg_G'.format(particleShape))
    colorB = cmds.getAttr('{}.mvg_B'.format(particleShape))

    if not cmds.attributeQuery('rgbPP', node='particleShape1', exists=True):
        cmds.addAttr(particleShape, shortName='rgbPP', longName='rgbPP', dt='vectorArray')

    totalParticle = cmds.particle(pointCloud, query=True, count=True)
    for i in range(totalParticle):
        cmds.particle(particleShape, edit=True, id=i, attribute='rgbPP', vectorValue=(colorR[i]/255., colorG[i]/255., colorB[i]/255.))

def loadPCDebugColor():
    import colorsys

    pointCloud = 'mvgPointCloud'
    particleShape = 'particleShape1'

    if not cmds.attributeQuery('rgbPP', node='particleShape1', exists=True):
        cmds.addAttr(particleShape, shortName='rgbPP', longName='rgbPP', dt='vectorArray')

    totalParticle = cmds.particle(pointCloud, query=True, count=True)
    visibilitySizePerPoint = cmds.getAttr('{}.mvg_visibilitySize'.format(pointCloud))
    maxVisibility = float(max(visibilitySizePerPoint))
    for id in range(totalParticle):
        v = visibilitySizePerPoint[id] / maxVisibility
        myColor = colorsys.hsv_to_rgb(v, 1.0, 1.0)
        if visibilitySizePerPoint[id] < 3:
            myColor = [1, 0, 0]
        cmds.particle(pointCloud, edit=True, attribute='rgbPP', order=id, vectorValue=myColor)

def openMVGWindow_CB():
    # ToolStats
    try:
        from toolStats import toolUsage
        toolUsage.addUsage('MayaMVG','vfx.mikros.int')
    except:
        print "WARNING : ToolStats module not found."
    pm.MVGCmd()

def exportSelectionAsABC_CB():
    exportSelectionAsABC()

def createLocatorFromVertex_CB():
    createLocatorFromVertex()

def loadPCColor_CB():
    loadPCColor()

def loadPCDebugColor_CB():
    loadPCDebugColor()

def mvgCreateMenu():
    gMainWindow = pm.mel.eval('$tmpVar=$gMainWindow')
    menuName = "mvgMenu"
    menuLabel = "MayaMVG"
    if(pm.menu(menuName, exists=True)):
        pm.deleteUI(menuName)
    if(gMainWindow != ""):
        pm.setParent(gMainWindow)
        menu = pm.menu(menuName, label=menuLabel, tearOff=True)
        pm.menuItem(parent=menu, label='Open...', command=pm.Callback(openMVGWindow_CB))
        pm.menuItem(parent=menu, label='Export selection as ABC', command=pm.Callback(exportSelectionAsABC_CB))
        pm.menuItem(parent=menu, label='Create locator from vertex', command=pm.Callback(createLocatorFromVertex_CB))
        pm.menuItem(parent=menu, divider=True)
        pm.menuItem(parent=menu, label='Load pointcloud color', command=pm.Callback(loadPCColor_CB))
        pm.menuItem(parent=menu, label='Load pointcloud debug color', command=pm.Callback(loadPCDebugColor_CB))

def mvgDeleteMenu():
    menuName = "mvgMenu"
    if(pm.menu(menuName, exists=True)):
        pm.deleteUI(menuName)
