import bpy, bmesh
import struct
#obj = bpy.context.active_object

"""
HEY USER:
Run this script in the blender scripting tool with the following steps:

1. Import your original GNO file into a collection named whatever OG_OBJ_COLLECTION_NAME is set to in the script here ('Collection' by default)
2. Make a second collection named whatever NEW_OBJ_COLLECTION_NAME is set to in the script here ('Collection 2' by default)
3. For every mesh you want to change, make a copy of the mesh from the original, place it in the new collection, and make sure the armature is removed after copying it
4. For export, make sure to select both the original meshes from the first collection and the changed meshes all at once before running the script
5. Running the script creates a new GNO file (same name as original GNO + "_out") in the directory the original GNO was imported from. This is your newly edited stage file.
"""

# REMINDERS:

# 1. Make sure that ALL OG objects AND NEW objects are selected and placed in their respective collections
# 2. Make sure that your collection names are set up properly
# 3. Overwrite the PATH_TO_OG_GNO with the original GNO path
# 4. Make sure the new object names are the same as the originals, plus the '.001' at the end

# FOR USERS: 
# OVERWRITE THIS WITH THE PATH TO THE GNO YOU IMPORTED TO BLENDER
# MAKE SURE TO USE DOUBLE SLASHES FOR PATHS, the path import does not work very well
PATH_TO_OG_GNO = "C:\\Users\\XXX\\Downloads\\test\\NightTests\\Unnamed_File_5.gno"


# DEPRECIATED: GNO now only saves in the original directory, unless this is reimplemented by you, the user
# FOR USERS:
# OVERWRITE THIS WITH WHERE YOU WANT YOUR GNO TO SAVE TO
# SAVE_PATH = "C:\\Users\\XXX\\Downloads\\test\\NightTests\\VertData\\"


# FOR USERS:
# OVERWRITE THIS WITH THE NAME OF THE COLLECTION THAT CONTAINS YOUR ORIGINAL GNO MESHES
OG_OBJ_COLLECTION_NAME = 'Collection'


# FOR USERS:
# OVERWRITE THIS WITH THE NAME OF THE COLLECTION THAT WILL CONTAIN YOUR NEW MESHES THAT WILL REPLACE THE OLD ONES
NEW_OBJ_COLLECTION_NAME = 'Collection 2'


# Step 1.
# Get ALL selected meshes from OG file collection

def save_OG_obj_data():
    if OG_OBJ_COLLECTION_NAME not in bpy.data.collections:
        print("No OG object collection found! Please ensure that OG_OBJ_COLLECTION_NAME exists in your hierarchy window, or change the value of this variable to match your new object collection name.")
        return False
    
    og_obj_vert_dict = {}
    
    for obj in bpy.context.selected_objects:
        # Add all the vertex pos data of these objects to a DS
        if obj.users_collection[0].name != OG_OBJ_COLLECTION_NAME:
            continue
        
        if obj.mode == 'EDIT':
            # this works only in edit mode,
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [vert.co for vert in bm.verts]
        else:
            # this works only in object mode,
            verts = [vert.co for vert in obj.data.vertices]

        # coordinates as tuples
        plain_verts = [vert.to_tuple() for vert in verts]
        # print(plain_verts)
        
        # Write these coordinates to a dict, using the name of the mesh as a key
        og_obj_vert_dict[obj.name] = plain_verts
        
    print(og_obj_vert_dict)
    return og_obj_vert_dict


# Step 2.
# Get ALL selected meshes from NEW file collection
# Ensure these meshes have the same vertex count, otherwise we will have an issue with the final file

