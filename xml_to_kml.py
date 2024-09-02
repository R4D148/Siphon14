import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_mace_xml(xml_file):
    """
    Parse the MACE Route XML file and extract waypoints.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return []

    waypoints = []

    # Navigate to the waypoints in the XML structure
    for waypoint in root.findall('.//XMLSerializableWaypoint'):
        try:
            geo_point = waypoint.find('.//currentGeoPoint')
            lat = float(geo_point.find('latitude').text)
            lon = float(geo_point.find('longitude').text)
            alt = float(geo_point.find('altitudeAboveGroundLevel_Feet').text)

            ordinal = waypoint.find('waypointOrdinalNumber').text
            ordinal = int(ordinal) if ordinal is not None else None

            waypoints.append((ordinal, lat, lon, alt))
        except Exception as e:
            print(f"Error processing waypoint: {e}. Waypoint data: {ET.tostring(waypoint, encoding='unicode')}")
            continue

    return waypoints

def convert_to_kml(waypoints, kml_file):
    """
    Convert waypoints to KML format and save to a file.
    """
    try:
        with open(kml_file, 'w') as file:
            # KML Header
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
            file.write('  <Document>\n')
            file.write('    <name>MACE Route</name>\n')

            # Iterate over waypoints and create placemarks
            for ordinal, lat, lon, alt in waypoints:
                file.write('    <Placemark>\n')
                file.write(f'      <name>Waypoint {ordinal}</name>\n')
                file.write('      <description>\n')
                file.write(f'        <![CDATA[Altitude: {alt:.2f} feet]]>\n')
                file.write('      </description>\n')
                file.write('      <Point>\n')
                file.write(f'        <coordinates>{lon},{lat},{alt:.2f}</coordinates>\n')
                file.write('      </Point>\n')
                file.write('    </Placemark>\n')

            # KML Footer
            file.write('  </Document>\n')
            file.write('</kml>\n')

            print(f"KML file successfully created: {kml_file}")
    except IOError as e:
        print(f"Error writing to KML file: {e}")

def select_and_convert_xml_to_kml():
    """
    Opens a file dialog to select the XML route file and a save dialog to specify the KML file.
    """
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select the XML file
    xml_file = filedialog.askopenfilename(
        title="Select XML Route File",
        filetypes=(("XML files", "*.xml"), ("All files", "*.*"))
    )

    if not xml_file:
        messagebox.showwarning("No file selected", "Please select a valid XML file.")
        return

    # Open a save dialog to specify the KML file destination
    kml_file = filedialog.asksaveasfilename(
        title="Save KML File As",
        defaultextension=".kml",
        filetypes=(("KML files", "*.kml"), ("All files", "*.*"))
    )

    if not kml_file:
        messagebox.showwarning("No save location", "Please specify a valid save location.")
        return

    try:
        waypoints = parse_mace_xml(xml_file)
        if not waypoints:
            messagebox.showerror("Error", "No waypoints were found or processed. Check the XML structure.")
            return

        convert_to_kml(waypoints, kml_file)
        messagebox.showinfo("Success", f"KML file created: {kml_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion:\n{e}")

if __name__ == "__main__":
    select_and_convert_xml_to_kml()
