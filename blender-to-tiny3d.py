import bpy
import math
import zlib

# 1 = type: (0 = box, 1 = cylinder, 2 = cone, 3 = plane, 4 = sphere)
#     Cylinder: type segmentsRadial
#     Cone: type segmentsRadial radiusBottom radiusTop
# 2 = group colour i (based on materials. Convert group names to numbers) (color, 3 figure hex, without #) (i = interact class - only need to add # the first time a group appears)
# 3 = position
# 4 = scale (if 1 value, apply that to all 3 axis)
# 5 = rotation (optional)

def radToDeg (val):
    return (val * 180) / math.pi

def parseNumber (val): # converts number to string, and removes trailing zeros
    text = str(round(val, 2))
    if text[len(text) - 1] == '0':
        text = text[0: len(text) - 1]
    if text[len(text) - 1] == '.':
        text = text[0: len(text) - 1]
    return text

def rgbToHex (r, g, b): # converts rgb values in the range of 0-1 to hex code
    hex = '%02x%02x%02x' % (math.floor(r * 255), math.floor(g * 255), math.floor(b * 255))
    # Convert to 3 digits only
    return hex[0] + hex[2] + hex[4]
output = ''

groupNames = ['general']
groupsRefs = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] # so we don't need to store the actual name, saving space

for obj in bpy.data.objects:
    
    if (output != ''): # i.e. this is a new entity
        output += '/'
    
    # work out which group this belongs to based on its material
    group = 'general'
    groupIndex = 0
    groupText = ''
    if obj.material_slots:
        group = obj.material_slots[0].name
    
    # does this group already exist?
    if group not in groupNames:
        # create a new group
        groupIndex = len(groupNames)
        groupNames.append(group)
        groupText = groupsRefs[groupIndex] + ' ' + rgbToHex(obj.material_slots[0].material.diffuse_color[0], obj.material_slots[0].material.diffuse_color[1], obj.material_slots[0].material.diffuse_color[2])
        
        # custom properties on the material:
        # (only I for interact at the moment, but this may expand in future)
        for customProp in obj.material_slots[0].material.keys():
            if customProp == 'Interact':
                groupText += ' I'

    else:
        groupIndex = groupNames.index(group)
        groupText = groupsRefs[groupIndex]

    # geometry
    if 'Cube' in obj.name:
        output += '0'
    elif 'Plane' in obj.name:
        output += '3'
    elif 'Cone' in obj.name:
        output += '2 '
        output += str(len(obj.data.polygons) - 2) + ' '
        if 'radiusBottom' not in obj.keys():
            obj['radiusBottom'] = 1
        if 'radiusTop' not in obj.keys():
            obj['radiusTop'] = 0
        output += str(obj['radiusBottom']) + ' '
        output += str(obj['radiusTop'])
    elif 'Cylinder' in obj.name:
        output += '1 '
        output += str(len(obj.data.polygons) - 2)
    
    output += ',' + groupText
    
    # position
    output += ',' + parseNumber(obj.location.x) + ' ' + parseNumber(obj.location.z) + ' ' + parseNumber(obj.location.y)
    
    # scale
    if obj.scale.x == obj.scale.y and obj.scale.x == obj.scale.z: # just write a single scale value
        output += ',' + parseNumber(obj.scale.x * 2) + ','
    else: 
        output += ',' + parseNumber(obj.scale.x * 2) + ' ' + parseNumber(obj.scale.z * 2) + ' ' + parseNumber(obj.scale.y * 2)

    # rotation
    if obj.rotation_euler.x != 0 or obj.rotation_euler.y != 0 or obj.rotation_euler.z != 0:
        output += ',' + parseNumber(radToDeg(obj.rotation_euler.x)) + ' ' + parseNumber(radToDeg(obj.rotation_euler.z)) + ' ' + parseNumber(radToDeg(obj.rotation_euler.y))

# print output
print(output)
print('(' + str(round(len(output) / 1024, 2)) + 'KB uncompressed, ' + str(round(len(zlib.compress(output.encode('utf-8'))) / 1024, 2)) + 'KB compressed)')
