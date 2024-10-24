#!/usr/bin/python

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import numpy as np





def make_sButton(arg):
    """create the sButton structure"""
    paramid = arg.find('PARAMID')
    paramid = paramid.text if paramid is not None else ''

    alias = arg.find('NAME')
    alias = alias.text if alias is not None else ''

    did = arg.find('TITLE')
    did = did.text if did is not None else ''

    uid = arg.find('UNIT')
    uid = uid.text if uid is not None else ''

    arg_type = arg.find('TYPE')
    arg_type = arg_type.text if arg_type is not None else ''

    value = arg.find('VALUE')
    value = np.array([float(i) for i in value.text.split(",")]) if value is not None else ''

    sArgument = {"paramid": paramid,
        "name": alias,
        "title": did,
        "unit": uid,
        "button_type": arg_type,
        "value": value,
        "div": ''
        }

    return sArgument

def make_sArgument(arg):
    """create the sArgument structure"""
    paramid = arg.find('PARAMID')
    paramid = paramid.text if paramid is not None else ''

    alias = arg.find('ALIAS')
    alias = alias.text if alias is not None else ''

    did = arg.find('DATASETID')
    did = did.text if did is not None else ''

    arg_type = arg.find('TYPE')
    arg_type = arg_type.text if arg_type is not None else ''

    range_arg = arg.find('RANGE')
    range_arg = np.array([float(i) for i in range_arg.text.split(",")]) if range_arg is not None else np.zeros(2)

    value = arg.find('VALUE')
    value = value.text if value is not None else ''

    sArgument = {"paramid": paramid,
        "alias": alias,
        "datasetid": did,
        "type": arg_type,
        "value": value,
        "range": range_arg
        }

    return sArgument

def make_sData(data):
    """create the sData structure"""
    type = data.find('TYPE')
    type = type.text if type is not None else ''

    pid = data.find('PARAMID')
    pid = pid.text if pid is not None else ''

    sData = {"paramid": pid,
        "type": type
    }

    return sData

def make_sProcessing(proc):
    """create the sProcessing structure"""

    name = proc.find('NAME')
    name = name.text if name is not None else ''

    order = proc.find('ORDER')
    order = order.text if order is not None else '-1'

    range_proc = proc.find('RANGE')
    range_proc = np.array([float(i) for i in range_proc.text.split(",")]) if range_proc is not None else np.zeros(2)

    value = proc.findall('VALUE')
    flag_first_val = 1
    values = None
    for val in value:
        if flag_first_val == 1:
            values = val.text if val is not None else ''
            flag_first_val = 0
        else:
            values = values + ',' + val.text if val is not None else ''

    arguments = proc.findall('ARGUMENT')
    num_arg = len(arguments)
    sArg = [dict() for x in range(num_arg)]
    i = 0
    for arg in arguments:
        sArg[i] = make_sArgument(arg)
        i+=1

    sProc = {"name": name,
		"range": range_proc,
		"value": values,
		"order": order,
		"num_arg": num_arg,
    	"sArgument": sArg
    }

    return sProc


