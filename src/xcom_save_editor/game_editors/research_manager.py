"""
Research manager for handling research projects in OpenXCom save files.
"""
from typing import Any, Dict, List, Optional, Tuple
from .base_manager import BaseManager


class ResearchProject:
    """Represents a research project."""
    
    def __init__(self, project_data: Dict[str, Any], base_index: int, project_index: int):
        self.data = project_data
        self.base_index = base_index
        self.project_index = project_index
    
    @property
    def name(self) -> str:
        return self.data.get('project', 'Unknown Project')
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        name = self.name.replace('STR_', '').replace('_', ' ')
        return name.title()
    
    @property
    def assigned_scientists(self) -> int:
        return self.data.get('assigned', 0)
    
    @property
    def time_spent(self) -> int:
        return self.data.get('spent', 0)
    
    @property
    def total_cost(self) -> int:
        return self.data.get('cost', 0)
    
    @property
    def time_remaining(self) -> int:
        return max(0, self.total_cost - self.time_spent)
    
    @property
    def progress_percentage(self) -> float:
        if self.total_cost == 0:
            return 100.0
        return (self.time_spent / self.total_cost) * 100
    
    @property
    def is_completed(self) -> bool:
        return self.time_spent >= self.total_cost
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.progress_percentage:.1f}% complete)"


class ResearchManager(BaseManager):
    """Manages research projects across all bases."""
    
    def get_all_research_projects(self) -> List[ResearchProject]:
        """Get all active research projects from all bases."""
        projects = []
        bases = self.get_current_value('bases')
        
        if not isinstance(bases, list):
            return projects
        
        for base_index, base in enumerate(bases):
            if not isinstance(base, dict) or 'research' not in base:
                continue
            
            research_list = base['research']
            if not isinstance(research_list, list):
                continue
            
            for project_index, project_data in enumerate(research_list):
                if isinstance(project_data, dict):
                    project = ResearchProject(project_data, base_index, project_index)
                    projects.append(project)
        
        return projects
    
    def get_active_research_projects(self) -> List[ResearchProject]:
        """Get only incomplete research projects."""
        return [proj for proj in self.get_all_research_projects() if not proj.is_completed]
    
    def get_completed_research_projects(self) -> List[ResearchProject]:
        """Get completed research projects."""
        return [proj for proj in self.get_all_research_projects() if proj.is_completed]
    
    def get_research_by_base(self, base_index: int) -> List[ResearchProject]:
        """Get research projects for a specific base."""
        all_projects = self.get_all_research_projects()
        return [proj for proj in all_projects if proj.base_index == base_index]
    
    def complete_research_project(self, project: ResearchProject) -> None:
        """
        Complete a specific research project.
        
        Args:
            project: The research project to complete
        """
        project_path = f"bases.{project.base_index}.research.{project.project_index}.spent"
        self.set_value(project_path, project.total_cost)
    
    def complete_all_research_projects(self) -> int:
        """
        Complete all active research projects.
        
        Returns:
            Number of projects completed
        """
        active_projects = self.get_active_research_projects()
        
        for project in active_projects:
            self.complete_research_project(project)
        
        return len(active_projects)
    
    def complete_research_projects_by_base(self, base_index: int) -> int:
        """
        Complete all research projects in a specific base.
        
        Args:
            base_index: Index of the base
            
        Returns:
            Number of projects completed
        """
        base_projects = self.get_research_by_base(base_index)
        active_projects = [proj for proj in base_projects if not proj.is_completed]
        
        for project in active_projects:
            self.complete_research_project(project)
        
        return len(active_projects)
    
    def set_research_progress(self, project: ResearchProject, progress_percentage: float) -> None:
        """
        Set research progress to a specific percentage.
        
        Args:
            project: The research project
            progress_percentage: Progress as percentage (0-100)
        """
        progress_percentage = max(0, min(100, progress_percentage))
        new_spent = int((progress_percentage / 100) * project.total_cost)
        
        project_path = f"bases.{project.base_index}.research.{project.project_index}.spent"
        self.set_value(project_path, new_spent)
    
    def get_base_names(self) -> List[str]:
        """Get names of all bases."""
        bases = self.get_current_value('bases')
        if not isinstance(bases, list):
            return []
        
        names = []
        for i, base in enumerate(bases):
            if isinstance(base, dict) and 'name' in base:
                names.append(base['name'])
            else:
                names.append(f"Base {i + 1}")
        
        return names
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Get a summary of research status across all bases."""
        all_projects = self.get_all_research_projects()
        active_projects = self.get_active_research_projects()
        
        base_names = self.get_base_names()
        base_summaries = []
        
        for i, base_name in enumerate(base_names):
            base_projects = self.get_research_by_base(i)
            base_active = [proj for proj in base_projects if not proj.is_completed]
            
            base_summaries.append({
                'name': base_name,
                'total_projects': len(base_projects),
                'active_projects': len(base_active),
                'completed_projects': len(base_projects) - len(base_active)
            })
        
        return {
            'total_projects': len(all_projects),
            'active_projects': len(active_projects),
            'completed_projects': len(all_projects) - len(active_projects),
            'bases': base_summaries
        }
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of changes made to research."""
        if not self.has_changes():
            return {'modified': {}, 'added': {}, 'removed': {}}
        
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # Compare original and current research states
        original_projects = ResearchManager(self.original_data).get_all_research_projects()
        current_projects = self.get_all_research_projects()
        
        completed_count = 0
        for current_proj in current_projects:
            # Find corresponding original project
            original_proj = None
            for orig_proj in original_projects:
                if (orig_proj.base_index == current_proj.base_index and 
                    orig_proj.project_index == current_proj.project_index):
                    original_proj = orig_proj
                    break
            
            if original_proj and original_proj.time_spent != current_proj.time_spent:
                if not original_proj.is_completed and current_proj.is_completed:
                    completed_count += 1
        
        if completed_count > 0:
            changes['modified']['research_completed'] = {
                'original': f"Research projects in progress",
                'current': f"{completed_count} research project(s) completed",
                'field': 'Research Progress'
            }
        
        return changes