def save_NEW_obj_data():
    if NEW_OBJ_COLLECTION_NAME not in bpy.data.collections:
        print("No new object collection found! Please ensure that NEW_OBJ_COLLECTION_NAME exists in your hierarchy window, or change the value of this variable to match your new object collection name.")
        return

    new_obj_vert_dict = {}

    for obj in bpy.context.selected_objects:
        # Add all the vertex pos data of these objects to a DS
        if obj.users_collection[0].name != NEW_OBJ_COLLECTION_NAME:
            continue
        if obj.mode == 'EDIT':
            # this works only in edit mode,
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [vert.co for vert in bm.verts]
        else:
            # this works only in object mode,
            verts = [vert.co for vert in obj.data.vertices]

        # coordinates as tuples
        plain_verts = [vert.to_tuple() for vert in verts]
        # print(plain_verts)
        
        # Write these coordinates to a dict, using the name of the mesh as a key
        # ENSURE THAT THESE MESH NAMES ARE THE SAME AS THE ORIGINALS + AN IDENTIFIER
        new_obj_vert_dict[obj.name] = plain_verts
    
    return new_obj_vert_dict
    

# Step 3.
# Save a copy of the OG GNO

def save_GNO_copy():
    # Save a copy of the input GNO here first, for security
    with open(PATH_TO_OG_GNO, "rb") as input_file:
        # Opens and reads a copy of the file for safety, we don't wanna overwrite our original for preservation's sake
        copy_of_gno = input_file.read()
        return copy_of_gno


# Step 4.
# Using the vertex data of the original file, find the start of the mesh in the given GNO, then replace the data

def search_and_destroy(OG_mesh_dict, NEW_mesh_dict, og_gno_data):
    
    # Create a new output file
    
    new_GNO_name = PATH_TO_OG_GNO.removesuffix(".GNO")
    new_GNO_name = PATH_TO_OG_GNO.removesuffix(".gno")
    new_GNO_name = new_GNO_name + "_out.gno"
    
    with open(new_GNO_name, "wb+") as output_file:
        
        output_file.write(og_gno_data)
        
        # Start by searching our file for the first vertex in our OG_mesh's mesh
        
        for name, vert_list in OG_mesh_dict.items():
            print("Searching for: " + str(name))
            
            first_coord = struct.pack(">fff", vert_list[0][0], vert_list[0][1], vert_list[0][2])
            print(first_coord.hex())
            first_coord_found = og_gno_data.find(first_coord)
            print(first_coord_found)
        
            if first_coord:
                # If all three were found successfully and matched, mesh data starts at x_coord data
                print("Start of mesh found: " + str(hex(first_coord_found)))
            else:
                # else if we don't find this first point, move onto the next mesh
                continue
        
        # Once file seeked out, time to destroy (replace) with new data
        
        # Use name to successfully find which mesh to replace this with
        
            new_mesh_key_name = str(name) + ".001" # We assume all object dupes have this suffix name, as blender applies this usually.
            current_new_obj = NEW_mesh_dict[new_mesh_key_name]
            
            print("Vertex count in curr_new_obj: " + str(len(current_new_obj)))
            i = 0

            # Sanity check to see if the old object and the new one are the exact same with no differences in vertex listing
            if vert_list == current_new_obj:
                continue

            # Search for old coordinate first, then replace that data with the new coordinate until mesh is finished
            for vertex in current_new_obj:
                og_coord = struct.pack(">fff", vert_list[i][0], vert_list[i][1], vert_list[i][2])
                coord_loc = og_gno_data.find(og_coord)
                output_file.seek(coord_loc)
                
                new_coord = struct.pack(">fff", vertex[0], vertex[1], vertex[2])
                output_file.write(bytearray(new_coord))
                i+=1
            # Seek to start for next mesh
            output_file.seek(0)
            pass
        

# OUR MAIN FUNCTION:
if __name__ == "__main__":
    
    # Step 1: Get objects we want to replace
    og_obj_vert_dict = save_OG_obj_data()
    
    # Step 2: Get objects we're replacing the former with
    new_obj_vert_dict = save_NEW_obj_data()
    
    # Step 3: Save a copy of the input GNO file
    og_gno_data = save_GNO_copy()
    
    # Step 4: Search and destroy, AKA find OG meshes, replace with NEW meshes
    search_and_destroy(og_obj_vert_dict, new_obj_vert_dict, og_gno_data)
    
    