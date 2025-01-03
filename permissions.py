import requests
import sys

# First, create an API key in Metabase. You need to go to settings->Admin-->authentication->API keys and create a new key associated with the Administrator group

MB_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxx' # You API key goes here
MB_SITE_URL = 'http://<your_metabase_instance_url>' # Your Metabase URL goes here

group_endpoint = f'{MB_SITE_URL}/api/permissions/group'
jwt_group_mapping_endpoint = f'{MB_SITE_URL}/api/setting/jwt-group-mappings'
properties_endpoint = f'{MB_SITE_URL}/api/session/properties'

def get_current_groups():
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': MB_API_KEY
    }
    response = requests.get(properties_endpoint, headers=headers)
    if response.status_code == 200:
        properties = response.json()
        return properties['jwt-group-mappings']
    else:
        print(f"Failed to get groups. Status code: {response.status_code}, Response: {response.text}")
        return []

def create_group(group_name):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': MB_API_KEY
    }
    data = {
        'name': group_name
    }
    response = requests.post(group_endpoint, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Group '{group_name}' created successfully with ID {response.json()['id']}")
    else:
        print(f"Failed to create group '{group_name}'. Status code: {response.status_code}, Response: {response.text}")
    return response.json()['id']

def map_group_to_jwt(current_groups, group_id, group_name, jwt_group):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': MB_API_KEY
    }
    # start with a copy of the existing mappings
    data = {
        "value": current_groups.copy()
    }
    
    # if the jwt group key already exists, append the new group id to its list
    if jwt_group in data["value"]:
        if group_id not in data["value"][jwt_group]:
            data["value"][jwt_group].append(group_id)
    # if the jwt group key does not exist, add it with the new group id
    else:
        data["value"][jwt_group] = [group_id]
        
    print(f"Current groups: {current_groups}")
    print(f"Updated groups: {data}")
    response = requests.put(jwt_group_mapping_endpoint, headers=headers, json=data)
    if response.status_code == 204:
        print(f"Group '{group_name}' successfully mapped to JWT group '{jwt_group}'")
    else:
        print(f"Failed to map group '{group_name}' to JWT group '{jwt_group}'. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python permissions.py <group_name> <jwt_group>")
        sys.exit(1)
    group_name = sys.argv[1]
    jwt_group = sys.argv[2]
    group_id = create_group(group_name)
    current_groups = get_current_groups()
    map_group_to_jwt(current_groups, group_id, group_name, jwt_group)