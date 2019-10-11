import bpy
import math
import zlib

# 1 = type: (0 = box, 1 = cylinder, 2 = cone, 3 = plane, 4 = sphere, 5 = dodecahedron)
#     Cylinder: type segmentsRadial
#     Cone: type segmentsRadial radiusBottom radiusTop
#     Sphere: type SegmentsWidth segmentsHeight
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
    if 'cube' in obj.name.lower():
        output += '0'
    elif 'plane' in obj.name.lower():
        output += '3'
    elif 'cone' in obj.name.lower():
        output += '2 '
        output += str(len(obj.data.polygons) - 2) + ' '
        if 'radiusBottom' not in obj.keys():
            obj['radiusBottom'] = 1
        if 'radiusTop' not in obj.keys():
            obj['radiusTop'] = 0
        output += str(obj['radiusBottom']) + ' '
        output += str(obj['radiusTop'])
    elif 'cylinder' in obj.name.lower():
        output += '1 '
        output += str(len(obj.data.polygons) - 2)
    elif 'sphere' in obj.name.lower():
        output += '4 '
        if 'segmentsWidth' not in obj.keys():
            obj['segmentsWidth'] = 12
        if 'segmentsHeight' not in obj.keys():
            obj['segmentsHeight'] = 8
        output += str(obj['segmentsWidth']) + ' '
        output += str(obj['segmentsHeight'])
    elif 'dodecahedron' in obj.name.lower():
        output += '5'
    
    output += ',' + groupText
    
    # position (Blender and A-Frame x axis are inversely proportional)
    output += ',' + parseNumber(obj.location.x * -1) + ' ' + parseNumber(obj.location.z) + ' ' + parseNumber(obj.location.y)
    
    # scale
    # default radiuses are 1 in A-Frame (rather than 0.5, so scale accordingly here)
    # A-Frame then uses 2 for default height for cones and cylinders
    if 'cone' in obj.name.lower() or 'cylinder' in obj.name.lower() or 'sphere' in obj.name.lower() or 'dodecahedron' in obj.name.lower():
        scaleX = obj.dimensions.x / 2
        scaleY = obj.dimensions.y / 2
        if 'sphere' in obj.name.lower() or 'dodecahedron' in obj.name.lower():
            scaleZ = obj.dimensions.z / 2
        else:
            scaleZ = obj.dimensions.z
    elif 'plane' in obj.name.lower(): # A-Frame planes use X and Y axis for scale, so this allows for this axis swap later on
        scaleX = obj.dimensions.x
        scaleY = 1
        scaleZ = obj.dimensions.y
    else:
        scaleX = obj.dimensions.x
        scaleY = obj.dimensions.y
        scaleZ = obj.dimensions.z
        
    if parseNumber(scaleX) == parseNumber(scaleY) and parseNumber(scaleX) == parseNumber(scaleZ): # just write a single scale value
        output += ',' + parseNumber(scaleX)
    else: 
        output += ',' + parseNumber(scaleX) + ' ' + parseNumber(scaleZ) + ' ' + parseNumber(scaleY)

    # rotation
    rotationX = obj.rotation_euler.x
    rotationY = obj.rotation_euler.y
    rotationZ = obj.rotation_euler.z
    if 'plane' in obj.name.lower(): # As default rotation for planes is different between A-Frame and Blender
        rotationX -= math.pi / 2
    if rotationX != 0 or rotationY != 0 or rotationZ != 0:
        output += ',' + parseNumber(radToDeg(rotationX)) + ' ' + parseNumber(radToDeg(rotationZ)) + ' ' + parseNumber(radToDeg(rotationY))

# print output
print(output)
print('(' + str(round(len(output) / 1024, 2)) + 'KB uncompressed, ' + str(round(len(zlib.compress(output.encode('utf-8'))) / 1024, 2)) + 'KB compressed)')
