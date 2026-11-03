# Abschlussbericht Praxissemester
Mirco Ick
2026-11-03

<div style="
  position: absolute;
  top: 30px;
  right: 6%;
  width: 15%;
  max-width: 300px;
  min-width: 100px;
  z-index: 10;
  pointer-events: none;
">

<img src="init/Airbus.png"
       style="width: 100%; height: auto; display: block;">

</div>

<div style="
  position: absolute;
  top: 120px;
  right: 6%;
  width: 15%;
  max-width: 300px;
  min-width: 100px;
  z-index: 10;
  pointer-events: none;
">

<img src="init/Logo_groß.png"
       style="width: 100%; height: auto; display: block;">

</div>

# Einleitung

Der industrielle 3D-Druck gewinnt in modernen Fertigungs- und
Instandhaltungsprozessen zunehmend an Bedeutung, da er eine flexible
Herstellung von Prototypen sowie Sonderlösungen ermöglicht. Bei der
Airbus DS Airborne Solutions GmbH in Bremen, einem eigenständigen
Tochterunternehmen der Airbus Defence and Space, dessen Wurzeln auf die
Gründung von Focke-Wulf im Jahr 1924 zurückgehen, nimmt dieses
Fertigungsverfahren eine zentrale Rolle als Support Prozess ein. Im
Fachbereich Produktion und Instandhaltung (Production and Maintenance,
P&M) wird der 3D-Druck eingesetzt, um spezielle Bauteile und Prototypen
für zivile sowie militärische Anwendungen zeitnah zu realisieren.

<div id="fig-site">

<img src="pics/adas.jpg" style="width:75.0%" />

Abbildung 1: ADAS Komplex (Peper & Söhne 2026)

</div>

Neben den im Privatgebrauch üblichen 3D-Druckern werden hier auch
industriellen Drucker verwendet. Diese sollen schneller, präziser sowie
vielseitigere 3D-Drucke fertigen können als häuslichen Geräte. Somit
hatte sich die ADAS einen industriellen 3D-Drucker der Marke *3DGence*,
eine Firma die sich auf diese industrie Drucker spezialisiert hat,
beschafft um die bestimmten Anwendungen des Prototypenbaus zu
gewährleisten. Das beschaffte Modell *Industry F421* wies allerdings
kurz nach der Beschaffung erhebliche softwareseitige Probleme auf, die
während des Druckbetriebs zu wiederholten Fehlermeldungen führten und
einen verlässlichen Einsatz erschwerten.

<div id="fig-3dgence">

<div id="fig-ansicht1">

<img src="pics/3dgence-industry-f421-seitlich2.png" id="fig-ansicht1"
style="width:75.0%" data-ref-parent="fig-3dgence" />

(a)

</div>

<div id="fig-ansicht2">

<img src="pics/3dgence-industry-f421-seitlich.png" id="fig-ansicht2"
style="width:75.0%" data-ref-parent="fig-3dgence" />

(b)

</div>

Abbildung 2: 3DGence Industry F421 (3DGence 2026)

</div>

Ziel der vorliegenden Arbeit ist daher die Erstellung einer
Machbarkeitsstudie zur Optimierung bzw. Weiterentwicklung des *3DGence
Industry F421*. Im Rahmen dieser Untersuchung wird analysiert, ob und
wie sich die Systemzuverlässigkeit sowie eventuell die Druckqualität
durch gezielte Anpassungen der Software- sowie Hardwarearchitektur
nachhaltig verbessern lassen. Hierzu werden zunächst die allgemeinen
Grundlagen des 3D-Drucks recherchiert und anschließend versucht die
einzelnen Baugruppen isoliert über Python anzusteuern. Nach den
isolierten Tests wird ein Referenzsystem herangezogen, um die
Ansteuerung der einzelnen Baugruppen zu validieren und die gewonnenen
Erkenntnisse auf das industrielle System zu übertragen. Zur Ansteuerung
wird hier einer Kombination aus einem Einplatinencomputer (Raspberry Pi
5) und ausgewähltem Klipper-Board verwendet. Die Ergebnisse dieser
Machbarkeitsanalyse dienen als fundierte Grundlage für die spätere
Systemintegration im Rahmen einer anschließenden Bachelorarbeit.

# Zeitplanung des Praktikums

Zu Beginn des Praktikums wurde mithilfe des Programmes *MS Project* eine
Zeitachse erstellt, um eine Übersicht über die verschiedenen
Aufgabenbereiche zu verschaffen. Hierbei wurden die zur Verfügung
stehenden 13,5 Wochen Praxissemester in vier größere Arbeitspakete
aufgeteilt. Auf diese Arbeitspakete wird nun in den nachfolgenden
Unterkapiteln näher eingegangen.

Die Arbeitspakete sind:

1.  Grundlagen des 3D-Drucks
2.  Einzelnes Ansteuern verschiedener Bauteile über Python
3.  Umsetzung an einem Referenzsystem
4.  Vergleich mit dem Referenzsystem mit dem 3DGence Industry F421

# Grundlagen des 3D-Drucks

Der 3D-Druck umfasst eine Anzahl von Fertigungsverfahren, bei denen
dreidimensionale Werkstücke durch das fortlaufende, schichtweise
Auftragen von Material aufgebaut werden. Im Gegensatz zu den klassischen
Fertigungsverfahren (wie Fräsen, Drehen oder Bohren), bei denen Material
von einem Rohling abgetragen wird erlaubt das additive Prinzip die
werkzeuglose und flexible Realisierung komplexer Geometrien. (Chan 2026)

## Das Grundprinzip der Schichtbauweise

Unabhängig von der spezifischen Ansteuerungstechnologie und dem
verarbeiteten Werkstoff folgt der Ablauf beim 3D-Druck immer einem
einheitlichen Ablauf.

1.  CAD-Konstruktion: Erstellung eines dreidimensionalen Computermodells
    in einem CAD-System.
2.  Schnittgenerierung (Slicing): Das CAD-Modell wird in ein
    übertragbares Dateiformat (z. B. STL, STEP oder 3MF) exportiert und
    von einer Slicing-Software verarbeitet. Dabei wird das Objekt
    rechnerisch in hunderte bis tausende horizontale Schichten zerlegt
    und der benötigte Steuerungs-Code (G-Code) erzeugt.
3.  Fertigung (Schichtaufbau): Die Druckmechanik setzt den
    Steuerungs-Code um und baut das Bauteil Schicht für Schicht auf
    einer Bauplattform auf.
4.  Nachbearbeitung (Post-Processing): Je nach Verfahren und
    Anforderungen folgen mechanische, thermische oder chemische
    Nachbehandlungsschritte (z. B. Entfernen von Stützstrukturen).

## Übersicht gängiger Fertigungsverfahren

Die DIN EN ISO/ASTM 52900 gliedert die additiven Fertigungsverfahren
nach ihren unterschiedlichen Prinzipien. Bei diesen Verfahren werden die
Werkstücke entweder durch selektives Aufschmelzen, Sintern oder
Aushärten von Material aufgebaut. Die nachfolgende Tabelle gibt einen
Überblick über die gängigen Verfahren, deren typischen Bezeichnungen
sowie die verarbeiteten Werkstoffe und Funktionsprinzipien.

| Verfahrensgruppe | Kürzel | Verarbeiteter Werkstoff | Funktionsprinzip |
|:---|:---|:---|:---|
| **Material Extrusion** | FFF / FDM | Thermoplaste (PLA, ABS, PETG, PEEK, ULTEM) | Ein thermoplastischer Draht (Filament) wird in einem Schmelzkopf verflüssigt und durch eine Düse selektiv aufgetragen. |
| **Vat Photopolymerization** | SLA / DLP | Photopolymer-Harze (Resin) | Flüssiges Kunstharz wird mittels Laserstrahl oder Projektor schichtweise durch UV-Licht punktuell ausgehärtet. |
| **Powder Bed Fusion** | SLS / SLM | Kunststoffe (PA12) oder Metallpulver (Edelstahl, Titan) | Ein feines Pulver wird in einem Pulverbett verteilt und per Laser lokal aufgeschmolzen bzw. versintert. |

Verfahrensübersicht 3D-Druck (Chan 2026)

## Material Extrusion

Weil der zu analysierende Drucker auf dem FFF bzw. FDM Verfahren
basiert, wurde sich mit diesen Verfahren näher beschäftigt. Hier spielen
primär thermoplastische Kunststoffe eine Rolle. Die Auswahl des
Materials bestimmt maßgeblich die thermischen und mechanischen
Eigenschaften des Zielbauteils:

- Standard-Kunststoffe: Unkompliziert zu verarbeiten (z. B. PLA, PETG).
  Geringe Temperaturbeständigkeit, vorrangig für funktionale Prototypen
  und einfache Gehäuse.
- Technische Kunststoffe: Erhöhte Festigkeit und Temperaturbeständigkeit
  (z. B. ABS, ASA, Polyamid/Nylon, PC). Benötigen meist geschlossene,
  beheizte Bauräume zur Vermeidung von Verzug (*Warping*).
