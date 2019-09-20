import bpy
import math
import zlib

def radToDeg (val):
    return (val * 180) / math.pi

def parseNumber (val):
    text = str(round(val, 2))
    if text[len(text) - 1] == '0':
        text = text[0: len(text) - 1]
    if text[len(text) - 1] == '.':
        text = text[0: len(text) - 1]
    return text

groupNames = ['general']
groupData = ['']

for obj in bpy.data.objects:

    #for slot in obj.material_slots:
    #    for prop in dir(slot):
    #        print(prop + ":")
    #        print(getattr(slot, prop, "undefined"))
    
    # work out which group this belongs to
    group = 'general'
    groupIndex = 0
    if obj.material_slots:
        group = obj.material_slots[0].name
    
    # does this group already exist?
    if group not in groupNames:
        # create a new group
        groupIndex = len(groupNames)
        groupNames.append(group)
        newText = '\r\n<a-entity mixin="#' + group + '"'
        if group != 'general':
            newText += ' merge'
        newText += '>'
        groupData.append(newText)
    else:
        groupIndex = groupNames.index(group)
    
    groupData[groupIndex] += '\r\n'
    if group != 'general':
        groupData[groupIndex] += '\t' #tab
    groupData[groupIndex] += '<a-entity'
    if 'Cube' in obj.name:
        groupData[groupIndex] += ' geometry="primitive: box"'
    elif 'Plane' in obj.name:
        groupData[groupIndex]+= ' geometry="primitive: plane"'
    elif 'Cylinder' in obj.name:
        groupData[groupIndex] += ' geometry="primitive: cylinder; segmentsHeight: 1; segmentsRadial: ' + str(len(obj.data.polygons) - 2) + '"'
    if obj.scale.x != 0.5 or obj.scale.y != 0.5 or obj.scale.z != 0.5: # as primitives are 2m by default in blender, scales are doubled    
        groupData[groupIndex] += ' scale="' + parseNumber(obj.scale.x * 2) + ' ' + parseNumber(obj.scale.z * 2) + ' ' + parseNumber(obj.scale.y * 2) + '"'
    if obj.location.x != 0 or obj.location.y != 0 or obj.location.z != 0:
        groupData[groupIndex] += ' position="' + parseNumber(obj.location.x) + ' ' + parseNumber(obj.location.z) + ' ' + parseNumber(obj.location.y) + '"'
    if obj.rotation_euler.x != 0 or obj.rotation_euler.y != 0 or obj.rotation_euler.z != 0:
        groupData[groupIndex] += ' rotation="' + parseNumber(radToDeg(obj.rotation_euler.x)) + ' ' + parseNumber(radToDeg(obj.rotation_euler.z)) + ' ' + parseNumber(radToDeg(obj.rotation_euler.y)) + '"'
    
    for customProp in obj.keys():
        if customProp != '_RNA_UI':
            groupData[groupIndex] += ' ' + customProp + '="' + str(obj[customProp]) + '"'
    
    groupData[groupIndex] += '></a-entity>'

output = ''
for text in groupData:
    output += text
    if groupNames[groupData.index(text)] != 'general':
        output += '\r\n</a-entity>'
print(output)
print('(' + str(round(len(output) / 1024, 2)) + 'KB uncompressed, ' + str(round(len(zlib.compress(output.encode('utf-8'))) / 1024, 2)) + 'KB compressed)')