from agio.core.entities.project import AProject
from agio.core.entities.company import ACompany
from agio.core.settings import get_local_settings, save_local_settings
from agio.tools.setup_logger import disabled_loggers


def load_projects():
    cmp = ACompany.current()
    for prj in AProject.iter(cmp):
        yield prj


def load_dialog_data():
    projects = load_projects()
    dialog_data = []
    for prj in projects:
        dialog_data.append({
            'project': prj,
            'settings': get_local_settings(prj)
            }
        )
    return dialog_data


def save_settings(data):
    """
    # loc_s.set('agio_pipe.local_roots', [
    #     {'name': 'projects', 'path': '/mnt/agio'},
    #     {'name': 'temp', 'path': '/tmp/agio'},
    # ])

    """
    for item in data.values():
        save_local_settings(item['settings'], item['project'])

