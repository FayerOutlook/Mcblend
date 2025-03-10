from ..Data import *

# This function checks if a given material's name contains any of the keywords in the provided array. 
# It returns True if a match is found, and False otherwise.

def MaterialIn(Array, material):
    for material_part in material.name.lower().replace("-", ".").split("."):
        try:
            for keyword, other in Array.items():
                if keyword == material_part:
                    return True
        except:
            for keyword in Array:
                if keyword in material_part:
                    return True
    return False

# This function checks if there is a connection between two nodes in a material's node tree based on the specified criteria. 
# It returns True if a connection is found, and False otherwise.
        
def IsConnectedTo(NodeFromName, NodeFromType, NodeToName, NodeToType, index, nodeTo=None):
    if nodeTo is None:
        for selected_object in bpy.context.selected_objects:
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    if material is not None:                       # Materials Check
                        for Node in material.node_tree.nodes:      # Every Node in Material Check
                            if NodeToName is not None:
                                if NodeToName in Node.name:
                            
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                return True
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:

                                                return True
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                                return True
                                            
                            if NodeToType is not None:
                                if NodeToType == Node.type:
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                    return True
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                                return True
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                                return True

                            if NodeToName is not None and NodeToType is not None:
                                if NodeToName == Node.name and NodeToType == Node.type:
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                    return True
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                                return True
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                                return True

    else:
        for selected_object in bpy.context.selected_objects:
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    if material is not None:

                        for link in nodeTo.inputs[index].links:
                            if NodeFromName is None and NodeFromType is None:
                                    return True

                            else:
                                if NodeFromName is not None and NodeFromType is None:
                                    if NodeFromName in link.from_node.name:
                                        return True

                                if NodeFromType is not None and NodeFromName is None:
                                    if NodeFromType == link.from_node.type:
                                        return True

                                if NodeFromName is not None and NodeFromType is not None:
                                    if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                        return True

def EmissionMode(PBSDF, material):
                
        if bpy.context.scene.world_properties.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or MaterialIn(Emissive_Materials, material)):
            return 1

        if bpy.context.scene.world_properties.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if bpy.context.scene.world_properties.emissiondetection == 'Manual' and MaterialIn(Emissive_Materials, material):
            return 3

def upgrade_materials():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            slot += 1
            for i, material in enumerate(selected_object.data.materials):
                if material is not None:
                    for original_material, upgraded_material in Materials_Array.items():
                        for material_part in material.name.lower().replace("-", ".").split("."):
                            if original_material == material_part:
                                if upgraded_material not in bpy.data.materials:
                                    try:
                                        with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                            data_to.materials = [upgraded_material]
                                    except:
                                        CEH('004')

                                    appended_material = bpy.data.materials.get(upgraded_material)
                                    selected_object.data.materials[i] = appended_material
                                else:
                                    selected_object.data.materials[i] = bpy.data.materials[upgraded_material]

                                selected_object.data.update()
                else:
                    CEH('m002', slot)
        else:
            CEH('m003', Data=selected_object)

# Fix World
                        
