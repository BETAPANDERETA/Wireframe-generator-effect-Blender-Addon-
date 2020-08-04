import bpy
from bpy.types import (
    AddonPreferences,
    Operator,
    Panel,
    PropertyGroup
)
from bpy.props import*

def crearMalla():
    
    #Material
    
    glow = bpy.data.materials.new(name = "emision")
    glow.use_nodes = True
    
    # Objetos
    
    objName = bpy.context.object.name
    obj = bpy.data.objects[objName]

    bpy.ops.object.duplicate()
    bpy.context.object.name = " Malla_" + objName 

    malla =  bpy.context.object.name
    objM = bpy.data.objects[malla]
    objM.data.materials.append(glow)
    
    #Tomado de: https://gumroad.com/l/python_crash_course
    
    nodes = glow.node_tree.nodes
    material_output = nodes.get("Material Output")
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_emission.inputs[0].default_value = ( 0.0, 0.3, 1.0, 1 ) #color
    node_emission.inputs[1].default_value = 10 #strength
    links = glow.node_tree.links
    new_link = links.new(node_emission.outputs[0], material_output.inputs[0])
    
    #Modificadores 

    sub_mod = objM.modifiers.new("Subdivision","SUBSURF")
    sub_mod.levels = 1
    malla_mod = objM.modifiers.new("Malla","WIREFRAME")
    malla_mod.thickness = 0.01
    dif_mod = objM.modifiers.new("Desaparecer","BOOLEAN")
    dif_mod_o = obj.modifiers.new("Desaparecer","BOOLEAN")
    
def crearNube(id,fuerza,ruido,dim,sub):
    
    bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 0))  
    nubeN = bpy.context.object.name
    nube = bpy.data.objects[nubeN]
    bpy.context.object.name = "Nube" + id
    bpy.context.object.display_type = 'WIRE'

    if len(dim)!=3:print("Dimension invalida")
    else:
        x = dim[0]
        y = dim[1] 
        z = dim[2]
        bpy.ops.transform.resize(value=(x, y, z))

    #Textura
    
    tex = bpy.data.textures.new("Ruido","DISTORTED_NOISE")
    tex.noise_scale = ruido
    
    #Modificadores
    sub_mod_n = nube.modifiers.new("Subdivision","SUBSURF")
    sub_mod_n.levels = sub

    dis_mod = nube.modifiers.new("Distorsion","DISPLACE")
    dis_mod.strength = fuerza
    dis_mod.texture = tex
    dis_mod.texture_coords = 'GLOBAL'
    
    #animaciones tomado de:https://docs.blender.org/api/current/info_quickstart.html
    
    nube.location[0] = 0.0
    nube.keyframe_insert(data_path="location", frame=0.0, index=0)
    nube.location[0] = 2.0
    nube.keyframe_insert(data_path="location", frame=120.0, index=0)
     
class WireframeGenerator(bpy.types.Operator):

    bl_idname = "object.wireframe_generator"
    bl_label = "Wireframe Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER','UNDO'}
    
    #Propiedades
    
    fuerza: FloatProperty(
        name = "Fuerza nube objeto",
        description = "Incrementa tamaño de la nube",
        default = .5,
        min = 0.0,
        max = 1.0,
    )
    
    fuerzaDos: FloatProperty(
        name = "Fuerza nube malla",
        description = "Incrementa tamaño de la nube",
        default = .5,
        min = 0.0,
        max = 1.0,
    )
    
    ruido: FloatProperty(
        name = "Ruido de nube",
        description = "Incrementa ruido  de la nube",
        default = .5,
        min = 0.0,
        max = 1.0,
    )
    
    ruidoDos: FloatProperty(
        name = "Ruido de nube",
        description = "Incrementa ruido  de la nube",
        default = .5,
        min = 0.0,
        max = 1.0,
    )
    
    subs:IntProperty(
        name = "Subdivision de nube",
        description = "Incrementa ruido  de la nube",
        default = 2,
        min = 0,
        max = 4,
    )
    
    subsDos:IntProperty(
        name = "Subdivision de nube",
        description = "Incrementa ruido  de la nube",
        default = 2,
        min = 0,
        max = 4,
    )
    
    @classmethod
    def poll(cls, context):
      return context.active_object is not None

    def execute(self, context):
        
        if bpy.context.object == None: print("Ningun objeto seleccionado")
        else:
            malla = crearMalla()
            nubeObj = crearNube("_objeto",self.fuerza,self.ruido,[1,1,1],self.subs)
            nubeM = crearNube("_malla",self.fuerzaDos,self.ruidoDos,[1,1,1],self.subsDos)
            
        #Imprimendo objetos de la coleccion
            
        cont=0

        for obj in bpy.data.objects:
                
            cont +=1
            print(str(cont) + str(obj.name))
            
        return {'FINISHED'}
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Wireframe generator v1.0")
        row = col.row()
        row.prop(self, "fuerza")
        row = col.row()
        row.prop(self, "fuerzaDos")
        row = col.row()
        row.prop(self, "ruido")
        row = col.row()
        row.prop(self, "ruidoDos")
        row = col.row()
        row.prop(self, "subs")
        row = col.row()
        row.prop(self, "subsDos")

def menu_func(self,context):
    
    self.layout.operator(WireframeGenerator.bl_idname)

def register():
    
    bpy.utils.register_class(WireframeGenerator)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    
    bpy.utils.unregister_class(WireframeGenerator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.wireframe_generator()