- Hochleistungskunststoffe: Werkstoffe wie PEEK, PEKK oder ULTEM bieten
  extreme thermische Beständigkeit, Chemikalienresistenz und mechanische
  Belastbarkeit. Diese Polymere erfordern spezialisierte
  Industriedrucker mit Düsenerwärmungen bis zu $500\,°C$ sowie aktiv
  beheizten Bauräumen ($> 100\,°C$).

# Erste Ansteuerungen

Nachdem nun die Grundlagen des 3D-Drucks recherchiert und verstanden
wurden, konnte an die Bauteilanalyse sowie Ansteuerung erster
entscheidender Komponenten mittels Python gemacht werden. Im ersten
Schritt wurde sich hierbei um die Grundkomponenten eines 3D-Druckers
beschäftigt. Die nachfolgenden Unterkapitel werden näher auf die
Vorgehensweise und die daraus entstehenden Erkenntnisse eingehen. Alle
erwähnten Skripte sowie Datenblätter und ergänzende Dokumentationen sind
dem Github-Repository (Ick 2026) zu entnehmen.

## Grundkomponenten eines 3D-Druckers

Um einen 3D-Drucker betreiben zu können braucht es prinzipiell drei
verschiedene Baugruppen. Diese drei existenziellen Baugruppen sind:

- Step-Motoren (Schrittmotoren): Steuern die horizontale sowie vertikale
  Bewegung des Druckkopfes über die X-/Y-/Z-Achse sowie die Steuerung
  des Filamentausschubs über den Extruder.
- Endschalter: Kommunikation mit den Step-Motoren ob ein Ende der Achsen
  erreicht wurde, um die Bewegung zu stoppen sowie die Position zu
  kalibrieren.
- Heizkomponenten: Erwärmung des Filaments im Hotend (Druckkopf) sowie
  bei Bedarf des Heatbeds (Heizbett).

### Step-Motoren

So gut wie alle in modernen 3D-Druckern verbauten Schrittmotoren
funktionieren identisch. Es gibt vier Adern, welche an vier verschiedene
im Motor sitzende Kontakte geführt werden. Diese Kontakte sind mit zwei
voneinander getrennten Spulen verbunden, welche bei Stromfluss ein
Magnetfeld erzeugen. Dieses Magnetfeld sorgt dafür, dass sich der Rotor
des Motors in eine bestimmte Position dreht. Somit lässt sich der Motor
sehr präzise und gezielt über das erzeugte Magnetfeld kontrollieren.
Sind die Positionen bzw. Winkel in Korrelation mit den Kontakten
bekannt, kann mit dem Motor eine Rotationsbewegung durchgeführt werden.
Die Nachfolgende
<a href="#fig-step_wiring" class="quarto-xref">Abbildung 11 (a)</a>
zeigt den internen Aufbau dieser Step-Motoren in Verbindung mit den
Steuerkontakten, oft als A+/A-/B+/B-, A1/A2/B1/B2 oder A/B/C/D
bezeichnet. Neben der Schaltung ist in der
<a href="#fig-step_sequence" class="quarto-xref">Abbildung 11 (b)</a>
die standard Reihenfolge der Ansteuerung dargestellt.

<div id="fig-step_motor">

<div id="fig-step_wiring">

<img src="pics/step.png" id="fig-step_wiring" style="width:50.0%"
data-ref-parent="fig-step_motor" />

(a)

</div>

<div id="fig-step_sequence">

<img src="pics/sequence.png" id="fig-step_sequence"
data-ref-parent="fig-step_motor" />

(b)

</div>

Abbildung 3: Step-Motor Aufbau (MOONS’ Industries 2026)

</div>

Anhand dieser Erkenntnisse wurde versucht diese Motoren anzusteuern. Da
jedoch ein Raspberry Pi nicht direkt den Strom bei der benötigten
Spannung bereitstellen kann, muss ein Motortreiber zwischengeschaltet
werden. Für diesen Versuch wurde ein bereits vorhandener *L298N Dual
H-Bridge Motor Driver* verwendet. Dieser Treiber hat passend zu den vier
Kontakten des Motors ebenfalls vier Anschlüsse, welche ein Steuersignal
vom Raspberry Pi 5 entgegennehmen um den Motor anzusteuern. Somit konnte
der Motor über die GPIO-Pins des Raspberry Pi 5 angesteuert werden. Es
wurde ein kleines Skript in Python (`4_wire_step.py`) geschrieben,
welches die Ansteuerung der Kontakte in der in
<a href="#fig-step_sequence" class="quarto-xref">Abbildung 11 (b)</a> zu
sehende Reihenfolge ansteuert. Um eine volle Funktion zu erzielen fehlte
noch die Drehrichtungsänderung sowie die Einbindung der *Steps*
(Motorschritte) und die Geschwindigkeitsänderung zur präzisen Steuerung.
Die Drehrichtungsänderung konnte durch die Invertierung der
Ansteuerungsreihenfolge der Kontakte umgesetzt werden. Die Einbindung
der Motorschritte wurde über einen Counter im Code umgesetzt. Dieser
zählt die Anzahl der Ansteuerungen und unterbricht die Schleife bei
Erreichen der gewünschten Zahl. Somit kann der Motor gezielt um eine
bestimmte Anzahl an *Steps* gedreht werden. Die Geschwindigkeitsänderung
des Motors kann über die Zeitabstände zwischen den verschiedenen
Ansteuerungen der Kontakte geregelt werden. Jedoch sei angemerkt, dass
bei höherer Drehzahl proportional das Drehmoment sinkt. Bei zu wenig
Drehmoment kann der Motor die benötigte Anfangsleistung nicht mehr
aufbringen und es kommt zu keiner Bewegung.

### Endschalter

Ein Endschalter ist nichts Weiteres als ein handelsüblicher Taster,
welcher bei Kontakt einen *Normally Closed* Kontakt öffnet oder einen
*Normally Opend* Kontakt schließt. Es gibt bei physischen Endschaltern
meist drei Adern, welche einen gemeinsamen Spannungs- bzw.
Ground-Kontakt, ein NO-Kontakt und einen NC-Kontakt beinhalten. Wird nun
der Schalter gedrückt wird die angeschlossene Spannung bzw. der
angeschlossene Ground weitergegeben oder unterbrochen, was eine
Zustandsänderung für das ausgehende Signal bedeutet. Diese
Zustandsänderung lässt sich nun in Bezug auf z.B. die Motoren setzen.

Hierfür wurde nun ein kleines einzelnes Python-Skript
(`limit_switch.py`) geschrieben, welches die Funktion des Endschalters
testet und validiert. Anschließend wurde in die Funktion der
Step-Motoren ein Endschalter mit eingebaut, womit der Motor bei Bedarf
gestoppt werden kann.

### Heizkomponenten

Die Heizelemente sind wohl die am einfachsten anzusteuerden Bauteile in
dieser Liste, da sie bei einer anliegenden Spannung Wärme erzeugen. Die
hier in einem Material eingebaute Spule, z.B. in das Hotend oder Heatbed
des Druckers, erwärmt sich bei Stromdurchfluss. Neben den Heizelementen
bedarf es jedoch noch mindestens eines Temperatursensors, welcher die
Temperatur überwacht und als Heizstopp fungiert. Diese
Temperatursensoren können als NTC (Heißleiter) oder PTC (Kaltleiter)
umgesetzt werden. Am beliebtesten sind hier jedoch die wie ein PTC
funktionierenden Platin-Sensoren, da diese PT100 bzw. PT1000 Glieder
einen sehr linearen Kurvenverlauf aufweisen. Außerdem sind sie so
optimiert, dass sie bei einer Temperatur von $T=0\,°C$ exakt einen
Widerstand von $R_{PT100}=100\,\Omega$ bzw. $R_{PT1000}=1000\,\Omega$
aufweisen. Sie sind somit ausgezeichnet für die Temperaturmessung
geeignet. Die
<a href="#fig-pt100_pt1000" class="quarto-xref">Abbildung 4</a> zeigt
einen Kurvenverlauf der beiden Temperatursensoren.

<div id="fig-pt100_pt1000">

<embed src="pics/pt100_pt1000.pdf" style="width:60.0%" />

Abbildung 4: Kennlinie der Pt100 und Pt1000 Sensoren

</div>

