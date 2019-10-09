/*
1 = type: (0 = box, 1 = cylinder, 2 = cone, 3 = plane, 4 = sphere, 5 = dodecahedron)
    Cylinder: type segmentsRadial
    Cone: type segmentsRadial radiusBottom radiusTop
    Sphere: type SegmentsWidth segmentsHeight
2 = group colour i (based on materials. Convert group names to numbers) (color, 3 figure hex, without #) (i = interact class - only need to add the first time a group appears)
3 = position
4 = scale (if 1 value, apply that to all 3 axis)
5 = rotation (optional)
*/

const tiny3D = (function () {

    const GEOMETRIES = ["box", "cylinder", "cone", "plane", "sphere", "dodecahedron"];
    
    return function (data, parentEl, callback) { // data and parentEl required, callback optional

        let groups = []; // {id: 0, el: <a-entity>}

        // loop through each entity
        data.split("/").forEach(function (entity) {

            // split entity into each component
            let sections = entity.split(",");

            let el = document.createElement("a-entity");


            // 1. geometry
            let geometryText = "primitive: ";
            let geometryData = sections[0].split(" ");
            geometryText += GEOMETRIES[parseInt(geometryData[0], 10)];
            el.setAttribute("geometry", geometryText);
            
            // segmentsRadial - cylinder/cone
            if (geometryData[0] === "1" || geometryData[0] === "2") {
                geometryText += "; segmentsHeight: 1; segmentsRadial: " + geometryData[1];
            }
            
            // cone - radiusBottom + radiusTop
            if (geometryData[0] === "2") {
                geometryText += "; radiusBottom: " + geometryData[2] + "; radiusTop: " + geometryData[3];
            }
            
            // sphere
            if (geometryData[0] === "4") {
                geometryData += "; segmentsHeight: " + geometryData[1] + "; segmentsWidth: " + geometryData[2];
            }
            
            // geometry attribute is added later, so we know whether to add "buffer: false"
            
            
            // 3. position
            el.setAttribute("position", sections[2]);
            

            // 4. scale
            let scaleData = sections[3];
            if (scaleData.indexOf(" ") === -1) { // it is just one value, apply that to all 3 axis
                el.setAttribute("scale", scaleData + " " + scaleData + " " + scaleData);
            } else { // copy it exactly
                el.setAttribute("scale", scaleData);
            }
            
            
            // 5. rotation
            if (sections.length >= 5) {
                el.setAttribute("rotation", sections[4]);
            }
            

            // 2. group - do this last so can add directly to group entity
            let groupData = sections[1].split(" ");

            // check if group already exists
            let groupIndex = -1;
            groups.forEach(function (group, index) {
                if (group.id === groupData[0]) {
                    groupIndex = index;
                } 
            });
            if (groupIndex === -1) { // add new group
                groups.push({
                    id: groupData[0],
                    el: document.createElement("a-entity")
                });
                groupIndex = groups.length - 1;
                groups[groupIndex].el.setAttribute("merge", "");
                groups[groupIndex].el.setAttribute("material", "color: #" + groupData[1]);
                if (groupData.length >= 3 && groupData[2].indexOf("i") !== -1) { // add interactive class
                    groups[groupIndex].el.className = "i";
                }
            }

            // add element to group
            geometryText += "; buffer: false";
            groups[groupIndex].el.appendChild(el);
            
            // set this last, as "buffer: false" is only added at the group stage
            el.setAttribute("geometry", geometryText);
            
        });
        
        // add each group to scene
        groups.forEach(function (group) {
            parentEl.appendChild(group.el); 
        });
        
        if (callback) {
            callback();
        }
        
    };
    
}());

// For advanced optimisation in Closure Compiler:
window['tiny3D'] = tiny3D;
