"""Replace both cable plugs by pairs of halves on their existing saved plates."""
from pack_sensor_grommet import pack

if __name__ == '__main__':
    pack(('TPU_passagem_aquecedor', 'TPU_passagem_sensor'),
         'wire_plugs_project_report.json')