Neben den Temperatursensoren sind außerdem noch Lüfter von Vorteil um
das Bauteil wieder abzukühlen bzw. die benötigte Temperatur zu halten
und nicht zu überschreiten. Standardisierte Lüfter beim 3D-Druck können
mit bis zu 24V über ein PWM-Signal betrieben werden. So wird über die
Pulsbreite der Signale die Spannung festgelegt. Als Beispiel kann man
einen $5\,\text{V}$ Lüfter in Verbindung mit einer maximalen
Signalspannung von $V_{sig}=5\,\text{V}$ nehmen. Dieses kontinuierliche
$5\,\text{V}$ Spannungssignal entspricht für den Lüfter eine Leistung am
Ausgang von $P_{max}=100\,\%$. Wird nun mithilfe der
Pulsweitenmodulation das Signal auf $50\,\%$ reduziert, das heißt es
wird kein Dauerimpuls gesendet, sondern ein Impuls mit einer Pulsbreite
von $t_{an}=50\,\%$ gesendet, so wird die Spannung auf
$V_{sig}=2,5\,\text{V}$ reduziert und der Lüfter läuft nur noch mit
$P=50\,\%$. Somit kann die Leistung des Lüfters über das PWM-Signal
geregelt werden. Die
<a href="#fig-pwm" class="quarto-xref">Abbildung 5</a> zeigt die
entstehende Signalspannung bei beispielhaften PWM-Signalen.

<div id="fig-pwm">

<embed src="pics/pwm.pdf" style="width:60.0%" />

Abbildung 5: Signalverlauf bei Pulsweitenmodulation

</div>

## Referenzsystem: Geeetech i3

Nach Ansteuerung der einzelnen Basiskomponenten wurde probiert mittels
eines Referenzdruckers die Bauteile anzusteuern. Dazu wurde ein
ausgesonderter *Geeetech i3* 3D-Drucker verwendet, welcher
hardwareseitig über einen *Arduino Mega 2560* betrieben wird. Die
<a href="#fig-i3" class="quarto-xref">Abbildung 6</a> zeigt das
verwendete Referenzsystem.

<div>

</div>

### Festlegung der Software

Da bereits der Arduino sowie der Raspberry Pi 5 zur Verfügung standen,
wurde sich nun auf die Lösung der Ansteuerung mittels zwei Boards
entschieden. Somit sollte der Arduino als Hardwaresteuerung und der
Raspberry Pi 5 für die komplexere Softwaresteuerung verantwortlich sein.
Für diese Art von Ansteuerung gibt es bereits sämtliche Open-Source
Lösungen. Unter anderem *Klipper*, *Marlin*, *RRF* oder auch *Kalico*.
Nach Recherchen hat sicher ergeben, dass die wohl meist verbreitete und
zugänglichste Variante *Klipper* ist. Klipper bietet mit der in Python
programmierten Funktionsklassen leichte Anpassungs- sowie
Erweiterungsmöglichkeiten und für sehr viele Lösungen bereits
vorgefertigte bauteilspezifische Module. Außerdem kann mit Hilfe von
*Mainsail* und *Moonraker* leicht eine IP adressenbasierte
Benutzeroberfläche für Klipper geschaffen werden, mit welcher sich alle
Komponenten steuern lassen und Änderungen im Code vorgenommen werden
können. Neben dieser Weboberfläche kann zusätzlich mit *Crowsnest* eine
Kamera eingebunden und mit *Klipper-Screen* diese Weboberfläche auch auf
dem am Raspberry Pi angeschlossenen Display angezeigt werden. Zusätzlich
können über G-Code direkt in der Weboberfläche Makros erstellt werden,
welche die Ansteuerung der einzelnen Komponenten vereinfachen oder z.B.
eine Startsequenz für den Drucker erstellt. Alle benötigten Softwares
sind einfach über deren eigenen Github-Repositories, direkt aus der
Konsole des Raspberry Pis, zu installieren und zu konfigurieren. Aus
diesem Grund bietet Klipper alles für die erfolgreiche Umsetzung des
Projektes und wird als Software verwendet.

### Ansteuerung des Referenzsystems

Die Ansteuerung des Referenzsystems gestaltete sich mithilfe von Klipper
und den bereits vorhandenen Modulen sowie der vorherigen Recherche der
einzelnen Komponenten einfach und nachvollziehbar. Als MCU für das
Referenzsystem wurde ein *Arduino Mega 2560* mit einem *RAMPS 1.4* Board
verwendet, welches bereits die benötigten Anschlüsse für die
Step-Motoren, Endschalter und Heizkomponenten bereitstellt. Um nun eine
Verbindung zwischen dem Raspberry Pi 5 und dem Arduino herzustellen
musste der Arduino zuerst mit der Klipper-Firmware geflasht werden. Dies
geschieht über die Konsole des Raspberry Pis und dem Befehl `makeconfig`
in dem geladenen Klipper-Ordner. Hierbei wird die Konfiguration des
Arduinos erstellt und anschließend mit dem Befehl `make flash` auf den
Arduino über ein USB-Kabel übertragen. Die anschließende Verbindung
zwischen dem Raspberry Pi 5 und dem Arduino wird ebenfalls über die
USB-Schnittstelle hergestellt.

Beim Betreten des Webinterfaces von Mainsail kann der Drucker über die
IP-Adresse des Raspberry Pis aufgerufen und dort auch die einzelnen
Komponenten angesteuert werden. Bevor jedoch die Komponenten angesteuert
werden konnten, musste zuerst die Konfiguration des Druckers in der
Klipper-Konfigurationsdatei `printer.cfg` hinterlegt werden. Hierbei
wurden die einzelnen Anschlüsse der Step-Motoren, Endschalter und
Heizkomponenten hinterlegt. Diese Pinbelegungen konnten aus den
Datenblättern des Arduinos sowie des RAMPS 1.4 Boards entnommen werden.
Außerdem wurden die einzelnen Parameter der Step-Motoren, Endschalter
und Heizkomponenten in der Konfigurationsdatei hinterlegt. Nach
erfolgreicher Konfiguration konnte der Drucker über das Webinterface von
Mainsail angesteuert werden. Für weitere Tests wurde mittels *Crowsnest*
eine Kamera an den Raspberry Pi 5 angeschlossen, um die Ansteuerung der
einzelnen Komponenten zu überwachen. Außerdem wurde ein kleines Display
an den Raspberry Pi 5 angeschlossen, um die Weboberfläche von Mainsail
auch auf dem Display anzeigen zu können. Somit konnte der Drucker auch
ohne einen Computer angesteuert werden. Die dafür benötigten Dateien
konnten direkt in der Weboberfläche von Mainsail erstellt, bearbeitet
und auf dem Raspberry Pi 5 gespeichert werden. Die
<a href="#fig-final_i3" class="quarto-xref">Abbildung 7</a> zeigt den
finalen Aufbau des Referenzsystems und die
<a href="#fig-mainsail_i3" class="quarto-xref">Abbildung 8</a> die
dazugehörige Weboberfläche über Mainsail.

<div id="fig-mainsail_i3">

<img src="pics/i3_klipper.jpg" style="width:80.0%" />

Abbildung 8: Geeetech i3 Klipper Weboberfläche mit Mainsail

</div>

# 3DGence Industry F421

Nach erfolgreicher Ansteuerung des Referenzsystems konnte sich an den
3DGence Industry F421 herangetastet werden. Der 3DGence Industry F421
ist ein industrieller 3D-Drucker, der auf dem FFF bzw. FDM Verfahren
basiert. Der Drucker wird über eine $32$-Ampere CEE-Steckdose betrieben
und verfügt über eine Vielzahl von Komponenten. Zu diesen Komponenten
gehören unter anderem:

- Step-Motoren für X-/Y- und Z-Achse sowie zwei Step-Motoren für die
  Extruder
- PWM-Motoren für den Filamentnachschub in Kombination mit Flow-Sensoren
  am Extruder
- Endschalter in Kombination mit Magnetsensoren für die genaue
  Positionserkennung des Druckkopfes
- Einen beheizten Bauraum sowie ein beheiztes Druckbett
- Verschiedene schnellwechsel Filament-Extruder-Köpfe für verschiedene
  Temperaturen mit:
  - Heizpatronen
  - Wägezellen (Loadcells)
  - Lüftern
  - Einem Servo zum Extruderwechsel
- Einem Display zur Anzeige von Informationen und zur Steuerung des
  Druckers
- Eine Kamera zur Überwachung des Druckprozesses
- Sämtliche Temperatursensoren zur Überwachung der Heizpatronen, des
  Druckbetts und des Bauraums
- Einem Battery-Backup-System, um den Druckprozess bei einem
  Stromausfall sicher zu beenden
- Diverse Lüfter für den Bauraum und die Mainboards
- Eine Vakuumpumpe für den Bauraum

Die Bauteile werden über zwei Mainboards software- sowie hardwareseitig
gesteuert. Der Aufbau passt also zu der Klipper typischen Ansteuerung.
Eine Abbildung der Hardware zur Steuerung des Industry F421 ist der
<a href="#fig-mainboards" class="quarto-xref">Abbildung 9</a> zu
ennehmen.

<div id="fig-mainboards">

<img src="pics/platine_gesamt.jpeg" style="width:63.0%" />

Abbildung 9: Steuerung des Industry F421

</div>

