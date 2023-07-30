# houseLayoutIndex = 103

from maya import *
from controller import MayaController
from param import args

import time

if __name__ == "__main__":
    # Connect Maya
    # import maya.cmds as cmds
    # cmds.commandPort(n="localhost:12345")
    print("start: ")
    mc = MayaController(PORT=12345)
    mc.SendPythonCommand("from maya.api import OpenMaya")
    print("mc: ")

    shapeLocalSource = "E://Temp/3Dfront/3D-FUTURE-model/"
    houseLayoutSource = "E://Temp/3Dfront/3D-FRONT/"
    allHouseLayouts = os.listdir(houseLayoutSource)

    IN_METER = False

    ### Load room layout json
    for houseLayoutIndex in range(1, 20):
        ### Set new scene
        mc.SetNewScene()

        print("houseLayoutIndex: ", houseLayoutIndex)
        houseLayoutFile = os.path.join(houseLayoutSource, allHouseLayouts[houseLayoutIndex])
        with open(houseLayoutFile) as f: sceneDict = json.load(f)
        
        ### Extract info
        instance_table = create_instance_table(sceneDict)
        mesh_table = create_mesh_table(sceneDict)
        material_table = create_material_table(sceneDict)
        furniture_table = create_furniture_table(sceneDict)

        ### Join information tables
        mesh_material = join(mesh_table, material_table, 'material_id', 'id', 'material_')
        mesh_all = join(mesh_material, instance_table, 'id', 'ref', 'instance_')
        furniture_all = join(furniture_table, instance_table, 'id', 'ref', 'instance_')

        furniture_list = list(zip(furniture_all['jid'], furniture_all['position'], furniture_all['rotation'], furniture_all['scale']))

        # create an empty group node with no children
        mc.SendPythonCommand("cmds.group( em=True, name='structure')")
        mc.SendPythonCommand("cmds.group( em=True, name='ceilings')")
        mc.SendPythonCommand("cmds.group( em=True, name='floors')")
        mc.SendPythonCommand("cmds.group( em=True, name='windows')")
        mc.SendPythonCommand("cmds.group( em=True, name='doors')")
        
        # create room structure
        merge_list = []
        for index, mesh in enumerate(zip(mesh_all['id'], mesh_all['type'], mesh_all['xyz'], 
                                            mesh_all['normal'], mesh_all['uv'], mesh_all['face'], mesh_all['color'])):             
            
            # Select the current set of objects
            mc.SendPythonCommand('cmds.select(all = True, hierarchy = True)')
            mc.SendPythonCommand('currentObjs = cmds.ls(selection = True )')

            id_, type_, xyz, normal, uv, face, color = mesh
            xyz = np.array(xyz.tolist()).astype(np.float)
            normal = np.array(normal.tolist()).astype(np.float)
            uv = np.array(uv.tolist()).astype(np.float)
            face = np.array(face.tolist()).astype(np.int)

            vertices = xyz.T.tolist()
            faces = face.T.tolist()
            
            vertices, faces = fix_vertices_and_faces(vertices, faces)
            # print(vertices,faces)
            
            mc.SendPythonCommand("meshFn = OpenMaya.MFnMesh()")
            
        #     time.sleep(0.1)

            code_multiLine = """
vertices = []
polygonFaces = []
polygonConnects = [] 
# print(vertices)
            """.replace("\n",r"\n")  

            message = 'python("{}")'.format(code_multiLine)
            mc.SendCommand(message)

        #     time.sleep(0.1)

            for v in vertices:
                x,y,z = v
                code_multiLine = f"""vertices.append(OpenMaya.MPoint({x}, {y}, {z}))""".replace("\n",r"\n")  
                #print(code_multiLine)
                message = 'python("{}")'.format(code_multiLine)
                mc.SendCommand(message)

            for f in faces:
                code_multiLine = f"""polygonFaces.append({len(f)})"""
                #code_multiLine = f"""polygonConnects += {f}"""
                # print(code_multiLine)
                message = 'python("{}")'.format(code_multiLine)
                mc.SendCommand(message)

            for f in faces:
                # code_multiLine = f"""polygonFaces.append({len(f)})"""
                code_multiLine = f"""polygonConnects += {f}"""
                # print(code_multiLine)
                message = 'python("{}")'.format(code_multiLine)
                mc.SendCommand(message)

            # Select and rename the newly added mesh
            mc.SendPythonCommand("meshFn.create(vertices, polygonFaces, polygonConnects)")
            mc.SendPythonCommand(f"cmds.sets(meshFn.name(), edit=True, forceElement=\\'initialShadingGroup\\')")

            #mc.SendPythonCommand('cmds.select(all = True)')
            #mc.SendPythonCommand('cmds.select(currentObjs, deselect = True)')
            #mc.SendPythonCommand('newObjs = cmds.ls(selection = True, transforms = True )')
            mc.SendPythonCommand("show_name = cmds.listRelatives(meshFn.name(), fullPath=True, parent=True)[0]")
            mc.SendPythonCommand(f"cmds.rename(show_name,'{type_}_{index}')")
            
            # Project UV
            # Hide object if it is a ceiling
            if "Ceiling" in type_:
                mc.SendPythonCommand(f"cmds.polyProjection('{type_}_{index}.f[0:]', type='Planar', md='y' )")
                mc.SendPythonCommand(f"cmds.parent( '{type_}_{index}', 'ceilings' )")
                mc.SendPythonCommand("cmds.hide()")
            elif "Floor" in type_:
                mc.SendPythonCommand(f"cmds.polyProjection('{type_}_{index}.f[0:]', type='Planar', md='y' )")
                mc.SendPythonCommand(f"cmds.parent( '{type_}_{index}', 'floors' )")
            elif "Window" in type_:
                mc.SendPythonCommand(f"cmds.parent( '{type_}_{index}', 'windows' )")
            else:
                mc.SendPythonCommand(f"cmds.polyProjection('{type_}_{index}.f[0:]', type='cylindrical')")
                mc.SendPythonCommand(f"cmds.parent( '{type_}_{index}', 'structure' )")
                merge_list.append(f'{type_}_{index}')
            # break

        # create furniture and lights group
        mc.SendPythonCommand("cmds.group( em=True, name='furniture')")
        mc.SendPythonCommand("cmds.group( em=True, name='lights')")     

        for index, furniture in enumerate(zip(furniture_all['id'], furniture_all['jid'], furniture_all['position'], furniture_all['rotation'], furniture_all['scale'])):
        
            fid, jid, position, rotation, scale = furniture
            raw_model_path = os.path.join(shapeLocalSource, jid, 'raw_model.obj').replace("\\","/")
            texture_path = os.path.join(shapeLocalSource, jid, 'texture.png').replace("\\","/")
        #     print(raw_model_path, os.path.exists(raw_model_path))
        #     print(texture_path, os.path.exists(texture_path))
            
        #     if scale[0] == 1:
        #         #print(fid, jid, position, rotation, scale)
        #         continue
            
            if  os.path.exists(raw_model_path) and os.path.exists(texture_path):
                fid = fid.split("/")[0]
                
                # If y position > 1, we see this as a light
                if position[1] > 1:
                    mc.SendPythonCommand(f"cmds.pointLight(position=[{position[0]},{position[1]},{position[2]}], name = 'light_{fid}', intensity=20)")
                    mc.SendPythonCommand(f"cmds.parent( 'light_{fid}', 'lights' )")
                    
                # print(fid)
                mc.SendPythonCommand(f"cmds.file('{raw_model_path}', i=True, gr=True, gn='furniture_group', mergeNamespacesOnClash=True, namespace='component_{fid}')")
                mc.SetObjectWorldTransform('furniture_group', position)
                # print("rotation: ", euler_from_quaternion(*rotation), rotation)
                mc.SetObjectLocalRotation('furniture_group',np.rad2deg(euler_from_quaternion(*rotation)))
                #mc.SetObjectAttribute("furniture_group", "scaleX", )
                
                # print("scale", scale)
                mc.SetObjectAttribute("furniture_group", "scaleX", scale[0])
                mc.SetObjectAttribute("furniture_group", "scaleY", scale[1])
                mc.SetObjectAttribute("furniture_group", "scaleZ", scale[2])

                mc.SendCommand("polyTriangulate -ch 1 furniture_group")
                mc.SendCommand("select -r furniture_group")
                mc.SendCommand("DeleteHistory;")
                
                mc.SendPythonCommand(f"cmds.parent( 'furniture_group', 'furniture' )")
                mc.SendPythonCommand(f"cmds.rename('furniture_group', 'furniture_{fid}')") 
   
            
        # scale 100 times
        mc.SendPythonCommand(f"cmds.scale(100, 100, 100, ['furniture','lights','structure','ceilings', 'floors', 'windows', 'doors'])")

        # merge room structure
        merge_command = "polyUnite -ch 1 -mergeUVSets 1 -centerPivot -name roomStruct "

        for poly_surface in merge_list:
            merge_command += poly_surface + " "

        merge_command += ";"

        # merge and triangulate
        mc.SendCommand(merge_command)
        mc.SendCommand("polyTriangulate -ch 1 roomStruct")
        mc.SendCommand("DeleteHistory;")

        mc.SendCommand("polyTriangulate -ch 1 floors")
        mc.SendCommand("select -r floors")
        mc.SendCommand("DeleteHistory;")

        # Export to omniverse
        code_multiLine = f"""
folder = OmniTC_BaseFolder + '/{str(houseLayoutIndex)}'
OmniTC_MakeFolderExistAndClean(folder)
OmniTC_MakeSureConnected()
fn = folder + '/layout.usd'
    """.replace("\n",r"\n")  

        mc.SendPythonCommand(code_multiLine)
        mc.SendCommand('optionVar -iv "omniverse_export_split_files" 0;')
        mc.SendPythonCommand('cmds.OmniExportCmd(f=fn)')

        time.sleep(10)