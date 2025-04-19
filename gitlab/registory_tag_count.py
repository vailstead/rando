import requests

# GitLab instance URL and access token
GITLAB_URL = 'https://gitlab.example.com'
ACCESS_TOKEN = 'your_access_token_here'

# GitLab API endpoint for listing repositories in a project
PROJECTS_API = f'{GITLAB_URL}/api/v4/projects'
REGISTRY_API = f'{GITLAB_URL}/api/v4/projects/{{project_id}}/container_registry/repositories/{{repository_id}}/tags'

# Function to get all projects
def get_projects():
    projects = []
    page = 1
    while True:
        response = requests.get(
            PROJECTS_API,
            headers={'Private-Token': ACCESS_TOKEN},
            params={'page': page, 'per_page': 100}  # Adjust per_page as needed
        )
        if response.status_code != 200:
            print(f"Error fetching projects: {response.text}")
            break
        data = response.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    return projects

# Function to get the container repositories for a project
def get_container_repositories(project_id):
    repositories = []
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/container_registry/repositories',
            headers={'Private-Token': ACCESS_TOKEN},
            params={'page': page, 'per_page': 100}
        )
        if response.status_code != 200:
            print(f"Error fetching repositories for project {project_id}: {response.text}")
            break
        data = response.json()
        if not data:
            break
        repositories.extend(data)
        page += 1
    return repositories

# Function to get tags for a container repository
def get_tags(project_id, repository_id):
    tags = []
    page = 1
    while True:
        response = requests.get(
            REGISTRY_API.format(project_id=project_id, repository_id=repository_id),
            headers={'Private-Token': ACCESS_TOKEN},
            params={'page': page, 'per_page': 100}
        )
        if response.status_code != 200:
            print(f"Error fetching tags for repository {repository_id}: {response.text}")
            break
        data = response.json()
        if not data:
            break
        tags.extend(data)
        page += 1
    return tags

# Main function to list tags for all repositories across all projects
def list_tags_for_all_repositories():
    projects = get_projects()
    for project in projects:
        print(f"\nProject: {project['name']} (ID: {project['id']})")
        repositories = get_container_repositories(project['id'])
        for repository in repositories:
            print(f"  Repository: {repository['name']} (ID: {repository['id']})")
            tags = get_tags(project['id'], repository['id'])
            if tags:
                print(f"    Tags:")
                for tag in tags:
                    print(f"      - {tag['name']}")
            else:
                print("    No tags found.")

if __name__ == '__main__':
    list_tags_for_all_repositories()