Nach der Einspeisung durch den $32$-Ampere Stecker auf der Rückseite des
Druckers, kommt es neben einer Weiterleitung eines $230\,\text{V}$
Wechselspannungssignals auch zu einer Transformation der Spannung auf
$24\,\text{V}$ und $48\,\text{V}$ Gleichspannung. Diese transformierten
Spannungen werden nun zu diversen Platinen weitergeführt. Die Verteilung
der Spannungen kann links mittig aus den zu erkennenden Reihenklemmen
der <a href="#fig-mainboards" class="quarto-xref">Abbildung 9</a>
entnommen werden. Von dort aus werden Leitungen mit $24\,\text{V}$ und
$48\,\text{V}$ auf das Hardwareboard, mittlere große grüne Platine,
geleitet. Das Hardwareboard verteilt nun die Versorgungsspannung an das
Softwareboard, schmale Platine rechts neben dem Hardwareboard.
Zusätzlich wird noch eine $230\,\text{V}$ Wechselspannung zu der roten,
oben links zu sehenden, Platine geführt. Diese Platine beinhaltet
verschiedene Relais für Bauteile, welche eine $230\,\text{V}$
Wechselspannungsversorgung benötigen. Unter den Platinen sind außerdem
drei Motortreiber mit $48\,\text{V}$ Versorgungsgleichspannung zu
erkennen.

Im nächsten Schritt wurden die einzelnen Komponenten des Druckers
identifiziert, die Leitungen zu den Platinen verfolgt und anschließend
mit dem Referenzsystem verglichen. Alle vier Seiten des aufgeschraubten
Druckers sind der
<a href="#fig-f421_offen" class="quarto-xref">Abbildung 10</a> zu
entnehmen. In der Folge wurde in Betracht gezogen, wie sich die
einzelnen Komponenten von den bereits angesteuerten unterscheiden und
wie sie bei Abweichung angesteuert werden können. Auch hier wird in den
nachfolgenden Unterkapiteln auf die einzelnen Komponenten eingegangen.
Dazu wurden die Unterkapitel in zwei Bereiche unterteilt, um bei der
Vielzahl an Komponenten den Überblick zu behalten. Es wurde aufgeteilt
in Grundkomponenten die für das grundlegende einfache Drucken nötig sind
und in zusätzliche Komponenten und Sensoren, die den Druck verbessern
aber nicht zwingend für simples Drucken benötigt werden.

<div id="fig-f421_offen">

<div id="fig-f421_offen_front">

<img src="pics/F421_front.jpeg" style="width:95.0%"
data-ref-parent="fig-f421_offen" />

(a) Frontansicht

</div>

<div id="fig-f421_offen_back">

<img src="pics/F421_back.jpeg" style="width:95.0%"
data-ref-parent="fig-f421_offen" />

(b) Rückansicht

</div>

<div id="fig-f421_offen_right">

<img src="pics/F421_right.jpeg" style="width:95.0%"
data-ref-parent="fig-f421_offen" />

(c) Rechte Seitenansicht

</div>

<div id="fig-f421_offen_left_oben">

<img src="pics/F421_left.jpeg" style="width:95.0%"
data-ref-parent="fig-f421_offen" />

(d) Linke Seitenansicht

</div>

Abbildung 10: Detaillierte Ansichten des geöffneten 3DGence Industry
F421

</div>

## Grundkomponenten des F421

### Motoren

**Step-Motor**

Der 3DGence Industry F421 besitzt insgesamt fünf einzelne Step-Motoren.
Darunter fallen zweimal die *AM23HSA4B0-03* für die X- und
Y-Achsenbewegung, einmal der *AM24HS5401-10N* für die Z-Achse und
zweimal die *17HS16-2004S1* für die Filament-Extrusion am Druckkopf. Die
beiden NEMA-Schrittmotoren funktionieren dabei identisch zu dem wie es
in <a href="#sec-step" class="quarto-xref">Kapitel 4.1.1</a> beschrieben
wurde.

Der 17HS16-2004S1
(<a href="#fig-step_17HS16-2004S1" class="quarto-xref">Abbildung 11
(a)</a>) ist dabei ein Schrittmotor der NEMA 17-Baugröße
(Gehäuseabmessungen $\approx 42 \times 40\,\text{mm}$) und bildet einen
kompakten Standard für den Extruderantrieb. Dieser Motor wird dabei mit
einem Nennstrom von $2{,}0\,\text{A}$ pro Phase betrieben (bei einem
Phasenwiderstand von ca. $1{,}3\,\Omega$), was eine Nennspannung von
etwa $2{,}6\,\text{V}$ ergibt. Der AM23HSA4B0-03
(<a href="#fig-step_AM23HSA4B0-03" class="quarto-xref">Abbildung 11
(b)</a>) für die X- und Y-Achse ist hingegen in der NEMA 23-Baugröße
($\approx 56 \times 77\,\text{mm}$) ausgeführt. Er liefert das
erforderliche Drehmoment, um den Druckkopf prazise in der Horizontalen
zu bewegen, und wird mit einem Phasenstrom von $3{,}7\,\text{A}$ bei
einem Phasenwiderstand von ca. $0{,}75\,\Omega$ betrieben (Nennspannung
$\approx 2{,}78\,\text{V}$). Im Vergleich dazu handelt es sich bei dem
AM24HS5401-10N
(<a href="#fig-step_AM24HS5401-10N" class="quarto-xref">Abbildung 11
(c)</a>) um einen noch leistungsstärkeren NEMA 24-Motor
($\approx 60 \times 85\,\text{mm}$), der aufgrund seines höheren
Drehmoments speziell für das heben des schweren Druckbetts eingesetzt
wird. Dieser kräftige Motor erfordert einen Phasenstrom von
$4{,}0\,\text{A}$ bei einer Nennspannung von $2{,}6\,\text{V}$
(entspricht einem Phasenwiderstand von ca. $0{,}65\,\Omega$). Es ist zu
beachten, dass diese Nennspannungen lediglich rein rechnerische Werte
aus dem ohmschen Widerstand darstellen ($U = R \cdot I$). In der Praxis
werden beide Motortypen von modernen Schrittmotortreibern mit einer
deutlich höheren Betriebsspannung ($24\,\text{V}-48\,\text{V}$)
versorgt, um auch bei höheren Drehzahlbereichen ein ausreichend hohes
Drehmoment zu gewährleisten.

Aus eben diesem Grund und dieser enormen Last der AM23HSA4B0-03
Schrittmotoren, wurden in dem originalen Aufbau die in
<a href="#fig-mainboards" class="quarto-xref">Abbildung 9</a> zu
sehenden Motortreiber verwendet. Diese *SR4-Plus* Motor-Treiber verfügen
über ihre eigene Spannungsversorgung und können so die benötigte Leitung
der Motoren erbringen. Außerdem werden die angesprochenen
Schritt-Signale mit ihren vier Kontakten zu einem *Step*, *Dir* und
*Enable* transformiert. So konnten über den *Step*-Kontakt die Anzahl
der Schritte, über den *Dir*-Kontakt die Richtung und über den
*Enable*-Kontakt die Aktivierung des Motor durchgeführt werden.

<div id="fig-step_motor">

<div id="fig-step_17HS16-2004S1">

<img src="pics/17HS16-2004S1.jpg" style="width:60.0%"
data-ref-parent="fig-step_motor" />

(a) 17HS16-2004S1 (Dolunto 2026)

</div>

<div id="fig-step_AM23HSA4B0-03">

<img src="pics/AM23HSA4B0-03.png" style="width:65.0%"
data-ref-parent="fig-step_motor" />

(b) AM23HSA4B0-03 (Amazon Vendor 2026)

</div>

<div id="fig-step_AM24HS5401-10N">

<img src="pics/AM24HS5401-10N.jpg" style="width:55.0%"
data-ref-parent="fig-step_motor" />

(c) AM24HS5401-10N (Electronics Panga 2026)

</div>

Abbildung 11: Step-Motoren des F421

</div>

**PWM-Motoren**

Neben den Schrittmotoren für die Achsen- und Extruderbewegung verfügt
der 3DGence Industry F421 über vier zusätzliche PWM-Motoren, die auf die
vier Filament-Plätze aufgeteilt sind, um das Material bedarfsgerecht zum
Druckkopf zu transportieren. In
<a href="#fig-filament" class="quarto-xref">Abbildung 12</a> sind die
Vorder- und Rückseite des Filamenteinschubs dargestellt.

<div id="fig-filament">

<div id="fig-filament_vorne">

<img src="pics/IMG_2254.jpeg" style="width:75.0%"
data-ref-parent="fig-filament" />

(a) Frontansicht Filamenteinschub

</div>

<div id="fig-filament_hinten">

<img src="pics/IMG_2253.jpeg" style="width:75.0%"
data-ref-parent="fig-filament" />

(b) Rückansicht Filamenteinschub

</div>

Abbildung 12: Filamenteinschub des F421

</div>

