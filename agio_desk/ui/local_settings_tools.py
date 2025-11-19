import json

from agio.core.entities.project import AProject
from agio.core.entities.company import ACompany
from agio.core import settings as local_settings
from agio.core import api

# query = '''
# query GetCompaniesWithProjects{
#   companies (
#     first: 10000,
#   ){
#     edges{
#       node {
#         id
#         name
#         code
#         projects{
#           id
#           name
#           code
#         }
#
#       }
#     }
#   }
# }'''
#
# def load_data():
#     data = api.client.make_query_raw(query)
#     companies = [item['node'] for item in data['data']['companies']['edges']]
#     for cmp in companies:
#         cmp['projects'] = [AProject(prj) for prj in cmp['projects']]
#     return companies
# load_data()


def load_companies():
    return list(ACompany.iter())


def load_projects(company_id):
    dialog_data = []
    for prj in AProject.iter(company_id):
        dialog_data.append({
            'project': prj,
            'settings': get_project_settings(prj)
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
        local_settings.save_local_settings(item['settings'], item['project'])


def get_project_settings(project_id):
    """
    Temporary function for any project settings
    TODO: move roots to core package
    """
    settings_file = local_settings.get_project_settings_file(project_id)
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            return json.load(f)
    return {
        'agio_pipe.local_roots': {
            "value": []
        }
    }