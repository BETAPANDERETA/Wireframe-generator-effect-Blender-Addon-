bl_info = {
    "name": "Wireframe generator effect",
    "author": "BETAPANDERETA <lbetancurd@unal.edu.co>",
    "version": (1, 5),
    "blender": (2, 82, 0),
    "location": "View3D > UI ",
    "description": "Agrega un efecto de generacion de malla a tus modelos",
    "warning": "Este Add-on esta sujeto a cambios y mejoras",
    "wiki_url": "https://github.com/BETAPANDERETA/Wireframe-generator-effect-Blender-Addon-",
}

import bpy 
from bpy.props import*

#Funcionalidad del Add-on

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

# Funcion principal <Aqui ocurre la magia > 

def generador():
    
    #Valores default
    defaultFuerza = .5
    defaultRuido = .5
    defaultSubs = 2
    defaultScale = [1,1,1]
    
    if bpy.context.object == None: print("Ningun objeto seleccionado")
    else:
        malla = crearMalla()
        nubeObj = crearNube("_objeto",defaultFuerza,defaultRuido,defaultScale,defaultSubs)
        nubeM = crearNube("_malla",defaultFuerza,defaultRuido,defaultScale,defaultSubs)

# Operador <Aca interpreto la funcionalidad para blender>
   
class WireframeGenerator(bpy.types.Operator):

    bl_idname = "object.wireframe_generator"
    bl_label = "Wireframe Generator"
    bl_description = "¡Genera un efecto increible! Click aqui para agregarlo"
       
    @classmethod
    def poll(cls, context):
      return context.active_object is not None and  context.object.select_get()==True  and context.object.type == 'MESH'

    def execute(self, context):
        
        generador()
            
        return {'FINISHED'}

#Panel en el UI de la vista 3D <Interfaz para usar el efecto >

class MYADDON_PT_my_panel(bpy.types.Panel):
    
    bl_label = "Wireframe generator"
    bl_idname = 'MYADDON_PT_my_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WGV1.5"
    
    def generadorModificadores(self,col,idMod,mod,texto,obj,icono):
        
        if obj.modifiers[idMod] is not None:
            col.label(text = texto,icon=icono)
            col.prop(obj.modifiers[idMod],mod)
        
     
    def draw(self, context):
        layout = self.layout
        
        obj = context.active_object # Objeto que esta activo en la seleccion
        
        row = layout.row()
        row.label(text="Autor: BETAPANDERETA",icon="COPY_ID")
        
        row = layout.row()
        row.label(text="version: 1.5",icon="INFO")
        
        row = layout.row()
        row.operator("object.wireframe_generator",icon = "EVENT_W")
        
        #Revisar alguna manera de no usar la excepcion, agregar modificadores de: keyframes,
        
        if context.active_object is not None and  context.object.select_get()==True:
            
            row = layout.row()
            row.label(text="Objeto seleccionado: " + obj.name)
            col = layout.column()
            row = layout.row()
            row.prop(obj,"scale")
            try:
                self.generadorModificadores(col,"Desaparecer",'object','Seleccione nube',obj,"MOD_BOOLEAN")
                self.generadorModificadores(col,"Subdivision",'levels','Subdiv. malla',obj,"MOD_SUBSURF")
                self.generadorModificadores(col,"Malla",'thickness','Grosor malla',obj,"MOD_WIREFRAME")
                
            except KeyError:
                    print("No se encuentra el modificador")
            
        else:
                row = layout.row()
                row.label(text="Objeto seleccionado: Ninguno")
        
        if obj is not None and  obj.select_get()==True:
            
            try:
                self.generadorModificadores(col,"Distorsion",'strength','Fuerza de efecto',obj,"MOD_DISPLACE")
                
            except KeyError:
                    print("No se encuentra el modificador o textura")
            
        else:
                print("No hay nube")

def register():
    bpy.utils.register_class(WireframeGenerator)
    bpy.utils.register_class(MYADDON_PT_my_panel)
    
def unregister():

    bpy.utils.unregister_class(MYADDON_PT_my_panel)
    bpy.utils.unregister_class(WireframeGenerator)

if __name__ == "__main__":
    register()