Bei den dortigen Antrieben handelt es sich um zweipolige
Gleichstrom-PWM-Motoren. Im Gegensatz zu den Schrittmotoren erfolgt ihre
Ansteuerung nicht über diskrete Phasenimpulse, sondern über eine
variable Pulsweitenmodulation (siehe
<a href="#sec-pwm" class="quarto-xref">Kapitel 4.1.3</a>) der
Versorgungsspannung. Die über das PWM-Signal festgelegte effektive
Mittelspannung und daraus resultierende Drehzahl des Motors sorgt für
den anfänglichen Materialtransport zum Druckkopf. Aufbauend darauf
wurden hier noch I²C-Konverter zwischengeschaltet, was eine komplette
Steuerung des Motors über eben dieses Protokoll ermöglicht. So lassen
sich über die vier Geräteadressen (0x6c, 0x6d, 0x6e und 0x6f) und den
Registeradressen (0x05 für die Vorwärtsrotation und 0x06 für
Rückwärtsrotation) die Geschwindigkeiten zwischen den Datenwerten 0x00
für Stillstand und 0xff für maximale Geschwindkeit festlegen. Nach
dieser Konfiguration kann der Motor unter der Registeradresse 0x0a mit
dem Datenwert 0x01 für Vorwärts- und 0x02 für Rückwärtsfahrt geändert
werden (Datenwert 0x00 bedeutet Stillstand).

### Endschalter

Im Gegensatz zu den Endschalter aus
<a href="#sec-limit_switch" class="quarto-xref">Kapitel 4.1.2</a>
besitzt der Industry F421 optische Endschalter. Diese optischen
Endschalter vom Model *TCST2103* funktionieren vom Prinzip wie eine
herkömmliche Lichtschranke. Sie bestehen aus einem Infrarot-Emitter
(einer LED) und einem Fototransistor als Empfänger, die durch einen
schmalen Spalt voneinander getrennt sind. Solange der Spalt frei ist,
trifft das Infrarotlicht ungehindert auf den Fototransistor, wodurch
dieser leitet. Sobald eine Achse ihre Referenzposition erreicht, schiebt
sich eine am Achsenschlitten befestigte Fahne in diesen Spalt und
unterbricht den Lichtstrahl. Dies führt zu einer unmittelbaren
Spannungsänderung am Signalpin, die von der Steuerung als Erreichen der
Endposition registriert wird. Der entscheidende Vorteil dieser optischen
Endschalter gegenüber mechanischen Mikroschaltern liegt in der
berührungslosen und somit verschleißfreien Abtastung, was präzise und
reproduzierbare Referenzfahrten (Homing) ermöglicht.

<div id="fig-TCST2103">

<img src="pics/TCST2103.png" style="width:20.0%" />

Abbildung 13: Endschalter TCST2103 (Conrad Electronic 2026)

</div>

Zur Ansteuerung des TCST2103 werden lediglich drei Anschlüsse benötigt:
Versorgungsspannung ($V_{\text{CC}}$), Masse ($\text{GND}$) und eine
Signalleitung ($V_\text{OUT}$). Die integrierte Infrarot-LED wird über
einen Vorwiderstand ($R_{\text{LED}} = 220\ \Omega-330\ \Omega$) an
$V_{\text{CC}}=5\,\text{V}$ betrieben, während der Kollektor des
Fototransistors über einen Pull-up-Widerstand mit der Signalleitung
verbunden ist. Solange der Lichtstrahl ungestört auf den Fototransistor
trifft, schaltet dieser durch und zieht das Signal auf $\text{GND}$
(Low). Wird der Lichtstrahl durch die Unterbrecherfahne blockiert,
sperrt der Transistor, sodass die Signalleitung über den
Pull-up-Widerstand auf $V_{\text{CC}}$ (High) gezogen wird. Dieses
High-Signal zeigt der Steuerung das Erreichen der Endposition an.

### Druckkopf Steuerung

Da nun die Achsenbewegung vollständig ist kann sich an den Druckkopf
gemacht werden. Durch die enorme Größe des Druckers und die Vielzahl der
Sensoren fällt der Druckkopf deutlich größer aus, als bei herkömmlichen
Geräten. So beinhaltet der Druckkopf neben den Heizelementen und Lüftern
auch Wägezellen zur Kalibrierung sowie einen Servo zur Extruder
Änderung. Eine Abbildung des Druckkopfes ist der
<a href="#fig-hotend" class="quarto-xref">Abbildung 14</a> zu entnehmen.

<div id="fig-hotend">

<div id="fig-hotend_front">

<img src="pics/druckkopf_front.jpg" style="width:63.0%"
data-ref-parent="fig-hotend" />

(a) Frontansicht

</div>

<div id="fig-hotend_rück">

<img src="pics/druckkopf_rück.jpeg" style="width:68.0%"
data-ref-parent="fig-hotend" />

(b) Rückansicht

</div>

Abbildung 14: Druckkopf des F421

</div>

Das Prinzip dieses Druckkopfes ist in
<a href="#fig-hotend_rück" class="quarto-xref">Abbildung 14 (b)</a> zu
erkennen. Der hier zu sehende *D-SUB28* Stecker ermöglicht die
verschiedenen Druckköpfe schnell und einfach bei Bedarf auszutauschen.
Aufgabe war es, die auf dem Druckkopf verbaute Platine in Verbindung mit
dem D-SUB Stecker zu bringen, um den Anschluss einer neuen Ansteuerung
möglich zu machen. Dazu wurde der Druckkopf im ersten Schritt
auseinander gebaut und die verbaute Platine mit einem Multimeter
durchgemessen.

<div id="fig-hotend_platine">

<div id="fig-hotend_platine_front">

<img src="pics/IMG_2077_1_.jpeg" style="width:66.0%"
data-ref-parent="fig-hotend_platine" />

(a) Druckkopf Frontansicht

</div>

<div id="fig-hotend_platine_rück">

<img src="pics/IMG_2073.jpeg" style="width:75.0%"
data-ref-parent="fig-hotend_platine" />

(b) Druckkopf Rückansicht

</div>

Abbildung 15: Platine des Druckkopf vom F421

</div>

Nach dem Durchmessen sind bereits mehrere Komponenten identifiziert und
mit den passenden PINs des D-SUBs in Verbindung gebracht worden. So
konnten die beiden Heizpatronen mit den Lüftern und den zwei PT1000
Glieder sowie der Servo angesteuert werden. Die Heizpatronen, die Lüfter
sowie die PT1000 Glieder sind hierbei identisch zu herkömmlichen
Modellen und lassen sich gleich zum Referenzsystem ansteuern. Der
verbaute Servo ist ein *HS-7955TG* der Firma HiTec und funktioniert über
ein klassisches PWM-Signal mit einer Frequenz von $50\,\text{Hz}$, bei
dem die jeweilige Impulsbreite im Bereich von $1\,\text{ms}$ bis
$2\,\text{ms}$ die exakte Position definiert. Im Druckkopf des Industry
F421 übernimmt dieser Servo das mechanische Umschalten zwischen den
Extrudern, weshalb für eine zuverlässige Funktion neben der
Spannungsversorgung ein präzises, störungsarmes Steuersignal
erforderlich ist.

Somit blieben einzig und allein die Wägezellen. Diese Loadcells geben
über Torsionsmodule eine zur Eingangsspannung und Krafteinwirkung
proportionale Ausgangsspannung aus. Nach Verstärkung lässt sich über
dieses Spannungssignal die anliegende Kraft bzw. Masse präzise
bestimmen, was für automatische Kalibrierprozesse genutzt werden kann.
Nach weiterer Analyse der Platine wurde deutlich, dass auch diese
Wägezellen über einen I²C-Bus mit dem Mainboard kommunizieren. Die auf
der Platinenrückseite verbauten Schaltungen bzw. ICs
(<a href="#fig-hotend_platine_rück" class="quarto-xref">Abbildung 15
(b)</a>) zeigten einen bis zum vorletzten Bauteil parallelen Aufbau. Als
erstes Bauteil war hierbei ein Verstärker-IC mit anschließender
I²C-Konvertierung verbaut (*Texas Instruments: INA333* und *Adafruit:
MCP96L01*). Diese SDA- und SCL-Leitungen wurden anschließend auf einen
gemeinsamen Speicher (*ATMEL732*) geführt, um im letzten Schritt an die
Ausgangspins übergeben zu werden.

### Heizbett

Auch beim Heizbett wird die Dimensionierung des industriellen Druckers
deutlich, da hier ein leistungsstarkes
$230\,\text{V}$-Wechselspannungs-Heizbett verbaut ist. Die Ansteuerung
erfolgt nicht direkt über das Steuerungsboard, sondern über die zuvor
angespochene Relais-Platine. Das Mainboard liefert hierbei lediglich ein
$3,3\,\text{V}$-Schaltsignal, um die Wechselspannung über dem Relais
durchzuschalten. Zur Temperaturüberwachung sind im Heizbett zwei
NTC-Temperatursensor integriert, welche als Messwertgeber für die
Steuerung dienen.

<div id="fig-heatbed">

<img src="pics/heizbett.png" style="width:60.0%" />

Abbildung 16: Heizbett des F421

</div>

### Not-Aus-System

