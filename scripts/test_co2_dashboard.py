#!/usr/bin/env python3
"""Check chronology, door durations, malformed serial input and durable local history."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from co2_dashboard import FALLBACK, Store, parse_log

HEADER=','.join(FALLBACK)+'\n'
def data(ms,ppm=50000,valid=1,temp='37.0'):
    values={key:'0' for key in FALLBACK}
    values.update(DATA='DATA',ms=str(ms),co2_ppm=str(ppm),co2_valid=str(valid),temp_c=temp,
                  co2_enabled='1',heater_enabled='1',last_pulse_ms='20',next_pulse_ms='20')
    return ','.join(values[key] for key in FALLBACK)+'\n'

def capture(boot=1,count=4):
    return f'BOOT_COUNT,{boot}\n'+HEADER+''.join(data(1000+i*2000) for i in range(count))

class Chronology(unittest.TestCase):
    def test_events_use_following_frame_and_door_has_ms_on_both_ends(self):
        text='BOOT_COUNT,1\n'+HEADER+data(1000)+'EVENT,door,open\n'+data(3000)+'EVENT,co2_pulse,20\n'+data(5000)+'EVENT,door,closed\n'+data(11000)
        session=parse_log(text,'capture.log',1000000000)[0]
        doors=[e for e in session['events'] if e['kind']=='door']
        self.assertEqual([e['duration_ms'] for e in doors],[8000,8000])
        self.assertEqual([e['t'] for e in doors],[1000000003,1000000011])
        self.assertIn('8.000 ms',doors[0]['label'])
        dose=next(e for e in session['events'] if e['kind']=='dose')
        self.assertEqual((dose['t'],dose['duration_ms']),(1000000005,20))
        self.assertEqual(next(e['t'] for e in session['events'] if e['kind']=='restart'),1000000000)

    def test_open_door_is_not_given_an_invented_closing_time(self):
        text=capture(count=1)+'EVENT,door,open\n'+data(3000)+data(9000)
        door=next(e for e in parse_log(text,'a',1000)[0]['events'] if e['kind']=='door')
        self.assertIsNone(door['duration_ms'])
        self.assertTrue(door['open_ended'])
        self.assertEqual(door['elapsed_ms'],6000)

    def test_does_not_infer_door_from_a_co2_drop(self):
        text=capture(count=1)+data(3000,2000)
        self.assertFalse(any(e['kind']=='door' for e in parse_log(text,'a',1000)[0]['events']))

    def test_preboot_garbage_invalid_sensor_and_incomplete_event(self):
        text=data(999999,65000)+'garbage\n'+capture(count=1)+data(3000,70000)+data(5000,42000,0,'nan')+'EVENT,co2_pulse,99\n'
        session=parse_log(text,'a',1000)[0]
        self.assertEqual(len(session['points']),3)
        self.assertEqual([p[1] for p in session['points']],[50000,None,None])
        self.assertIsNone(session['points'][-1][2])
        self.assertFalse(any(e['kind']=='dose' for e in session['events']))
        json.dumps(session,allow_nan=False)

    def test_new_captures_use_host_clock_for_samples_and_door_events(self):
        text='HOST_TIME,1700000000\nBOOT_COUNT,1\n'+HEADER
        text+='HOST_TIME,1700000001\n'+data(1000)
        text+='HOST_TIME,1700000003.1\nEVENT,door,open\nHOST_TIME,1700000003.7\n'+data(3000)
        text+='HOST_TIME,1700000011.5\nEVENT,door,closed\nHOST_TIME,1700000011.7\n'+data(11000)
        session=parse_log(text,'new.log',1234)[0]
        self.assertFalse(session['estimated_time'])
        self.assertEqual(session['points'][0][0],1700000001)
        doors=[e for e in session['events'] if e['kind']=='door']
        self.assertEqual([e['duration_ms'] for e in doors],[8400,8400])
        self.assertAlmostEqual(doors[0]['t'],1700000003.1)

    def test_locked_raw_and_counter_wrap_are_preserved_separately(self):
        def locked(ms,raw):
            row=data(ms,raw,0).strip().split(',');row[24]='1'
            return ','.join(row)+'\n'
        text='BOOT_COUNT,1\n'+HEADER+data(1000,59000)+locked(3000,65470)+locked(5000,785)+locked(7000,1581)+locked(9000,65000)
        points=parse_log(text,'wrap',1000)[0]['points']
        self.assertEqual([p[12] for p in points],[59000,65470,66321,67117,65000])
        self.assertEqual([p[11] for p in points],[59000,65470,785,1581,65000])
        self.assertIsNone(points[2][1])
        self.assertEqual(points[2][8],1)
        self.assertTrue(points[2][13])
        self.assertFalse(points[-1][13])
        # A capture starting low and locked cannot reveal how many wraps happened.
        unknown=parse_log('BOOT_COUNT,2\n'+HEADER+locked(1000,785),'unknown',1000)[0]['points'][0]
        self.assertEqual(unknown[12],785);self.assertFalse(unknown[13])
        # A recorded door opening is not evidence of counter rollover.
        door=parse_log('BOOT_COUNT,3\n'+HEADER+locked(1000,65000)+'EVENT,door,open\n'+locked(3000,500),'door-wrap',1000)[0]['points'][-1]
        self.assertEqual(door[12],500);self.assertFalse(door[13])

    def test_legacy_no_response_is_history_not_a_current_alert(self):
        text=capture(count=1)+'EVENT,co2_no_response,auto_off\n'+data(3000,6400)
        event=next(e for e in parse_log(text,'fault',1000)[0]['events'] if e['raw'].startswith('EVENT,co2_no_response'))
        self.assertEqual(event['kind'],'control')
        self.assertIn('versão antiga',event['label'])

    def test_dose_tooltip_has_actual_average_basis(self):
        header=FALLBACK[:]
        header[17]='basis_ms';header[19]='basis_rise_ppm';header[20]='basis_steps'
        row=data(3000).strip().split(',');row[17]='100';row[19]='5000';row[20]='5'
        text='BOOT_COUNT,1\n'+','.join(header)+'\n'+data(1000)+'EVENT,co2_pulse,20\n'+','.join(row)+'\n'
        dose=next(e for e in parse_log(text,'basis',1000)[0]['events'] if e['kind']=='dose')
        self.assertEqual((dose['basis_ms'],dose['basis_rise_ppm'],dose['basis_steps']),(100,5000,5))

    def test_restart_segments_and_rollover(self):
        sessions=parse_log(capture(1,3)+capture(2,2),'a',1000)
        self.assertEqual(len(sessions),2)
        self.assertNotEqual(sessions[0]['id'],sessions[1]['id'])
        self.assertGreater(sessions[1]['points'][0][0],sessions[0]['points'][-1][0])
        text='BOOT_COUNT,3\n'+HEADER+data(4294966000)+data(1000)
        sessions=parse_log(text,'b',1000)
        self.assertEqual(len(sessions),1)
        self.assertAlmostEqual(sessions[0]['points'][1][0]-sessions[0]['points'][0][0],2.296,places=3)

class Durability(unittest.TestCase):
    def test_archive_append_rotation_and_source_disappearance(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);source=base/'tmp';source.mkdir();archive=base/'logs/telemetria'
            path=source/'capture.log';path.write_text(capture(1,8))
            store=Store(source,archive)
            self.assertEqual(store.refresh()[0]['boot'],1)
            original=(archive/path.name).read_bytes()
            with path.open('a') as f:f.write(data(18000))
            store.refresh()
            self.assertTrue((archive/path.name).read_bytes().startswith(original))
            self.assertEqual((archive/path.name).read_bytes(),path.read_bytes())
            path.write_text(capture(2,2))
            sessions=store.refresh()
            self.assertEqual({s['boot'] for s in sessions},{1,2})
            self.assertEqual(len(list(archive.glob('*--archived-*.log'))),1)
            path.unlink()
            recovered=Store(source,archive).refresh()
            self.assertEqual({s['boot'] for s in recovered},{1,2})

    def test_annotations_keep_duration_and_validate_values(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);store=Store(base/'missing',base/'logs/telemetria')
            item={'t':time.time(),'kind':'door','label':'Porta aberta para inspeção','duration_ms':20000}
            store.add_annotation(item)
            notes=store.annotations()
            self.assertEqual(notes[0]['duration_ms'],20000)
            self.assertEqual(notes[0]['source'],'annotation')
            for invalid in [dict(item,duration_ms=-1),dict(item,duration_ms='nan'),dict(item,kind='CO2 ON'),dict(item,t=0),dict(item,label='')]:
                with self.assertRaises(ValueError):store.add_annotation(invalid)

if __name__=='__main__':unittest.main()