def fix_world():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    PBSDF = None
                    image_texture_node = None
                    scene = bpy.context.scene
                    WProperties = scene.world_properties

                    if MaterialIn(Alpha_Blend_Materials, material):
                        material.blend_method = 'BLEND'
                    else:
                        material.blend_method = 'HASHED'
                    
                    material.shadow_method = 'HASHED'

                    if WProperties.delete_useless_textures:
                        for node in material.node_tree.nodes:
                            if node.type == "TEX_IMAGE" and ".00" in node.name:
                                material.node_tree.nodes.remove(node)

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node
                            image_texture_node.interpolation = "Closest"

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                                
                    if (image_texture_node and PBSDF) != None:
                        if not IsConnectedTo(None, None, None, None, "Alpha", PBSDF):
                            material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])
                        
                        # Emission
                        if EmissionMode(PBSDF, material):
                            if blender_version("4.x.x"):
                                if not IsConnectedTo(None, None, None, None, "Emission Color", PBSDF):
                                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission Color"])
                            else:
                                if not IsConnectedTo(None, None, None, None, "Emission", PBSDF):
                                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission"])

                            if (EmissionMode(PBSDF, material) == 1 or EmissionMode(PBSDF, material) == 3) and PBSDF.inputs["Emission Strength"].default_value == 0:
                                PBSDF.inputs["Emission Strength"].default_value = 1

                        # Backface Culling
                        if WProperties.backface_culling:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                material.use_backface_culling = True
                                
                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:
                                            bfc_node = node
                                            break
                                
                                if bfc_node == None:
                                    if "Backface Culling" not in bpy.data.node_groups:
                                        try:
                                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["Backface Culling"]
                                        except:
                                            CEH("004")
                                    
                                    bfc_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    bfc_node.node_tree = bpy.data.node_groups["Backface Culling"]
                                    bfc_node.location = (PBSDF.location.x - 170, PBSDF.location.y - 110)

                                material.node_tree.links.new(image_texture_node.outputs[1], bfc_node.inputs[0])

                                for node in material.node_tree.nodes:
                                    if node.type == "BSDF_PRINCIPLED":
                                        for link in node.inputs["Alpha"].links:                                            
                                            if link.from_node.name != bfc_node.name:                                                
                                                for output in link.from_node.outputs:
                                                    for link_out in output.links:
                                                        if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                            material.node_tree.links.new(link_out.from_socket, bfc_node.inputs[0]) 
                                                            break
                            
                                material.node_tree.links.new(bfc_node.outputs[0], PBSDF.inputs["Alpha"])
                        else:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:                                            
                                            for link in node.inputs[0].links:     
                                                for output in link.from_node.outputs:
                                                    for link_out in output.links:
                                                        if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                            material.node_tree.links.new(link_out.from_socket, PBSDF.inputs["Alpha"])
                                            material.node_tree.nodes.remove(node)

                                material.use_backface_culling = False

                        selected_object.data.update()
                else:
                    CEH('m002', slot)
        else:
            CEH('m003', Data=selected_object)