Aufgrund der hohen Motorleistungen sowie der anliegenden Ströme und
Spannungen verfügt der *3DGence Industry F421* über ein zentrales
Not-Aus-System. Dieses schaltet im Notfall über ein Sicherheitsrelais
sowie zwei vorgeschaltete Schütze sämtliche $230\,\text{V}$- und
$48\,\text{V}$-Leitungen ab. Die für die Software-Steuerungsplatinen und
das Display benötigte $24\,\text{V}$-Spannungsversorgung bleibt hingegen
erhalten, sodass die Software aktiv bleibt, während alle gefährlichen
Lasten und Motoren sicher spannungsfrei geschaltet sind. Der Aufbau des
Not-Aus ist in
<a href="#fig-notaus" class="quarto-xref">Abbildung 17</a> dargestellt.
Zur Statusüberprüfung wurde hier eine Leitung mit zwei Adern von den
NO-Kontakten der Schütze zum Hardwareboard zurückgeleitet.

<div id="fig-notaus">

<img src="pics/notaus.jpeg" style="width:45.0%" />

Abbildung 17: Not-Aus Steuerung des F421

</div>

## Zusätzliche Komponenten und Sensoren des F421

Neben den zum Drucken erforderlichen Bauteilen gibt es noch diverse
weitere Komponenten, welche den Druck verbessern, erweitern und das
ganze System anwenderfreundlicher gestalten. Auf diese Komponenten wird
jedoch nicht weiter in einer solchen Fülle eingegangen.

### Komponenten zur Verbesserung der Druckqualität

#### Positionserkennung über Magnetleiste

Da es bei Schrittmotoren im Betrieb gelegentlich zu Schrittverlusten
kommen kann, sind zur Erhöhung der Positioniergenauigkeit an der X- und
Y-Achse zusätzlich zu den optischen Endschaltern Magnetleisten mit
entsprechenden Magnetsensoren
(<a href="#fig-positionierung" class="quarto-xref">Abbildung 18</a>)
verbaut. Die Aufgabe dieser Sensoren besteht darin, die nach dem Homing
durch die Endschalter eingenommene Position kontinuierlich und
hochpräzise zu erfassen.

Dies geschieht über die Generierung eines Rechtecksignals, während sich
der Sensor über den magnetischen Maßstab bewegt. Bei einer Erhöhung der
Bewegungsgeschwindigkeit des Schlittens steigt proportional die Frequenz
dieses Rechtecksignals an. Durch das Zählen der Impulse und Auswerten
der Flanken lässt sich so zu jedem Zeitpunkt die exakte Position des
Druckkopfes auf der Achse bestimmen.

#### Flowsensor am Extruder

Für eine reibungslose und staufreie Filamentförderung sind direkt an den
Extrudern verbaute Flowsensoren bzw. Drehgeber integriert
(<a href="#fig-flow" class="quarto-xref">Abbildung 19</a>). Diese
basieren auf dem *AS5048B*-IC und dienen dazu, zu erkennen, ob Filament
anliegt und sich ordnungsgemäß durch das System bewegt und sich kein
Stau gebildet hat. Dabei erfasst der Magnetsensor über ein Magnetfeld
die Rotation eines mit dem Vorschub gekoppelten rotierenden Elements und
leitet diese Information per I²C-Bus an das Mainboard weiter. Intern
werden diese Datenwerte zu geeigneten Winkeln umgewandelt, um dem System
Informationen zu liefern.

<div>

</div>

### Diverse Temperaturregulierungskomponenten

Neben den im Druckkopf verbauten Heiz-, Lüftungs- sowie
Temperaturmessungskomponenten gibt es etliche weitere Bauteile zur
Temperatursteuerung an unterschiedlichen Orten im Drucker. Die folgende
Tabelle gibt eine übersichtliche Struktur über die verbauten Komponenten
zur Temperaturregulierung und deren funktionale Aufteilung im *3DGence
Industry F421*:

| Ort / Bereich | Heizelement | Lüfterelement | Temperaturelement |
|:---|:---|:---|:---|
| Bauraum | Bauraumheizung ($230\,\text{V}$, geschaltet über Relais-Platine) | Umwälzlüfter ($230\,\text{V}$, geschaltet über Relais-Platine) | $1\times$ PT1000 & $1\times$ NTC |
| Filament-Einschub | Heizelement (gekoppelt mit dem PWM-Lüfter) | PWM-Lüfter ($24\,\text{V}$, steuerung über I²C-Bus) | $2\times$ PT1000-Sensoren, Datenwerte kommen als HEX-Zahl in Celsius |
| Gehäuse | – | PWM-Gehäuselüfter ($24\,\text{V}$) | – |
| $230\,\text{V}$-Platine | – | Relais-Lüfter ($5\,\text{V}$) | – |

Sonstige Temperatursteuerungskomponenten des F421

### Vakuumpumpe für den Bauraum

Bei der Verarbeitung sehr hochwertiger und hochtemperaturbeständiger
Kunststoffe (wie beispielsweise PEEK oder PEKK) entstehen chemische
sowie potenziell gesundheitsschädliche Dämpfe und Entgasungen. Um diese
kontrolliert abzusaugen und ein Abscheiden im Druckraum zu verhindern,
ist im F421 unterhalb des Heizbetts eine spezielle Vakuumpumpe verbaut,
die für einen gezielten Unterdruck und die geordnete Abführung der
Prozessabgase sorgt. Als Kernkomponenten fungieren hierbei ein
bürstenloser Radialgebläsemotor vom Typ *Wonsmart WS9290B-48-240-X200*
zur Erzeugung des Luftstroms sowie eine Vakuum- und Ventileinheit vom
Typ *SMC ZK2-ZSVB-A* zur Regelung und Überwachung des Unterdrucks. Der
Motor wird hierbei ebenfalls über die $230\,\text{V}$ Relais-Platine und
die Ventileinheit über die $24\,\text{V}$-Versorgung des Hardwareboards
angesteuert. Das Steuersignal der Ventileinheit erlaubt es der
Steuerung, das Vakuum je nach Prozessphase gezielt zuzuschalten oder
abzulassen. Das integrierte Druckmessglied der SMC-Einheit gibt wiederum
Rückmeldung an das System, um das Erreichen des erforderlichen
Unterdrucks kontinuierlich zu überwachen und bei einem Vakuumabfall eine
Schutzabschaltung auszulösen.

### NFC-Sensoren und LED-Steuerung für Filamenterkennung

Neben den bereits angesprochenen PWM-Motoren im Filamenteinschub
befinden sich an jedem der vier Filamentplätze ein NFC-Lesegerät sowie
eine zugehörige LED-Statusanzeige. Beide Komponenten sind auf
gemeinsamen Platinen verbaut und werden ebenfalls direkt über den
I²C-Bus angesteuert und konfiguriert.

Um Materialverwechslungen auszuschließen und spulenbezogene Parameter
automatisiert zu laden, lesen die NFC-Lesegeräte die auf den
Herstellerspulen integrierten NFC-Chips (z. B. Materialtyp und Farbe)
aus und übermitteln die Daten an die Steuerung. Die gekoppelte
RGB-LED-Statusanzeige an den jeweiligen Einschüben signalisiert visuell
den Zustand des jeweiligen Filamentschachts. Diese mit PWM-Motoren, NFC
und einer LED-Steuerung ausgestatteten, komplett erläuterten, Platinen
sind der
<a href="#fig-filament_hinten" class="quarto-xref">Abbildung 12 (b)</a>
zu entnehmen.

### Batterie-Steuerung bei Stromausfall

Für die Ausfallsicherheit bei Unterbrechungen der Netzspannung verfügt
der Drucker über ein integrierte USV. Bei einem Stromausfall übernimmt
die Batteriesteuerung unmittelbar die Versorgung der internen
$24\,\text{V}$-, $48\,\text{V}$- und $230\,\text{V}$-Steuerung. Dies
ermöglicht es der Software, den aktuellen Systemzustand und die genauen
Druckkoordinaten sicher auf dem Speicher abzulegen, bevor das System
geordnet herunterfährt, sodass der Druckprozess nach Wiederkehr der
Spannungsversorgung nahtlos fortgesetzt werden kann. Hier wurden eine
*FSP Power Station: Knight RM 6KL* Batteriesteuerung mit einem *RoHS
Compliant: MPF0005900GP* Batteriepack verbaut.

### Bauteile zur Bedienfreunderlichkeit

#### Kamera zur Überwachung des Druckprozesses

Zur Fernüberwachung und Prozessdokumentation ist im Bauraum eine Kamera
integriert. Das original verbaute Kameramodul basiert auf einem
*OV2640*-Sensor
(<a href="#fig-OV2640" class="quarto-xref">Abbildung 20 (a)</a>).
Aufgrund der spezifischen Ansteuerung und Schnittstelle lässt sich
dieses Modul jedoch nicht direkt mit dem Raspberry Pi verbinden, weshalb
ein Austausch erforderlich wäre.

