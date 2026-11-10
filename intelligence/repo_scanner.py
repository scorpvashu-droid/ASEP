import os
from pathlib import Path

class LocalRepository:
    "scans and validates a local project folder using manual initialization"

    ignorefiles=[".git", ".svn", ".hg", "__pycache__", ".venv", "venv", "env", "node_modules", ".pytest_cache", ".mypy_cache", ".idea", ".vscode"]
    #IGNORE={ignorefiles}
    IGNORE=set(ignorefiles)

    def setup_path(self, repo_path: str|Path, extra_skips: set[str]|None=None):
        self.repo_location=Path(repo_path).expanduser().resolve()

        if extra_skips is None:
            skip_folders=set()
        else:
            skip_folders=extra_skips

        self._skip_folders=self.IGNORE.union(skip_folders)
        self.check_valid()
        return self

    def check_valid(self)->None: #none is return type

        #check operating system if this folder exists??
        if not self.repo_location.exists():
            raise FileNotFoundError(f"File does not exists: {self.repo_location}")
        #check if given path is a folder or any .img or .png
        if not self.repo_location.is_dir():
            raise NotADirectoryError(f"provided path is not a folder: {self.repo_location}")

    @property
    def isit_a_git_repo(self)->bool:
            git_path = self.repo_location / ".git"

            #print("Checking path:", self.repo_location)
            #print("Git path:", git_path)
            #print("Git exists:", git_path.exists())
            #print("Git is directory:", git_path.is_dir())

            return git_path.is_dir()    
        #return (self.repo_location/".git").is_dir()
        #".git" basically add .git by end of file path to check if it exists
        #example user/destop/my_app is file path 
        #it adds .git by end of this to check if it exists

    def get_all_files(self)->list[Path]:
        #take relative paths skipping ignore folders
        all_files=[]
        """
        os.walks directly walks into repo_location and on each folder it touch.
        It does 3 things:
        current root: full path of directory
        subfolder: list of directory inside current_root 
        file_names: a list of file inside current_root
        """
        for current_root, subfolders, file_names in os.walk(self.repo_location):
            subfolders[:] = [
                folder for folder in subfolders
                if folder not in self._skip_folders and not folder.startswith(".")
            ]
            relative_folder=Path(current_root).relative_to(self.repo_location)

            for file in file_names:
                if file in self._skip_folders or file.startswith("."):
                    continue
                all_files.append(relative_folder/file)
        return all_files 

    def get_summary(self)->dict:
        #gather files into a list of dict
        file_list=list(self.get_all_files())
        return{
            "root_path": str(self.repo_location),
            "is_git": self.isit_a_git_repo,
            "total_files": len(file_list),
        }

if __name__=="__main__":
    import sys
    if len(sys.argv)>1:
        path_input=sys.argv[1]
    else:
        path_input="."

    try:
        repo=LocalRepository()
        repo.setup_path(path_input)
        summary_data=repo.get_summary()

        print(f"Repo loaded: {summary_data['root_path']}")
        print(f"Git Repo: {summary_data['is_git']}")
        print(f"Total files: {summary_data['total_files']}")
        """
        for file in repo.get_all_files():
            print(file)
        """
    except(FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
        