def make_sAxis(axis):
    """create an empty sAxis structure"""

    # in case of pre-defined fixed range
    axis_range = axis.find('RANGE')
    axis_range = np.array([float(i) for i in axis_range.text.split(",")]) if axis_range is not None else np.zeros(2)

    pregen_range = axis.find('PREGEN_RANGE')
    pregen_range = np.array([float(i) for i in pregen_range.text.split(",")]) if pregen_range is not None else np.zeros(2)

    type = axis.find('TYPE')
    type = type.text if type is not None else ''

    log = axis.find('LOG')
    log = int(float(log.text)) if log is not None else 0

    display = axis.find('DISPLAY')
    display = int(float(display.text)) if display is not None else 1

    num_tick = axis.find('NUM_TICK')
    num_tick = int(float(num_tick.text)) if num_tick is not None else 0

    num_min_tick = axis.find('NUM_MIN_TICK')
    num_min_tick = int(float(num_min_tick.text)) if num_min_tick is not None else 0

    unit = axis.find('UNIT')
    unit = unit.text if unit is not None else ''

    label = axis.find('LABEL')
    label = label.text if label is not None else ''

    tick_val = axis.find('TICKVALUES')
    if tick_val is not None:
        tick_val = np.array([float(i) for i in tick_val.text.split(",")]) 
        tick_flag = 1
    else :
        tick_val = np.zeros(6)
        tick_flag = 0

    tick_label = axis.find('TICKNAMES')
    tick_label = tick_label.text.split(",") if tick_label is not None else ['','','','','','']

    flag_rotate = axis.find('ROTATE')
    if flag_rotate is not None:
        if flag_rotate.text == '1':
            flag_rotate = 0
        else:
            flag_rotate = 270
    else :
        flag_rotate = 270

    sAxis = {"type": type,
		"range": axis_range,
		"range_calc": np.zeros(2),
		"pregen_range": pregen_range,
		"log": log,
		"unit": unit,
		"label": label,
		"num_tick": num_tick,
		"tick_val": tick_val,
		"tick_label": tick_label,
                "tick_flag": tick_flag,
		"num_min_tick": num_min_tick,
		"display": display,
                "rotate": flag_rotate
    }

    return sAxis

def make_sLine(line):
    """create the sLine structure"""
    thick = line.find('THICK')
    thick = int(float(thick.text)) if thick is not None else 2

    style = line.find('STYLE')
    style = int(float(style.text)) if style is not None else 1

    color = line.find('COLOR')
    color = color.text if color is not None else 'black'

    symbol = line.find('SYMBOL')
    symbol = symbol.text if symbol is not None else ''

    line_type = line.find('TYPE')
    line_type = line_type.text if line_type is not None else 'line'

    legend = line.find('LEGEND')
    legend = int(float(legend.text)) if legend is not None else 1

    name = line.find('NAME')
    name = name.text if name is not None else ''

    sLine = {"thick": thick,
		"style": style,
		"color": color,
		"symbol": symbol,
        	"name": name,
		"legend": legend,
                "type": line_type
    }

    return sLine

def make_sPlot(plot):
    """create the sPlot structure"""
    ptype = plot.find('PLOT_TYPE')
    ptype = ptype.text if ptype is not None else ''

    order = plot.find('ORDER')
    order = order.text if order is not None else '-1'

    line = plot.find('LINE')
    sLine = make_sLine(line) if line is not None else dict()


    axis = plot.findall('AXIS')
    num_axis = len(axis)
    sAxis = [dict() for x in range(num_axis)]
    i = 0
    for axe in axis:
        sAxis[i] = make_sAxis(axe)
        i+=1

    processings = plot.findall('PROCESSING')
    num_proc = len(processings)
    sProc = [dict() for x in range(num_proc)]
    i = 0
    for proc in processings:
        sProc[i] = make_sProcessing(proc)
        i+=1

    datas = plot.findall('PLOT_DATA')
    num_data = len(datas)
    sData= [dict() for x in range(num_data)]
    i = 0
    for data in datas:
        sData[i] = make_sData(data)
        i+=1

    sPlot = {"plot_type": ptype,
		"order": order,
		"sLine": sLine,
		"num_axis": num_axis,
		"num_proc": num_proc,
		"num_data": num_data,
        	"num_record": 0,
		"sAxis":  sAxis,
		"sProcessing": sProc,
		"sData": sData
    }

    return sPlot

def make_sSubpanel(sub):
    """create the sSubpanel structure"""
    order = sub.find('ORDER')
    order = order.text if order is not None else '-1'

    rel_size = sub.find('SIZE')
    rel_size = rel_size.text if rel_size is not None else '1.'

    plots = sub.findall('PLOT')
    num_plots = len(plots)
    sPlot = [dict() for x in range(num_plots)]
    i = 0

    for plot in plots:
        sPlot[i] = make_sPlot(plot)
        i+=1


    sSubpan = {"order": order,
		"rel_size": float(rel_size)*100.,
		"num_plots": num_plots,
		"sPlot": sPlot
    }

    return sSubpan