Durch den langen Leitungsweg von etwa $2\,\text{m}$ vom
Steuerungsbereich bis in den Bauraum scheiden parallele oder
CSI-Kameraschnittstellen aus, sodass zwingend auf eine USB-Verbindung
zurückgegriffen werden muss. Eine geeignete und Raspberry Pi kompatible
Alternative stellt hierbei beispielsweise die USB-Kamera
*U20CAM-1080P-WDR*
(<a href="#fig-U20CAM" class="quarto-xref">Abbildung 20 (b)</a>) dar,
welche bei moderaten Kosten alle geforderten Eigenschaften für eine
zuverlässige Prozessüberwachung erfüllt.

<div id="fig-kameras">

<div id="fig-OV2640">

<img src="pics/OV2640.jpg" style="width:50.0%"
data-ref-parent="fig-kameras" />

(a) OV2640 Kameramodul

</div>

<div id="fig-U20CAM">

<img src="pics/U20CAM.jpg" style="width:50.0%"
data-ref-parent="fig-kameras" />

(b) U20CAM-1080p-wdr USB-Kamera (Innomaker 2026)

</div>

Abbildung 20: Originales und alternatives Kameramodul für den F421

</div>

#### Display mit Touchscreen

Als Display zur einfachen Bedienung dient ein an der Front verbautes
Touchscreen-Display. Ursprünglich ist im F421 ein industrielles Display
vom Typ *Riverdi RVT101HVLNWC00-B* verbaut. Da dieses Display jedoch
über eigene Firmware angesteuert wird und nicht direkt mit dem Raspberry
Pi kompatibel ist, muss es im Zuge der Umrüstung ausgetauscht werden.

Als funktionale und vollständig Raspberry-Pi-kompatible Alternative
kommt ein hochauflösendes 10,1-Zoll-Touchscreen-Display zum Einsatz.
Dieses wird direkt über HDMI für das Bildsignal und USB für die
Touch-Eingaben an dem Raspberry Pi angebunden. Es ermöglicht somit die
direkte lokale Bedienung des Druckers über KlipperScreen, von der
Dateiauswahl über die Ausführung von Kalibrierungs- und
Homing-Prozeduren bis hin zur Echtzeitüberwachung aller Temperatur- und
Achsenparameter.

<div id="fig-display">

<img src="pics/display.jpg" style="width:50.0%" />

Abbildung 21: Alternatives Display für den F421 (Hamtysan 2026)

</div>

# Festlegung der Hardwareboards

## Klipper MCU

Nach ausführlicher Analyse der einzelnen Komponenten des 3DGence
Industry F421 muss nun ein geeignetes Mainboard ausgewählt werden,
welches die hardwareseitige Steuerung des Druckers übernimmt. Die
Recherche ergab, dass die Auswahl an geeigneten Steuerplatinen stark
eingeschränkt ist, da die reine Anzahl sowie benötigte Leistung der
anzusteuernden Komponenten die Kapazitäten herkömmlicher Klipper-Boards
deutlich übersteigt.

Der einzige Kandidat, der den hohen Anforderungen gerecht wird, ist das
*BIGTREETECH Kraken* in den Revisionen V1.0 bzw. V1.1. Die Entscheidung
fiel letztlich auf das neuere *BIGTREETECH Kraken V1.1*
(<a href="#fig-kraken" class="quarto-xref">Abbildung 22</a>).

<div id="fig-kraken">

<img src="pics/krakenv1.1.png" style="width:75.0%" />

Abbildung 22: BIGTREETECH Kraken V1.1 (BigTreeTech 2026)

</div>

Das BTT Kraken V1.1 bietet im Vergleich zu Standard-Mainboards eine
Reihe wesentlicher Vorteile und Leistungsmerkmale:

- Integrierte Treiberstufen: Acht hochleistungsfähige
  Motoren-Steckplätze mit integrierten TMC5160-Treibern (ausgelegt für
  hohe Spannungen bis zu $60\,\text{V}$), die das erforderliche hohe
  Drehmoment für die leistungsstarken Achsmotoren ohne zusätzliche
  Treiber bereitstellen.
- Leistungsstarke Mikrocontroller-Architektur: Ein
  $32$-Bit-ARM-Cortex-M7-Prozessor (STM32H723ZGT6) mit $550\,\text{MHz}$
  Taktfrequenz sorgt für ausreichend Rechenkapazität zur Verarbeitung
  komplexer Bewegungs- und Sensorikdaten.
- Präzise Temperaturerfassung: Zwei integrierte MAX31865-Module zur
  hochpräzisen Auswertung von PT1000-Widerstandsthermometern sowie fünf
  zusätzliche NTC-Widerstandsmesseingänge.

- Leistungsfähige Aktor- und Servo-Anschlüsse:
  - Eine Servo-Steuerung mit bis zu $5\,\text{V}$ und $1\,\text{A}$
    Stromstärke.
  - Vier separate Heizelement Anschlüsse mit jeweils bis zu
    $8\,\text{A}$ Schaltleistung.
  - Sechs 2-adrige Lüfteranschlüsse (PWM) mit individuell einstellbaren
    Ausgangsspannungen von $5\,\text{V}$ bis $24\,\text{V}$.
  - Zwei 4-adrige Lüfteranschlüsse (PWM/Tacho) mit ebenfalls
    einstellbarer Ausgangsspannung ($5\,\text{V}$ bis $24\,\text{V}$).
  - Fünf zusätzliche, dauerhaft aktive $24\,\text{V}$-I/O-Ausgänge
    speziell für die Gehäuse- und Bauraumbelüftung.
- Flexible Sensorik und Endschalter: Acht einzelne
  Endschalter-Steckplätze, die flexibel auch zur Erkennung und Abfrage
  weiterer Systemmodule genutzt werden können.
- Getrennte Eingangsspannungen: Getrennte Einspeisungen für die
  Systemspannung ($\text{VIN}$), Motorenspannung ($\text{HV-VIN}$) und
  das Heizbett ($\text{Bed-VIN}$).
- Diverse Schnittstellen:
  - I²C-, SPI- und CAN-Bus-Schnittstellen zur nahtlosen Anbindung der
    externen Sensoren.
  - UART-Schnittstelle über USB und GPIOs zur zuverlässigen und
    kabellosen Kommunikation mit dem übergeordneten
    Steuerungs-Raspberry-Pi.
  - EXP1- und EXP2-Anschlüsse für kompatible Displays oder alternative
    $3{,}3\,\text{V}$-Logikausgänge.
  - Zwei RGB-Anschlüsse zur LED-Statusbeleuchtung, ein USB-C-Eingang,
    ein USB-A-Ausgang sowie ein integrierter MicroSD-Karten-Slot.

<img src="pics/kraken_pins.png" style="width:90.0%"
alt="BIGTREETECH Kraken V1.1 PINOUT (BigTreeTech 2026)" />

## Ergänzende Hardwareboards

Da das BIGTREETECH Kraken V1.1 bereits den Großteil aller im 3DGence
Industry F421 verbauten Komponenten abdecken kann, sind nur für wenige
Spezialaufgaben zusätzliche Hilfsboards erforderlich. Die verbleibenden
Komponenten, die nicht direkt auf dem Hauptboard verschaltet werden
konnten, betreffen die Positionierungssensoren der Magnetleisten sowie
ein zusätzliches PT1000-Messelement.

#### RP2040 Zero

Zur Auswertung der schnellen Positionierungssignale der X- und
Y-Achsen-Magnetleisten kann ein *RP2040 Zero* eingesetzt werden. Seine
primäre Aufgabe besteht darin, die hochfrequenten Rechtecksignale der
Magnetsensoren zu erfassen, zu zählen und bei Bedarf an den Host
(Raspberry Pi 5) zu übermitteln. Da die Signale der Magnetleisten mit
$5\,\text{V}$ arbeiten, muss zum Schutz der $3{,}3\,\text{V}$-Logik des
RP2040 ein entsprechender Spannungsteiler vorgeschaltet werden.
Anschließend wird der Mikrocontroller als sekundäre MCU für Klipper
geflasht und über eine weitere serielle UART-Schnittstelle in das
Gesamtsystem integriert.

#### MAX31865

Da die beiden integrierten PT1000-Steckplätze des Kraken V1.1 bereits
vollständig durch die Sensoren des Druckkopfes belegt sind, wird für das
verbleibende Temperaturmesselement des Bauraums ein separates
*MAX31865*-Modul per SPI-Schnittstelle am Host angeschlossen. Das
Breakout-Board wird mit $3{,}3\,\text{V}$ versorgt und benötigt die
SPI-Leitungen CLK, SDI (MOSI), SDO (MISO) sowie einen Chip-Select-Pin am
Kraken. In der Klipper-Firmware stehen hierfür standardisierte Module
zur Verfügung, bei denen nach Definition der Pins und Hinterlegung des
Referenzwiderstands eine präzise Temperaturerfassung gewährleistet ist.

<div>

</div>

#### Adapter-Platine

