# JTIS — Konzept-Dokument

**Judo Tournament Information System**
*Version 1.0 — Stand: Juni 2026*

---

## Inhaltsverzeichnis

1. [Vision & Überblick](#1-vision--überblick)
2. [SaaS & Multi-Tenancy](#2-saas--multi-tenancy)
3. [Rollen & Rechte](#3-rollen--rechte)
4. [Modulübersicht](#4-modulübersicht)
5. [Modul 0: Event-Einstellungen](#5-modul-0-event-einstellungen)
6. [Modul 1: Helfer-, Personal- & Einsatzplanung](#6-modul-1-helfer--personal---einsatzplanung)
7. [Modul 2: Venue-Management](#7-modul-2-venue-management)
8. [Modul 3: Transport-Management](#8-modul-3-transport-management)
9. [Modul 4: Kommunikation](#9-modul-4-kommunikation)
10. [Modul 5: Projekt-/Aufgabenmanagement](#10-modul-5-projekt-aufgabenmanagement)
11. [Modul 6: Finanz-Controlling](#11-modul-6-finanz-controlling)
12. [Modul 7: Hotel-/Unterkunftsmanagement](#12-modul-7-hotel-unterkunftsmanagement)
13. [Organisations-Einstellungen (Tenant-Ebene)](#13-organisations-einstellungen-tenant-ebene)
14. [Tech-Stack](#14-tech-stack)
15. [Integrationen](#15-integrationen)
16. [Internationalisierung](#16-internationalisierung)
17. [Datenschutz (DSGVO)](#17-datenschutz-dsgvo)
18. [Datenmodell-Entwürfe](#18-datenmodell-entwürfe)
19. [MVP-Roadmap](#19-mvp-roadmap)

---

## 1. Vision & Überblick

JTIS (Judo Tournament Information System) ist eine **webbasierte, modulare SaaS-Software** für die Organisation von Sport-Veranstaltungen mit initialem Fokus auf Judo-Turniere.

### Abgrenzung

JTIS deckt **alles vor, neben und nach** einem Turnier ab — **nicht** die Turnierdurchführung selbst (Kampfabwicklung, Ergebniserfassung, Turnierbaum). Dafür existiert die etablierte Software **TUMAG** (dokume), mit der JTIS perspektivisch Daten austauscht.

### Scope

| Bereich | JTIS | TUMAG |
|---|---|---|
| Event-Planung & Konfiguration | ✅ | ❌ |
| Helfer-/Personalplanung | ✅ | ❌ |
| Venue-Management | ✅ | ❌ |
| Transport-Logistik | ✅ | ❌ |
| Kommunikation | ✅ | ❌ |
| Aufgabenmanagement | ✅ | ❌ |
| Finanz-Controlling | ✅ | ❌ |
| Hotel-/Unterkunftsverwaltung | ✅ | ❌ |
| Turnierdurchführung (Kampf, Ergebnis) | ❌ | ✅ |
| Teilnehmer-Meldung (Wettkampf) | ❌ | ✅ |

### Langfristiger Ausblick

Der Arbeitstitel „JTIS" ist judo-spezifisch. Langfristig ist ein **sportartübergreifender Name** geplant, da die Modulstruktur (Helfer, Transport, Venue, Finanzen) für beliebige Sportveranstaltungen anwendbar ist.

---

## 2. SaaS & Multi-Tenancy

### Architektur

JTIS wird als **Single-Instance, Multi-Tenant SaaS** betrieben:

- **Eine Instanz** bedient alle Kunden (Organisationen)
- Jede **Organisation** ist ein eigenständiger Tenant
- Jede Organisation kann **beliebig viele Veranstaltungen** anlegen
- Strikte Datentrennung durch **Row-Level Multi-Tenancy** mit `tenant_id`

### Tenant-Hierarchie

```
SaaS-Plattform (JTIS)
└── Organisation (Tenant)
    ├── Org-Einstellungen (Stammdaten, Templates, Abrechnungssätze)
    ├── Veranstaltung A
    │   ├── Module (aktiviert/deaktiviert)
    │   └── Rollen & Berechtigungen
    └── Veranstaltung B
        ├── Module (aktiviert/deaktiviert)
        └── Rollen & Berechtigungen
```

### Datenisolation

- PostgreSQL **Row-Level Security (RLS)** auf Basis von `tenant_id`
- Jede Datenbankabfrage wird automatisch auf den aktiven Tenant eingeschränkt
- Cross-Tenant-Zugriff ist technisch ausgeschlossen

### SaaS-Abrechnung

- Gebühren über einen **Payment-Provider** (noch zu bestimmen)
- Abrechnungsmodell (pro Event, pro Modul, Flatrate) wird im Detail noch definiert
- Perspektivisch auch Zahlungsabwicklung für Startgebühren o.Ä. denkbar

---

## 3. Rollen & Rechte

### Konzept: RBAC pro Modul

JTIS setzt auf **Role-Based Access Control (RBAC)** mit modulspezifischer Granularität:

- Rollen werden **pro Modul** definiert
- Jedes Modul bringt eigene Rollen-Templates mit
- Organisationen können eigene Rollen konfigurieren
- Event-spezifische Rollenzuweisungen sind möglich

### Zielgruppen und Zugriffsebenen

| Zielgruppe | Zugriff | Login erforderlich |
|---|---|---|
| Plattform-Admin | Alle Tenants, System-Konfiguration | ✅ |
| Organisations-Admin | Alle Events einer Organisation, Org-Einstellungen | ✅ |
| Event-Leitung | Alle Module eines Events | ✅ |
| Modul-Verantwortliche | Spezifisches Modul (z.B. Transport-Leitung) | ✅ |
| Helfer | Eigene Schichten, Einsatzpläne | ✅ |
| Delegationen | Self-Service (Transport, Hotel) | ❌ (optional) |
| Externe (z.B. Fahrer) | Eingeschränkte Ansichten | ❌ (optional) |

### Self-Service ohne Login

Bestimmte Bereiche sind **ohne Login** zugänglich, z.B.:

- Delegationen hinterlegen Reisedaten für Transport
- Delegationen melden Zimmerbedarf an
- Helfer-Registrierung über öffentliches Portal

Der Zugriff erfolgt über **Token-basierte Links** (zeitlich begrenzt, eindeutig pro Delegation/Person).

---

## 4. Modulübersicht

### Modulare Architektur

Jedes Modul ist ein **eigenständiger Funktionsbereich**, der pro Event aktiviert oder deaktiviert werden kann. Module können untereinander Daten referenzieren.

### Modul-Katalog

| Nr. | Modul | Ebene | MVP-Phase | Abhängigkeiten |
|---|---|---|---|---|
| — | Organisations-Einstellungen | Organisation | 1 | — |
| 0 | Event-Einstellungen | Veranstaltung | 1 | — |
| 1 | Helfer-, Personal- & Einsatzplanung | Veranstaltung | 2 | Modul 0 |
| 2 | Venue-Management | Veranstaltung | 3 | Modul 0 |
| 3 | Transport-Management | Veranstaltung | 4 | Modul 0, Modul 1 (Fahrer) |
| 4 | Kommunikation | Querschnitt | Post-MVP | Alle Module (als Infrastruktur-Layer) |
| 5 | Projekt-/Aufgabenmanagement | Veranstaltung | Post-MVP | Modul 0 |
| 6 | Finanz-Controlling | Veranstaltung | Post-MVP | Modul 0, Modul 1 (Abrechnung) |
| 7 | Hotel-/Unterkunftsmanagement | Veranstaltung | Post-MVP | Modul 0, Modul 3 (Transport) |

### Modulverknüpfungen

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│   Modul 1   │────▶│   Modul 3     │────▶│   Modul 7    │
│   Helfer    │     │   Transport   │     │   Hotel      │
│             │     │  (Fahrer aus  │     │  (Adressen   │
│             │     │   Modul 1)    │     │   als Stops) │
└──────┬──────┘     └───────────────┘     └──────┬───────┘
       │                                         │
       ▼                                         ▼
┌─────────────┐                          ┌──────────────┐
│   Modul 6   │◀─────────────────────────│   Modul 6    │
│   Finanzen  │   (Kosten-Tracking)      │   Finanzen   │
└─────────────┘                          └──────────────┘
       ▲
       │
┌──────┴──────┐
│   Modul 4   │  ◀── wird von allen Modulen genutzt
│   Komm.     │
└─────────────┘
```

---

## 5. Modul 0: Event-Einstellungen

**MVP-Priorität:** Phase 1
**Ebene:** Veranstaltung

### Zweck

Zentrale Konfiguration einer Veranstaltung. Jedes Event beginnt hier — erst nach der Grundkonfiguration können weitere Module aktiviert werden.

### Funktionsumfang

#### Event-Details
- Name der Veranstaltung
- Datum / Zeitraum (Start- und Enddatum)
- **Zeitzone** (Pflichtfeld — kritisch bei internationalen Events)
- Beschreibung
- Veranstaltungsort (Referenz auf Venue, sofern Modul 2 aktiv)
- Status (Entwurf, Aktiv, Abgeschlossen, Archiviert)

#### Modulaktivierung
- Pro Event können Module einzeln aktiviert/deaktiviert werden
- Deaktivierte Module sind unsichtbar und liefern keine Daten
- Abhängigkeiten werden geprüft (z.B. Transport braucht Helfer für Fahrer)

#### Event-spezifische Rollen
- Rollenzuweisung für dieses Event
- Ergänzend zu Org-weiten Rollen
- Modul-spezifische Rechtevergabe

#### Konfigurierbare Optionen
- Self-Service-Änderungen durch Delegationen erlauben (ja/nein)
- Tracking-Funktionen aktivieren (ja/nein)
- Öffentliche Sichtbarkeit bestimmter Daten
- Weitere modulspezifische Schalter

---

## 6. Modul 1: Helfer-, Personal- & Einsatzplanung

**MVP-Priorität:** Phase 2
**Ebene:** Veranstaltung
**Abhängigkeiten:** Modul 0

### Zweck

Vollständige Verwaltung aller Helfer und ihres Einsatzes — von der Registrierung über die Schichtplanung bis zur Einsatzdokumentation.

### Funktionsumfang

#### Helfer-Typen
- **Frei konfigurierbar** je Organisation (Definition auf Org-Ebene)
- Beispiele: Mattenpersonal, Fahrer, Sanitäter, Kampfrichter (KaRi), Einlass, Catering
- Helfer-Typen bestimmen verfügbare Einsatzbereiche und Abrechnungssätze
- Helfer-Typ „Fahrer" kann für das Transport-Modul reserviert/gesperrt werden

#### Helfer-Registrierung
- **Self-Service-Portal**: Helfer melden sich eigenständig an
- Erfasste Daten: Name, Kontakt, verfügbare Zeiten, Präferenzen, Helfer-Typ
- **Bestätigungs-Workflow**: Orga-Team prüft und bestätigt Registrierungen
- **Einsatzbestätigung**: Helfer erhalten Bestätigung mit Einsatzdetails

#### Schichtplanung
- Schichten definieren (Name, Zeitraum, Ort, benötigte Helfer-Anzahl)
- Schicht-Templates auf Organisations-Ebene (wiederverwendbar)
- Helfer manuell oder automatisch zuweisen
- Über-/Unterbesetzung erkennen
- Schichtübersicht (Tages-/Wochenansicht)

#### Helfer-Posten
- Konkrete Posten mit Aufgabenbeschreibung definieren
- Posten innerhalb einer Schicht zuweisen
- Standort-Referenz (z.B. „Matte 3", „Eingang Nord")

#### Qualifikationen
- **Nicht im MVP** — aber Architektur wird vorbereitet
- Perspektivisch: Qualifikationsanforderungen pro Posten, Abgleich mit Helfer-Profilen
- Zertifikate, Lizenzen (z.B. Kampfrichter-Lizenz)

#### Abrechnung (Datenlieferant)
- Die Einsatzplanung liefert **Stunden und Einsatzdaten** an Modul 6 (Finanz-Controlling)
- Keine eigene Abrechnungslogik — nur Datenerfassung
- Verknüpfung: Helfer-Typ → Abrechnungssatz (aus Org-Einstellungen) → Modul 6

---

## 7. Modul 2: Venue-Management

**MVP-Priorität:** Phase 3
**Ebene:** Veranstaltung
**Abhängigkeiten:** Modul 0

### Zweck

Verwaltung aller Veranstaltungsorte (Hallen, Räume, Außenbereiche) und deren Buchung durch interne Teams und externe Delegationen.

### Funktionsumfang

#### Hallen-/Raumverwaltung
- Venues anlegen mit Stammdaten (Name, Adresse, Kapazität, Ausstattung)
- Mehrere Venues pro Event möglich
- Venues sind **innerhalb einer Organisation eventübergreifend wiederverwendbar**
- Räume innerhalb eines Venues (z.B. Halle A, Aufwärmhalle, Presseraum)

#### Buchungsverwaltung
- Räume/Hallen für Zeitslots buchen
- Buchungen durch Orga-Team und/oder Delegationen (z.B. Trainingshalle)
- Konflikt-Erkennung bei Doppelbuchungen
- Status-Tracking (angefragt, bestätigt, storniert)

#### Lagekarte
- Kartenansicht mit **Leaflet + OpenStreetMap**
- Venues auf der Karte markieren
- Routing-Informationen für Transport-Modul

#### Explizite Abgrenzung
- **KEINE Flächenplanung** (Hallenaufteilung, Mattenplan)
- **KEINE Infrastruktur-Verwaltung** (Strom, Wasser, Technik)

---

## 8. Modul 3: Transport-Management

**MVP-Priorität:** Phase 4
**Ebene:** Veranstaltung
**Abhängigkeiten:** Modul 0, Modul 1 (für Fahrer)

### Zweck

Komplette Transport-Logistik — von Shuttle-Routen über Fuhrpark bis zur Self-Service-Buchung durch Delegationen.

### Funktionsumfang

#### Shuttle-Routen
- **Feste Routen**: Vordefinierte Strecken (z.B. Flughafen → Hotel → Halle)
- **Individuelle Routen**: Einmalige Sonderfahrten
- Haltestellen definieren (verknüpft mit Venues aus Modul 2 und Hotels aus Modul 7)
- Kartenansicht mit **Leaflet + OpenStreetMap**

#### Fuhrpark-Verwaltung
- **Eigene Fahrzeuge**: Typ, Kapazität, Verfügbarkeit
- **Externe Mietbusse**: Anbieter, Mietdauer, Kosten
- Fahrzeugzuordnung zu Routen/Fahrten

#### Fahrplan
- **Feste Abfahrtszeiten**: Regulärer Fahrplan (z.B. stündlich)
- **On-Demand**: Paralleler Betrieb von Shuttle nach Bedarf
- Kombination beider Modi pro Route möglich

#### Fahrer
- Greift auf **Modul 1 (Helfer-Planung)** zurück
- Helfer-Typ „Fahrer" wird für Transport reserviert
- Fahrer-Schichten und -Zuordnung über Einsatzplanung
- Führerschein-Klassen (perspektivisch über Qualifikationen)

#### Transportbuchung
- **Massen-Import**: CSV/Excel-Upload für viele Delegationen gleichzeitig
- **Self-Service**: Delegationen buchen eigenständig
- Buchungsübersicht für Orga-Team

#### Self-Service für Delegationen
- **Ohne Login** zugänglich (Token-basierte Links)
- Reisedaten hinterlegen (Ankunft, Abfahrt, Personenzahl, Gepäck)
- Eigene Buchungen einsehen
- **Änderungen durch Delegationen**: Optional — muss pro Event durch die Organisation explizit erlaubt werden (Schalter in Event-Einstellungen)

#### Tracking
- **Optional** — kann zentral durch die Organisation deaktiviert werden
- Live-Position von Shuttles (wenn aktiviert)
- Geschätzte Ankunftszeit
- Benachrichtigungen bei Verspätungen (über Modul 4)

---

## 9. Modul 4: Kommunikation

**Typ:** Querschnittsmodul (Infrastruktur-Layer)
**Ebene:** Übergreifend (Organisation + Veranstaltung)

### Zweck

Zentraler Kommunikations-Layer, den **alle Module** nutzen. Kein eigenständiges „Nachrichten-Tool", sondern die Infrastruktur für jede Art von Benachrichtigung und Massenkommunikation.

### Funktionsumfang

#### Kanäle
- **E-Mail**: Primärer Kanal für formelle Kommunikation
- **WhatsApp**: Für schnelle, informelle Benachrichtigungen
- **Telegram**: Alternativ zu WhatsApp
- Kanal-Präferenz pro Empfänger konfigurierbar

#### Templates
- **Organisations-Ebene**: Vorlagen für wiederkehrende Kommunikation (z.B. Helfer-Bestätigung)
- **Event-Ebene**: Event-spezifische Anpassungen
- Platzhalter/Variablen für dynamische Inhalte (Name, Schicht, Datum, etc.)
- Mehrsprachige Templates

#### Massen- und Einzelkommunikation
- Massenversand an Gruppen (z.B. alle Helfer, alle Delegationen)
- Individuelle Nachrichten
- Filter- und Segmentierungsmöglichkeiten

#### Automatische Benachrichtigungen
- Modulübergreifende Trigger, z.B.:
  - „Schicht beginnt in 1 Stunde" (Modul 1)
  - „Shuttle-Abfahrt in 30 Minuten" (Modul 3)
  - „Aufgabe überfällig" (Modul 5)
  - „Zimmerkontingent fast erschöpft" (Modul 7)
- Konfigurierbare Trigger pro Modul und Event

#### Protokollierung
- Vollständiges Kommunikationsprotokoll über alle Module
- Zustellstatus pro Nachricht und Kanal
- Verknüpfung mit Quellobjekt (z.B. welche Schicht, welche Buchung)

---

## 10. Modul 5: Projekt-/Aufgabenmanagement

**Ebene:** Veranstaltung

### Zweck

Strukturierte Aufgabenverwaltung für die gesamte Event-Vorbereitung und -Durchführung.

### Funktionsumfang

#### Aufgabenverwaltung
- Aufgaben mit **beliebig vielen Unteraufgaben** (unbegrenzte Verschachtelung)
- **Einmalige Aufgaben**: z.B. „Genehmigung einholen"
- **Regelmäßige Aufgaben**: z.B. „Wöchentlicher Status-Check"
- Aufgabenzuordnung an Personen (Verantwortliche + Mitarbeiter)
- Kategorien zur Strukturierung

#### Fristenüberwachung
- Fälligkeitsdatum pro Aufgabe
- Erinnerungen vor Fristablauf (über Modul 4)
- Eskalation bei Überschreitung
- Zeitliche Abhängigkeiten zwischen Aufgaben

#### Darstellungsformen
- **Liste**: Klassische Aufgabenliste mit Filtern
- **Kanban**: Spaltenbasierte Ansicht (z.B. Offen → In Arbeit → Erledigt)
- **Gantt**: Zeitstrahl mit Abhängigkeiten und Meilensteinen

#### Automatisierung
- **Auto-Trigger**: Zeitgesteuerte Aktionen, z.B.:
  - „30 Tage vor Event → Einladungen an Delegationen versenden"
  - „7 Tage vor Event → Schichtpläne finalisieren"
  - „1 Tag nach Event → Feedback-Umfrage senden"
- Trigger können Aktionen in anderen Modulen auslösen

#### Modulverknüpfung
- Aufgaben können mit Objekten aus anderen Modulen verknüpft werden
- Beispiel: „Delegation TUR vom Flughafen abholen" → verknüpft mit Transportbuchung in Modul 3
- Beispiel: „Trainingshalle buchen" → verknüpft mit Venue-Buchung in Modul 2

---

## 11. Modul 6: Finanz-Controlling

**Ebene:** Veranstaltung

### Zweck

Finanzielle Übersicht und Kontrolle über ein Event — kein Buchhaltungssystem, sondern ein Controlling-Werkzeug.

### Funktionsumfang

#### Budgetplanung
- **Gesamtbudget** pro Event definieren
- Budget in **Posten** aufteilen (z.B. Halle, Transport, Personal, Catering)
- Posten können Modulen/Bereichen zugeordnet werden

#### Soll/Ist-Vergleich
- Geplante Kosten vs. tatsächliche Ausgaben
- Abweichungsanzeige pro Posten
- Übersichtliches Dashboard

#### Helfer-Abrechnung
- Automatische Berechnung: **Stunden × Abrechnungssatz**
- Stunden aus Modul 1 (Einsatzplanung)
- Abrechnungssätze aus Organisations-Einstellungen
- Aufstellung pro Helfer und Helfer-Typ

#### Einnahmen-Tracking
- **Startgebühren**: Import/manuelle Erfassung
- **Sponsoring**: Zugesagte und erhaltene Beträge
- **Zuschüsse**: Verbandsförderungen, öffentliche Mittel
- Einnahmen-Kategorien frei definierbar

#### Kostenstellen
- Pro Modul/Bereich definierbar
- Zuordnung von Ausgaben zu Kostenstellen
- Auswertung nach Kostenstellen

#### Abrechnungssätze (Organisations-Ebene)
- Zentral auf Org-Ebene definiert, für alle Events verwendbar
- Beispiele:
  - Kampfrichter (KaRi): 80 €/Tag
  - Helfer: 12 €/Stunde
  - Fahrt-Pauschale: 0,30 €/km

#### Export
- **CSV-Export** für externe Weiterverarbeitung
- **DATEV-Export** für Steuerberater/Buchhaltung
- Filterbarer Export (Zeitraum, Kostenstelle, Kategorie)

#### Explizite Abgrenzung
- **KEINE Rechnungsstellung** (kein Rechnungsgenerator)
- **KEIN Freigabe-Workflow** (keine Genehmigungsketten für Ausgaben)

---

## 12. Modul 7: Hotel-/Unterkunftsmanagement

**Ebene:** Veranstaltung
**Abhängigkeiten:** Modul 0, optional Modul 3 (Transport), Modul 6 (Finanzen)

### Zweck

Verwaltung von Zimmerkontingenten, Verteilung an Delegationen und Generierung von Rooming-Listen.

### Funktionsumfang

#### Kontingent-Verwaltung
- Zimmerkontingente bei Hotels buchen/reservieren
- Kontingente an Delegationen verteilen
- Verfügbarkeits-Tracking (gebucht, zugewiesen, frei)
- Stornierungsfristen hinterlegen

#### Zimmertypen
- **EZ** (Einzelzimmer)
- **DZ** (Doppelzimmer)
- **MBZ** (Mehrbettzimmer)
- Weitere Typen frei definierbar
- Preise pro Typ und Hotel

#### Self-Service
- Delegationen melden eigenständig ihren Unterkunftsbedarf an
- Angabe: Anzahl Personen, Zimmertyp-Präferenz, Zeitraum
- Bestätigung durch Orga-Team

#### Rooming-Listen
- Automatische Generierung von Rooming-Listen für Hotels
- Export als PDF/Excel
- Gruppierung nach Delegation, Zimmertyp, Zeitraum

#### Alternative Unterkünfte
- Nicht nur Hotels — auch z.B. **Turnhallen mit Feldbetten** (Jugend-Turniere)
- Flexible Unterkunftstypen (Hotel, Pension, Jugendherberge, Sporthalle, etc.)

#### Verknüpfungen
- **Transport (Modul 3)**: Hotel-Adressen als Shuttle-Haltestellen verfügbar
- **Finanz-Controlling (Modul 6)**: Kosten-Tracking für Unterkünfte → automatische Übernahme

---

## 13. Organisations-Einstellungen (Tenant-Ebene)

### Zweck

Zentrale Konfiguration, die für **alle Events einer Organisation** gilt. Wiederverwendbare Stammdaten und Templates.

### Funktionsumfang

| Bereich | Beschreibung |
|---|---|
| Stammdaten | Name, Adresse, Logo, Kontaktdaten der Organisation |
| Helfer-Typen | Definition aller verfügbaren Helfer-Typen (Modul 1) |
| Schicht-Templates | Wiederverwendbare Schichtvorlagen (Modul 1) |
| Abrechnungssätze | Stunden-/Tagessätze pro Helfer-Typ, km-Pauschalen (Modul 6) |
| Kommunikations-Templates | Org-weite Nachrichtenvorlagen (Modul 4) |
| Venue-Stammdaten | Wiederverwendbare Venues (Modul 2) |
| Benutzer-Verwaltung | Org-weite Rollenzuweisung |
| SaaS-Abrechnung | Abo-Verwaltung, Zahlungsmethode |

---

## 14. Tech-Stack

### Übersicht

| Schicht | Technologie |
|---|---|
| **Backend** | Python 3.12+ / FastAPI |
| **ORM** | SQLAlchemy 2.x |
| **Migrationen** | Alembic |
| **Frontend** | React 18+ / TypeScript |
| **UI-Framework** | react-bootstrap 5 |
| **Routing** | React Router v6+ |
| **Datenbank** | PostgreSQL 16+ (Row-Level Security) |
| **Auth** | Keycloak (OIDC / OAuth2) |
| **API** | REST mit OpenAPI (auto-generated via FastAPI) |
| **Karten** | Leaflet + OpenStreetMap |
| **Payment** | Provider TBD |
| **Infrastruktur** | Docker Compose (Dev + Prod) |
| **Hosting** | VPS-Start, Cloud-ready |

### Architektur-Entscheidungen

#### Backend — FastAPI
- Moderne, performante Python-API
- Automatische OpenAPI-Dokumentation
- Async-Support für I/O-lastige Operationen
- Pydantic für Validierung und Serialisierung

#### Frontend — React + TypeScript
- Komponentenbasierte UI-Architektur
- TypeScript für Typsicherheit
- react-bootstrap für konsistentes, responsives Design
- React Router für clientseitiges Routing

#### Datenbank — PostgreSQL mit RLS
- Row-Level Security für Tenant-Isolation
- `tenant_id` auf allen relevanten Tabellen
- Bewährte, skalierbare relationale Datenbank
- JSON/JSONB für flexible Datenstrukturen wo sinnvoll

#### Auth — Keycloak
- Separater Auth-Service (nicht im Monolith)
- OIDC/OAuth2-Standard
- Wiederverwendbar für andere Projekte
- Self-Service: Registrierung, Passwort-Reset
- Social Logins perspektivisch möglich
- Mandantenfähig (Realms)

#### Infrastruktur — Docker Compose
- Einheitliche Dev- und Prod-Umgebung
- Services: API, Frontend, PostgreSQL, Keycloak, Redis (optional)
- Start auf VPS, Migration zu Cloud (AWS/GCP) bei Bedarf möglich

---

## 15. Integrationen

### Geplante Integrationen

| Integration | Beschreibung | Priorität |
|---|---|---|
| **TUMAG (dokume)** | Import/Export von Teilnehmer- und Ergebnisdaten | Hoch |
| **Judo-Verbände** | Datenaustausch mit DJB, EJU, IJF | Mittel |
| **iCal-Export** | Schichten und Events als Kalender-Abonnement | Hoch |
| **Karten** | Leaflet + OpenStreetMap (kostenlos, Open Source) | Im MVP |
| **Payment-Provider** | SaaS-Abrechnung, perspektivisch Startgebühren | Mittel |
| **Dateiablage** | Eigene Lösung (kein externer Cloud-Speicher) | Mittel |

### API-Strategie

- **Private API**: Keine öffentliche REST-API für Dritte
- Integrationen nur über definierte, kontrollierte Schnittstellen
- Perspektivisch: Webhook-Support für ausgewählte Partner (z.B. TUMAG)

---

## 16. Internationalisierung

### Mehrsprachigkeit (i18n)

- **Start-Sprachen**: Deutsch + Englisch
- Alle UI-Texte über i18n-Framework (z.B. react-i18next)
- Backend-Nachrichten und Templates ebenfalls übersetzbar
- Weitere Sprachen bei Bedarf ergänzbar

### Zeitzone

- **Pflichtfeld** bei Event-Erstellung
- Alle Zeitangaben werden intern in UTC gespeichert
- Anzeige erfolgt in der Event-Zeitzone
- Benutzer können optional eigene Zeitzone wählen

### Währung

- **Start**: EUR (Euro)
- Architektur vorbereitet für weitere Währungen
- Währung pro Event konfigurierbar

---

## 17. Datenschutz (DSGVO)

### Anforderungen

| Bereich | Maßnahme |
|---|---|
| **Löschfristen** | Automatische Löschung personenbezogener Daten nach konfigurierbaren Fristen |
| **Einwilligungen** | Dokumentierte Einwilligungen für Datenverarbeitung und Kommunikation |
| **Datenexport** | Betroffene können ihre Daten in maschinenlesbarem Format exportieren (Art. 20 DSGVO) |
| **Auskunftsrecht** | Übersicht aller gespeicherten Daten einer Person (Art. 15 DSGVO) |
| **Löschrecht** | Anfrage auf Datenlöschung bearbeitbar (Art. 17 DSGVO) |
| **Internationale Teilnehmer** | Besondere Berücksichtigung bei nicht-EU Teilnehmern (z.B. Datentransfer) |
| **Verarbeitungsverzeichnis** | Dokumentation aller Verarbeitungstätigkeiten |
| **Auftragsverarbeitung** | AV-Verträge mit Sub-Prozessoren (Hosting, Payment, etc.) |

### Technische Maßnahmen

- Verschlüsselung in Transit (TLS) und at Rest
- Tenant-Isolation durch RLS
- Audit-Log für Datenzugriffe
- Pseudonymisierung wo möglich
- Minimale Datenspeicherung (Datensparsamkeit)

---

## 18. Datenmodell-Entwürfe

### Übergreifende Konventionen

- Alle Tabellen mit Tenant-Bezug enthalten `tenant_id` (UUID, FK → `organizations`)
- Standardfelder: `id` (UUID PK), `created_at`, `updated_at`, `created_by`, `updated_by`
- Soft-Delete via `deleted_at` (nullable Timestamp)
- Alle Zeitangaben in UTC

---

### 18.1 Core / Multi-Tenancy

#### `organizations` — Organisationen (Tenants)

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | Tenant-ID |
| `name` | VARCHAR(255) | Organisationsname |
| `slug` | VARCHAR(100) UNIQUE | URL-freundlicher Bezeichner |
| `address` | JSONB | Adressdaten |
| `logo_url` | TEXT | Logo-URL |
| `contact_email` | VARCHAR(255) | Kontakt-E-Mail |
| `settings` | JSONB | Org-weite Einstellungen |
| `subscription_plan` | VARCHAR(50) | SaaS-Tarif |
| `created_at` | TIMESTAMPTZ | Erstellungsdatum |
| `updated_at` | TIMESTAMPTZ | Letzte Änderung |

#### `users` — Benutzer (plattformweit)

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | User-ID |
| `keycloak_id` | UUID UNIQUE | Referenz zu Keycloak |
| `email` | VARCHAR(255) UNIQUE | E-Mail-Adresse |
| `display_name` | VARCHAR(255) | Anzeigename |
| `phone` | VARCHAR(50) | Telefonnummer |
| `preferred_language` | VARCHAR(5) | Bevorzugte Sprache (z.B. `de`) |
| `created_at` | TIMESTAMPTZ | Erstellungsdatum |

#### `organization_members` — Org-Mitgliedschaften

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK → organizations | Tenant |
| `user_id` | UUID FK → users | Benutzer |
| `role` | VARCHAR(50) | Rolle in der Organisation |
| `created_at` | TIMESTAMPTZ | Beitrittsdatum |

**Beziehungen:**
- `organizations` 1:n `organization_members`
- `users` 1:n `organization_members`

---

### 18.2 Modul 0: Event-Einstellungen

#### `events` — Veranstaltungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | Event-ID |
| `tenant_id` | UUID FK → organizations | Tenant |
| `name` | VARCHAR(255) | Veranstaltungsname |
| `description` | TEXT | Beschreibung |
| `start_date` | DATE | Startdatum |
| `end_date` | DATE | Enddatum |
| `timezone` | VARCHAR(50) NOT NULL | Zeitzone (z.B. `Europe/Berlin`) |
| `status` | VARCHAR(20) | `draft`, `active`, `completed`, `archived` |
| `settings` | JSONB | Event-spezifische Einstellungen |
| `created_at` | TIMESTAMPTZ | Erstellungsdatum |
| `updated_at` | TIMESTAMPTZ | Letzte Änderung |

#### `event_modules` — Aktivierte Module pro Event

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `module_key` | VARCHAR(50) | Modul-Schlüssel (z.B. `helpers`, `transport`) |
| `is_active` | BOOLEAN | Aktiv/Inaktiv |
| `config` | JSONB | Modulspezifische Event-Konfiguration |

#### `event_roles` — Rollenzuweisungen pro Event

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `user_id` | UUID FK → users | Benutzer |
| `module_key` | VARCHAR(50) | Modul (oder `*` für alle) |
| `role` | VARCHAR(50) | Rolle (z.B. `admin`, `viewer`, `editor`) |

**Beziehungen:**
- `organizations` 1:n `events`
- `events` 1:n `event_modules`
- `events` 1:n `event_roles`

---

### 18.3 Modul 1: Helfer-, Personal- & Einsatzplanung

#### `helper_types` — Helfer-Typen (Org-Ebene)

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `name` | VARCHAR(100) | Bezeichnung (z.B. „Mattenpersonal") |
| `description` | TEXT | Beschreibung |
| `is_driver` | BOOLEAN | Fahrer-Typ (für Transport-Modul) |
| `hourly_rate` | DECIMAL(10,2) | Stundensatz (€) |
| `daily_rate` | DECIMAL(10,2) | Tagessatz (€) |
| `mileage_rate` | DECIMAL(10,4) | km-Pauschale (€) |

#### `helpers` — Helfer-Registrierungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `user_id` | UUID FK → users | Benutzer (optional, bei Self-Service ohne Login: NULL) |
| `helper_type_id` | UUID FK → helper_types | Helfer-Typ |
| `first_name` | VARCHAR(100) | Vorname |
| `last_name` | VARCHAR(100) | Nachname |
| `email` | VARCHAR(255) | E-Mail |
| `phone` | VARCHAR(50) | Telefon |
| `status` | VARCHAR(20) | `registered`, `confirmed`, `rejected`, `cancelled` |
| `availability` | JSONB | Verfügbare Zeiten |
| `notes` | TEXT | Anmerkungen |

#### `shifts` — Schichten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `name` | VARCHAR(255) | Schichtname |
| `start_time` | TIMESTAMPTZ | Beginn |
| `end_time` | TIMESTAMPTZ | Ende |
| `location` | VARCHAR(255) | Einsatzort |
| `required_count` | INTEGER | Benötigte Helfer-Anzahl |
| `helper_type_id` | UUID FK → helper_types | Benötigter Helfer-Typ |

#### `shift_assignments` — Schichtzuweisungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `shift_id` | UUID FK → shifts | Schicht |
| `helper_id` | UUID FK → helpers | Helfer |
| `post_id` | UUID FK → posts | Posten (optional) |
| `status` | VARCHAR(20) | `assigned`, `confirmed`, `no_show`, `completed` |

#### `posts` — Helfer-Posten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `name` | VARCHAR(255) | Postenname |
| `description` | TEXT | Aufgabenbeschreibung |
| `location_ref` | VARCHAR(255) | Standort-Referenz (z.B. „Matte 3") |
| `shift_id` | UUID FK → shifts | Zugehörige Schicht |

**Beziehungen:**
- `helper_types` 1:n `helpers`
- `events` 1:n `helpers`
- `events` 1:n `shifts`
- `shifts` 1:n `shift_assignments`
- `helpers` 1:n `shift_assignments`
- `shifts` 1:n `posts`

---

### 18.4 Modul 2: Venue-Management

#### `venues` — Veranstaltungsorte (Org-Ebene, wiederverwendbar)

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `name` | VARCHAR(255) | Name des Venues |
| `address` | JSONB | Adressdaten |
| `latitude` | DECIMAL(10,7) | Breitengrad |
| `longitude` | DECIMAL(10,7) | Längengrad |
| `capacity` | INTEGER | Max. Kapazität |
| `amenities` | JSONB | Ausstattung |
| `notes` | TEXT | Anmerkungen |

#### `venue_rooms` — Räume innerhalb eines Venues

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `venue_id` | UUID FK → venues | Zugehöriger Venue |
| `name` | VARCHAR(255) | Raumname |
| `capacity` | INTEGER | Kapazität |
| `room_type` | VARCHAR(50) | Typ (Halle, Aufwärmraum, etc.) |

#### `event_venues` — Venue-Zuordnung zu Events

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `venue_id` | UUID FK → venues | Venue |
| `role` | VARCHAR(50) | Funktion (z.B. `main`, `warmup`, `press`) |

#### `venue_bookings` — Raumbuchungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `room_id` | UUID FK → venue_rooms | Raum |
| `booked_by` | VARCHAR(255) | Buchender (Delegation/Team) |
| `start_time` | TIMESTAMPTZ | Buchungsbeginn |
| `end_time` | TIMESTAMPTZ | Buchungsende |
| `purpose` | VARCHAR(255) | Zweck (z.B. „Training") |
| `status` | VARCHAR(20) | `requested`, `confirmed`, `cancelled` |

**Beziehungen:**
- `venues` 1:n `venue_rooms`
- `venues` n:m `events` (über `event_venues`)
- `venue_rooms` 1:n `venue_bookings`

---

### 18.5 Modul 3: Transport-Management

#### `delegations` — Delegationen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `country_code` | VARCHAR(3) | Ländercode (z.B. `GER`, `TUR`) |
| `name` | VARCHAR(255) | Delegationsname |
| `contact_name` | VARCHAR(255) | Ansprechperson |
| `contact_email` | VARCHAR(255) | E-Mail |
| `contact_phone` | VARCHAR(50) | Telefon |
| `access_token` | VARCHAR(255) UNIQUE | Token für Self-Service-Zugang |
| `person_count` | INTEGER | Personenzahl |

#### `shuttle_routes` — Shuttle-Routen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `name` | VARCHAR(255) | Routenname |
| `route_type` | VARCHAR(20) | `fixed`, `individual` |
| `is_active` | BOOLEAN | Aktiv |

#### `route_stops` — Haltestellen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `route_id` | UUID FK → shuttle_routes | Route |
| `name` | VARCHAR(255) | Haltestellenname |
| `address` | JSONB | Adresse |
| `latitude` | DECIMAL(10,7) | Breitengrad |
| `longitude` | DECIMAL(10,7) | Längengrad |
| `stop_order` | INTEGER | Reihenfolge |
| `venue_id` | UUID FK → venues | Venue-Referenz (optional) |
| `accommodation_id` | UUID FK → accommodations | Unterkunft-Referenz (optional) |

#### `vehicles` — Fuhrpark

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `name` | VARCHAR(255) | Bezeichnung |
| `vehicle_type` | VARCHAR(50) | Typ (Bus, PKW, Sprinter) |
| `capacity` | INTEGER | Sitzplätze |
| `ownership` | VARCHAR(20) | `own`, `rental` |
| `rental_provider` | VARCHAR(255) | Mietanbieter (bei Rental) |
| `license_plate` | VARCHAR(20) | Kennzeichen |
| `cost_per_day` | DECIMAL(10,2) | Tageskosten |

#### `trips` — Fahrten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `route_id` | UUID FK → shuttle_routes | Route |
| `vehicle_id` | UUID FK → vehicles | Fahrzeug |
| `driver_helper_id` | UUID FK → helpers | Fahrer (aus Helfer-Planung) |
| `departure_time` | TIMESTAMPTZ | Abfahrtszeit |
| `arrival_time` | TIMESTAMPTZ | Geplante Ankunft |
| `trip_type` | VARCHAR(20) | `scheduled`, `on_demand` |
| `status` | VARCHAR(20) | `planned`, `active`, `completed`, `cancelled` |
| `current_lat` | DECIMAL(10,7) | Aktuelle Position (Tracking) |
| `current_lng` | DECIMAL(10,7) | Aktuelle Position (Tracking) |

#### `transport_bookings` — Transportbuchungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `delegation_id` | UUID FK → delegations | Delegation |
| `trip_id` | UUID FK → trips | Zugewiesene Fahrt (optional) |
| `pickup_location` | VARCHAR(255) | Abholort |
| `dropoff_location` | VARCHAR(255) | Zielort |
| `arrival_datetime` | TIMESTAMPTZ | Ankunftszeit (Reisedaten) |
| `departure_datetime` | TIMESTAMPTZ | Abreisezeit (Reisedaten) |
| `person_count` | INTEGER | Personenzahl |
| `luggage_info` | TEXT | Gepäckhinweise |
| `status` | VARCHAR(20) | `requested`, `assigned`, `completed`, `cancelled` |
| `source` | VARCHAR(20) | `self_service`, `import`, `manual` |

**Beziehungen:**
- `events` 1:n `delegations`
- `events` 1:n `shuttle_routes`
- `shuttle_routes` 1:n `route_stops`
- `events` 1:n `vehicles`
- `shuttle_routes` 1:n `trips`
- `vehicles` 1:n `trips`
- `helpers` 1:n `trips` (als Fahrer)
- `delegations` 1:n `transport_bookings`
- `trips` 1:n `transport_bookings`

---

### 18.6 Modul 4: Kommunikation

#### `message_templates` — Nachrichtenvorlagen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event (NULL = Org-Ebene) |
| `name` | VARCHAR(255) | Vorlagenname |
| `channel` | VARCHAR(20) | `email`, `whatsapp`, `telegram` |
| `subject` | VARCHAR(255) | Betreff (E-Mail) |
| `body` | TEXT | Inhalt mit Platzhaltern |
| `language` | VARCHAR(5) | Sprache |
| `variables` | JSONB | Verfügbare Platzhalter |

#### `messages` — Gesendete Nachrichten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `template_id` | UUID FK → message_templates | Verwendete Vorlage (optional) |
| `channel` | VARCHAR(20) | Kanal |
| `recipient_type` | VARCHAR(50) | Empfängertyp (helper, delegation, etc.) |
| `recipient_id` | UUID | Empfänger-ID |
| `recipient_address` | VARCHAR(255) | E-Mail/Telefon |
| `subject` | VARCHAR(255) | Betreff |
| `body` | TEXT | Inhalt (gerendert) |
| `status` | VARCHAR(20) | `queued`, `sent`, `delivered`, `failed` |
| `sent_at` | TIMESTAMPTZ | Sendezeitpunkt |
| `source_module` | VARCHAR(50) | Auslösendes Modul |
| `source_entity_id` | UUID | Referenz zum auslösenden Objekt |

#### `notification_rules` — Automatische Benachrichtigungsregeln

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `module_key` | VARCHAR(50) | Quell-Modul |
| `trigger_type` | VARCHAR(50) | Trigger (z.B. `shift_reminder`) |
| `trigger_config` | JSONB | Konfiguration (z.B. `{"minutes_before": 60}`) |
| `template_id` | UUID FK → message_templates | Zu verwendende Vorlage |
| `channel` | VARCHAR(20) | Kanal |
| `is_active` | BOOLEAN | Aktiv |

**Beziehungen:**
- `message_templates` 1:n `messages`
- `message_templates` 1:n `notification_rules`
- `events` 1:n `messages`

---

### 18.7 Modul 5: Projekt-/Aufgabenmanagement

#### `tasks` — Aufgaben

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `parent_task_id` | UUID FK → tasks | Übergeordnete Aufgabe (NULL = Top-Level) |
| `title` | VARCHAR(255) | Titel |
| `description` | TEXT | Beschreibung |
| `status` | VARCHAR(20) | `open`, `in_progress`, `done`, `cancelled` |
| `priority` | VARCHAR(10) | `low`, `medium`, `high`, `critical` |
| `category` | VARCHAR(100) | Kategorie |
| `assignee_id` | UUID FK → users | Verantwortliche Person |
| `due_date` | TIMESTAMPTZ | Fälligkeitsdatum |
| `is_recurring` | BOOLEAN | Regelmäßige Aufgabe |
| `recurrence_rule` | JSONB | Wiederholungsregel (bei recurring) |
| `linked_module` | VARCHAR(50) | Verknüpftes Modul |
| `linked_entity_id` | UUID | Verknüpftes Objekt |
| `sort_order` | INTEGER | Sortierung |

#### `task_collaborators` — Aufgaben-Mitarbeiter

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `task_id` | UUID FK → tasks | Aufgabe |
| `user_id` | UUID FK → users | Mitarbeiter |
| `role` | VARCHAR(20) | `assignee`, `reviewer`, `observer` |

#### `task_automations` — Auto-Trigger

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `name` | VARCHAR(255) | Name der Automatisierung |
| `trigger_type` | VARCHAR(50) | `time_before_event`, `time_after_event`, `task_completed` |
| `trigger_config` | JSONB | Konfiguration (z.B. `{"days_before": 30}`) |
| `action_type` | VARCHAR(50) | `create_task`, `send_notification`, `update_status` |
| `action_config` | JSONB | Aktion-Konfiguration |
| `is_active` | BOOLEAN | Aktiv |

**Beziehungen:**
- `tasks` 1:n `tasks` (Unteraufgaben, self-referencing)
- `tasks` 1:n `task_collaborators`
- `events` 1:n `tasks`
- `events` 1:n `task_automations`

---

### 18.8 Modul 6: Finanz-Controlling

#### `budgets` — Budgets

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `total_amount` | DECIMAL(12,2) | Gesamtbudget |
| `currency` | VARCHAR(3) | Währung (z.B. `EUR`) |
| `notes` | TEXT | Anmerkungen |

#### `budget_items` — Budgetposten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `budget_id` | UUID FK → budgets | Budget |
| `name` | VARCHAR(255) | Postenname |
| `planned_amount` | DECIMAL(12,2) | Geplanter Betrag |
| `actual_amount` | DECIMAL(12,2) | Tatsächlicher Betrag |
| `cost_center` | VARCHAR(100) | Kostenstelle |
| `module_key` | VARCHAR(50) | Zugehöriges Modul |
| `category` | VARCHAR(100) | Kategorie |

#### `revenues` — Einnahmen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `category` | VARCHAR(100) | Kategorie (Startgebühren, Sponsoring, Zuschuss) |
| `description` | VARCHAR(255) | Beschreibung |
| `expected_amount` | DECIMAL(12,2) | Erwarteter Betrag |
| `received_amount` | DECIMAL(12,2) | Erhaltener Betrag |
| `received_date` | DATE | Eingangsdatum |
| `source` | VARCHAR(255) | Quelle (Sponsor, Verband, etc.) |

#### `helper_compensations` — Helfer-Abrechnungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `helper_id` | UUID FK → helpers | Helfer |
| `total_hours` | DECIMAL(6,2) | Gesamtstunden |
| `hourly_rate` | DECIMAL(10,2) | Stundensatz |
| `daily_rate` | DECIMAL(10,2) | Tagessatz |
| `total_days` | DECIMAL(4,1) | Gesamttage |
| `mileage_km` | DECIMAL(8,1) | Gefahrene km |
| `mileage_rate` | DECIMAL(10,4) | km-Satz |
| `total_amount` | DECIMAL(12,2) | Gesamtbetrag |
| `status` | VARCHAR(20) | `calculated`, `approved`, `paid` |

**Beziehungen:**
- `events` 1:1 `budgets`
- `budgets` 1:n `budget_items`
- `events` 1:n `revenues`
- `helpers` 1:n `helper_compensations`

---

### 18.9 Modul 7: Hotel-/Unterkunftsmanagement

#### `accommodations` — Unterkünfte

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `event_id` | UUID FK → events | Event |
| `name` | VARCHAR(255) | Name (Hotel, Jugendherberge, Sporthalle, etc.) |
| `accommodation_type` | VARCHAR(50) | `hotel`, `hostel`, `gym_hall`, `pension`, `other` |
| `address` | JSONB | Adresse |
| `latitude` | DECIMAL(10,7) | Breitengrad |
| `longitude` | DECIMAL(10,7) | Längengrad |
| `contact_name` | VARCHAR(255) | Ansprechperson |
| `contact_email` | VARCHAR(255) | E-Mail |
| `contact_phone` | VARCHAR(50) | Telefon |
| `cancellation_deadline` | DATE | Stornierungsfrist |
| `notes` | TEXT | Anmerkungen |

#### `room_contingents` — Zimmerkontingente

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `accommodation_id` | UUID FK → accommodations | Unterkunft |
| `room_type` | VARCHAR(10) | `EZ`, `DZ`, `MBZ`, `other` |
| `room_type_label` | VARCHAR(100) | Anzeigename |
| `total_count` | INTEGER | Gesamtkontingent |
| `booked_count` | INTEGER | Bereits zugewiesen |
| `price_per_night` | DECIMAL(10,2) | Preis pro Nacht |
| `currency` | VARCHAR(3) | Währung |

#### `accommodation_bookings` — Unterkunftsbuchungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID PK | — |
| `tenant_id` | UUID FK | Tenant |
| `contingent_id` | UUID FK → room_contingents | Kontingent |
| `delegation_id` | UUID FK → delegations | Delegation |
| `guest_name` | VARCHAR(255) | Gastname |
| `check_in` | DATE | Check-in-Datum |
| `check_out` | DATE | Check-out-Datum |
| `room_type` | VARCHAR(10) | Zimmertyp |
| `room_number` | VARCHAR(20) | Zimmernummer (wenn bekannt) |
| `status` | VARCHAR(20) | `requested`, `confirmed`, `cancelled` |
| `source` | VARCHAR(20) | `self_service`, `manual`, `import` |
| `total_cost` | DECIMAL(10,2) | Gesamtkosten |

**Beziehungen:**
- `events` 1:n `accommodations`
- `accommodations` 1:n `room_contingents`
- `room_contingents` 1:n `accommodation_bookings`
- `delegations` 1:n `accommodation_bookings`
- `accommodations` können als `route_stops` im Transport referenziert werden

---

### 18.10 Modulübergreifende Beziehungen (Zusammenfassung)

```
organizations ──1:n──▶ events
                       │
         ┌─────────────┼──────────────────┬────────────────┐
         ▼             ▼                  ▼                ▼
     helpers        venues          delegations        budgets
         │             │                  │                │
         ▼             ▼                  ▼                ▼
     shifts      venue_bookings   transport_bookings  budget_items
         │                                │
         ▼                                ▼
  shift_assignments                    trips ◀── vehicles
         │                                │
         ▼                                ▼
  helper_compensations             route_stops ◀── accommodations
    (→ Modul 6)                                        │
                                                       ▼
                                               accommodation_bookings
                                                  (→ delegations)

  messages ◀── notification_rules ◀── alle Module
  tasks   ◀── task_automations    ◀── Modulverknüpfungen
```

---

## 19. MVP-Roadmap

### Phase 1: Core + Event-Einstellungen + Auth

**Ziel:** Lauffähige Basisplattform mit Multi-Tenancy und Authentifizierung.

| Komponente | Beschreibung |
|---|---|
| Multi-Tenancy | Organisations-Verwaltung, `tenant_id`, RLS |
| Auth (Keycloak) | Login, Registrierung, RBAC-Grundstruktur |
| Event-Einstellungen (Modul 0) | Event anlegen, konfigurieren, Module aktivieren |
| Org-Einstellungen | Stammdaten, Benutzer-Verwaltung |
| Tech-Basis | Docker Compose, CI/CD, API-Grundstruktur |

**Ergebnis:** Man kann sich einloggen, eine Organisation anlegen, ein Event erstellen und Module aktivieren.

---

### Phase 2: Helfer-/Personal-/Einsatzplanung (Modul 1)

**Ziel:** Vollständige Helfer-Verwaltung von Registrierung bis Einsatz.

| Komponente | Beschreibung |
|---|---|
| Helfer-Typen | Konfiguration auf Org-Ebene |
| Registrierung | Self-Service-Portal + Bestätigungs-Workflow |
| Schichtplanung | Schichten erstellen, Helfer zuweisen |
| Helfer-Posten | Posten definieren und besetzen |
| Schicht-Templates | Wiederverwendbare Vorlagen |

**Ergebnis:** Helfer können sich registrieren, werden bestätigt und Schichten zugewiesen.

---

### Phase 3: Venue-Management (Modul 2)

**Ziel:** Veranstaltungsorte verwalten und buchen.

| Komponente | Beschreibung |
|---|---|
| Venue-Verwaltung | Venues und Räume anlegen |
| Buchungssystem | Zeitslot-Buchungen mit Konflikterkennung |
| Kartenansicht | Leaflet + OpenStreetMap Integration |
| Event-Zuordnung | Venues zu Events verknüpfen |

**Ergebnis:** Venues sind auf einer Karte sichtbar, Räume buchbar.

---

### Phase 4: Transport-Management (Modul 3)

**Ziel:** Transport-Logistik für internationale Events.

| Komponente | Beschreibung |
|---|---|
| Delegationen | Delegations-Verwaltung |
| Shuttle-Routen | Feste und individuelle Routen |
| Fuhrpark | Eigene + Mietfahrzeuge |
| Fahrplan | Feste Zeiten + On-Demand |
| Self-Service | Token-basierter Zugang für Delegationen |
| Transportbuchung | Massen-Import + Einzelbuchung |

**Ergebnis:** Delegationen können Reisedaten hinterlegen, Shuttles werden geplant und zugewiesen.

---

### Post-MVP: Weitere Module

| Phase | Modul | Beschreibung |
|---|---|---|
| 5 | Kommunikation (Modul 4) | E-Mail, WhatsApp, Telegram — zentraler Nachrichten-Layer |
| 6 | Aufgabenmanagement (Modul 5) | Aufgaben, Kanban, Gantt, Automatisierung |
| 7 | Finanz-Controlling (Modul 6) | Budget, Abrechnung, Export |
| 8 | Hotel-Management (Modul 7) | Kontingente, Rooming-Listen, Self-Service |

---

*Dieses Dokument wird kontinuierlich weiterentwickelt und bildet die Grundlage für die technische Umsetzung von JTIS.*