def make_sPanel(panel):
    """create the sPanel structure"""
    pid = panel.find('PANEL_ID')
    pid = pid.text if pid is not None else ''

    info = panel.find('INFO')
    info = info.text if info is not None else ''

    rel_size = panel.find('SIZE')
    rel_size = rel_size.text if rel_size is not None else '1.'

    abs_size = panel.find('ABSOLUTE_SIZE')
    abs_size = abs_size.text if abs_size is not None else ''

    axis = panel.find('AXIS')
    sAxis = make_sAxis(axis) if axis is not None else dict()

    panel_type = panel.find('PANEL_TYPE')
    panel_type = panel_type.text if panel_type is not None else 'line'

    subpanels = panel.findall('SUBPANEL')
    num_subpan = len(subpanels)
    sSubpanel = [dict() for x in range(num_subpan)]
    i = 0

    for sub in subpanels:
        sSubpanel[i] = make_sSubpanel(sub)
        i+=1

    buttons = panel.findall('BUTTON')
    num_buttons = len(buttons)
    sButton = [dict() for x in range(num_buttons)]
    i = 0
    for button in buttons:
        sButton[i] = make_sButton(button)
        i+=1

    sPanel = {"panelid": pid,
		"size": rel_size,
		"abs_size": abs_size,
		"info": info,
		"num_subpan": num_subpan,
		"num_button": num_buttons,
		"panel_type": panel_type,
		"sXaxis": sAxis,
		"sSubpanel": sSubpanel,
		"sButton": sButton
        }

    return sPanel



def get_cef_from_did(did,cef_list):
    matching_cef = [s for s in cef_list if did+"__" in s]
    return matching_cef[0]



def get_lParam(panel,cef_list):
# look for all the parameters that will be required for plotting
# differentiate the processed parameter from the CEF ones
# identify the CEF files to be read from the list

    listParam = []
    # the parameters are inside the processing elements
    processings = panel.findall('.//PROCESSING')
    num_proc = len(processings)

    for proc in processings:
        # check arguments children
        # if datasetid exists then parameter comes directly from cef files (unprocessed)
        arguments = proc.findall('ARGUMENT')
        num_arg = len(arguments)
        for arg in arguments:
            pid = arg.find('PARAMID')
            did = arg.find('DATASETID')
            vid = arg.find('VALUE')
            rid = arg.find('RANGE')

            if did is not None:
                cef = get_cef_from_did(did.text,cef_list)
                listParam.append({'paramid':pid.text,'in_cef':1,'cef':cef,'fix':0,'value':vid,'range':rid})
            elif vid is not None:
                listParam.append({'paramid':pid.text,'in_cef':0,'cef':'','fix':1,'value':vid.text,'range':''})
            elif rid is not None:
                listParam.append({'paramid':pid.text,'in_cef':0,'cef':'','fix':1,'value':'','range':np.array([float(i) for i in rid.text.split(",")])})
            else:
                listParam.append({'paramid':pid.text,'in_cef':0,'cef':'','fix':0,'value':vid,'range':rid})

    # check also the plotted parameters if they come directly from the CEF file
    plots = panel.findall('.//PLOT_DATA')
    num_plots = len(plots)

    for plot in plots:
        pid = plot.find('PARAMID')
        did = plot.find('DATASETID')
        if did is not None:
            cef = get_cef_from_did(did.text,cef_list)
            listParam.append({'paramid':pid.text,'in_cef':1,'cef':cef,'fix':0,'value':'','range':''})

    return listParam



def read_panel_xml(xmlFile,cef_list):
    """ Main routine for reading panel XML file """
#xmlFile = "/Users/dherment/Desktop/python/IDL_PANEL/xml/CAA_PANEL_C1_CG_EFW_L3_P_CAA.XML"

    print('Reading', xmlFile)

    with open(xmlFile, 'rt') as f:
        tree = ET.parse(f)

    panel = tree.getroot()
    sPanel = make_sPanel(panel)

    lParam = get_lParam(panel,cef_list)


    return (sPanel,lParam)
