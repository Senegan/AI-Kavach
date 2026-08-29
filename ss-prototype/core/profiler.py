from pathlib import Path


class EnvironmentProfiler:

    EXTENSIONS = {
        ".c": "C",
        ".h": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".hpp": "C++",
        ".py": "Python",
    }

    def profile(self, target):

        target = Path(target)

        files = list(target.rglob("*")) if target.is_dir() else [target]

        languages = set()
        source_files = []

        for file in files:
            if not file.is_file():
                continue

            language = self.EXTENSIONS.get(file.suffix.lower())

            if language:
                languages.add(language)
                source_files.append(str(file))

        build_system = self.detect_build_system(target)

        return {
            "languages": sorted(languages),
            "source_files": source_files,
            "build_system": build_system,
            "has_c_compiler": self.command_exists("gcc"),
            "has_cpp_compiler": self.command_exists("g++"),
            "has_python": self.command_exists("python3"),
        }

    def detect_build_system(self, target):

        if not target.is_dir():
            return "single-file"

        files = {p.name for p in target.iterdir()}

        if "CMakeLists.txt" in files:
            return "cmake"

        if "Makefile" in files:
            return "make"

        if "pyproject.toml" in files:
            return "python-pyproject"

        if "requirements.txt" in files:
            return "python-requirements"

        return "unknown"

    @staticmethod
    def command_exists(command):
        import shutil
        return shutil.which(command) is not None