def create_env(self=None):
    scene = bpy.context.scene
    world = scene.world
    clouds_exists = False
    sky_exists = False

    if (any(node.name == clouds_node_tree_name for node in bpy.data.node_groups)):
        clouds_exists = True

    if world != None and (any(node.name == "Mcblend Sky" for node in bpy.data.node_groups)):
        if world_material_name in bpy.data.worlds:
            sky_exists = True
    
    if clouds_exists == True or sky_exists == True:

        # Recreate Sky
        if self != None:

            if self.reset_settings == True:
                world_material = bpy.context.scene.world.node_tree

                for node in world_material.nodes:
                    if node.type == 'GROUP':
                        if "Mcblend Sky" in node.node_tree.name:
                            if blender_version("4.x.x"):
                                for group in bpy.data.node_groups:
                                    if node.node_tree.name in group.name:
                                        node.inputs["Time"].default_value = group.interface.items_tree["Time"].default_value
                                        node.inputs["Rotation"].default_value[0] = group.interface.items_tree["Rotation"].default_value[0]
                                        node.inputs["Rotation"].default_value[1] = group.interface.items_tree["Rotation"].default_value[1]
                                        node.inputs["Rotation"].default_value[2] = group.interface.items_tree["Rotation"].default_value[2]
                                        node.inputs["Pixelated Stars"].default_value = group.interface.items_tree["Pixelated Stars"].default_value
                                        node.inputs["Stars Amount"].default_value = group.interface.items_tree["Stars Amount"].default_value
                                        node.inputs["Rain"].default_value = group.interface.items_tree["Rain"].default_value
                                        node.inputs["End"].default_value = group.interface.items_tree["End"].default_value
                                        node.inputs["End Stars Rotation"].default_value[0] = group.interface.items_tree["End Stars Rotation"].default_value[0]
                                        node.inputs["End Stars Rotation"].default_value[1] = group.interface.items_tree["End Stars Rotation"].default_value[1]
                                        node.inputs["End Stars Rotation"].default_value[2] = group.interface.items_tree["End Stars Rotation"].default_value[2]
                                        node.inputs["End Stars Strength"].default_value = group.interface.items_tree["End Stars Strength"].default_value
                                        node.inputs["End Stars Color"].default_value  = group.interface.items_tree["End Stars Color"].default_value
                                        node.inputs["Moon Strenght"].default_value = group.interface.items_tree["Moon Strenght"].default_value
                                        node.inputs["Sun Strength"].default_value = group.interface.items_tree["Sun Strength"].default_value
                                        node.inputs["Stars Strength"].default_value = group.interface.items_tree["Stars Strength"].default_value
                                        node.inputs["Camera Ambient Light Strength"].default_value = group.interface.items_tree["Camera Ambient Light Strength"].default_value
                                        node.inputs["Non-Camera Ambient Light Strength"].default_value = group.interface.items_tree["Non-Camera Ambient Light Strength"].default_value
                                        node.inputs["Moon Color"].default_value = group.interface.items_tree["Moon Color"].default_value
                                        node.inputs["Sun Color"].default_value = group.interface.items_tree["Sun Color"].default_value
                                        node.inputs["Sun Color In Sunset"].default_value = group.interface.items_tree["Sun Color In Sunset"].default_value
                                        node.inputs["Stars Color"].default_value  = group.interface.items_tree["Stars Color"].default_value
                            else:
                                for group in bpy.data.node_groups:
                                    if node.node_tree.name in group.name:
                                        node.inputs["Time"].default_value = group.inputs["Time"].default_value
                                        node.inputs["Rotation"].default_value[0] = group.inputs["Rotation"].default_value[0]
                                        node.inputs["Rotation"].default_value[1] = group.inputs["Rotation"].default_value[1]
                                        node.inputs["Rotation"].default_value[2] = group.inputs["Rotation"].default_value[2]
                                        node.inputs["Pixelated Stars"].default_value = group.inputs["Pixelated Stars"].default_value
                                        node.inputs["Stars Amount"].default_value = group.inputs["Stars Amount"].default_value
                                        node.inputs["Rain"].default_value = group.inputs["Rain"].default_value
                                        node.inputs["End"].default_value = group.inputs["End"].default_value
                                        node.inputs["End Stars Rotation"].default_value[0] = group.inputs["End Stars Rotation"].default_value[0]
                                        node.inputs["End Stars Rotation"].default_value[1] = group.inputs["End Stars Rotation"].default_value[1]
                                        node.inputs["End Stars Rotation"].default_value[2] = group.inputs["End Stars Rotation"].default_value[2]
                                        node.inputs["End Stars Strength"].default_value = group.inputs["End Stars Strength"].default_value
                                        node.inputs["End Stars Color"].default_value  = group.inputs["End Stars Color"].default_value
                                        node.inputs["Moon Strenght"].default_value = group.inputs["Moon Strenght"].default_value
                                        node.inputs["Sun Strength"].default_value = group.inputs["Sun Strength"].default_value
                                        node.inputs["Stars Strength"].default_value = group.inputs["Stars Strength"].default_value
                                        node.inputs["Camera Ambient Light Strength"].default_value = group.inputs["Camera Ambient Light Strength"].default_value
                                        node.inputs["Non-Camera Ambient Light Strength"].default_value = group.inputs["Non-Camera Ambient Light Strength"].default_value
                                        node.inputs["Moon Color"].default_value = group.inputs["Moon Color"].default_value
                                        node.inputs["Sun Color"].default_value = group.inputs["Sun Color"].default_value
                                        node.inputs["Sun Color In Sunset"].default_value = group.inputs["Sun Color In Sunset"].default_value
                                        node.inputs["Stars Color"].default_value  = group.inputs["Stars Color"].default_value

            if self.create_sky == 'Recreate Sky':
                if world == bpy.data.worlds.get(world_material_name):

                    bpy.data.worlds.remove(bpy.data.worlds.get(world_material_name), do_unlink=True)
                
                for group in bpy.data.node_groups:
                    if "Mcblend" in group.name:
                        bpy.data.node_groups.remove(group)

                try:
                    with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                    bpy.context.scene.world = appended_world_material
                except:
                    CEH('004')

            if self.create_sky == 'Create Sky':

                if world_material_name in bpy.data.worlds:
                    bpy.context.scene.world = bpy.data.worlds.get(world_material_name)
                else:
                    print("World not found (Create Sky)")

            if self.create_clouds == 'Recreate Clouds':
                for obj in scene.objects:
                    if obj.get("Mcblend ID") == "Clouds":
                        bpy.data.objects.remove(obj, do_unlink=True)

                if clouds_node_tree_name in bpy.data.node_groups:
                    bpy.data.node_groups.remove(bpy.data.node_groups.get(clouds_node_tree_name))

                if "Clouds" in bpy.data.materials:
                    bpy.data.materials.remove(bpy.data.materials.get("Clouds"))
                
                if blender_version("4.x.x"):
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]

                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]

                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]

                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

                bpy.context.object["Mcblend ID"] = "Clouds"
            
            clouds_exists = False
            
            if self.create_clouds == 'Create Clouds':

                if clouds_node_tree_name in bpy.data.node_groups:
                    bpy.data.node_groups[clouds_node_tree_name]
                else:
                    print("Clouds geometry nodes not found (Create Clouds)")
                
                if "Clouds" in bpy.data.materials:
                    bpy.data.materials["Clouds"]
                else:
                    print("Clouds material not found (Create Clouds)")

                for obj in scene.objects:
                    if obj.get("Mcblend ID") == "Clouds":
                        clouds_exists =True

                if clouds_exists == False:
                    bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                    bpy.context.object.name = "Clouds"
                    bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                    geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                    geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

                    bpy.context.object["Mcblend ID"] = "Clouds"
        else:
            bpy.ops.wm.recreate_env('INVOKE_DEFAULT')

    else:
        
        # Create Sky
        if scene.env_properties.create_sky:
            try:
                if world_material_name not in bpy.data.worlds:
                    with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                else:
                    appended_world_material = bpy.data.worlds[world_material_name]
                bpy.context.scene.world = appended_world_material
            except:
                CEH("004")

        for obj in scene.objects:
            if obj.get("Mcblend ID") == "Clouds":
                clouds_exists = True

        if scene.env_properties.create_clouds and clouds_exists == False:               
            if blender_version("4.x.x"):     
                if clouds_node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]
                else:
                    bpy.data.node_groups[clouds_node_tree_name]
                
                if "Clouds" not in bpy.data.materials:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    bpy.data.materials["Clouds"]
            else:
                if clouds_node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]
                else:
                    bpy.data.node_groups[clouds_node_tree_name]
                
                if "Clouds" not in bpy.data.materials:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    bpy.data.materials["Clouds"]

            bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
            bpy.context.object.name = "Clouds"
            bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            bpy.context.object["Mcblend ID"] = "Clouds"
            

    bpy.context.view_layer.update()

