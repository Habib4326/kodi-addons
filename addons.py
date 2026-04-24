import os
import hashlib
import zipfile
import shutil
import xml.etree.ElementTree as ET

OUTPUT_XML = "addons.xml"
OUTPUT_MD5 = "addons.xml.md5"
ZIPS_DIR = "zips"


def clean_xml_header(content):
    return content.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()


def get_addon_info(folder):
    addon_xml_path = os.path.join(folder, "addon.xml")

    if not os.path.exists(addon_xml_path):
        return None, None, None

    try:
        tree = ET.parse(addon_xml_path)
        root = tree.getroot()

        addon_id = root.attrib.get("id")
        version = root.attrib.get("version")

        with open(addon_xml_path, "r", encoding="utf-8") as f:
            content = clean_xml_header(f.read())

        return addon_id, version, content

    except Exception as e:
        print(f"❌ Skipped (broken): {folder} → {e}")
        return None, None, None


def zip_addon(folder, addon_id, version):
    zip_folder = os.path.join(ZIPS_DIR, addon_id)
    os.makedirs(zip_folder, exist_ok=True)

    zip_name = f"{addon_id}-{version}.zip"
    zip_path = os.path.join(zip_folder, zip_name)

    # Remove old zips
    for f in os.listdir(zip_folder):
        if f.endswith(".zip"):
            os.remove(os.path.join(zip_folder, f))

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.path.dirname(folder))
                z.write(full_path, rel_path)

    print(f"📦 Zipped: {zip_name}")


def generate_addons_xml(addons_data):
    content = '<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n\n'

    for addon_xml in addons_data:
        content += addon_xml + "\n\n"

    content += "</addons>\n"

    with open(OUTPUT_XML, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ addons.xml generated")


def generate_md5():
    with open(OUTPUT_XML, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()

    with open(OUTPUT_MD5, "w") as f:
        f.write(md5)

    print("✅ addons.xml.md5 generated")


def main():
    if not os.path.exists(ZIPS_DIR):
        os.makedirs(ZIPS_DIR)

    addons_data = []

    for folder in sorted(os.listdir(".")):
        if os.path.isdir(folder) and folder not in ["zips", "__pycache__"]:
            addon_id, version, xml_content = get_addon_info(folder)

            if addon_id and version:
                print(f"✔ Processing: {addon_id} ({version})")

                zip_addon(folder, addon_id, version)
                addons_data.append(xml_content)

    generate_addons_xml(addons_data)
    generate_md5()

    print("\n🎉 Repo Build Complete!")


if __name__ == "__main__":
    main()