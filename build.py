import site
import PyInstaller.__main__
import sys

def main() -> None:
    executable_name = sys.argv[1]
    sitepackage_dir = site.getsitepackages()[-1]
    PyInstaller.__main__.run([
        '--onefile',        
        '--name',
        f'{executable_name}',
        '--add-data',
        f'{sitepackage_dir}/license_expression/data/scancode-licensedb-index.json:./license_expression/data',
        '--add-data',
        f'{sitepackage_dir}/spdx_tools/spdx/parser/tagvalue/*:./spdx_tools/spdx/parser/tagvalue',
        'src/opossum_lib/cli.py',
    ])

if __name__ == "__main__":
    main()
