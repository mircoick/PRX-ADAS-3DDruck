# Praxissemester: Machbarkeitsanalyse zum System-Update eines 3D-Industriedruckers

In diesem Repository ist die technische und wirtschaftliche Machbarkeit eines System-Updates (Hardware & Software) für den 3D-Industriedrucker **3Dgence INDUSTRY F421** dokumentiert. Im Rahmen des Praxissemesters bei der **Airbus DS Airborne Solutions GmbH** wurde die Migration auf moderne Open-Source-Komponenten untersucht.

---

## Dokumentation & Berichte

Die offiziellen Berichte und Ausarbeitungen stehen hier zur Verfügung:
- **Zwischenbericht:** 
  [&#128196; PDF](docs/Zwischen_Mirco_Ick_5312533.pdf)

- **Abschlussbericht:** 
  [&#128196; PDF](docs/prx_final_report.pdf) &nbsp;|&nbsp; [&#127760; Webseite](https://mircoick.github.io/PRX-ADAS-3DDruck/prx_final_report.html)

---

## Repository-Struktur

Das Repository gliedert sich in folgende Hauptkomponenten:

<table>
  <thead>
    <tr>
      <th>Verzeichnis</th>
      <th>Beschreibung</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="docs/"><code>docs/</code></a></td>
      <td>Exportdateien des Quarto-Quellcodes u. a. die Bachelor-Thesis.</td>
    </tr>
    <tr>
      <td><a href="hardware_doc/"><code>hardware_doc/</code></a></td>
      <td>Ergänzende Projektdokumentationen, Pinbelegungen und Sensor-Spezifikationen.
    </tr>
    </tr>
    <tr>
      <td><a href="info/"><code>info/</code></a></td>
      <td>Datenblätter und Firmeninfos.</td>
    </tr>
    <tr>
      <td><a href="kicad/"><code>kicad/</code></a></td>
      <td>Idee einer Adapterplatine mit Schaltplänen.</td>
    </tr>
    <tr>
      <td><a href="klipper/"><code>klipper/</code></a></td>
      <td>Konfigurationsdateien, Makros und Firmware-Anpassungen für Klipper.</td>
    </tr>
    <tr>
      <td><a href="print_data/"><code>print_data/</code></a></td>
      <td>Testdrucke, Slicer-Profile und druckspezifische Daten.</td>
    </tr>
    <tr>
      <td><a href="python/"><code>python/</code></a></td>
      <td>Skripte zur isolierten Sensor- und Hardware-Ansteuerung.</td>
    </tr>
    <tr>
      <td><a href="report/"><code>report/</code></a></td>
      <td>Quarto-Quellcode (<code>.qmd</code>) und Build-Artefakte der Berichte.</td>
    </tr>
  </tbody>
</table>

---

## Systemdaten & Key Facts

* **Hersteller:** 3Dgence
* **Modell:** INDUSTRY F421
* **Kernziele:** Evaluierung neuer Steuerungs-Hardware (u. a. Mainboard- und Sensor-Integration), Firmware-Umstellung auf Klipper sowie Analyse der technischen und wirtschaftlichen Realisierbarkeit.
