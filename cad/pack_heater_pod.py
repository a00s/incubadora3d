"""Update the heater pod mesh while preserving the user's plate and settings."""
from pack_sensor_grommet import pack

if __name__ == '__main__':
    pack(('caixinha_encaixe_aquecedor',), 'heater_pod_project_report.json')
