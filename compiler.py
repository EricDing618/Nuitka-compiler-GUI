import subprocess
from typing import List, Callable
import os

class NuitkaCompiler:
    @staticmethod
    def compile(
        file_path: str,
        options: dict,
        output_callback: Callable[[str], None],
        progress_callback: Callable[[], None]
    ) -> tuple[bool, str]:
        """
        Compile the Python file using Nuitka with the specified options
        """
        command = ["python", "-m", "nuitka"]
        
        # Basic options
        if options.get('standalone'):
            command.append("--standalone")
        if options.get('onefile'):
            command.append("--onefile")
        if options.get('remove_output'):
            command.append("--remove-output")
        if options.get('follow_imports'):
            command.append("--follow-imports")
        if options.get('show_progress'):
            command.append("--show-progress")
        if options.get('show_memory'):
            command.append("--show-memory")
            
        # Advanced options
        if options.get('windows_icon_path'):
            command.extend(["--windows-icon-from-ico", options['windows_icon_path']])
        if options.get('company_name'):
            command.extend(["--company-name", options['company_name']])
        if options.get('product_name'):
            command.extend(["--product-name", options['product_name']])
        if options.get('file_version'):
            command.extend(["--file-version", options['file_version']])
        if options.get('output_dir'):
            command.extend(["--output-dir", options['output_dir']])
        if options.get('python_flag'):
            command.extend(["--python-flag", options['python_flag']])
        if options.get('enable_console'):
            command.append("--enable-console")
        else:
            command.append("--disable-console")
        if options.get('windows_uac_admin'):
            command.append("--windows-uac-admin")
        if options.get('windows_uac_uiaccess'):
            command.append("--windows-uac-uiaccess")
        if options.get('include_package'):
            for package in options['include_package'].split(','):
                if package.strip():
                    command.extend(["--include-package", package.strip()])
        if options.get('include_module'):
            for module in options['include_module'].split(','):
                if module.strip():
                    command.extend(["--include-module", module.strip()])
        
        command.append(file_path)
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_callback(output)
                progress_callback()
                
            return process.returncode == 0, ""
            
        except Exception as e:
            return False, str(e)
