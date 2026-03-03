from sqlmodel import SQLModel, Field


class ProjectTeam(SQLModel, table=True):
    __tablename__ = "project_team"
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    team_id: int = Field(foreign_key="team.id", primary_key=True)