Da die Anschlussbelegungen und Steckverbindungen des BIGTREETECH Kraken
V1.1 nicht direkt mit dem originalen Kabelbaum des F421 übereinstimmen,
ist die Entwicklung einer Adapter-Platine von großem Vorteil. Diese
ermöglicht das direkte Einstecken der bestehenden Systemstecker ohne
aufwendiges Konfektionieren oder Umcrimpen. Die Verbindung zwischen der
Adapter-Platine und dem Hauptboard bzw. dem Steuerungs-Raspberry Pi
erfolgt dabei über kompakte Kabelbrücken. So könnte ein eventueller
Rückbau ebenfalls gewährleistet werden.

Zusätzlich bietet die Adapter-Platine Steckplätze zur direkten Aufnahme
der Ergänzungskomponenten, wie dem RP2040 Zero zur Auswertung der
Magnetleisten-Positionssensoren und dem externen MAX31865-Modul. Dies
verhindert unnötigen Verdrahtungsaufwand, reduziert Störeinflüsse auf
den Signalleitungen und sorgt für einen übersichtlichen,
wartungsfreundlichen Schaltschrankaufbau. Ein Entwurf einer solchen
Adapterplatine kann der
<a href="#fig-Adapterplatine_oben" class="quarto-xref">Abbildung 25</a>
und der
<a href="#fig-Adapterplatine" class="quarto-xref">Abbildung 26</a>
entnommen werden.

<div id="fig-Adapterplatine_oben">

<img src="pics/Adapterplatine_oben.png" style="width:65.0%" />

Abbildung 25: Adapterplatinen Entwurf Ansicht 1

</div>

<div id="fig-Adapterplatine">

<img src="pics/Adapterplatine.png" style="width:65.0%" />

Abbildung 26: Adapterplatinen Entwurf Ansicht 2

</div>

# Fazit und Ausblick

Im Rahmen der vorliegenden Machbarkeitsstudie wurde die
Steuerungshardware und -software des industriellen 3D-Druckers *3DGence
Industry F421* im Detail analysiert, um eine eventuelle Umrüstung bzw.
Weiterentwicklung des Systems zu evaluieren.

## Zusammenfassung der Erkenntnisse

Durch die schrittweise Vorgehensweise, beginnend bei den physikalischen
Grundlagen der Material Extrusion über isolierte Ansteuertests mittels
Python bis hin zur Validierung an einem Arduino-basierten Referenzsystem
(*Geeetech i3*) mit Klipper, konnten sämtliche Teilsysteme des F421
erfolgreich identifiziert und deren Funktionsweise aufgeschlüsselt
werden. Es wurde festgestellt, dass eine Umrüstung auf die
Open-Source-Software Klipper mit einem geeigneten Klipper-Board
(*BigTreeTech Kraken v1.1*) möglich und vielversprechend ist. Dabei
können fast alle der im System verbauten Komponenten direkt über das
Board angesteuert und konfiguriert werden, was bereits einfache Drucke
möglich machen würde. Zur Verbesserung der Druckqualität lassen sich
anschließend noch zusätzliche u. a. auch externe Komponenten einbringen.
Die dazu benötigte Hardware ist leicht zu beschaffen und kann, abgesehen
von der Adapterplatine, bei vielen Händlern gekauft werden. Eine selbst
entworfene Adapterplatine würde im letzten Schritt, durch saubere
Leitungsführung und Minimierung der Störeinflüsse, das Projekt
abschließen und ein solides Gesamtkonzept bereitstellen.

## Ausblick und nächste Schritte

Die Ergebnisse dieser Arbeit bilden die fundierte Grundlage für das
anschließende Hauptprojekt im Rahmen der Bachelorarbeit. Die Umsetzung
gliedert sich dabei in die primär notwendigen Grundkomponenten sowie
weiterführende Erweiterungen bei verbleibender Zeit.

In einem ersten Schritt werden die für den grundlegenden Druckbetrieb
essenziellen Komponenten umgesetzt. Dazu gehört die Einbindung der
Achsen- wie Extruder-Motoren über das Kraken-Board sowie die Erstellung
der zentralen `printer.cfg` in Klipper zur Grundansteuerung der
Heizkomponenten, Endschalter und Lüfter. Dies umfasst den gesamten
Druckkopf mit Aufheizen, Kühlung und Temperaturerfassung, den
Filament-Nachschub von unten sowie die Ansteuerung des Servos, um den
Betrieb mit zwei Filamenten zu ermöglichen.

Bei verbleibender Zeit werden in den darauffolgenden Schritten
erweiternde Systemkomponenten wie die Loadcells, zusätzliche
Temperaturregelungen, die USV oder auch die Vakuumpumpe integriert. Auf
Basis des final feststehenden Komponentenbestands wird abschließend die
Adapterplatine entworfen und bestückt, um alle Anschlüsse sauber
zusammenzuführen und einen professionellen Schaltschrankaufbau zu
gewährleisten.

# Literaturverzeichnis

*Zur sprachlichen Überarbeitung und Optimierung des Satzbaus sowie als
Denkanstoß bei der Erstellung der Testcodes der I²C-Klipper
Ansteuerungen wurden die Sprachmodelle ChatGPT OpenAI (2026) und Gemini
Google (2026) eingesetzt. Die inhaltliche Kontrolle und Validierung
aller generierten Inhalte erfolgte eigenständig durch den Verfasser.*

<div id="refs" class="references csl-bib-body hanging-indent">

<div id="ref-3dgence_f421" class="csl-entry">

3DGence. 2026. „Industry F421 – High-Performance 3D-Drucker“.
<https://3dgence.com/de/3d-drucker/industry-f421/>.

</div>

<div id="ref-AM23HSA4B0-03" class="csl-entry">

Amazon Vendor. 2026. „AM23HSA4B0-03 Stepper Motor“.
<https://www.amazon.com/dp/B0DQ56PN1Q>.

</div>

<div id="ref-Github_Kraken" class="csl-entry">

BigTreeTech. 2026. „BIGTREETECH-Kraken“.
<https://github.com/bigtreetech/BIGTREETECH-Kraken>.

</div>

<div id="ref-3D-Druck_Leitfaden" class="csl-entry">

Chan, Violet. 2026. „Der vollständige Leitfaden zum FDM-3D-Druck: Vom
Design zum Bauteil“.
<https://www.rapiddirect.com/de/blog/fdm-3d-printing-complete-guide/>.

</div>

<div id="ref-TCST2103" class="csl-entry">

Conrad Electronic. 2026. „Vishay Gabel-Lichtschranke TCST 2103“.
<https://www.conrad.de/de/p/vishay-gabel-lichtschranke-tcst-2103-tcst-2103-kontrasterkennung-1-st-184250.html>.

</div>

<div id="ref-17HS16-2004S1" class="csl-entry">

Dolunto. 2026. „NEMA 17 Stepper Motor (7HS16-2004S1)“.
<https://www.amazon.de/DOLUNTO-Bipolarer-Schrittmotor-7HS16-2004S1-Drucker/dp/B0B7HHF4QS>.

</div>

<div id="ref-AM24HS5401-10N" class="csl-entry">

Electronics Panga. 2026. „MOONS’ AM24HS5401-10N NEMA 24 Stepper Motor“.
<https://electronicspanga.com/shop/moons-am24hs5401-10n-nema24-4-5a-step1-8-2-pahse-4-wires-stepping-motor-stm312/>.

</div>

<div id="ref-gemini" class="csl-entry">

Google. 2026. *Gemini (Modell mit aktiviertem „hohen Denkaufwand“)*.
Large Language Model.

</div>

<div id="ref-display" class="csl-entry">

Hamtysan. 2026. „Raspberry Pi Touch Screen“.
<https://www.amazon.de/dp/B0B9M5SCG4>.

</div>

<div id="ref-Github" class="csl-entry">

Ick, Mirco. 2026. „Github Praxis-ADAS-3DDruck“.
<https://github.com/mircoick/Praxis-ADAS-3DDruck>.

</div>

<div id="ref-u20cam" class="csl-entry">

Innomaker. 2026. „1080P USB2.0 UVC Kamera“.
<https://www.amazon.de/dp/B0H26BG9RP>.

</div>

<div id="ref-meiners2024" class="csl-entry">

Meiners, Mirco. o. J. „Vorgaben für PRX-Berichte“. Technisches
Berichtswesen. Hochschule Bremen.

</div>

<div id="ref-step_motor" class="csl-entry">

MOONS’ Industries. 2026. *AM23HSA4B0-03: NEMA 23 Standard Hybrid Stepper
Motor Datasheet*.
<https://www.moonsindustries.com/p/am-series-standard-hybrid-stepper-motors/am23hsa4b0-03-000004611110013316>.

</div>

<div id="ref-chatgpt" class="csl-entry">

OpenAI. 2026. *ChatGPT (Modell mit aktiviertem „Nachdenken“-Modus)*.
Large Language Model.

</div>

<div id="ref-adas" class="csl-entry">

Peper & Söhne. 2026. „QUARTIER LLOYD INDUSTRIEPARK - BREMEN“.
<https://peperundsoehne.de/gewerbepark-lloyd-industriepark---bremen>.

</div>

</div>
