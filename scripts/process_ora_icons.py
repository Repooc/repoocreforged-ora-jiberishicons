import xml.etree.ElementTree as ET
import os
import zipfile
import shutil

def get_output_folder(ora_file):
    """Extract the output folder name from the .ora filename."""
    # Get the part after the last hyphen, before .ora
    folder_name = ora_file.rsplit('-', 1)[-1].replace('.ora', '')
    # Convert to lowercase and replace underscores with hyphens
    return folder_name.lower().replace('_', '-')

def process_ora_file(ora_file):
    """Process an .ora file: unzip, rename files, and cleanup."""
    if not os.path.exists(ora_file):
        print(f"Error: File not found: {ora_file}")
        return False

    # Get output folder name from .ora filename
    output_folder = get_output_folder(ora_file)
    
    # Create unique temp directory for this ora file
    temp_dir = f"temp-{output_folder}"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Unzip .ora file
        with zipfile.ZipFile(ora_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        os.makedirs(output_folder, exist_ok=True)

        # Process stack.xml
        xml_file = os.path.join(temp_dir, "stack.xml")
        if not os.path.exists(xml_file):
            raise FileNotFoundError(f"stack.xml not found in {ora_file}")

        # Parse and process files
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for stack in root.findall('.//stack'):
            for layer in stack.findall('.//layer'):
                name = layer.get('name')
                src = layer.get('src')

                if name and src:
                    src_path = os.path.join(temp_dir, src)
                    _, ext = os.path.splitext(src)
                    dest_file = os.path.join(output_folder, f"{name}{ext}")

                    if os.path.exists(src_path):
                        shutil.copy2(src_path, dest_file)
                        print(f"Processed: {name}{ext}")
                    else:
                        print(f"Warning: Source file not found: {src_path}")

        return True

    except Exception as e:
        print(f"Error processing {ora_file}: {e}")
        return False

    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    """Main function to process all .ora files."""
    print("\nStarting main processing...")
    
    # Find all .ora files in current directory
    ora_files = [f for f in os.listdir('.') if f.endswith('.ora')]
    
    if not ora_files:
        print("No .ora files found in current directory")
        return False, []

    print(f"Found {len(ora_files)} .ora files:", ora_files)
    
    success = True
    processed_folders = set()  # Use a set to avoid duplicates
    
    for ora_file in ora_files:
        print(f"\nProcessing {ora_file}...")
        output_folder = get_output_folder(ora_file)
        processed_folders.add(output_folder)
        if not process_ora_file(ora_file):
            success = False

    # Output folders in a format that GitHub Actions can parse
    print("::set-output name=processed_folders::" + " ".join(processed_folders))
    return success, list(processed_folders)

if __name__ == "__main__":
    success, folders = main()
    print("\nProcessed folders:", folders)
    print("Success:", success)
