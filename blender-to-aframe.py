import bpy
import math
import zlib

def radToDeg (val):
    return (val * 180) / math.pi

def parseNumber (val): # converts number to string, and removes trailing zeros
    text = str(round(val, 2))
    if text[len(text) - 1] == '0':
        text = text[0: len(text) - 1]
    if text[len(text) - 1] == '.':
        text = text[0: len(text) - 1]
    return text

groupNames = ['general']
groupData = ['']

for obj in bpy.data.objects:
    
    # work out which group this belongs to based on its material
    group = 'general'
    groupIndex = 0
    if obj.material_slots:
        group = obj.material_slots[0].name
    
    # does this group already exist?
    if group not in groupNames:
        # create a new group
        groupIndex = len(groupNames)
        groupNames.append(group)
        newText = '\r\n<a-entity material="color: ' + parseNumber(obj.material_slots[0].material.diffuse_color[0]) + ' ' + parseNumber(obj.material_slots[0].material.diffuse_color[1]) + ' ' + parseNumber(obj.material_slots[0].material.diffuse_color[2]) + '"'
        
        # custom properties on the material:
        for customProp in obj.material_slots[0].material.keys():
            if customProp != '_RNA_UI':
                newText += ' ' + customProp + '="' + str(obj.material_slots[0].material[customProp]) + '"'
        
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
        groupData[groupIndex] += ' geometry="primitive: box'
    elif 'Plane' in obj.name:
        groupData[groupIndex] += ' geometry="primitive: plane'
    elif 'Cone' in obj.name:        
        if 'radiusBottom' not in obj.keys():
            obj['radiusBottom'] = 1
        if 'radiusTop' not in obj.keys():
            obj['radiusTop'] = 0
        groupData[groupIndex] += ' geometry="primitive: cone; segmentsHeight: 1; segmentsRadial: ' + str(len(obj.data.polygons) - 2) + '; radiusBottom: ' + str(obj['radiusBottom']) + '; radiusTop: ' + str(obj['radiusTop'])
    elif 'Cylinder' in obj.name:
        groupData[groupIndex] += ' geometry="primitive: cylinder; segmentsHeight: 1; segmentsRadial: ' + str(len(obj.data.polygons) - 2)
    
    # need to set buffer to false for merged geometries
    if group == 'general':
        groupData[groupIndex] += '"'
    else:
        groupData[groupIndex] += '; buffer: false"'
    
    if obj.scale.x != 0.5 or obj.scale.y != 0.5 or obj.scale.z != 0.5: # as primitives are 2m by default in blender, scales are doubled    
        groupData[groupIndex] += ' scale="' + parseNumber(obj.scale.x * 2) + ' ' + parseNumber(obj.scale.z * 2) + ' ' + parseNumber(obj.scale.y * 2) + '"'
    if obj.location.x != 0 or obj.location.y != 0 or obj.location.z != 0:
        groupData[groupIndex] += ' position="' + parseNumber(obj.location.x) + ' ' + parseNumber(obj.location.z) + ' ' + parseNumber(obj.location.y) + '"'
    if obj.rotation_euler.x != 0 or obj.rotation_euler.y != 0 or obj.rotation_euler.z != 0:
        groupData[groupIndex] += ' rotation="' + parseNumber(radToDeg(obj.rotation_euler.x)) + ' ' + parseNumber(radToDeg(obj.rotation_euler.z)) + ' ' + parseNumber(radToDeg(obj.rotation_euler.y)) + '"'
    
    # custom properties on the object:
    unwantedKeys = ['_RNA_UI', 'cycles', 'radiusBottom', 'radiusTop']
    for customProp in obj.keys():
        if customProp not in unwantedKeys:
            groupData[groupIndex] += ' ' + customProp + '="' + str(obj[customProp]) + '"'
    
    groupData[groupIndex] += '></a-entity>'

output = ''
for text in groupData:
    output += text
    if groupNames[groupData.index(text)] != 'general':
        output += '\r\n</a-entity>'
print(output)
print('(' + str(round(len(output) / 1024, 2)) + 'KB uncompressed, ' + str(round(len(zlib.compress(output.encode('utf-8'))) / 1024, 2)) + 'KB compressed)')
