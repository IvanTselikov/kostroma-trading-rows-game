from project_controller import Project
import sys

if __name__ == '__main__':
    try:
        project = Project(sys.argv[-1])
        if len(sys.argv) == 3 or len(sys.argv) == 4 and sys.argv[0] == 'python':
            # project_controller.exe -c path
            # нужно скомпилировать проект
            project.run(recompile=True, new_console=False)
        elif len(sys.argv) == 2 or len(sys.argv) == 3 and sys.argv[0] == 'python':
            # project_controller.exe path
            # нужно запустить уже скомпилированный проект
            project.run(recompile=False, new_console=False)
    except Exception as e:
        print(e)
        input('Для выхода нажмите любую клавишу...')
        sys.exit(0)