# Fix materials
    
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    image_texture_node = None
                    PBSDF = None

                    material.blend_method = 'HASHED'
                    material.shadow_method = 'HASHED'

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node
                            node.interpolation = "Closest" 
                        
                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if (image_texture_node and PBSDF) != None:
                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])
                else:
                    CEH('m002', slot)
        else:
            CEH('m003', selected_object)
            
        selected_object.data.update()
#
        
# Set Procedural PBR
        
def setproceduralpbr():
    for selected_object in bpy.context.selected_objects:
        counter = -1
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    image_texture_node = None
                    PBSDF = None
                    bump_node = None
                    PNormals = None
                    image_difference_X = 1
                    image_difference_Y = 1
                    PNormals_exists = False
                    Current_node_tree = None
                    scene = bpy.context.scene
                    PProperties = scene.ppbr_properties

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node

                        if node.type == "BUMP":
                            bump_node = node

                        if node.type == "GROUP":
                            if "PNormals" in node.node_tree.name:
                                PNormals = node
                                Current_node_tree = node.node_tree

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if PBSDF is not None:
                        if image_texture_node is not None:
                            # Use Normals
                            if PProperties.use_normals:

                                if PProperties.normals_selector == 'Bump':
                                    if PNormals is not None:
                                        material.node_tree.nodes.remove(PNormals)

                                    if image_texture_node and bump_node is None:
                                        bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                                        bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                                        material.node_tree.links.new(image_texture_node.outputs["Color"], bump_node.inputs['Height'])
                                        material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                                        bump_node.inputs[0].default_value = PProperties.bump_strength

                                    if bump_node is not None:
                                        bump_node.inputs[0].default_value = PProperties.bump_strength
                                else:
                                    if bump_node is not None:
                                        material.node_tree.nodes.remove(bump_node)
                                    
                                    if PNormals is None:
                                        if f"PNormals; {material.name}" in bpy.data.node_groups:
                                            PNormals_exists = True
                                            Current_node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                        
                                        if PNormals_exists == False:
                                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["PNormals"]

                                            counter += 1

                                            PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')

                                            try:
                                                bpy.data.node_groups[f"PNormals.{counter}"].name = f"PNormals; {material.name}"
                                                PNormals.node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                                for node in PNormals.node_tree.nodes:
                                                    if node.type == "TEX_IMAGE":
                                                        node.image = image_texture_node.image
                                            except:
                                                bpy.data.node_groups[f"PNormals"].name = f"PNormals; {material.name}"
                                                PNormals.node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                                for node in PNormals.node_tree.nodes:
                                                    if node.type == "TEX_IMAGE":
                                                        node.image = image_texture_node.image

                                            PNormals.location = (PBSDF.location.x - 200, PBSDF.location.y - 132)

                                        else:
                                            PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                            PNormals.node_tree = Current_node_tree
                                            PNormals.location = (PBSDF.location.x - 200, PBSDF.location.y - 132)
                                            for node in bpy.data.node_groups[Current_node_tree.name].nodes:
                                                if node.type == "TEX_IMAGE":
                                                    node.image = image_texture_node.image

                                    else:
                                        for node in bpy.data.node_groups[Current_node_tree.name].nodes:
                                            if node.type == "TEX_IMAGE":
                                                node.image = image_texture_node.image
                                    

                                    if image_texture_node.image.size[0] > image_texture_node.image.size[1]:
                                        image_difference_X = image_texture_node.image.size[1] / image_texture_node.image.size[0]

                                    if image_texture_node.image.size[0] < image_texture_node.image.size[1]:
                                        image_difference_Y = image_texture_node.image.size[0] / image_texture_node.image.size[1]

                                    PNormals.inputs["Size"].default_value = PProperties.pnormals_size
                                    PNormals.inputs["Blur"].default_value = PProperties.pnormals_blur
                                    PNormals.inputs["Strength"].default_value = PProperties.pnormals_strength
                                    PNormals.inputs["Exclude"].default_value = PProperties.pnormals_exclude
                                    PNormals.inputs["Min"].default_value = PProperties.pnormals_min
                                    PNormals.inputs["Max"].default_value = PProperties.pnormals_max
                                    PNormals.inputs["Size X Multiplier"].default_value = PProperties.pnormals_size_x_multiplier * image_difference_X
                                    PNormals.inputs["Size Y Multiplier"].default_value = PProperties.pnormals_size_y_multiplier * image_difference_Y

                                    material.node_tree.links.new(PNormals.outputs['Normal'], PBSDF.inputs['Normal'])
                            else:
                                
                                if bump_node is not None:
                                    material.node_tree.nodes.remove(bump_node)
                                
                                if PNormals is not None:
                                    material.node_tree.nodes.remove(PNormals)

                                
                        # Change PBSDF Settings                                
                        if PProperties.change_bsdf:
                            PBSDF.inputs["Roughness"].default_value = PProperties.roughness
                            if blender_version("4.x.x"):
                                PBSDF.inputs["Specular IOR Level"].default_value = PProperties.specular
                            else:
                                PBSDF.inputs["Specular"].default_value = PProperties.specular


                        # Use SSS                            
                        if PProperties.use_sss  == True:
                            if MaterialIn(SSS_Materials, material):
                                PBSDF.subsurface_method = PProperties.sss_type

                                if PProperties.connect_texture:
                                    for node in material.node_tree.nodes:
                                        if node.type == "BSDF_PRINCIPLED":
                                            for link in node.inputs[0].links:
                                                if blender_version("4.x.x"):
                                                    material.node_tree.links.new(link.from_socket, PBSDF.inputs['Subsurface Radius'])
                                                else:
                                                    material.node_tree.links.new(link.from_socket, PBSDF.inputs['Subsurface Color'])
                                else:
                                    for link in material.node_tree.links:
                                        if blender_version("4.x.x"):
                                            if link.to_socket == PBSDF.inputs["Subsurface Radius"]:
                                                material.node_tree.links.remove(link)
                                        else:
                                            if link.to_socket == PBSDF.inputs["Subsurface Color"]:
                                                material.node_tree.links.remove(link)

                                
                                if blender_version("4.x.x"):
                                    PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                                    PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale
                                else:
                                    PBSDF.inputs["Subsurface"].default_value = PProperties.sss_weight

                                PBSDF.inputs["Subsurface Radius"].default_value[0] = 1.0
                                PBSDF.inputs["Subsurface Radius"].default_value[1] = 1.0
                                PBSDF.inputs["Subsurface Radius"].default_value[2] = 1.0
                        else:
                            if blender_version("4.x.x"):
                                PBSDF.inputs["Subsurface Weight"].default_value = 0
                            else:
                                PBSDF.inputs["Subsurface"].default_value = 0


                        # Make Metals                            
                        if PProperties.make_metal == True and MaterialIn(Metal, material):
                            PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic
                            PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness

                            
                        # Make Reflections                            
                        if PProperties.make_reflections == True and MaterialIn(Reflective, material):
                            PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness


                        # Make Better Emission and Animate Textures                            
                        if (PProperties.make_better_emission == True or PProperties.animate_textures == True) and EmissionMode(PBSDF, material):
                            image_texture_node = None
                            node_group = None
                            
                            # Texture Check
                            for node in material.node_tree.nodes:
                                if node.type == "TEX_IMAGE":
                                    if ".00" not in node.name:
                                        image_texture_node = node

                            # The Main Thing
                            if image_texture_node != None:

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if BATGroup in node.node_tree.name:
                                            node_group = node
                                            break

                                # BATGroup Import if BATGroup isn't in File
                                if node_group == None:
                                    if BATGroup not in bpy.data.node_groups:
                                        with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                            data_to.node_groups = [BATGroup]

                                    node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    node_group.node_tree = bpy.data.node_groups[BATGroup]

                                # Settings Set
                                if MaterialIn(Emissive_Materials, material) == True:
                                    for material_part in material.name.lower().replace("-", ".").split("."):
                                        for material_name, material_properties in Emissive_Materials.items():
                                            if material_name == material_part:
                                                for property_name, property_value in material_properties.items():
                                                    if property_name == "Divider":
                                                        node_group.inputs[property_name].default_value = property_value * bpy.context.scene.render.fps/30
                                                    else:
                                                        node_group.inputs[property_name].default_value = property_value

                                                node_group.inputs["Better Emission"].default_value = PProperties.make_better_emission

                                                if "Middle Value" in material_properties and 11 in material_properties and 12 in material_properties and "Adder" in material_properties and "Divider" in material_properties:
                                                    node_group.inputs["Animate Textures"].default_value = PProperties.animate_textures
                                else:
                                    for material_name, material_properties in Emissive_Materials.items():
                                        if material_name == "Default":
                                            for property_name, property_value in material_properties.items():
                                                if property_name == "Divider":
                                                    node_group.inputs[property_name].default_value = property_value * bpy.context.scene.render.fps/30
                                                else:
                                                    node_group.inputs[property_name].default_value = property_value

                                            node_group.inputs["Better Emission"].default_value = PProperties.make_better_emission
                                            node_group.inputs["Animate Textures"].default_value = PProperties.animate_textures
                                
                                # Color Connection if Nothing Connected
                                if blender_version("4.x.x"):
                                    if not IsConnectedTo(None, None, None, "BSDF_PRINCIPLED", "Emission Color"):
                                        material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs["Emission Color"])
                                else:
                                    if not IsConnectedTo(None, None, None, "BSDF_PRINCIPLED", "Emission"):
                                        material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs["Emission"])
                                    
                                for node in material.node_tree.nodes:
                                    if node.type == "BSDF_PRINCIPLED":
                                        for link in node.inputs["Emission Strength"].links:
                                            if link.from_node != node_group:
                                                for output in link.from_node.outputs:
                                                    for link in output.links:
                                                        if link.to_socket.node.name == node.name:
                                                            material.node_tree.links.new(link.from_socket, node_group.inputs["Multiply"])

                                node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 250)
                                if blender_version("4.x.x"):
                                    material.node_tree.links.new(image_texture_node.outputs[0], node_group.inputs["Emission Color"])
                                else:
                                    material.node_tree.links.new(image_texture_node.outputs[0], node_group.inputs["Emission Color"])
                                material.node_tree.links.new(node_group.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])

                        if PProperties.make_better_emission == False and PProperties.animate_textures == False:
                            for node in material.node_tree.nodes:
                                if node.type == 'GROUP':
                                    if BATGroup in node.node_tree.name:
                                        material.node_tree.nodes.remove(node)
                else:
                    CEH('m002', slot)
                
        else:
            CEH('m003', Data=selected_object)
            
        selected_object.data.update()
#
        
# TODO:
    # Upgrade World - Сделать так чтобы выбирались определённые фейсы у мира > они отделялись от него в отдельный объект > Как-то группировались > Производилась замена этих объектов на риги (Сундук)
    # Texture logic - Сделать использование текстур из папки, например из папки tex или из папки майнкрафта
    # Upgrade World - Сщединённое стекло: Импортировать текстуры соединённого > Выбираются фейсы с материалом стекла > Математически вычислить находятся ли стёкла рядом (if Glass.location.x + 1: поставить сообтветствующую текстуру стекла)