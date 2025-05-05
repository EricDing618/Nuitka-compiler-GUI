import subprocess
from typing import List, Callable
import os
import sys
import re
import colorama
import importlib
import pkg_resources
import io
import threading
import queue

# Initialize colorama with no output wrapping
colorama.init(wrap=False)

class NuitkaCompiler:
    REQUIRED_PACKAGES = {
        'nuitka': '2.0.0',
        'colorama': '0.4.6',
        'PyQt6': '6.4.0'
    }

    @staticmethod
    def verify_dependencies(output_callback: Callable[[str], None]) -> bool:
        """Verify all required packages are installed with correct versions"""
        try:
            for package, min_version in NuitkaCompiler.REQUIRED_PACKAGES.items():
                try:
                    installed_version = pkg_resources.get_distribution(package).version
                    if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(min_version):
                        output_callback(f"Warning: {package} version {installed_version} is older than required {min_version}\n")
                        return False
                except pkg_resources.DistributionNotFound:
                    output_callback(f"Error: Required package {package} is not installed\n")
                    return False
            return True
        except Exception as e:
            output_callback(f"Error checking dependencies: {str(e)}\n")
            return False

    @staticmethod
    def get_python_path() -> str:
        """Get the correct Python interpreter path"""
        if sys.platform == "win32":
            python_exe = os.path.join(sys.prefix, "python.exe")
            if not os.path.exists(python_exe):
                python_exe = sys.executable
            return python_exe
        return sys.executable

    @staticmethod
    def _stream_reader(stream, output_queue: queue.Queue):
        """Read from a stream and put lines into a queue"""
        try:
            for line in iter(stream.readline, ''):
                output_queue.put(line)
        except (IOError, UnicodeDecodeError):
            pass
        finally:
            stream.close()

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
        try:
            # Verify dependencies first
            if not NuitkaCompiler.verify_dependencies(output_callback):
                return False, "Missing or outdated dependencies"

            # Validate file path
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            # Normalize path to avoid encoding issues
            file_path = os.path.abspath(file_path)
            
            # Get correct Python interpreter path
            python_exe = NuitkaCompiler.get_python_path()
            command = [python_exe, "-m", "nuitka"]
            
            # Disable color output from Nuitka to avoid ANSI issues
            os.environ['NUITKA_DISABLE_COLORS'] = '1'
            
            # Add verbose output
            command.append("--verbose")
            
            # Add show-progress if requested
            if options.get('show_progress'):
                command.append("--show-progress")
                command.append("--show-modules")
            
            # Add show-memory if requested
            if options.get('show_memory'):
                command.append("--show-memory")
            
            # Basic options
            if options.get('standalone'):
                command.append("--standalone")
            if options.get('onefile'):
                command.append("--onefile")
            if options.get('remove_output'):
                command.append("--remove-output")
            if options.get('follow_imports'):
                command.append("--follow-imports")
                
            # Advanced options
            if options.get('windows_icon_path'):
                command.extend(["--windows-icon-from-ico="+options['windows_icon_path']])
            if options.get('company_name'):
                command.extend(["--company-name="+options['company_name']])
            if options.get('product_name'):
                command.extend(["--product-name="+options['product_name']])
            if options.get('file_version'):
                command.extend(["--file-version="+options['file_version']])
            if options.get('output_dir'):
                # Ensure output directory exists
                os.makedirs(options['output_dir'], exist_ok=True)
                command.append(f"--output-dir={options['output_dir']}")
            if options.get('python_flag'):
                flag = options['python_flag']
                if flag:  # Only add flag if it's not empty
                    command.append(f"--python-flag=-{flag}")
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
                        command.extend(["--include-package="+package.strip()])
            if options.get('include_module'):
                for module in options['include_module'].split(','):
                    if module.strip():
                        command.extend(["--include-module="+module.strip()])
            
            # Build name option
            if options.get('build_name'):
                command.append(f"--output-filename={options['build_name']}")
            
            # Add C compiler if specified
            if options.get('c_compiler'):
                command.extend(["--mingw64" if options['c_compiler'] == 'mingw64' else
                              "--msvc" if options['c_compiler'] == 'msvc' else 
                              "--mingw32" if options['c_compiler'] == 'mingw32' else
                              "--clang" if options['c_compiler'] == 'clang' else ""])
            
            command.append(file_path)
            
            output_callback("Starting compilation with command:\n" + " ".join(command) + "\n")
            
            # Add environment variables for better compatibility
            env = dict(os.environ)
            env.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONLEGACYWINDOWSFSENCODING': '0',
                'PYTHONLEGACYWINDOWSSTDIO': '0',
                'PYTHONDONTWRITEBYTECODE': '1'
            })

            # Create process with no ANSI color codes
            startupinfo = None
            if sys.platform == "win32":
                # Hide console window on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Create output queue for thread-safe reading
            output_queue = queue.Queue()
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                shell=False,
                encoding='utf-8',
                errors='replace',
                startupinfo=startupinfo,
                env=env
            )

            # Start output reader threads
            stdout_thread = threading.Thread(
                target=NuitkaCompiler._stream_reader,
                args=(process.stdout, output_queue)
            )
            stderr_thread = threading.Thread(
                target=NuitkaCompiler._stream_reader,
                args=(process.stderr, output_queue)
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            # Track progress patterns
            progress_patterns = {
                r"Compiling module": "Compiling modules...",
                r"Linking": "Linking executable...",
                r"Creating executable": "Creating final executable...",
                r"Copying dependency": "Copying dependencies...",
                r"Packaging": "Packaging files..."
            }

            # Process output from queue
            while process.poll() is None or not output_queue.empty():
                try:
                    # Get output with timeout to prevent hanging
                    try:
                        line = output_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    # Strip ANSI codes
                    clean_line = re.sub(r'\033\[[0-9;]*[mGKH]', '', line)

                    # Check for progress patterns
                    for pattern, message in progress_patterns.items():
                        if re.search(pattern, clean_line):
                            output_callback(f"\n{message}\n")
                            progress_callback()
                            break
                    
                    # Filter and output the line
                    if not any(skip in clean_line for skip in ['INFO:', 'DEBUG:', 'TRACE:']):
                        output_callback(clean_line)

                except Exception as e:
                    # Log error but continue processing
                    print(f"Error processing output: {str(e)}", file=sys.stderr)
                    continue

            # Wait for reader threads to finish
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

            # Get the return code
            return_code = process.poll()

            if return_code == 0:
                output_callback("\nCompilation completed successfully!\n")
                
                # Show output location
                output_dir = options.get('output_dir', os.path.dirname(file_path))
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                if options.get('onefile'):
                    exe_name = f"{base_name}.exe" if sys.platform == "win32" else base_name
                    output_callback(f"\nExecutable created: {os.path.join(output_dir, exe_name)}\n")
                else:
                    output_callback(f"\nOutput directory: {output_dir}\n")
                
                return True, ""
            else:
                error_msg = "Compilation failed with return code: " + str(return_code)
                output_callback("\n" + error_msg + "\n")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Compilation error: {str(e)}"
            output_callback("\n" + error_msg + "\n")
            return False, error_msg
        finally:
            # Clean up colorama
            colorama.deinit()
