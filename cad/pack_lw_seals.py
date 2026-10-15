"""Assign all TPU seals and their coupons to TPU-LW in the saved project.

Clone the user's TPU material into a dedicated slot; existing slots stay exact.
A separate print project places one seal or cable half on each plate.
"""
import copy
import math
import json
import shutil
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from pack_forming_tools import CORE, PROD, NS, values, meta, load_mesh

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v59'
PROFILE=json.loads((ROOT/'cad/profiles/esun_tpu_lw.json').read_text())
TPU_NAMES=['junta_V_porta_TPU','amostra_V_porta_TPU','TPU_passagem_aquecedor','TPU_passagem_sensor',
           'bucha_sensor_TPU','amostra_bucha_sensor_TPU_15.3','amostra_bucha_sensor_TPU_15.5',
           'junta_porta','amostra_junta_TPU','amostra_junta_TPU_labios_0p8']
PRINT_NAMES=['amostra_V_porta_TPU','junta_V_porta_TPU','TPU_passagem_aquecedor','TPU_passagem_sensor']+TPU_NAMES[4:]
SPEED_KEYS=('outer_wall_speed','inner_wall_speed','sparse_infill_speed',
            'internal_solid_infill_speed','top_surface_speed','gap_infill_speed',
            'initial_layer_speed','initial_layer_infill_speed','bridge_speed',
            'overhang_1_4_speed','overhang_2_4_speed','overhang_3_4_speed',
            'overhang_4_4_speed','overhang_totally_speed')
SETTINGS={k:'25' for k in SPEED_KEYS}
SETTINGS.update(enable_support='0',layer_height='0.2',initial_layer_print_height='0.2',
                wall_loops='3',sparse_infill_density='100%',top_shell_layers='4',
                bottom_shell_layers='4',seam_position='aligned',
                enable_overhang_speed='0',
                internal_bridge_speed='100%',extruder='4',
                avoid_crossing_wall='1',ironing_type='no ironing')

OBJECT_SETTINGS={name:{'sparse_infill_density':'30%','sparse_infill_pattern':'gyroid'} for name in ('TPU_passagem_sensor','TPU_passagem_aquecedor')}

def setmeta(node,key,value):
    item=next((m for m in node.findall('metadata') if m.get('key')==key),None)
    if item is None:meta(node,key,value)
    else:item.set('value',str(value))


