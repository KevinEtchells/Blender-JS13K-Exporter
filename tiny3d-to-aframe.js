const tiny3D = (function () {

    const GEOMETRIES = ["box", "cylinder", "cone", "plane", "sphere", "dodecahedron"];
    
    return function (data, parentEl, callback) { // data and parentEl required, callback optional

        let groups = []; // {id: 0, el: <a-entity>}

        // loop through each entity
        let entities = data.split("/");
        for (let entityIndex = 0; entityIndex < entities.length; entityIndex++) { // for loop rather than forEach as we add new entities when processing modifiers

            // split entity into each component
            let sections = entities[entityIndex].split(",");

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
            if (sections.length >= 5 && sections[4]) {
                el.setAttribute("rotation", sections[4]);
            }
            
            
            // 6. modifiers
            if (sections.length >= 6) {
                if (sections[5].indexOf("m") === 0) { // mirror modifier
                    let mirrorObjectIndex = parseInt(sections[5].replace("m", ""));
                    let mirrorPosition = entities[mirrorObjectIndex].split(",")[2];
                    let mirrorX = parseFloat(mirrorPosition.split(" ")[0]);
                    let objectPosition = sections[2];
                    let objectX = parseFloat(objectPosition.split(" ")[0]);
                    let difference = objectX - mirrorX;
                    let newEntity = "";
                    sections.forEach(function (section, sectionIndex) {
                        if (sectionIndex !== 0) {
                            newEntity += ",";
                        }
                        if (sectionIndex === 2) {
                            // TO DO: + or - difference may depend on if objectX is > or < mirrorX
                            newEntity += objectPosition.replace(/-?[0-9]*/, objectX - (difference * 2) );
                        } else if (sectionIndex !== 5) { // we want to add all sections back in except for modifiers
                            newEntity += sections[sectionIndex];
                        }
                    });
                    entities.push(newEntity);
                }
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
            
        }
        
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
