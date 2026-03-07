import sys
from sqlmodel import Session, select
import requests
import os

# Put DB context in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import engine
from models.user_model import User
from models.project_model import Project
from models.team_model import Team
from models.project_team_model import ProjectTeam
from models.team_member_model import TeamMember
from auth.security import get_password_hash

BASE_URL = "http://127.0.0.1:8011"

def main():
    print("=== TASKPIE API DIAGNOSTIC SCRIPT ===")
    
    # 1. Inspect local database safely to get a user
    with Session(engine) as session:
        user = session.exec(select(User)).first()
        if not user:
            print("No users found in database!")
            return
            
        print(f"-> Found testing user: {user.email}")
        
        # Test projects and teams linked to this user
        db_projects = session.exec(select(Project).where(Project.owner_id == user.id)).all()
        print(f"-> User owns {len(db_projects)} projects")
        
        db_memberships = session.exec(select(TeamMember).where(TeamMember.user_id == user.id)).all()
        print(f"-> User is in {len(db_memberships)} teams")
        
        # Just manually create an access token for this user so we can test the API as them
        from auth.jwt_handler import create_access_token
        access_token = create_access_token(user_id=user.id)
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        print("\n=== PINGING SECURE API ENDPOINTS ===")
        # Get my teams via API
        resp = requests.get(f"{BASE_URL}/teams/", headers=headers)
        teams = resp.json()
        print(f"GET /teams/ => Status {resp.status_code}")
        
        # Get my projects via API
        resp = requests.get(f"{BASE_URL}/projects/", headers=headers)
        projects = resp.json()
        print(f"GET /projects/ => Status {resp.status_code}")
        
        for project in projects:
            print(f"\n- Testing project: {project['name']} (ID {project['id']})")
            
            # Fetch members for this project
            resp_m = requests.get(f"{BASE_URL}/projects/{project['id']}/members", headers=headers)
            print(f"  GET /projects/{project['id']}/members => Status {resp_m.status_code}")
            
            if resp_m.status_code == 200:
                members = resp_m.json()
                print(f"  -> Returned {len(members)} team members that can be assigned.")
            else:
                print(f"  -> ERRROR: {resp_m.text}")

        # Check existing relations in DB that SHOULD be visible
        for team in teams:
            team_id = team['id']
            links = session.exec(select(ProjectTeam).where(ProjectTeam.team_id == team_id)).all()
            print(f"\n- DB Links: Team '{team['name']}' is linked to {len(links)} projects.")
            for link in links:
                print(f"  -> Project {link.project_id}")

if __name__ == "__main__":
    main()