def patch(names=None):
    path=ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf'
    with zipfile.ZipFile(path) as z:entries={i.filename:(i,z.read(i)) for i in z.infolist()}
    model=ET.fromstring(entries['3D/3dmodel.model'][1])
    config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    oldconfig=copy.deepcopy(config)
    resources=model.find('m:resources',NS);build=model.find('m:build',NS)
    project=json.loads(entries['Metadata/project_settings.config'][1])
    material_count=len(project['filament_type']);assert material_count in (3,4)
    if material_count==4:assert project['filament_settings_id'][3].startswith('eSUN TPU-LW')
    previous=copy.deepcopy(project)
    # The saved project has three material slots. All length-three arrays are
    # material arrays; printer/extruder/process arrays have other lengths.
    for key,value in project.items():
        if material_count==3 and isinstance(value,list) and len(value)==3:value.append(copy.deepcopy(value[1]))
    for key,value in PROFILE['filament_overrides'].items():
        if key not in project:project[key]=['nil']*4
        assert isinstance(project[key],list) and len(project[key])==4,key
        project[key][3]=value
    for key,value in previous.items():
        assert project[key][:3]==value[:3] if isinstance(value,list) and len(value)==material_count else project[key]==value,key
    updates={};removed=set();records=[]
    names=names or TPU_NAMES
    for name in names:
        saved=next(o for o in config.findall('object') if values(o).get('name')==name)
        wrapper=next(o for o in resources if o.get('id')==saved.get('id'))
        item=next(i for i in build if i.get('objectid')==saved.get('id'))
        component=wrapper.find('m:components/m:component',NS)
        target=component.get(f'{{{PROD}}}path').lstrip('/')
        owner=ET.fromstring(updates.get(target,entries[target][1]))
        meshobj=next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
        plate=next(p for p in config.findall('plate') if any(values(i).get('object_id')==saved.get('id') for i in p.findall('model_instance')))
        jobs=[(saved,wrapper,item,meshobj,plate,None)]
        for record,wrap,bi,mo,pl,half in jobs:
            # GUI expects the global/vector setting here. A scalar object
            # override causes DynamicConfig::opt_float() to reject its type.
            for m in list(record.findall('metadata')):
                if m.get('key')=='small_perimeter_speed':record.remove(m)
            for key,value in (SETTINGS|OBJECT_SETTINGS.get(name,{})).items():setmeta(record,key,value)
            for part in record.findall('part'):
                for m in list(part.findall('metadata')):
                    if m.get('key')=='extruder':m.set('value','4')
            filename=f'{name}_metade_{half}' if half else name
            orient=(lambda p:(p[0],-p[2],p[1])) if name in ('junta_V_porta_TPU','junta_porta') else None
            points,faces,size=load_mesh(OUT/f'{filename}.stl',orient)
            transform=[float(v) for v in bi.get('transform').split()]
            if name in ('junta_V_porta_TPU','junta_porta'):
                transform[:9]=[1,0,0,0,1,0,0,0,1]
                bi.set('transform',' '.join(format(v,'.9g') for v in transform))
                for assembled in config.find('assemble'):
                    if assembled.get('object_id')==record.get('id'):assembled.set('transform',bi.get('transform'))
            assert transform[:9]==[1,0,0,0,1,0,0,0,1]
            mo.remove(mo.find('m:mesh',NS));mesh=ET.SubElement(mo,f'{{{CORE}}}mesh')
            vv=ET.SubElement(mesh,f'{{{CORE}}}vertices');tt=ET.SubElement(mesh,f'{{{CORE}}}triangles')
            for p in points:ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(p[i]-(transform[11] if i==2 else 0),'.9g') for i,a in enumerate('xyz')})
            for face in faces:ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{i+1}':str(v) for i,v in enumerate(face)})
            pid=int(values(pl)['plater_id'])
            for m in list(pl.findall('metadata')):
                if m.get('key') in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):removed.add(m.get('value'));pl.remove(m)
            removed.add(f'Metadata/plate_{pid}_small.png')
            records.append(dict(peca=values(record)['name'],stl=filename+'.stl',bandeja=pid,dimensoes_mm=size))
        updates[target]=ET.tostring(owner,encoding='utf-8',xml_declaration=True)
    for old in oldconfig.findall('object'):
        if values(old)['name'] not in names:
            new=next(o for o in config.findall('object') if o.get('id')==old.get('id'))
            assert ET.tostring(old)==ET.tostring(new),values(old)['name']
    updates.update({'3D/3dmodel.model':ET.tostring(model,encoding='utf-8',xml_declaration=True),
                    'Metadata/model_settings.config':ET.tostring(config,encoding='utf-8',xml_declaration=True),
                    'Metadata/project_settings.config':json.dumps(project,indent=2,ensure_ascii=False).encode()})
    tmp=path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w') as z:
        for name,(info,data) in entries.items():
            if name not in removed:z.writestr(info,updates.get(name,data))
    tmp.replace(path);shutil.copy2(path,OUT/'incubadora_v59_CrealityPrint_7.2.1.3mf')
    make_print_project(path)
    report=dict(pecas=records,perfis_anteriores_preservados=True,demais_objetos_preservados=True,
                bandejas=36,pecas_total=39,perfil_novo=4,perfil_experimental_fluxo=True)
    (OUT/'tpulw_project_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))

def make_print_project(path):
    with zipfile.ZipFile(path) as z:entries={i.filename:(i,z.read(i)) for i in z.infolist()}
    model=ET.fromstring(entries['3D/3dmodel.model'][1]);config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    project=json.loads(entries['Metadata/project_settings.config'][1])
    resources=model.find('m:resources',NS);build=model.find('m:build',NS)
    newconfig=ET.Element('config');newresources=ET.Element(f'{{{CORE}}}resources');newbuild=ET.Element(f'{{{CORE}}}build')
    assemble=ET.SubElement(newconfig,'assemble');updates={};nextid=max(int(o.get('id')) for o in resources)+1
    names=PRINT_NAMES
    columns=math.ceil(math.sqrt(len(names)+2))
    jobs=[]
    for name in names:
        saved=next(o for o in config.findall('object') if values(o).get('name')==name)
        wrapper=next(o for o in resources if o.get('id')==saved.get('id'))
        item=next(i for i in build if i.get('objectid')==saved.get('id'))
        component=wrapper.find('m:components/m:component',NS)
        target=component.get(f'{{{PROD}}}path').lstrip('/')
        owner=ET.fromstring(entries[target][1]);meshobj=next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
        for half in (('A','B') if name.startswith('TPU_passagem') else (None,)):
            record=copy.deepcopy(saved);wrap=copy.deepcopy(wrapper);bi=copy.deepcopy(item);mo=copy.deepcopy(meshobj)
            filename=name+f'_metade_{half}' if half else name
            if half=='B':
                record.set('id',str(nextid));wrap.set('id',str(nextid));bi.set('objectid',str(nextid));mo.set('id',str(nextid+1));wrap.find('m:components/m:component',NS).set('objectid',str(nextid+1))
                wrap.set(f'{{{PROD}}}UUID',str(uuid.uuid4()));bi.set(f'{{{PROD}}}UUID',str(uuid.uuid4()))
                for part in record.findall('part'):part.set('id',str(nextid+1))
                nextid+=2
            setmeta(record,'name',filename)
            for part in record.findall('part'):setmeta(part,'name',filename);setmeta(part,'source_file',filename+'.stl')
            if half:
                points,faces,size=load_mesh(OUT/f'{filename}.stl');dz=float(bi.get('transform').split()[11])
                mo.remove(mo.find('m:mesh',NS));mesh=ET.SubElement(mo,f'{{{CORE}}}mesh');vv=ET.SubElement(mesh,f'{{{CORE}}}vertices');tt=ET.SubElement(mesh,f'{{{CORE}}}triangles')
                for p in points:ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(p[i]-(dz if i==2 else 0),'.9g') for i,a in enumerate('xyz')})
                for face in faces:ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{i+1}':str(v) for i,v in enumerate(face)})
            pid=len(jobs)+1;transform=bi.get('transform').split();transform[9]=str(110+264*((pid-1)%columns));transform[10]=str(110-264*((pid-1)//columns));bi.set('transform',' '.join(transform))
            plate=ET.Element('plate');meta(plate,'plater_id',pid);meta(plate,'plater_name',f'{pid} - TPU-LW - {filename}');meta(plate,'locked','false')
            instance=ET.SubElement(plate,'model_instance');meta(instance,'object_id',record.get('id'));meta(instance,'instance_id',0);meta(instance,'identify_id',1000+pid)
            ET.SubElement(assemble,'assemble_item',object_id=record.get('id'),instance_id='0',transform=bi.get('transform'),offset='0 0 0')
            newconfig.insert(len(newconfig)-1,record);newconfig.insert(len(newconfig)-1,plate);newresources.append(wrap);newbuild.append(bi)
            if target not in updates:
                cleanowner=copy.deepcopy(owner)
                for node in list(cleanowner.find('m:resources',NS)):cleanowner.find('m:resources',NS).remove(node)
                updates[target]=cleanowner
            updates[target].find('m:resources',NS).append(mo);jobs.append(dict(peca=filename,bandeja=pid))
    # Inline meshes and contiguous IDs avoid production-submodel remapping when
    # extracting a subset of the user's saved multi-plate project.
    inline=ET.Element(f'{{{CORE}}}resources')
    for index,(record,bi,plate,assembled) in enumerate(zip(newconfig.findall('object'),newbuild,newconfig.findall('plate'),assemble)):
        oldid=record.get('id');wrap=next(o for o in newresources if o.get('id')==oldid)
        component=wrap.find('m:components/m:component',NS);target=component.get(f'{{{PROD}}}path').lstrip('/')
        mo=copy.deepcopy(next(o for o in updates[target].find('m:resources',NS) if o.get('id')==component.get('objectid')))
        mid,oid=str(index*2+1),str(index*2+2)
        mo.set('id',mid);wrap.set('id',oid);component.set('objectid',mid)
        for node in (mo,wrap,component,bi):
            for attr in list(node.attrib):
                if attr.startswith('{'+PROD+'}'):del node.attrib[attr]
        record.set('id',oid);bi.set('objectid',oid);assembled.set('object_id',oid)
        for part in record.findall('part'):part.set('id',mid)
        setmeta(plate.find('model_instance'),'object_id',oid)
        inline.append(mo);inline.append(wrap)
    newresources=inline;updates={}
    for node in list(model.findall('m:metadata',NS)):
        if node.get('name','').startswith('Thumbnail_'):model.remove(node)
    # The native importer requires all object records before the plate records.
    ordered=list(newconfig.findall('object'))+list(newconfig.findall('plate'))+[assemble]
    for node in list(newconfig):newconfig.remove(node)
    for node in ordered:newconfig.append(node)
    model.remove(resources);model.remove(build);model.append(newresources);model.append(newbuild)
    for key in SPEED_KEYS:project[key]=['25'] if isinstance(project.get(key),list) else '25'
    project.update(layer_height='0.2',initial_layer_print_height='0.2',enable_support='0',brim_type='no_brim',skirt_loops='0',wall_loops='3',sparse_infill_density='100%',top_shell_layers='4',bottom_shell_layers='4',small_perimeter_speed=['25'],internal_bridge_speed=['100%'],enable_overhang_speed=['0'],seam_position='aligned',print_sequence='by layer',avoid_crossing_wall='1',outer_wall_acceleration='500',inner_wall_acceleration='500',default_acceleration='500',initial_layer_acceleration='500')
    written={'3D/3dmodel.model':ET.tostring(model,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':ET.tostring(newconfig,encoding='utf-8',xml_declaration=True),'Metadata/project_settings.config':json.dumps(project,indent=2,ensure_ascii=False).encode()}
    written.update({n:ET.tostring(o,encoding='utf-8',xml_declaration=True) for n,o in updates.items()})
    # Keep material arrays together exactly as in the validated full project;
    # the TPU-LW slot is moved first for the only physical K1C nozzle.
    for key,value in project.items():
        if isinstance(value,list) and len(value)==4:project[key]=[value[3]]+value[:3]
    for record in newconfig.findall('object'):
        setmeta(record,'extruder','1')
        for m in list(record.findall('metadata')):
            if m.get('key')=='small_perimeter_speed':record.remove(m)
    project['enable_prime_tower']='0'
    project['ironing_type']='no ironing'
    project['printable_area']=['0x0','220x0','220x220','0x220']
    project['machine_start_gcode']='\n'.join(line for line in project['machine_start_gcode'].splitlines() if not line.startswith('T['))
    written['Metadata/model_settings.config']=ET.tostring(newconfig,encoding='utf-8',xml_declaration=True)
    written['Metadata/project_settings.config']=json.dumps(project,indent=2,ensure_ascii=False).encode()
    relpath='3D/_rels/3dmodel.model.rels'
    relations=ET.fromstring(entries[relpath][1])
    for relation in list(relations):
        target=relation.get('Target','').lstrip('/')
        if target not in updates:relations.remove(relation)
    written[relpath]=ET.tostring(relations,encoding='utf-8',xml_declaration=True).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    destination=OUT/'vedacoes_eSUN_TPU_LW.3mf'
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,(info,data) in entries.items():
            if name in written:z.writestr(info,written.pop(name))
            elif name in ('[Content_Types].xml','_rels/.rels','3D/_rels/3dmodel.model.rels','Metadata/creality.config'):z.writestr(info,data)
        for name,data in written.items():z.writestr(name,data)
    (OUT/'tpulw_print_plates.json').write_text(json.dumps(jobs,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':
    import sys
    patch(('junta_V_porta_TPU','amostra_V_porta_TPU') if '--door-only' in sys.argv else None)
