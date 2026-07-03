import bpy, bmesh
import struct

# obj = bpy.context.active_object


# REMINDERS:

# 1. Make sure that ALL OG objects AND NEW objects are selected and placed in their respective collections
# 2. Make sure that your collection names are set up properly
# 3. Overwrite the PATH_TO_OG_GC with the original GC path
# 4. Make sure the new object names are the same as the originals, plus the '.001' at the end

# FOR USERS:
# OVERWRITE THIS WITH THE PATH TO THE GC YOU SENT IN
PATH_TO_OG_GC = "C:\\Users\\smasi\\Downloads\\test\\NightTests\\Unnamed_File_5.GC"

# FOR USERS:
# OVERWRITE THIS WITH WHERE YOU WANT YOUR GC TO SAVE TO
SAVE_PATH = "C:\\Users\\smasi\\Downloads\\test\\EggTests\\VertData\\"

# FOR USERS:
# OVERWRITE THIS WITH THE NAME OF THE COLLECTION THAT CONTAINS YOUR ORIGINAL GC MESHES
OG_OBJ_COLLECTION_NAME = 'Collection'

# FOR USERS:
# OVERWRITE THIS WITH THE NAME OF THE COLLECTION THAT WILL CONTAIN YOUR NEW MESHES THAT WILL REPLACE THE OLD ONES
NEW_OBJ_COLLECTION_NAME = 'Collection 2'


# DO NOT TOUCH THESE DEFINITIONS

# Step 1.
# Get ALL selected meshes from OG file collection

def save_OG_obj_data():
    if OG_OBJ_COLLECTION_NAME not in bpy.data.collections:
        print(
            "No OG object collection found! Please ensure that OG_OBJ_COLLECTION_NAME exists in your hierarchy window, or change the value of this variable to match your new object collection name.")
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
        print(
            "No new object collection found! Please ensure that NEW_OBJ_COLLECTION_NAME exists in your hierarchy window, or change the value of this variable to match your new object collection name.")
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
# Save a copy of the OG GC

def save_GC_copy():
    # Save a copy of the input GC here first, for security
    with open(PATH_TO_OG_GC, "rb") as input_file:
        # Opens and reads a copy of the file for safety, we don't wanna overwrite our original for preservation's sake
        copy_of_GC = input_file.read()
        return copy_of_GC


# Step 4.
# Using the vertex data of the original file, find the start of the mesh in the given GC, then replace the data
def search_and_destroy(OG_mesh_dict, NEW_mesh_dict, og_GC_data):
    # Create a new output file

    new_GC_name = PATH_TO_OG_GC.removesuffix(".GC")
    new_GC_name = PATH_TO_OG_GC.removesuffix(".gc")
    new_GC_name = new_GC_name + "_out.gc"

    with open(new_GC_name, "wb+") as output_file:

        output_file.write(og_GC_data)

        # Start by searching our file for the first vertex in our OG_mesh's mesh

        for name, vert_list in OG_mesh_dict.items():
            print("Searching for: " + str(name))

            first_coord = struct.pack(">fff", vert_list[0][0], vert_list[0][1], vert_list[0][2])
            print(first_coord.hex())
            first_coord_found = og_GC_data.find(first_coord)
            print(first_coord_found)

            if first_coord:
                # If all three were found successfully and matched, mesh data starts at x_coord data
                start_of_mesh = first_coord_found
                #                output_file.seek(start_of_mesh)
                print("Start of mesh found: " + str(hex(first_coord_found)))
            #                input("Continue?")
            else:
                # else if we don't find this first point, move onto the next mesh
                continue

            # Once file seeked out, time to destroy (replace) with new data

            # Use name to successfully find which mesh to replace this with

            new_mesh_key_name = str(name) + ".001"  # We assume all object dupes have this name
            current_new_obj = NEW_mesh_dict[new_mesh_key_name]

            print("Vertex count in curr_new_obj: " + str(len(current_new_obj)))
            i = 0

            if vert_list == current_new_obj:
                continue

            for vertex in current_new_obj:
                og_coord = struct.pack(">fff", vert_list[i][0], vert_list[i][1], vert_list[i][2])
                coord_loc = og_GC_data.find(og_coord)
                output_file.seek(coord_loc)

                new_coord = struct.pack(">fff", vertex[0], vertex[1], vertex[2])
                output_file.write(bytearray(new_coord))
                i += 1
            # Seek to start
            output_file.seek(0)
            pass


# OUR MAIN FUNCTION:

if __name__ == "__main__":
    # Step 1: Get objects we want to replace
    og_obj_vert_dict = save_OG_obj_data()

    # Step 2: Get objects we're replacing the former with
    new_obj_vert_dict = save_NEW_obj_data()

    # Step 3: Save a copy of the input GC file
    og_GC_data = save_GC_copy()

    # Step 4: Search and destroy, AKA find OG meshes, replace with NEW meshes
    search_and_destroy(og_obj_vert_dict, new_obj_vert_dict, og_GC_data)

