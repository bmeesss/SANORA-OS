# SANORA OS — Architectuur- en onderzoeksdocument

> **Status:** Concept 0.1 — fase **RESEARCH & ARCHITECTURE** — **ter goedkeuring**
> **Datum:** 2026-11-01 (lokale tijd UTC)
> **Repository:** `bmeesss/SANORA-OS` (publiek), werkbranch `arena/fa064594-sanora-os`, basiscommit `c4fb1d2`
> **Auteur:** Arena AI Agent Mode (hoofdontwikkelaar / systeemarchitect / technisch onderzoek)
> **Doel van dit bestand:** het enige resultaat van de eerste opdracht. Er is **geen** ISO, geen pakket, geen code en geen configuratie gebouwd.
> **Goedkeuringsregel:** alle keuzes in dit document zijn **voorstellen**. Er wordt niets geïmplementeerd voordat de gebruiker (en eventueel ChatGPT als reviewer) de basisarchitectuur expliciet heeft goedgekeurd.

---

## 0. Leeswijzer, status en methode

### 0.1 Labels voor feiten, aannames en aanbevelingen

In dit document wordt elk type uitspraak expliciet gelabeld:

| Label | Betekenis |
|---|---|
| **[FEIT]** | Geverifieerd in de repository of in een genoemde officiële bron, met bronnummer `[S#]` en raadpleegdatum. |
| **[AANNAME]** | Nog niet geverifieerd; gebruikt om een ontwerp te kunnen bespreken. Moet later door meting of besluit worden bevestigd. |
| **[AANBEVELING]** | Een technische keuze met argumenten én nadelen. Vereist goedkeuring. |
| **[RISICO]** | Bekend gevaar met impact en mitigatie. |
| **[OPEN VRAAG]** | Onderzoeksvraag of beslissing die nog openstaat (§21). |
| **[NIET GETEST]** | Bewust nog niet gemeten, gebouwd of geverifieerd. Geen enkele bewering over werking wordt hier gedaan. |

### 0.2 Bronvermelding

Externe informatie wordt inline aangeduid met `[S#]`. §23 bevat de volledige lijst met URL's en **raadpleegdatum 2026-11-01** voor alle bronnen. Waar officiële documentatie ontbreekt, staat dat expliciet vermeld; er worden geen cijfers of commando's verzonnen. Secundaire bronnen zijn alleen gebruikt om officiële pagina's te vinden en worden niet als bewijs geciteerd, tenzij expliciet aangegeven.

### 0.3 Juridische disclaimer

Dit document bevat een **technische** interpretatie van licenties en handelsmerkregels. Het is **geen juridisch advies**. Voor opname van propriëtaire drivers of firmware in een publiek distributeerbare ISO is een onafhankelijke juridische toets vereist (§9, §10, §12, §20).

### 0.4 Eerder goedgekeurde beslissingen

**[FEIT]** Er zijn geen eerder goedgekeurde architectuurbeslissingen. De repository bevat alleen de initiële `README.md` (§1.2). Dit document is daarom het eerste voorstel en bevat een eigen besluitenlogboek (§0.5). Toekomstige wijzigingen in goedgekeurde keuzes worden als nieuwe ADR voorgesteld en nooit stilzwijgend doorgevoerd.

### 0.5 Besluitenlogboek (ADR's, allemaal *voorgesteld*)

| ID | Voorgestelde beslissing | Status |
|---|---|---|
| ADR-0001 | Basis = Debian 13 *trixie* stable (amd64), geen eigen kernel vanaf nul | Voorgesteld |
| ADR-0002 | Desktop = KDE Plasma op Wayland, eigen identiteit via Global Theme / KWin-scripts / configuratie | Voorgesteld |
| ADR-0003 | Pakketbeheer = apt/dpkg + eigen ondertekende repo; Flatpak voor applicaties; geen snap als standaardkanaal | Voorgesteld |
| ADR-0004 | ISO = `live-build` met `SOURCE_DATE_EPOCH` en reproduceerbaarheidscontrole | Voorgesteld |
| ADR-0005 | Installer = Calamares (Codeberg), met Debian Installer als terugvaloptie | Voorgesteld |
| ADR-0006 | Licentie = nog te kiezen; voorstel: code GPL-2.0-or-later of Apache-2.0, documentatie/assets CC-BY-SA-4.0 | Voorgesteld, zie §21 |

---

## 1. Samenvatting van het project

### 1.1 Projectidentiteit

**[FEIT]** SANORA OS is een open-source Linux-distributie in oprichting. Doelarchitectuur: x86-64 (`amd64`). Ontwikkelomgeving: Arena AI, GitHub en ChatGPT als aanvullende reviewer. De licentie is nog niet bepaald. **[FEIT]** De GitHub-repository is publiek, heeft geen beschrijving en geen geregistreerde licentie (`licenseInfo: null`), en is aangemaakt op 2026-11-01. (Repository-inspectie, lokaal via `git` en `gh`; zie §1.2.)

**[AANBEVELING]** Behandel SANORA OS als een **downstream-distributie met eigen identiteit**, niet als een "theme op een bestaande distro". De eigen identiteit zit in: een samenhangende desktopconfiguratie, eigen SANORA-componenten, een gecureerde softwarecollectie, eigen installatie- en updatebeleid, eigen documentatie en eigen branding — niet in een fork van de kernel of van een desktopomgeving.

**[AANBEVELING]** Gebruik macOS uitsluitend als referentie voor **kwaliteitsniveau** (consistentie, animatiekwaliteit, duidelijke foutmeldingen, voorspelbaarheid). Kopieer geen Apple-logo's, iconen, wallpapers, geluiden, typografie, beschermde interface-elementen of handelsmerken. Alle eigen assets worden origineel ontworpen en onder een eigen, gedocumenteerde licentie uitgebracht (§12, §18).

### 1.2 Stap 1 — Repository-inspectie (resultaat, zonder wijzigingen)

**[FEIT]** Inspectie uitgevoerd op 2026-11-01 vóór enige wijziging, met `git status`, `git log`, `git ls-files`, `find` en `gh repo view`:

| Kenmerk | Bevinding |
|---|---|
| Repository | `https://github.com/bmeesss/SANORA-OS.git`, publiek, default branch `main` |
| Aangemaakt | 2026-11-01 22:27:18 UTC |
| Werkbranch | `arena/fa064594-sanora-os`, vanaf `c4fb1d2bbc48408a67f30006e8435690a5e9e70a` |
| Commits | 1: `c4fb1d2 Initial commit` |
| Getrackte bestanden | Alleen `README.md` |
| Inhoud `README.md` | Eén regel: `# SANORA-OS` (12 bytes) |
| Mappen | Geen; geen `.github/`, geen `docs/`, geen `src/`, geen `tests/` |
| Code / configuratie | Afwezig |
| Documentatie | Afwezig (alleen de titelregel) |
| Licentiebestand | Afwezig |
| CI / workflows / tests | Afwezig |
| Issue- en PR-templates | Afwezig |
| Release notes / changelog | Afwezig |
| Build- of ISO-configuratie | Afwezig |
| Beschrijving / projectmetadata | Leeg |

**[FEIT]** Tijdens de inspectie is **niets verwijderd, gewijzigd of toegevoegd**. Het enige nieuwe bestand na deze opdracht is dit document; `README.md` is onaangeraakt gelaten.

**[FEIT]** Ontbrekende onderdelen (inventarisatie): projectvisie, technische eisen, architectuur, keuze van basis en desktop, licentie, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue-/PR-templates, CI, tests, releasebeleid, hardwarecompatibiliteitslijst, buildpijplijn, installer, branding, softwarecentrum en documentatie.

**[NIET GETEST]** Er zijn geen builds, installaties of benchmarks uitgevoerd. Alle uitspraken over toekomstige werking zijn ontwerp, geen verificatie.

### 1.3 Samenvatting van de aanbevolen architectuur in één alinea

**[AANBEVELING]** Debian 13 *trixie* stable (amd64) als basis met directe Debian-security-updates; KDE Plasma op Wayland als desktop, vormgegeven met een eigen SANORA Global Theme, KWin-scripts en systeemconfiguratie; apt/dpkg voor het basissysteem plus een kleine, ondertekende SANORA-repository; Flatpak/Flathub als standaard applicatiekanaal; KDE Discover als softwarecentrum; Calamares als installer; `live-build` voor de ISO met reproduceerbaarheidscontrole; beveiliging via AppArmor, firewall, polkit, LUKS2, ondertekende pakketten en gecontroleerde automatische security-updates; geen telemetrie en geen verplichte accounts. De belangrijkste nadelen zijn de oudere Debian-kernel (6.12) ten opzichte van Ubuntu 26.04 (7.0), de afhankelijkheid van een kleine groep maintainers voor eigen pakketten, en de aanzienlijke drempel voor eigen Secure Boot-ondertekening (§20, R-01).

---

## 2. Productvisie

### 2.1 Visie

**[AANBEVELING]** SANORA OS moet een dagelijks bruikbare, stabiele, snelle, veilige en visueel consistente distributie worden. De maatstaf is niet "hoe snel kan er een ISO komen", maar "kan een gebruiker zonder Linux-ervaring dit systeem een jaar lang zonder frictie gebruiken". **Kwaliteit boven snelheid** is de bindende projectregel en wordt in elke fase als acceptatiecriterium opgenomen (§19).

### 2.2 Design en gebruikerservaring — uitgangspunten

**[AANBEVELING]** Concrete, toetsbare UX-doelen (nog geen implementatie):

- Eigen, herkenbare visuele identiteit: kleurensysteem, typografie, iconen, wallpapers, systeemgeluiden, boot- en inlogervaring.
- Consistente light- en dark-modus die **alle** meegeleverde systeemapplicaties en dialogen omvat; geen half omgezette dialogen.
- Een dock, menubalk en applicatiestarter die qua gedrag, animatieduur en hiërarchie op elkaar zijn afgestemd.
- Vloeiende maar efficiënte animaties, met respect voor de systeeminstelling "verminder beweging" / reduced motion — een optie die GNOME 50 expliciet biedt [S20] en die Plasma via toegankelijkheidsinstellingen ondersteunt [S17][S18].
- Eén instellingeninterface: geen losse configuratietools die elkaar tegenspreken.
- Begrijpelijke foutmeldingen met een concreet vervolgpad ("wat kan ik nu doen?"), ook bij hardware- en driverfouten.
- Toegankelijkheid als eerste eis: schermlezer, toetsenbordnavigatie, kleurenfilters, schaalvergroting, contrast. GNOME 50 en Plasma 6.8 investeren aantoonbaar in toegankelijkheid (Orca, reduced motion, dwell clicker, kleurenblindheidsfilters) [S17][S20]; SANORA moet dit niveau minimaal evenaren en meten (§11, §19).

**[RISICO]** "Premium uitstraling" is geen meetbare eis. **[AANBEVELING]** Vertaal het naar toetsbare criteria: geen gemengde toolkit-dialogen, geen niet-geschaalde iconen bij 200% schaal, animatieduur binnen een vastgestelde bandbreedte, contrast volgens WCAG-richtlijnen, en een vaste set screenshots per release die handmatig wordt gereviewd.

### 2.3 Performance, hardware, gebruiksgemak, privacy

**[AANBEVELING]** Zie §3 voor eisen, §10 voor hardware, §11 voor meetbare performance, §12/§13 voor beveiliging en privacy. **[FEIT]** De projectvisie vraagt om "zo laag mogelijk RAM-gebruik" en "zo weinig mogelijk achtergrondprocessen"; dit document definieert die als **KPI's met een meetprotocol** (§11) en past **geen enkele tweak** toe. **[AANBEVELING]** Geen optimalisatie zonder aantoonbare regressie- of verbeteringsmeting tegen de gekozen basisdistributie; stabiliteit gaat vóór een kleine winst.

### 2.4 Afbakening van deze fase

**[AANBEVELING]** In de huidige fase worden **geen** mappen `docs/`, `architecture/`, `branding/`, `desktop/`, `packages/`, `installer/`, `iso/`, `scripts/`, `tests/` of `build/` aangemaakt. §18 is uitsluitend een voorstel. Er wordt geen kernel gebouwd, geen desktop geconfigureerd, geen ISO geproduceerd en geen publieke release voorbereid.

---

## 3. Technische eisen

### 3.1 Functionele eisen (F)

| ID | Eis | Toetsbaar criterium (later te verifiëren) |
|---|---|---|
| F-01 | Installeerbaar op x86-64 UEFI-systemen, offline | Installatie zonder netwerk slaagt; ISO bevat alle benodigde pakketten |
| F-02 | Automatische hardwaredetectie | CPU, GPU, Wi-Fi, Bluetooth, audio, touchpad, opslag correct geïdentificeerd in de hardwaretestmatrix (§10) |
| F-03 | Light/dark-modus, consistent | Alle systeemapplicaties volgen de modus; geautomatiseerde screenshot-check |
| F-04 | Softwarecentrum met updates | Installeren/verwijderen/bijwerken van apps en firmware via één UI |
| F-05 | Betrouwbare updates en herstel | Security-updates automatisch; rollback van een mislukte update aantoonbaar (§12.8) |
| F-06 | Begrijpelijke foutmeldingen | Foutscenario's uit de testsuite hebben een niet-technische uitleg én een vervolgactie |
| F-07 | Eenvoudig systeembeheer | Geen verplichte terminal voor dagelijkse taken |
| F-08 | Documentatie | README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, release notes, HCL, installatiegids |

### 3.2 Niet-functionele eisen (N)

| ID | Eis | Meetwijze (§11) |
|---|---|---|
| N-01 | Laag idle-RAM | `MemAvailable` uit `/proc/meminfo`, na gestandaardiseerde idle-periode |
| N-02 | Lage CPU-belasting in idle | PSI/`pidstat`/`systemd`-unitmeting, zelfde meetvenster |
| N-03 | Snelle boot | `systemd-analyze time`, `blame`, `critical-chain` [S43] |
| N-04 | Snelle applicatiestart | Koude start, herhaald, mediaan + spreiding |
| N-05 | SSD/NVMe-prestaties | `fio` met vastgelegde workloadparameters |
| N-06 | Energiebeheer | Gemeten vermogen/accuduur op vaste referentielaptops |
| N-07 | GPU-versnelling | Aantoonbaar versnelde compositing en video-decode via DRM/Mesa-statistieken [S30] |
| N-08 | Beperkte standaardsoftware | Tellbare pakketlijst + tellbaar aantal actieve systemd-units |
| N-09 | Geen onnodige achtergrondservices | Elke actieve unit heeft een gedocumenteerde eigenaar en reden |
| N-10 | Reproduceerbare ISO waar haalbaar | Twee builds bit-voor-bit gelijk, gecontroleerd met `diffoscope`/`reprotest` [S54][S55][S56] |

**[FEIT]** `systemd-analyze` meet de tijd tot alle services zijn *gestart*, niet tot ze volledig geïnitialiseerd zijn, en `blame` kan misleidend zijn door parallelism en wachtende services [S43]. **[AANBEVELING]** Gebruik daarom meerdere meetbronnen en rapporteer altijd de beperkingen van de methode.

### 3.3 Randvoorwaarden

- **[FEIT]** Geen eigen Linux-kernel vanaf nul (projectregel). Wél: bestaande distro-kernel, eventueel eigen packaging/configuratie.
- **[FEIT]** Geen apple-assets of -branding.
- **[AANBEVELING]** Geen onnodige nieuwe afhankelijkheden: elk nieuw pakket, elke nieuwe service en elk nieuw buildgereedschap krijgt een ADR met onderbouwing en een exit-strategie.
- **[AANNAME]** Het project start met een zeer kleine groep maintainers (mogelijk één persoon + AI-ondersteuning). **[RISICO]** Dit is de belangrijkste capaciteitsbeperking; de architectuur is daarom bewust minimaal en leunt zwaar op upstream (§20, R-09).

### 3.4 Vereiste bronnen/infrastructuur (nog niet aanwezig)

**[AANBEVELING]** minimaal: een ondertekende APT-repository, een ISO-buildrunner met voldoende schijfruimte (Debian Live Manual/noot: GNOME-images vragen tijdens de build ~17 GB [S54]), een testmatrix met fysieke hardware, een publieke downloadlocatie met checksums, en een proces voor sleutelbeheer. **[FEIT]** Geen van deze is nu aanwezig in de repository.

### 3.5 Systeemarchitectuur (Stap 5) — lagenmodel

**[AANBEVELING]** Lagenmodel met expliciete eigendomsgrens. "Upstream" betekent: ongewijzigd of minimaal geconfigureerd overgenomen, met eigen security-updates van upstream. "SANORA" betekent: door dit project ontwikkeld en onderhouden.

| Laag | Component | Herkomst | Wie onderhoudt | Status |
|---|---|---|---|---|
| Firmware/UEFI | UEFI, microcode, device firmware, fwupd/LVFS | Upstream [S38][S39] | Hardwarefabrikant / LVFS / Debian | Voorgesteld |
| Boot | shim + GRUB 2 (of systemd-boot), MOK | Debian / rhboot [S40][S41] | Debian + SANORA (eigen sleutels) | Voorgesteld, risico R-01 |
| Kernel | Debian 6.12 LTS + security-fixes; optioneel backportkernel | Debian [S8][S11][S15] | Debian; SANORA bewaakt compatibiliteit | Voorgesteld |
| Drivers | DRM/KMS: amdgpu, i915, xe, nouveau; Mesa; NVIDIA open kernel modules | Kernel/Mesa/NVIDIA [S30][S31][S34][S36] | Upstream | Voorgesteld |
| Basis-OS | Debian 13 trixie stable, `main` + `non-free-firmware`, systemd | Debian [S8][S11][S13] | Debian | Voorgesteld |
| Displayserver | Wayland (KWin) + XWayland; geen X11-sessie | KDE / Wayland [S18][S29] | KDE / freedesktop | Voorgesteld |
| Desktop | KDE Plasma, System Settings, Discover | KDE [S17][S26] | KDE / Debian | Voorgesteld |
| **SANORA-laag** | Global Theme, iconen, wallpapers, geluiden, KWin-scripts, standaardconfiguratie, SANORA-instellingen, SANORA-welcome, SANORA-updatebeleid | **Eigen ontwikkeling** | **SANORA** | Voorgesteld |
| Pakketbeheer | apt/dpkg + eigen ondertekende repo; Flatpak/Flathub | Debian / Flatpak [S16][S49] | Debian + SANORA (repo) | Voorgesteld |
| Softwarecentrum | KDE Discover + AppStream + fwupd-backend | KDE / freedesktop [S26][S27][S28] | KDE + SANORA (metadata/curatie) | Voorgesteld |
| Installer | Calamares + SANORA-branding/modules, LUKS2, Btrfs | Calamares [S61][S62] | Calamares + SANORA | Voorgesteld |
| ISO | `live-build` + reproduceerbaarheidscontrole | Debian Live [S53][S54] | SANORA | Voorgesteld |
| Beveiliging | AppArmor, firewall, polkit, LUKS2, sandboxing, ondertekende repo | Debian / upstream [S44][S45][S46][S42] | Debian + SANORA (beleid) | Voorgesteld |
| Documentatie/tests | docs, ADR's, HCL, tests, CI | Eigen ontwikkeling | SANORA | Voorgesteld |

**[AANBEVELING]** De grens is hard: SANORA **forkt** Plasma, de kernel of Mesa niet. Alleen configuratie, thema's, metadata, kleine eigen applicaties, packaging en documentatie zijn eigen werk. Dit houdt de updateketen hanteerbaar en maakt de herkomst per bestand documenteerbaar (§18: `THIRD_PARTY.md` / SBOM).

### 3.6 Upstream vs. eigen ontwikkeling — samenvatting

**[FEIT]** Volgens de Debian-derivativepagina worden derivatives aangemoedigd, is de gedistribueerde software DFSG-vrij en worden verwijzingen naar Debian (naam, logo, services) vervangen door eigen varianten [S12][S13]. **[AANBEVELING]** Documenteer per release exact welke pakketten uit Debian komen, welke uit de SANORA-repo komen en welke assets eigen werk zijn; gebruik SPDX-identifiers [S51] en een machineleesbare SBOM.

---

## 4. Vergelijking van Linux-bases

### 4.1 Feitenmatrix (geraadpleegd 2026-11-01)

| Criterium | Ubuntu LTS | Fedora Linux | Debian stable |
|---|---|---|---|
| Huidige release | 26.04 LTS "Resolute Raccoon", apr 2026 [S1][S3] | Fedora 44, apr 2026; ~6-maandelijkse cadans [S6] | Debian 13 "trixie", 9 aug 2025; laatste puntrelease 13.7 op 12 sep 2026 [S8] |
| Releasecyclus | 6 maanden; LTS elke 2 jaar in april [S1] | ~6 maanden, kwaliteitsafhankelijk [S6] | "when ready", ~2 jaar; stable/testing/unstable [S8] |
| Ondersteuningsduur | 26.04: standaard tot mei 2031, ESM tot mei 2036, Legacy tot mei 2041 [S1] | ~13 maanden; release N tot 4 weken na N+2 [S6] | 3 jaar vol + 2 jaar LTS = 5 jaar; trixie EOL 2028-08-09, LTS tot 2030-06-30 [S8][S9] |
| Kernel bij release | 7.0 (GA en HWE) [S2][S4] | nieuwste upstream-kernel, snel wisselend [S6] | 6.12-serie [S11] |
| Kernelvernieuwing | HWE-stack met nieuwe kernels op oudere LTS [S2] | Doorlopende kernelupdates | Backports: nieuwere pakketten uit testing, "as-is", minder getest, geen reguliere security-ondersteuning van het Security Team [S15] |
| Pakketbeheer | apt/dpkg, APT 3 in 26.04; sterke snap-integratie [S4] | dnf/rpm (DNF5 in F44) | apt/dpkg, ~69.830 pakketten in trixie [S11][S16] |
| Desktop in release | GNOME 50 (Wayland-only sessie) [S3][S4][S20] | GNOME 50 Workstation; KDE Spin beschikbaar [S20] | GNOME 48, Plasma 6.3.6, Xfce 4.20 naast elkaar [S11] |
| Beveiligingsupdates | Canonical; ESM/Pro deels commercieel [S1] | Fedora Security Team, korte looptijd [S6] | Debian Security Team met backports van fixes op bevroren versies; LTS-team apart [S9][S14] |
| Stabiliteit | LTS bevroren basis + HWE-beweging | Snelle innovatie, vaker regressierisico | Zeer conservatief; security-fixes worden teruggeport i.p.v. nieuwe upstream-versies [S14] |
| Juridisch / derivative | Gemodificeerde herdistributie met Canonical-trademarks vereist goedkeuring/licentie, óf verwijderen van trademarks + herbouwen van eigen binaries [S5] | "Fedora Remix" toegestaan onder trademarkrichtlijnen; `fedora-logos`/`fedora-release` vervangen; officiële "Fedora"-naam gereserveerd [S7] | Derivatives expliciet welkom; DFSG-vrije software; eigen naam/logo/services [S12][S13] |
| Geschiktheid als eigen distro | Goede techniek, maar juridische en merkmatige frictie + snap-afhankelijkheid | Uitstekende tooling (osbuild/lorax, SELinux), maar 13-maands levensduur dwingt tot jaarlijkse rebase | Beste juridische en operationele uitgangspositie voor een langdurig onderhouden, onafhankelijke distributie |

**[FEIT]** Ubuntu 26.04 Desktop vereist volgens de officiële release notes minimaal 6 GB RAM en 25 GB opslag voor een comfortabele ervaring [S3]. **[FEIT]** Ubuntu 26.04 gebruikt o.a. systemd 259, APT 3, Dracut, `sudo-rs`/Rust-coreutils; `pkcon` is verwijderd [S4]. **[FEIT]** Debian 13 bevat Qt 6.8.2, KDE Frameworks 6.13, Plasma 6.3.6, systemd 257, cryptsetup 2.7 en Linux 6.12 [S11].

### 4.2 Beoordeling per technologie (niet op populariteit)

**Ubuntu LTS — argumenten vóór:** langste ondersteuningsvenster [S1]; HWE-kernel voor nieuwe hardware [S2]; TPM-gebonden FDE en volwassen NVIDIA-Wayland-verbeteringen in 26.04 [S3][S4]; grote community; kant-en-klare installer- en image-tooling.
**Nadelen:** het IPRights-beleid maakt een *gemodificeerde* Ubuntu-afgeleide met de *buntu-merken juridisch lastig — herdistributie vereist Canonical-goedkeuring/certificering of het verwijderen van trademarks én herbouw van binaries [S5]; snap is sterk geïntegreerd [S4] en de Snap Store-serverzijde is niet open source (een architectuur- en leveranciersafhankelijkheid); hogere minimale RAM-eis [S3]; Universe-pakketten vallen buiten de standaard 5-jaarsdekking (ESM/Pro) [S1]; GNOME 50 is Wayland-only [S4][S20], wat minder vrijheid geeft voor een eigen desktoprichting.

**Fedora — argumenten vóór:** nieuwste kernel/Mesa/Plasma, sterke SELinux- en firewall-standaarden, Flatpak-first, uitstekende image-tooling (`osbuild`/`lorax`) [S59][S60], en een expliciet toegestane Remix-vorm [S7].
**Nadelen:** ~13 maanden ondersteuning per release [S6] betekent voor een jonge distributie een vrijwel permanente rebase; dat is onverenigbaar met "kwaliteit boven snelheid" zonder een groot release-engineeringteam; trademarkregels vereisen het vervangen van release/logo-pakketten [S7]; RPM/dnf vereist andere packagingkennis dan de grootste binaire ecosysteemstandaard.

**Debian stable — argumenten vóór:** 5 jaar ondersteuning [S8][S9]; derivatives expliciet welkom en juridisch vrij [S12][S13]; DFSG-licentietoetsing van tevoren uitgevoerd; officiële media mogen niet-vrije firmware bevatten [S13]; enorme, stabiele pakketcollectie [S11]; security-fixes worden teruggeport zonder API/ABI-breuk [S14]; `live-build` met aantoonbare reproduceerbaarheidsinspanningen [S53][S54]; geen verplichte vendor-store.
**Nadelen:** oudere pakketversies (kernel 6.12, Plasma 6.3.6) [S11]; backports zijn "as-is" en krijgen geen reguliere security-ondersteuning van het Security Team [S15]; LTS-fase wordt door een apart team met beperktere pakketdekking gedaan [S9]; minder kant-en-klare "premium desktop"-componenten; eigen werk aan theming/installer/softwarecentrum blijft volledig bij SANORA.

### 4.3 Juridische en distributierechtelijke noot

**[FEIT]** Canonical's IPRights Policy stelt: herdistributie van Ubuntu is toegestaan in ongewijzigde vorm; bij gemodificeerde versies die de trademarks dragen is goedkeuring/certificering nodig, anders moeten de trademarks worden verwijderd/vervangen en moeten eigen binaries worden herbouwd [S5]. **[FEIT]** Debian's Social Contract §4 zegt dat anderen distributies met Debian en andere werken mogen maken "zonder enige vergoeding" en zonder juridische beperkingen die dat gebruik verhinderen; §5 staat niet-vrije firmware op officiële media toe [S13]. **[FEIT]** Fedora kent een "Remix"-regime met verplichte vervanging van `fedora-logos`, `fedora-release` en `fedora-release-notes` [S7]. **[AANBEVELING]** Deze drie feiten wegen zwaarder dan kleine technische verschillen: voor een zelfstandige, publieke distributie zonder juridische afdeling is de Debian-route de laagste frictie.

---

## 5. Aanbevolen Linux-basis

### 5.1 Aanbeveling

**[AANBEVELING]** Kies **Debian 13 "trixie" stable, uitsluitend `amd64`**, als basis voor de eerste levenscyclus, met:
- `main` + `non-free-firmware` in de APT-bronnen (firmware, geen vrije-softwareclaim die de hardwareondersteuning belemmert) [S11][S13];
- `trixie-security` en `trixie-updates` actief;
- een **kleine, ondertekende SANORA-repository** voor eigen pakketten en configuratie;
- een gedocumenteerde rebase naar Debian 14 (*forky*) zodra die stable wordt (§19, fase 7/9).

### 5.2 Argumenten

1. **Onderhoudbaarheid:** 5 jaar beveiligingsdekking en teruggeporte fixes [S8][S9][S14] beperken de noodzaak tot eigen patchwerk.
2. **Juridische vrijheid:** derivatives zijn welkom, software is DFSG-vrij, alleen naam/logo/services hoeven te worden vervangen [S12][S13]. Dit voorkomt het Ubuntu-herbouwprobleem [S5] en de Fedora-merkregels [S7].
3. **Stabiliteit boven nieuwheid:** het security-team wijzigt versies minimaal om API/ABI-breuk te vermijden [S14] — precies wat een dagelijks bruikbare desktop nodig heeft.
4. **Ecosysteem:** apt/dpkg [S16] + ~69.830 pakketten [S11] + AppStream-metadata via APT [S28] + Flatpak-ondersteuning [S49].
5. **Buildbaarheid:** Debian Live Manual, `live-build`, en een officiële reproduceerbaarheidstrack met Jenkins/openQA/diffoscope [S53][S54].
6. **Geen vendor-lock-in:** geen verplichte account, geen verplichte store, geen commercieel ESM-abonnement voor de basisdekking.

### 5.3 Nadelen en eerlijke tegenargumenten

- **[RISICO]** Kernel 6.12 [S11] kan tekortschieten voor de nieuwste Intel Core Ultra / Ryzen / Arc-generaties. Ubuntu 26.04 biedt 7.0 [S2][S4], Fedora nog nieuwer [S6]. Mitigatie: §9 (selectieve backports) + hardwaretestmatrix §10. **[AANNAME]** Voor de meeste 2024–2026 x86-64-consumentenhardware volstaat 6.12 met firmware; dit moet worden gemeten, niet aangenomen.
- **[RISICO]** Plasma 6.3.6 is niet de huidige Plasma-LTS (6.6, ondersteund tot ~feb 2029) [S19] en mist latere verbeteringen. Zie §7.4.
- **[RISICO]** Backports zijn "as-is", minder getest en zonder reguliere security-dekking van het Security Team [S15]; Debian-LTS-documentatie waarschuwt dat backports na ~3 jaar geen ondersteuning meer krijgen en niet door het LTS-team worden gedekt. **[AANBEVELING]** Gebruik backports alleen voor expliciet gedocumenteerde, per-hardware noodzakelijke pakketten en monitor ze actief.
- **[RISICO]** Debian stable is conservatief: "moderne" gebruikers verwachten misschien nieuwere applicaties. Mitigatie: Flatpak als applicatiekanaal (§14).
- **[RISICO]** 5 jaar is korter dan Ubuntu's 5+5+5 [S1]. Mitigatie: een geplande rebase per Debian-stable-release, met een upgrade-test in §19.

### 5.4 Verworpen alternatieven en waarom

| Alternatief | Reden van verwerping |
|---|---|
| Ubuntu 26.04 LTS | Merkenrechtelijke frictie bij gemodificeerde herdistributie [S5], snap/store-afhankelijkheid [S4], hogere systeemeisen [S3], GNOME-Wayland-only richting [S4][S20]. Technisch sterk, organisatorisch minder passend. |
| Fedora 44 / Fedora KDE Spin | ~13 maanden levensduur [S6] dwingt tot jaarlijkse rebase; onhaalbaar met de aangenomen kleine capaciteit. Tooling ([S59][S60]) blijft wel een referentie voor §17. |
| Debian testing (*forky*) | Geen security-garantie van het Security Team, bewegend doel [S8][S14]; ongeschikt als releasebasis. |
| Eigen kernel / LFS-achtige opbouw | Explicit verboden door de projectregels; onhoudbare security- en driverlast. |
| Image-based/immutable basis (rpm-ostree/bootc) | Interessant voor herstelbaarheid, maar voegt een tweede packagingmodel toe. **[OPEN VRAAG]** §21, Q-07: pas evalueren ná fase 3. |

### 5.5 Goedkeuringspunt

**[AANBEVELING]** ADR-0001 ter goedkeuring voorleggen. Zonder goedkeuring: geen enkele buildconfiguratie aanmaken.

---

## 6. Vergelijking van desktopomgevingen

### 6.1 Eerlijkheid over RAM/CPU/GPU-cijfers

**[FEIT]** Er bestaan **geen door de drie upstream-projecten gepubliceerde, methodologisch vergelijkbare** idle-RAM-, CPU- of GPU-metingen. Secundaire benchmarks gebruiken verschillende distributies, pakketversies, sessies, schermresoluties, compositor-instellingen en meetmomenten; de gerapporteerde waarden lopen daardoor sterk uiteen en zijn onderling niet vergelijkbaar. **[AANBEVELING]** Dit document geeft daarom **geen getallen** voor RAM/CPU/GPU-verbruik en doet geen uitspraak als "X is lichter dan Y" op basis van die bronnen. **[AANBEVELING]** In plaats daarvan wordt in §11 een eigen, herhaalbaar meetprotocol gedefinieerd dat alle drie kandidaten op identieke hardware en identieke basis meet vóór definitieve keuze (fase 2). **[NIET GETEST]** Er zijn in deze fase geen metingen gedaan.

**[FEIT]** Wel objectief geverifieerd: GNOME 50 (mrt 2026) rapporteert geheugenreductie in Files en algemene CPU/memory-verbeteringen in GNOME 48 [S20][S4]; Plasma 6.8 (okt 2026) noemt o.a. latency-verbeteringen en CPU-affinity-instellingen [S17]; Xfce 4.20 noemt opgeloste geheugenlekken [S22]. Dit zijn upstream-claims over eigen releases, geen vergelijkende benchmark.

### 6.2 Kwalitatieve vergelijking

| Criterium | KDE Plasma | GNOME | XFCE |
|---|---|---|---|
| Versie in Debian 13 | Plasma 6.3.6, Qt 6.8.2, KF 6.13 [S11] | GNOME 48 [S11] | Xfce 4.20 [S11] |
| Huidige upstream (2026-11-01) | 6.8 (14 okt 2026) [S17]; 6.6 is LTS tot ~feb 2029 [S19] | 50 (18 mrt 2026) [S20] | 4.20 (15 dec 2024) [S22] |
| Wayland-status | Wayland default sinds 6.0; vanaf 6.8 Wayland-exclusive, XWayland blijft [S18][S19] | Wayland-native; Ubuntu 26.04 biedt geen X11-GNOME-sessie meer [S4][S20] | Wayland **experimenteel**, geen eigen Wayland-compositor; Labwc/Wayfire nodig; `xfwm4` niet geport [S21][S22] |
| Aanpasbaarheid | Zeer hoog: Global Themes [S23], KWin-scripts via `kpackagetool6`/`kwriteconfig6` [S24], declaratieve KWin-effects in QML [S25], System Settings als centraal punt | Bewust gestuurd; maatwerk vooral via GNOME Shell-extensies die bij elke Shell-release kunnen breken | Hoog voor klassieke X11-instellingen, maar beperkt voor een samenhangende moderne shell |
| Animaties / compositor | KWin met configureerbare effects, VRR, HDR-ondersteuning [S18][S25] | Mutter, vloeiend en strak geregisseerd; reduced motion als systeemoptie [S20] | Xfwm4-compositor, traditioneler; Wayland-pad nog niet af [S21] |
| Toegankelijkheid | Schermlezer, sticky/bounce keys, zoom, kleurfilters; 6.8 voegt dwell clicker toe [S17][S18] | Orca, reduced motion, braille, muis-review in Wayland [S20] | Basisvoorzieningen; minder actieve upstream-investering zichtbaar in de geraadpleegde release-informatie |
| Instellingeninterface | Eén System Settings met KCM's; ook bruikbaar voor eigen SANORA-KCM's | Strak, maar uitbreidingen vragen eigen UI-beslissingen | Modulair, minder uniform |
| Softwarecentrum | Discover met Flatpak-, PackageKit-, Snap- en AppStream-backends + fwupd-ondersteuning [S26] | GNOME Software | Geen eigen vergelijkbaar centrum |
| Mogelijkheid voor eigen desktopervaring | **Hoog:** thema + scripts + configuratie zonder fork | **Laag–middel:** sterke upstream-visie, maatwerk vaak via fragiele extensies | **Middel:** lichte basis, maar Wayland- en moderniseringsachterstand |
| Onderhoudsrisico voor SANORA | Qt6/KF6-versiekoppeling; X11-sessie verdwijnt [S18] | Extensie-API-koppeling; richting wordt upstream bepaald | Wayland-onvolledigheid zou SANORA zelf moeten oplossen |

### 6.3 Afweging per omgeving

**KDE Plasma — vóór:** grootste configureerbaarheid via officiële, gedocumenteerde mechanismen [S23][S24][S25]; Wayland volwassen en upstream committeert zich volledig aan Wayland [S18]; System Settings biedt één consistente instellingeninterface; Discover integreert zowel pakketten, Flatpak als firmware [S26]; Qt/Kirigami maakt eigen SANORA-apps naast de desktop mogelijk; geen verplichte fork nodig voor een eigen identiteit. **Tegen:** Qt6/KF6-stack versiebeheer; Plasma-releases volgen een ~4-maandscadans [S19]; de LTS-uitgave 6.6 is een commerciële samenwerking [S19] en zit niet in Debian 13 [S11]; X11-valweg verdwijnt in 6.8 [S18].

**GNOME — vóór:** zeer gepolijste, consistente default-ervaring; sterke toegankelijkheid [S20]; Wayland-native; minder eigen onderhoud aan look-and-feel. **Tegen:** een eigen identiteit realiseren zonder te vervallen in "een thema" is moeilijker; maatwerk via Shell-extensies is versiegevoelig; Ubuntu 26.04 laat zien dat upstream de X11-sessie verwijdert [S4][S20], dus de richtingsvrijheid is beperkt; GNOME's ontwerpvisie botst sneller met een eigen dock-/menubalkconcept.

**XFCE — vóór:** traditioneel lichte, eenvoudige basis; geschikt voor oudere hardware; Xfce 4.20 heeft aantoonbaar onderhoud gepleegd [S22]. **Tegen:** Wayland-ondersteuning is expliciet experimenteel, er is geen eigen Wayland-compositor en `xfwm4` is niet geport [S21]; dat zou SANORA dwingen tot het zelf onderhouden van een compositor (Labwc/Wayfire) — precies het soort complexe architectuur dat de projectregels verbieden; minder geschikt voor de gewenste premium animatie- en consistentiedoelstelling.

---

## 7. Aanbevolen desktopomgeving

### 7.1 Aanbeveling

**[AANBEVELING]** Kies **KDE Plasma op Wayland** als desktopbasis (ADR-0002), in eerste instantie op de **Debian 13-versie (Plasma 6.3.6)** [S11], met een eigen **SANORA Global Theme** [S23], KWin-scripts/effects [S24][S25], een eigen standaardconfiguratie (panel, dock, starter, sneltoetsen, light/dark) en eigen iconen, wallpapers en systeemgeluiden. XWayland blijft beschikbaar voor legacy-applicaties [S18][S29]. Er wordt **geen X11-sessie** aangeboden.

### 7.2 Argumenten

1. **Eigen identiteit zonder fork:** Global Themes, KWin-scripts en KCM's zijn officiële uitbreidingspunten [S23][S24][S25]; daarmee is een eigen desktopervaring realiseerbaar terwijl Plasma, KWin en de security-updates upstream blijven.
2. **Wayland-strategie:** KDE heeft de X11-sessie vanaf 6.8 bewust uitgefaseerd en XWayland behouden [S18]; aansluiten bij die richting voorkomt dat SANORA een stervende sessie moet onderhouden.
3. **Consistentie:** System Settings + KCM-architectuur maakt één instellingeninterface mogelijk; eigen SANORA-instellingen kunnen daar als KCM in worden opgenomen.
4. **Softwarecentrum & firmware:** Discover ondersteunt meerdere backends en firmware-updates [S26], wat §15 en §10 vereenvoudigt.
5. **Toegankelijkheid:** aantoonbare upstream-investering [S17][S18], met een expliciete test in §19.
6. **Prestatiedoelstelling:** de keuze wordt pas definitief na de eigen, vergelijkende baseline-meting (§11, fase 2). **[AANNAME]** Plasma zal naar verwachting minimaal vergelijkbaar zijn met de andere kandidaten op de gekozen hardware; dit is een hypotheses, geen claim.

### 7.3 Nadelen en risico's

- **[RISICO]** Debian 13 levert Plasma 6.3.6 [S11], terwijl 6.6 de LTS is (tot ~feb 2029) [S19] en 6.8 actueel is [S17]. Eigen backportage van een nieuwere Plasma-/Qt-/KF6-stack is een forse, meerjarige packaginglast. **[AANBEVELING]** In v1 níet backporten; accepteer de Debian-versie en plan de rebase naar Debian 14 (§19). **[OPEN VRAAG]** Q-05 (§21).
- **[RISICO]** Plasma-releases komen ~elke 4 maanden [S19]; eigen thema's en scripts moeten bij elke rebase regressief getest worden.
- **[RISICO]** Qt6/KF6-compatibiliteit van eigen KCM's/scripts vereist CI tegen meerdere versies.
- **[RISICO]** XWayland dekt niet alle legacy-toepassingen (schermopname, global shortcuts, automatisering); KDE benoemt dit zelf [S18]. Mitigatie: compatibiliteitstestlijst in §10/§19.
- **[RISICO]** Een "premium" thema kan ten koste gaan van contrast/toegankelijkheid. Mitigatie: toegankelijkheidstoets als harde release-gate.

### 7.4 Alternatief scenario (voor de reviewer)

**[AANBEVELING — ter discussie]** Mocht de gebruiker kiezen voor Ubuntu 26.04 LTS als basis, dan wordt GNOME 50 de facto de desktop (Wayland-only) [S4][S20] en verschuift de eigen identiteit naar een eigen shell-extensieset — met hoger onderhoudsrisico. Mocht Fedora KDE worden gekozen, dan is de nieuwste Plasma beschikbaar maar vervalt de 5-jaarsstabiliteit [S6]. Beide varianten veranderen ADR-0001 én ADR-0002 en moeten als nieuw voorstel worden vastgelegd, niet stilzwijgend.

---

## 8. Wayland- en GPU-strategie

### 8.1 Displayserver

**[FEIT]** Wayland is een protocol en architectuur; er is niet één gemeenschappelijke Wayland-server zoals Xorg, maar elke omgeving levert een eigen compositor [S29]. **[AANBEVELING]** SANORA gebruikt **KWin als Wayland-compositor**, met XWayland voor X11-applicaties [S18][S29]. Geen eigen compositor, geen X11-logsessie, geen Xorg als default. **[FEIT]** KDE stelt dat X11-applicaties via XWayland blijven werken, dat schermopname/-casting en automatisering aandachtspunten blijven, en dat Wayland op NVIDIA-hardware inmiddels volwassen is [S18].

### 8.2 Grafische stack per vendor

**[FEIT]** De kernel-GPU-documentatie beschrijft DRM/KMS, atomic modesetting, GEM/TTM, PRIME, sync objects en drivers waaronder `amdgpu`, `i915`, `xe` en `nouveau` [S30]; `xe` is de nieuwere Intel-driver voor toekomstige/gebaseerde platforms [S31]. **[FEIT]** Wayland-clienttoegang en sandbox-permissies (`--socket=wayland`, `--socket=fallback-x11`, `--device=dri`) zijn gedocumenteerd in Flatpak [S48].

| Vendor | Kerneldriver | Userspace | Status / aandachtspunt |
|---|---|---|---|
| Intel geïntegreerd / oudere Gen | `i915` (DRM/KMS) [S30] | Mesa Iris/ANV, VA-API | Basisvoorziening; test per generatie |
| Intel Arc / nieuwere platforms | `xe` [S31] | Mesa ANV/Iris | Vereist voldoende nieuwe kernel + firmware; **risico op Debian 6.12**, zie §9 |
| AMD Radeon (GCN/RDNA) | `amdgpu` [S30] | Mesa RadeonSI / RADV, VA-API | Open stack; firmware uit `linux-firmware` [S38] |
| NVIDIA GeForce (Turing t/m Hopper) | Open kernel modules (MIT/GPLv2) óf propriëtaire modules; userspace blijft propriëtair [S36][S37] | NVIDIA userspace + EGL/GBM, Vulkan | Open modules zijn de aanbevolen keuze van NVIDIA [S36]; Blackwell+ **alleen** open [S36] |
| NVIDIA oude GPU's / fallback | `nouveau` [S30] | Mesa | Beperktere features; valweg, geen primaire strategie |

**[FEIT]** NVIDIA's README (driver 615.78.08) stelt: de open kernelmodules zijn dual MIT/GPLv2 gelicentieerd, NVIDIA beveelt ze aan op alle GPUs die ze ondersteunen, de userspace-componenten zijn identiek ongeacht de modulekeuze, de twee flavors zijn wederzijds uitsluitend, en Blackwell en later worden **alleen** door de open modules ondersteund [S36]. **[FEIT]** Diezelfde README noemt nadelen van open modules t.o.v. propriëtaire modules zonder GSP: langzamere GPU-initialisatie, langere S3/S4/RTD3-latentie en marginaal hoger verbruik in sommige scenario's [S36]. **[FEIT]** De NVIDIA-repo (versie 615.78.08, commit 7 okt 2026) vereist dat de kernelmodules met **bijbehorende GSP-firmware en userspace van dezelfde release** worden gebruikt [S34].

### 8.3 Wayland-specifieke aandachtspunten

**[AANBEVELING]** Test verplicht: expliciete synchronisatie (linux-drm-syncobj / EGL explicit sync) op NVIDIA, GBM-allocator, multi-monitor met verschillende refresh rates, fractionele schaling, VRR, HDR, schermopname via portals, klembord, globale sneltoetsen, touchpad-gestures en remote desktop. **[FEIT]** GNOME 50 noemt verbeterde VRR/fractional scaling en soepelere NVIDIA-ervaring [S4][S20]; KDE noemt adaptive sync, optionele tearing, high-refresh multi-monitor en HDR op Wayland [S18]. Deze claims zijn **upstream-claims**, geen SANORA-metingen.

**[RISICO]** Propriëtaire kernelmodules + Wayland + Secure Boot vormen een drievoudige foutbron (§12.2, §20 R-01/R-02). **[AANBEVELING]** NVIDIA-ondersteuning als **opt-in ná installatie** leveren (niet in de default-ISO), met een duidelijke wizard die driverversie, kernelversie, Secure Boot-status en de bijbehorende licentie toont (§12.5, §14).

### 8.4 GPU-prestaties en meetbaarheid

**[AANBEVELING]** Gebruik DRM client usage stats (fdinfo) voor GPU-utilisatie per client [S30], naast framerate-/frametime-metingen. **[NIET GETEST]** Geen GPU-metingen uitgevoerd; drempelwaarden volgen na de baseline in fase 2/8.

---

## 9. Kernel- en driverstrategie

### 9.1 Uitgangspunten

**[FEIT]** Geen eigen kernel vanaf nul (projectregel). **[FEIT]** Debian 13 levert de 6.12-kernelserie [S11]; op 2026-11-01 toont kernel.org `7.3.1` als nieuwste stable en `6.18.60`, `6.12.115`, `6.6.161`, `6.1.191`, `5.15.224`, `5.10.273` als longterm [S32][S33]. **[FEIT]** Ubuntu 26.04 gebruikt 7.0 met HWE [S2][S4]. **[AANBEVELING]** SANORA volgt de Debian-kernel; de distro levert beveiligingsfixes door terug te porten op de bevroren versie, wat ABI/API-stabiliteit garandeert [S14].

### 9.2 Kernelbeleid (voorgesteld)

| Onderdeel | Beleid |
|---|---|
| Default kernel | Door Debian ondertekende `linux-image-amd64` uit trixie (6.12) + `trixie-security` [S8][S11] |
| Nieuwe hardware | **Selectief** `trixie-backports`-kernel, alleen voor aantoonbaar niet-werkende hardware; per pakket gedocumenteerd; [S15] waarschuwt: "as-is", minder getest, geen reguliere security-support van het Security Team |
| Configuratie | Geen eigen kernelpatches in v1; alleen bootparameters en module-opties via `/etc` |
| Eigen kernelpackage | Alleen overwegen als hardwarematrix aantoont dat backports structureel tekortschieten; dan als ADR met CI, CVE-monitoring en ondertekening |
| Microcode | `intel-microcode` / `amd64-microcode` via Debian, met documentatie over herkomst |
| Firmware | `linux-firmware` / Debian `non-free-firmware`; officiële Debian-media mogen die bevatten [S13][S38] |
| Firmware-updates | `fwupd` + LVFS, inclusief offline/immutable-image-opties en mirrorstrategie [S39] |
| Module-ondertekening | Eigen/out-of-tree modules (o.a. NVIDIA/DKMS) moeten met een MOK worden ondertekend bij Secure Boot [S40] |

**[RISICO]** De kloof tussen Debian 6.12 en kernel.org 7.3 [S33] is het grootste hardwarecompatibiliteitsrisico van de gekozen basis. **[AANBEVELING]** Meet dit in fase 4 met een representatieve hardwarematrix vóór enige belofte over ondersteuning.

### 9.3 Firmware en juridische herkomst

**[FEIT]** De `linux-firmware`-repository bevat naast blobs een `LICENSE`, een `LICENSES/`-map en `LICENSE-CRITERIA.md`: firmware valt dus niet onder één uniforme licentie [S38]. **[FEIT]** Debian's Social Contract §5 staat toe dat officiële media firmware bevatten die zelf niet aan de DFSG voldoet, en moedigt distributeurs aan de licenties van `contrib`/`non-free` te lezen [S13]. **[FEIT]** LVFS-documentatie vereist van vendors een juridische verklaring dat firmware herdistribueerbaar is, en ondersteunt het meeleveren van `.cab`-bestanden in een image of het spiegelen van goedgekeurde firmware [S39].

**[AANBEVELING]** Onderhoud een machineleesbare `firmware-inventory.md` met per blob: bestandsnaam, SHA-256, herkomst, SPDX-licentie [S51], herdistributievoorwaarde en de vraag of juridische toets is gedaan. **[FEIT]** De NVIDIA Driver License Agreement staat distributie van de SOFTWARE toe voor gebruik met kernels onder een OSI-goedgekeurde opensourcelicentie, mits de binaire bestanden **ongewijzigd** blijven en de overeenkomst aan elke ontvanger wordt verstrekt; zij bevat daarnaast beperkingen (geen reverse engineering, geen gewijzigde headers, geen datacentergebruik voor GeForce/Titan) [S37]. **[AANBEVELING]** Neem NVIDIA daarom niet ongewijzigd op in de ISO zonder juridische toets en zonder dat de licentietekst meegeleverd wordt; een opt-in installatie na first boot met expliciete acceptatie is de veiligere route. **[FEIT]** Dit is een technische lezing, geen juridisch advies (§0.3).

### 9.4 Driverstrategie per hardwareklasse

Zie §10.3 voor de volledige hardwarematrix. **[AANBEVELING]** Prioriteit: (1) in-kernel open drivers + firmware; (2) open kernelmodules met propriëtaire userspace waar noodzakelijk (NVIDIA); (3) propriëtaire drivers alleen opt-in en gedocumenteerd; (4) `nouveau` als minimale valweg.

---

## 10. Hardwarecompatibiliteitsstrategie

### 10.1 Doel en scope

**[AANBEVELING]** x86-64 alleen in v1; ARM64 later (§21, Q-10). Ondersteuning wordt **bewezen met tests**, niet beloofd op basis van aanwezigheid van een driver. **[FEIT]** Ubuntu 26.04 noemt als officiële minimumspecificatie 2 GHz dual-core, 6 GB RAM, 25 GB opslag [S3]; SANORA heeft nog geen eigen minimum vastgesteld — **[OPEN VRAAG]** Q-03 (§21).

### 10.2 Detectie- en rapportageketen

**[AANBEVELING]** Gebruik bestaande mechanismen: kernel/sysfs/udev voor detectie, `lspci`/`lsusb`/`lshw`-achtige inventarisatie, `fwupdmgr` voor firmware [S39], NetworkManager/BlueZ/PipeWire/libinput voor respectievelijk netwerk, Bluetooth, audio en invoer, en `power-profiles-daemon`/kernel-cpufreq voor energiebeheer. **[AANBEVELING]** Elke detectiefout resulteert in een begrijpelijke melding met een concreet vervolgpad (F-06), niet in een stille fallback.

**[AANBEVELING]** Publiceer een **Hardware Compatibility List (HCL)** met per getest systeem: exacte hardware-ID's, kernelversie, Mesa-versie, firmwareversies, driver-flavor, Wayland-sessie, testresultaten, datum en tester. Geen "ondersteund" zonder testrapport.

### 10.3 Hardwarematrix (ontwerp, niet getest)

| Klasse | Open driver / component | Propriëtair / firmware | Specifiek aandachtspunt |
|---|---|---|---|
| Intel Core CPU | In-kernel sched/cpufreq, `intel_pstate` | `intel-microcode` | Nieuwere generaties vragen mogelijk kernel > 6.12 (§9) |
| AMD Ryzen CPU | In-kernel `amd-pstate` | `amd64-microcode` | Idem |
| NVIDIA GeForce | Open kernelmodules (MIT/GPLv2) [S34][S36], `nouveau` [S30] als valweg | Propriëtaire userspace + GSP-firmware [S34][S36][S37] | Wayland explicit sync, module-ondertekening, RTD3-latentie [S36] |
| AMD Radeon / iGPU | `amdgpu` [S30] + Mesa | Firmware uit `linux-firmware` [S38] | RADV/RadeonSI-versie, VA-API |
| Intel geïntegreerd / Intel Arc | `i915` / `xe` [S30][S31] + Mesa | Firmware/microcode [S38] | `xe` mogelijk niet volledig op 6.12; GuC/HuC-firmware |
| Wi-Fi | In-kernel mac80211-drivers | Vendor-firmware [S38] | Grootste firmwareafhankelijkheid; offline-installatie moet firmware bevatten |
| Bluetooth | BlueZ + kernel | Firmware [S38] | Koppelen, suspend/resume, audio-profielen |
| Ethernet | In-kernel drivers | Soms firmware [S38] | 2.5GbE-controllers vragen nieuwere kernel |
| Audio | ALSA/sof + PipeWire | SOF/DSP-firmware [S38] | Laptop-microfoons, jack-detectie, suspend |
| Touchpad / toetsenbord | libinput/evdev, HID | Soms firmware | Gestures, palm-rejectie, Fn-toetsen |
| SATA / NVMe | In-kernel `ahci`/`nvme` | NVMe-firmware via fwupd [S39] | TRIM/discard, power states, APST |
| Laptop | ACPI/platform drivers, power-profiles | BIOS/UEFI-updates via LVFS [S39] | Suspend, accuduur, thermals, dock/hotplug |
| Desktop | Idem | Idem | Multi-monitor, USB, wake-from-suspend |

### 10.4 Onderscheid open / propriëtair / firmware — samenvatting

**[FEIT]** In de kernel aanwezige drivers (amdgpu, i915, xe, nouveau, nvme, mac80211) zijn open source; NVIDIA levert zowel open kernelmodules (dual MIT/GPLv2) als propriëtaire modules, maar de userspace blijft propriëtair [S30][S31][S36]; firmware is veelal een binaire blob met per-bestand verschillende licenties [S38]; LVFS levert door vendors ondertekende firmware met herdistributieverklaring [S39]. **[AANBEVELING]** Maak dit onderscheid zichtbaar in de UI: "open driver", "open kernelmodule + gesloten userspace", "firmware vereist", met uitleg wat dat voor de gebruiker betekent.

### 10.5 Juridische voorwaarden (beknopt)

**[AANBEVELING]** Vóór de eerste publieke ISO: juridische toets van (a) alle firmwareblobs in het image [S38][S13], (b) NVIDIA-licentie en leveringswijze [S37], (c) eventuele codecs en fonts, (d) eigen vs. upstream-assets. **[FEIT]** Debian moedigt CD-/image-makers expliciet aan de licenties in `contrib`/`non-free` te controleren [S13]. **[FEIT]** Geen van deze toetsen is nu uitgevoerd.

---

## 11. Performanceplan

### 11.1 Uitgangspunt: geen verzonnen benchmarks

**[NIET GETEST]** Er zijn **geen** prestatieresultaten behaald of gemeten. Dit hoofdstuk definieert uitsluitend **indicatoren, meetmethoden en een vergelijkingsprotocol**. **[FEIT]** Secundaire RAM/CPU-cijfers voor desktopomgevingen zijn methodologisch niet vergelijkbaar (§6.1). **[AANBEVELING]** Er worden geen streefwaarden ("< 800 MB RAM") vastgelegd voordat de baseline-meting is gedaan; wel worden de **acceptatieregels voor het meetproces** vastgelegd.

### 11.2 KPI-definities

| KPI | Definitie | Meetmiddel | Waarom deze definitie |
|---|---|---|---|
| KPI-1 Idle-RAM | `MemAvailable` uit `/proc/meminfo`, 5 min na volledige desktop-load, 10 herhalingen, mediaan + p95 | `/proc/meminfo`, script | `MemAvailable` is bruikbaarder dan "free" omdat cache meetelt |
| KPI-2 Idle-CPU | Gemiddelde CPU-bezigheid en PSI over 10 minuten idle; per-unit activiteit | `pidstat`, PSI, `systemctl list-units` | Voorkomt dat één service onzichtbaar blijft |
| KPI-3 Bootduur | `systemd-analyze time`: firmware→kernel→initrd→userspace, plus `graphical.target` [S43] | `systemd-analyze` [S43] | Officieel, reproduceerbaar; beperking: meet start, niet volledige initialisatie [S43] |
| KPI-4 Unit-bijdrage | `systemd-analyze blame` / `critical-chain` als **diagnose**, niet als ranglijst [S43] | `systemd-analyze` | De man page waarschuwt expliciet voor misleidende resultaten [S43] |
| KPI-5 Applicatiestart | Koude start tot "eerste bruikbare frame", 15 herhalingen na drop-caches, mediaan + spreiding | eigen harness + `hyperfine`-achtige timing | Koude start is wat gebruikers ervaren |
| KPI-6 Schijfprestaties | Sequentieel/willekeurig lezen/schrijven, vaste queue depth en blokgrootte | `fio` met vastgelegde jobfile | Parameters moeten in de repo staan, anders is vergelijken zinloos |
| KPI-7 Energieverbruik | Gemiddeld systeemvermogen in idle en bij vastgestelde workload; accuduur op referentielaptops | externe meter / `powerstat`-achtige logging + batterijmeting | Zonder vaste workload geen vergelijking |
| KPI-8 GPU | Aantoonbare hardwareversnelling; frame-tijd, geen dropped frames bij vastgestelde animatie; DRM fdinfo-utilisatie [S30] | DRM-stats + frametime-log | Meet "vloeiend", niet alleen "aanwezig" |
| KPI-9 Service-last | Aantal actieve units + aantal standaard geïnstalleerde pakketten | `systemctl`, `dpkg-query` | Directe proxy voor "onnodige achtergrondprocessen" |
| KPI-10 Update-impact | Tijd en downtime van een security-update, en hersteltijd bij rollback | testsuite + snapshots | Betrouwbaarheid is ook performance |

### 11.3 Meetprotocol

**[AANBEVELING]** Vaste referentieomgeving: minimaal drie fysieke systemen (Intel-iGPU laptop, AMD-Radeon desktop, NVIDIA-GeForce laptop), dezelfde schijf, dezelfde resolutie/schaal, dezelfde licht-/donkermodus, dezelfde achtergrondservices, geen netwerkactiviteit tijdens meting, vaste kernel en Mesa-versie gelogd, 3 runs op 3 dagen. **[AANBEVELING]** Baseline = **ongewijzigde Debian 13 met KDE Plasma** op exact dezelfde hardware; SANORA wordt altijd tegen die baseline vergeleken, nooit tegen een andere distributie.

**[AANBEVELING]** Regressieregel: elke wijziging in de SANORA-laag (thema, script, service, pakket) moet een meetbare delta op de relevante KPI rapporteren. Een optimalisatie zonder meetbare verbetering wordt **niet** doorgevoerd. **[AANBEVELING]** Stabiliteitsregel: een KPI-verbetering die een faalpercentage in de functionele tests verhoogt, wordt verworpen. **[RISICO]** Metingen op virtuele machines zijn niet representatief voor GPU/energie; alleen gebruiken voor functionele CI, niet voor KPI-publicatie.

### 11.4 Rapportage

**[AANBEVELING]** Per release een `PERFORMANCE.md` met ruwe data, hardware-ID's, exacte versies, commando's, methodologie, beperkingen en de vergelijking met de baseline. **[NIET GETEST]** Geen enkele waarde is nu beschikbaar; alle KPI-tabellen blijven leeg tot fase 2/8.

---

## 12. Beveiligingsstrategie

### 12.1 Uitgangspunten

**[AANBEVELING]** Kies uitsluitend oplossingen die een kleine organisatie realistisch kan onderhouden: inherente distro-mechanismen, geen eigen MAC-beleid vanaf nul, geen eigen HSM-proces zonder budget. **[FEIT]** Debian backport security-fixes op bevroren versies om API/ABI-breuk te voorkomen [S14]; AppArmor is sinds kernel 2.6.36 in de mainline kernel en biedt per-applicatie MAC [S44]; firewalld biedt zones, D-Bus-interface en scheiding tussen runtime en permanente configuratie [S45]; polkit regelt autorisatie voor systeemacties [S46]; `unattended-upgrades` automatiseert security-updates via `apt-daily`-timers [S47]; Flatpak isoleert applicaties standaard en gebruikt portals voor gecontroleerde toegang [S48].

### 12.2 Secure Boot — grootste realiteitscheck

**[FEIT]** Debian ondersteunt Secure Boot sinds Debian 10 via een door Microsoft ondertekende **shim** die Debian's eigen sleutels bevat; eigen kernels/modules kunnen via een **MOK (Machine Owner Key)** worden ondertekend; de wiki beschrijft DKMS-ondertekening en de beperkingen van Secure Boot [S40]. **[FEIT]** `rhboot/shim` is een actief onderhouden project met o.a. SBAT-revocatiebeleid en MOK-beheer [S41].

**[RISICO — R-01, hoog]** Een eigen distributie die haar **eigen** shim/bootketen door Microsoft wil laten ondertekenen, heeft te maken met een extern reviewproces, sleutelbeheer, SBAT-revocaties, GRUB-/kernel-updates en doorlopende verantwoordelijkheid. **[AANBEVELING]** In v1 **niet** streven naar een eigen door Microsoft ondertekende shim. Drie fasen:
1. **Fase A (v1):** documenteer Secure Boot helder; ondersteun installatie met Secure Boot uitgeschakeld én, waar mogelijk, hergebruik van de door Debian ondertekende keten met uitsluitend door Debian ondertekende kernels. Eigen/out-of-tree modules (NVIDIA) vereisen dan MOK-registratie door de gebruiker [S40].
2. **Fase B:** evalueer eigen MOK-beleid, ondertekening van eigen kernelmodules in CI en documentatie voor NVIDIA/DKMS.
3. **Fase C (alleen met budget/juridische toets):** eigen shim-ondertekening. Dit is een expliciete goedkeuringsbeslissing, geen implementatiestap in deze fase.

**[FEIT]** Secure Boot is een boot-integriteitsmaatregel, geen bescherming tegen alle aanvallen; de Debian-wiki beschrijft dit expliciet [S40].

### 12.3 Firewall, MAC, machtigingen, sandboxing

| Maatregel | Voorstel | Argument / nadeel |
|---|---|---|
| Firewall | Standaard `firewalld` met conservatieve zone, inkomend verkeer dicht, uitgaand toegestaan [S45] | D-Bus-API en zone-model zijn volwassen; nadeel: extra service en complexiteit t.o.v. kale `nftables`-regels — daarom expliciete ADR |
| MAC | AppArmor-profielen van Debian aan, eigen profielen alleen voor eigen daemons [S44] | In-kernel, lichter te onderhouden dan een nieuw SELinux-beleid; nadeel: minder fijnmazig dan SELinux |
| Autorisatie | polkit voor systeemacties; geen root-standaardsessie; geen wachtwoordloze `sudo` [S46] | Standaard op Linux-desktops; nadeel: eigen KCM's moeten correcte polkit-acties definiëren |
| App-isolatie | Flatpak als standaard voor gebruikersapps; portals i.p.v. brede rechten; `--socket=system-bus`/`session-bus` vermijden [S48] | Sandbox + portals zijn gedocumenteerd [S48]; nadeel: sommige apps vragen alsnog ruime permissies — die worden in de UI zichtbaar gemaakt |
| Systeemapps | Draaien als gewone gebruiker; systemd-unit hardening via `systemd-analyze security` [S43] | Meetbaar; nadeel: hardening kan functies breken, dus per unit testen |

### 12.4 Automatische beveiligingsupdates

**[AANBEVELING]** `unattended-upgrades` standaard aan voor **security-updates uit `trixie-security` én de ondertekende SANORA-repo**; applicatie-updates via Discover/Flatpak blijven gebruikersgestuurd [S47][S26]. **[FEIT]** Debian gebruikt `apt-daily.timer` en `apt-daily-upgrade.timer`; `unattended-upgrades` draait standaard niet op accuvoeding, en de wiki waarschuwt dat apt/dpkg niet atomair is bij stroomonderbreking [S47]. **[AANBEVELING]** Daarom: geen geforceerde updates op accu, duidelijke notificatie bij uitstel, en verplichte rollback-voorziening (§12.8). **[AANBEVELING]** Eigen repo moet met een offline/gescheiden bewaarde sleutel ondertekend worden en `Release`-bestanden met checksums leveren, analoog aan de door Debian beschreven integriteitsketen [S8].

### 12.5 Schijfversleuteling

**[AANBEVELING]** Optionele LUKS2-versleuteling tijdens installatie, met passphrase + herstelsleutel; geen TPM-ontgrendeling als **default** in v1. **[FEIT]** `systemd-cryptenroll` ondersteunt TPM2, FIDO2, PKCS#11, passphrases en herstelsleutels, en bindt secrets aan PCR's (doorgaans 7, 11 en 14 bij shim/MOK) [S42]. **[RISICO]** TPM-binding is gevoelig voor firmware-/bootketenwijzigingen; de man page adviseert PCR 0/2 te vermijden en certificaatvalidatie boven directe metingen te verkiezen [S42]. **[AANBEVELING]** TPM2-ontgrendeling pas als opt-in ná fase 7, met herstelsleutel verplicht en een regressietest voor kernel-/firmware-updates.

### 12.6 Softwareherkomst en supply chain

**[AANBEVELING]** (1) uitsluitend ondertekende repositories, (2) SPDX-identifiers per bestand/pakket [S51], (3) machineleesbare SBOM per ISO, (4) `SOURCE_DATE_EPOCH` en reproduceerbare builds [S55][S56], (5) `diffoscope`/`reprotest`-vergelijking van twee onafhankelijke builds [S54], (6) provenance/attestaties volgens SLSA-niveaus als **referentiekader**, niet als claim [S50], (7) gedocumenteerde sleutelrotation en een `SECURITY.md` met meldpad. **[FEIT]** SLSA v1.0 is een specificatie met niveaus en aanbevolen attestation-formaten; de site geeft aan dat v1.2 inmiddels actueel is [S50]. **[AANBEVELING]** Gebruik de actuele versie bij implementatie en claim geen SLSA-niveau zonder externe verificatie.

### 12.7 Privacy-gerelateerde beveiliging

Zie §13. **[AANBEVELING]** Geen standaard telemetrie, geen verplichte cloud-account, geen standaard externe DNS-provider zonder keuze, geen ongevraagde crash-upload.

### 12.8 Herstel en rollback

**[AANBEVELING]** Geen "atomair" systeem claimen op apt/dpkg ([S47] waarschuwt). **[AANBEVELING]** Voorstel: Btrfs-root met subvolumes en `snapper`-snapshots rond updates, plus bootbare snapshots. **[FEIT]** openSUSE-documentatie beschrijft `snapper rollback`, maar ook dat `/home` standaard buiten de snapshots valt en dat een rollback dus géén gebruikersdata-back-up is [S52]. **[AANBEVELING]** Documenteer dat expliciet, en bied daarnaast een herstelmodus in de ISO (offline `chroot`-herstel, pakket-cache, logboek). **[OPEN VRAAG]** Q-07: later een image-based/immutable model overwegen; dat is nu bewust niet gekozen vanwege complexiteit.

### 12.9 Nadelen van de gekozen beveiligingsstrategie

**[RISICO]** AppArmor is minder fijnmazig dan SELinux; `firewalld` voegt een daemon toe; LUKS2 + TPM2 verhoogt herstelcomplexiteit; geen eigen shim betekent minder controle over de bootketen; automatische updates kunnen regressies veroorzaken. **[AANBEVELING]** Al deze nadelen worden geaccepteerd in ruil voor **realistisch onderhoudbaar** zijn, en worden als risico's in §20 bewaakt.

---

## 13. Privacystrategie

**[AANBEVELING]** Privacy is een default, geen instelling achteraf:

| Principe | Concrete uitwerking |
|---|---|
| Geen advertenties | Geen gesponsorde apps, geen "aanbevolen" commerciële inhoud in het softwarecentrum |
| Geen tracking | Geen telemetrie, geen unieke installatie-ID, geen standaard crash-upload; eventuele statistieken uitsluitend **opt-in**, lokaal, anoniem en met inzage vóór verzenden |
| Geen verplichte accounts | Installatie, updates en dagelijks gebruik zonder account; online diensten zijn optioneel |
| Transparantie | `PRIVACY.md` met per component: welke data het systeem verwerkt, waar, waarom en hoe uit te schakelen |
| Dataminimalisatie | HCL-rapportage (§10.2) bevat geen serienummers of gebruikersdata; alleen hardware-ID's en versies |
| Softwareherkomst | Zichtbare bron per app/pakket (Debian-repo, SANORA-repo, Flathub, firmware via LVFS) [S12][S39][S49] |
| Toestemming | Portal-gebaseerde toegang tot bestanden, camera, microfoon en schermopname; permissies zichtbaar in de UI [S48] |
| Lokale verwerking | Zoeken, indexeren en diagnostiek standaard lokaal |
| Firmware | `fwupd`/LVFS alleen na expliciete gebruikersactie; LVFS-documentatie stelt dat de gebruiker expliciet moet instemmen met een firmware-update [S39] |
| Logging | Logs lokaal, met rotatie; geen standaard upload; duidelijke retentie |

**[FEIT]** Flatpak-portals vragen impliciet toestemming via bijvoorbeeld de bestandskiezer en beperken standaard de toegang tot host-bestanden, netwerk, devices en D-Bus [S48]. **[RISICO]** Flathub en LVFS zijn externe diensten; **[AANBEVELING]** documenteer welke verbindingen het systeem standaard maakt (repo-updates, AppStream-metadata, firmware-metadata, NTP) en bied een offline-modus. **[NIET GETEST]** Er is nog geen privacy-audit uitgevoerd.

---

## 14. Package management

### 14.1 Voorgesteld model

**[AANBEVELING]** Twee kanalen met een duidelijke scheiding:

| Kanaal | Doel | Beheerder | Ondertekening |
|---|---|---|---|
| `apt`/`dpkg` (Debian `main`, `non-free-firmware`, `trixie-security`, `trixie-updates`) [S8][S13][S16] | Basis-OS, kernel, drivers, firmware, systeembibliotheken | Debian | Debian-archiefsleutels; `Release`/`Release.gpg`-keten [S8] |
| Eigen SANORA-repo | SANORA-thema, configuratie, KWin-scripts, eigen apps, installermodules, branding-pakketten | SANORA | Eigen GPG-sleutel, offline bewaard, `Signed-By` per bron |
| Flatpak/Flathub [S49] | Eindgebruikersapplicaties | Upstream / Flathub | Flatpak-repo-ondertekening |

**[FEIT]** Debian's APT-handleiding beschrijft apt/dpkg als pakketsysteem [S16]; Debian garandeert integriteit via ondertekende `Release`-bestanden met checksums van `Packages`-bestanden [S8]. **[FEIT]** Flatpak is een onafhankelijk project met runtimes en "build once, run on many distros" [S49]; sandboxrechten worden statisch in het manifest vastgelegd [S48].

### 14.2 Waarom geen snap als standaardkanaal (voorstel)

**[AANBEVELING]** Snap wordt niet als standaard applicatiekanaal opgenomen. Argumenten: (1) de serverzijde van de Snap Store is geen open, zelf te hosten component — dit botst met de eis van transparante softwareherkomst en onafhankelijkheid; (2) Ubuntu 26.04 integreert snap diep in GNOME Shell [S4], wat bij een niet-Ubuntu-basis extra integratielast geeft; (3) twee concurrerende sandboxmodellen vergroten de documentatie- en testlast. **[FEIT]** KDE Discover ondersteunt wél een Snap-backend [S26]; **[AANBEVELING]** die backend blijft beschikbaar voor gevorderde gebruikers maar wordt niet standaard geactiveerd. Nadeel: sommige leveranciers publiceren alleen snaps; mitigatie: documenteer alternatieven (Flatpak, deb, upstream-tarball) in het softwarecentrum.

### 14.3 Curatie en versiebeleid

**[AANBEVELING]** Beperkte standaardsoftware met een `manifest`-bestand in de repo dat per pakket uitlegt waarom het aanwezig is en wie de eigenaar is. **[AANBEVELING]** `apt pinning` om te voorkomen dat de SANORA-repo onbedoeld Debian-pakketten overschrijft. **[FEIT]** Debian-backports hebben een lagere prioriteit en worden "as-is" geleverd [S15]; **[AANBEVELING]** pin backports expliciet en log elke uitzondering in een ADR.

### 14.4 Nadelen

**[RISICO]** Eigen repo betekent eigen sleutelbeheer, eigen build-CI, eigen CVE-opvolging voor eigen code en een single point of failure. **[AANBEVELING]** Houd de repo daarom klein: configuratie en thema's als `Architecture: all`-pakketten, zo weinig mogelijk gecompileerde code. **[RISICO]** Flatpak-runtimes verbruiken extra schijfruimte; dat wordt als KPI-9/§11 gemeten, niet als aanname afgedaan.

---

## 15. Softwarecentrum

### 15.1 Aanbeveling

**[AANBEVELING]** **KDE Discover** als softwarecentrum [S26], met AppStream-metadata [S27][S28] en geselecteerde backends: Flatpak, PackageKit (voor apt), fwupd (firmware), en KNS voor Plasma-add-ons. **[FEIT]** Discover kan volgens de officiële applicatiepagina software uit meerdere bronnen beheren (distributie-repo, Flatpak, Snap, AppImages) en heeft aparte Flatpak-, PackageKit-, Snap- en AppStream-preview-backends [S26]. **[FEIT]** AppStream is de distro-agnostische metadatastandaard voor softwarecentra, inclusief firmware- en driver-componenten [S27]; Debian genereert AppStream-metadata automatisch via APT [S28]. **[FEIT]** Discover heeft sinds Plasma 5.14 een fwupd-backend voor firmware-updates (KDE-aankondiging) en wordt in LVFS-documentatie als client genoemd [S39].

### 15.2 Eigen SANORA-laag

**[AANBEVELING]** Eigen werk beperkt tot: (1) curatie (een "SANORA-selectie"-collectie), (2) eigen AppStream-metainfo voor eigen apps met `appstreamcli validate` [S27][S28], (3) een consistente presentatie van permissies (Flatpak) en herkomst, (4) later een geïntegreerd **SANORA Systeembeheer** voor updates, snapshots, drivers en privacy — als KCM in System Settings, niet als losse app. **[AANBEVELING]** Geen eigen store-server in v1.

### 15.3 Nadelen en risico's

- **[RISICO]** De PackageKit-backend voegt een extra abstractielaag toe; Ubuntu 26.04 heeft `pkcon` verwijderd [S4]. **[AANBEVELING]** Evalueer of Discover's apt-integratie zonder PackageKit kan, of kies expliciet voor PackageKit met een eigen testset. **[OPEN VRAAG]** Q-08.
- **[RISICO]** Flatpak-permissies worden door upstream-appbeheerders bepaald; gebruikers zien mogelijk ruime rechten [S48]. Mitigatie: waarschuwingen in de UI en een SANORA-curatielijst.
- **[RISICO]** Firmware-updates via LVFS vragen netwerktoegang en vendor-ondertekende metadata [S39]; offline-installatie moet dat uitleggen.
- **[RISICO]** Discover-versies volgen Plasma [S26]; bij elke rebase regressietesten.

---

## 16. Installer

### 16.1 Vergelijking

| Installer | Herkomst | Sterk | Beperking voor SANORA |
|---|---|---|---|
| **Calamares** [S61][S62] | Distributie-onafhankelijk framework, Qt/C++ met Python-modules, YAML-configuratie, branding en externe modules | Officieel ontworpen voor maatwerk per distro; modules voor partitionering, bootloader, gebruikers, LUKS [S62]; ondersteunt inmiddels Plasma Login Manager, NVMe/MMC-herkenning en 4K-alignment [S61] | Project is overgestapt van GitHub naar **Codeberg** (release 3.4.0 markeert de volledige overgang; 3.4.2 is de eerste getagde Codeberg-release) [S61]; **[FEIT]** de oude GitHub-repository is op 18 aug 2025 gearchiveerd en de `Deploy-LUKS`-wikipagina is sinds 2021 niet meer bijgewerkt [S62] — de LUKS-instructies moeten dus opnieuw tegen de actuele Codeberg-documentatie worden gevalideerd; eigen modules vergen onderhoud |
| Debian Installer (d-i) | Debian [S10] | Officieel, extreem betrouwbaar, HTTP Boot in trixie [S11] | Minder geschikt voor een "premium" grafische beginner-ervaring; minder thembaar |
| Ubuntu Desktop Installer / Subiquity | Canonical [S3][S4] | Modern, TPM-FDE in 26.04 [S4] | Gebonden aan Ubuntu en Canonical-IP [S5]; niet herbruikbaar op Debian-basis |
| Anaconda / Kickstart | Fedora [S60] | Zeer krachtig, automatiseerbaar | RPM-/Fedora-ecosysteem; past niet bij apt-basis |
| Calamares-alternatief: eigen installer | — | Volledige controle | Onnodig complex, expliciet ontmoedigd door de projectregels |

### 16.2 Aanbeveling

**[AANBEVELING]** **Calamares** (ADR-0005) met:
- eigen SANORA-branding, welkomstscherm en licentie-/privacy-uitleg;
- automatische en handmatige partitionering; 4K-alignment; NVMe-herkenning [S61];
- LUKS2-optie met herstelsleutel; de (historische) LUKS-documentatie noemt o.a. `cryptsetup`, KPMcore, GRUB 2 en een correcte initramfs-keyfile-keten, plus Debian-specifieke `initramfscfg`/`initramfs`-, `grubcfg`- en `crypttabOptions`-instellingen [S62]. **[FEIT]** Die wikipagina komt uit de inmiddels gearchiveerde GitHub-repo en is sinds 2021 niet bijgewerkt [S62]; **[AANBEVELING]** valideer de volledige keten in fase 4 tegen de actuele Codeberg-documentatie voordat encryptie als ondersteund wordt beschouwd;
- Btrfs-subvolumes met een `@`/`@home`-indeling als voorbereiding op snapshots (§12.8);
- offline-installatie: alle pakketten en benodigde firmware op de ISO, netwerk optioneel [S3][S13];
- hardwaredetectie vóór de schijfstap, met begrijpelijke melding bij ontbrekende firmware (F-06);
- een "samenvatting vóór wijzigen"-scherm dat exact toont wat er gaat gebeuren.
- **[FEIT]** Calamares is een framework en nadrukkelijk **geen kant-en-klare installer**; distributies leveren zelf de configuratie [S61].

### 16.3 Nadelen en risico's

**[FEIT]** De originele GitHub-repository van Calamares is op 18 augustus 2025 door de eigenaar gearchiveerd en is read-only; releases vinden sinds 3.4.x op Codeberg plaats [S61][S62]. **[RISICO]** Upstream-migratie naar Codeberg [S61] betekent dat issue-tracking, releases en signing keys daar moeten worden gevolgd; een gearchiveerde GitHub-repo of mirror is onvoldoende als bron. **[RISICO]** LUKS + initramfs + GRUB + Secure Boot is een keten met veel faalpunten, en de geraadpleegde LUKS-handleiding is historisch [S40][S62]. **[AANBEVELING]** Begin met één eenvoudige, volledig geteste partitiescenario (UEFI + GPT + EFI-partitie + één root, optioneel LUKS2) en breid daarna stapsgewijs uit. **[NIET GETEST]** Er is geen installatie uitgevoerd.

---

## 17. ISO-buildstrategie

### 17.1 Vergeleken tools

| Tool | Basis | Sterk | Beperking |
|---|---|---|---|
| **`live-build` (Debian Live)** [S53][S54] | Debian | Officiële Debian-tool voor live/ISO-images; `lb`-configuratie in Git; officiële reproduceerbaarheidsinspanningen met Jenkins + openQA + `diffoscope`/`reprotest` [S54]; produceert squashfs + ISO/Live-medium | **[FEIT]** Volgens de Debian-wiki zijn bookworm-images reproduceerbaar, zijn **trixie 13.2-images dat niet** (bootschermen en firmware-patronen wijken af; de kern-squashfs wel), en zijn forky-images weer reproduceerbaar [S54]. Grote builds (~17 GB voor GNOME) en snapshot-afhankelijkheid [S54]. |
| `mkosi` (systemd) [S57] | Multi-distro (apt/dnf/pacman/zypper) | Bouwt aangepaste OS-images, ondersteunt btrfs-subvolumes, LUKS, UEFI, verity, SHA256SUMS + GPG-ondertekening, heeft integratietests die images booten [S57] | Gericht op **disk images**, niet primair op klassieke live-ISO's; extra abstractielaag; vereist recente systemd/kernel [S57] |
| `debos` [S58] | Debian | YAML-recepten, actief onderhouden (commit op 2026-11-01), gericht op Debian-images | Vooral image-builder, minder live-ISO-voorzieningen; eigen workflow |
| `osbuild` / Image Builder [S59] | Fedora/RHEL-ecosysteem | Sterke, declaratieve image-pijplijn; bootc-integratie | RPM-georiënteerd; past niet bij een apt-basis zonder forse aanpassing |
| `lorax` / `livemedia-creator` [S60] | Fedora/Anaconda | Bouwt Anaconda `boot.iso`, live images, filesystem images | Aan Anaconda/Fedora gebonden [S60] |
| Ubuntu `ubuntu-image` / `livecd-rootfs` | Ubuntu [S3] | Volwassen Canonical-pijplijn | Gebonden aan Ubuntu-IP [S5]; niet bruikbaar op Debian-basis |

### 17.2 Aanbeveling

**[AANBEVELING]** Start met **`live-build`** (ADR-0004) omdat het de native Debian-route is, de reproduceerbaarheidsinfrastructuur al bestaat [S53][S54], en het de minste nieuwe concepten toevoegt. Bewaar `mkosi` [S57] en `debos` [S58] als evaluatie voor later (bijvoorbeeld voor een image-based updatepad, §21 Q-07). Gebruik Fedora's `osbuild`/`lorax` [S59][S60] **alleen als referentie** voor CI- en testpatronen, niet als bouwtool.

**[AANBEVELING]** Reproduceerbaarheidsaanpak:
1. `SOURCE_DATE_EPOCH` vastzetten op de laatste commit-/changelog-tijd [S55];
2. vastgelegde pakketbron (snapshotmirror of twee builds binnen het 6-uursvenster van `deb.debian.org`) [S54][S56];
3. deterministische ISO/squashfs-metadata: `xorriso --modification-date`, vaste UUID/label, `-no-compression`/`MKSQUASHFS_OPTIONS` waar nodig, clamping van mtimes [S56];
4. initramfs reproduceerbaar bouwen; `isohybrid --id` vastzetten [S56];
5. twee onafhankelijke builds vergelijken met `diffoscope` en `reprotest` [S54];
6. functionele smoke-tests via openQA-achtige automatisering [S54];
7. publicatie van `SHA256SUMS` + GPG-handtekening + SBOM + buildlog.

**[FEIT]** Reproduceer-builds documenteren dat system images lastig zijn door tijdstempels, UUID's, bootloader- en initramfs-metadata, en dat `SOURCE_DATE_EPOCH` de standaard is om die te vervangen [S55][S56]. **[FEIT]** De Debian-wiki toont dat reproduceerbaarheid per release kan regresseren [S54]. **[AANBEVELING]** Claim daarom nooit "reproduceerbaar" zonder een geslaagde dubbele build per release; rapporteer afwijkingen eerlijk.

### 17.3 Live-omgeving, offline, hardwaredetectie, updatebaarheid

**[AANBEVELING]** De ISO bevat: een live-sessie met dezelfde SANORA-desktop (zodat de gebruiker vóór installatie kan testen), alle firmware die nodig is voor de ondersteunde hardwarematrix [S13][S38], de Calamares-installer, en een offline pakketset. **[FEIT]** Ubuntu 26.04 documenteert dat een internetverbinding aanbevolen maar niet vereist is voor de initiële installatie [S3] — een bruikbaar referentiepunt voor de SANORA-eis F-01. **[AANBEVELING]** Updatebaarheid: het geïnstalleerde systeem wijst naar de gewone APT-repo's + SANORA-repo, niet naar de ISO; de installatie koppelt geen "bevroren image" aan de gebruiker. **[RISICO]** Firmware-opname in de ISO vergroot de juridische toetslast (§9.3, §10.5) en de ISO-omvang.

### 17.4 Nadelen van `live-build`

**[RISICO]** Trixie-images waren op het moment van raadpleging niet volledig reproduceerbaar [S54]; de tool vraagt root-achtige bouwrechten, veel schijfruimte en een snapshotstrategie; de live-sessie en de geïnstalleerde sessie kunnen subtiel verschillen. **[AANBEVELING]** Mitigeer met een verplichte "live vs. installed"-vergelijkingstest in elke release (§19).

---

## 18. GitHub-repositorystructuur (voorstel — **niet aanmaken in deze fase**)

### 18.1 Voorgestelde boom

```
SANORA-OS/
├── README.md                        # bestaand; later uitbreiden, niet overschrijven zonder PR
├── SANORA_OS_ARCHITECTURE.md        # dit document
├── LICENSE                         # nog te kiezen (§21, Q-01)
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── PRIVACY.md
├── CHANGELOG.md
├── THIRD_PARTY.md                   # upstream vs. eigen werk, SPDX per component
├── .github/
│   ├── ISSUE_TEMPLATE/              # bug, hardware, feature, security (YAML forms)
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── workflows/                   # lint, docs, shellcheck, linkcheck, reproduceerbaarheid
│   └── dependabot.yml               # alleen waar zinvol
├── docs/                            # gebruikersdocumentatie, installatie, FAQ
│   ├── installation.md
│   ├── hardware.md                  # HCL
│   ├── performance/                 # PERFORMANCE.md + ruwe data
│   └── releases/                    # release notes per versie
├── architecture/
│   ├── adr/                         # ADR-0001 … met status: proposed/accepted/superseded
│   ├── decisions.md
│   └── threat-model.md
├── branding/                        # eigen assets + licentie + bronbestanden (SVG/PNG/OGG)
├── desktop/                         # Global Theme, KWin-scripts, KCM's, standaardconfiguratie
├── packages/                        # debian/-packaging van SANORA-componenten
├── installer/                       # Calamares-branding, modules, settings.conf
├── iso/                             # live-build-config, package-lists, hooks
├── scripts/                         # kleine, geteste hulpscripts
├── tests/                           # HCL-tests, smoke-tests, KPI-harness, fixtures
├── build/                           # GENEGEERDE uitvoer; geen artefacten in Git
└── .gitignore                       # build/, ISO's, caches, secrets
```

**[FEIT]** GitHub documenteert dat issue-/PR-templates op de default branch in `.github/ISSUE_TEMPLATE` staan, dat issue forms `.yml` gebruiken, en dat `config.yml` de templatekiezer configureert; ook `SECURITY.md` wordt daar beschreven [S63]. **[AANBEVELING]** Alle community-bestanden komen in kleine, afzonderlijke PR's (§22), zodat reviewbaarheid behouden blijft.

### 18.2 Conventies (voorstel)

- **[AANBEVELING]** Geen binaire buildartefacten of ISO's in Git; gebruik releases/assets en een `.gitignore` conform de bestaande externe-opslagconventies van het project (nog niet aanwezig).
- **[AANBEVELING]** Elke map bevat een korte `README.md` met doel, eigenaar en "wat hoort hier niet thuis".
- **[AANBEVELING]** ADR-formaat: context, overwogen opties, beslissing, argumenten, nadelen, status, datum, reviewer. Wijziging van een geaccepteerde ADR = nieuwe ADR met `supersedes`.
- **[AANBEVELING]** SPDX-headers in bronbestanden [S51]; `THIRD_PARTY.md` documenteert per upstream-component de licentie en herkomst.
- **[AANBEVELING]** CI: markdown-linkcheck, shellcheck, YAML-lint, `appstreamcli validate` [S27], en (vanaf fase 3) een reproduceerbare dubbele build.

---

## 19. Ontwikkelroadmap

> **[AANBEVELING]** Elke fase eindigt met een expliciete gate. Zonder geslaagde testcriteria en "definitie van voltooiing" wordt de volgende fase niet gestart. Geschatte doorlooptijd wordt bewust **niet** genoemd: er is nog geen teamcapaciteit of budget bekend (§21, Q-04). **[NIET GETEST]** Geen enkele fase is gestart; fase 1 is het huidige document.

### Fase 1 — Research en architectuur *(huidige fase)*

| | |
|---|---|
| **Doel** | Eén goedgekeurd, onderbouwd architectuurdocument en een inventaris van de huidige repo. |
| **Werkzaamheden** | Repository-inspectie (§1.2), brononderzoek (§23), basis-/desktopvergelijking (§4–§7), architectuurontwerp (§3.5), KPI-/beveiligings-/ISO-ontwerp, risico-inventaris, roadmap, dit document. |
| **Afhankelijkheden** | Toegang tot repo en officiële documentatie. |
| **Risico's** | Verouderde aannames; onvoldoende capaciteit; onduidelijke licentie; scope-creep naar implementatie. |
| **Testcriteria** | 23 verplichte secties aanwezig; alle bronlinks geverifieerd; alle `[S#]`-referenties oplosbaar; geen wijziging aan bestaande bestanden; geen nieuwe mappen. |
| **Definitie van voltooiing** | Dit document is gereviewd door gebruiker én (optioneel) ChatGPT en **expliciet goedgekeurd**; ADR-0001 t/m 0006 hebben status `accepted` of een genoteerd bezwaar. |

### Fase 2 — Technische basis vaststellen

| | |
|---|---|
| **Doel** | Basis, desktop, licentie en meetmethode definitief vastleggen. |
| **Werkzaamheden** | Goedkeuring ADR's; `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue-/PR-templates in kleine PR's [S63]; opzetten testlab; baseline-meting Debian 13 + Plasma volgens §11; KPI-drempels ná meting vastleggen; vaststellen minimumhardware. |
| **Afhankelijkheden** | Fase 1-goedkeuring; beslissing Q-01/Q-03/Q-04 (§21). |
| **Risico's** | Licentiekeuze blokkeert branding; onvoldoende fysieke hardware voor baseline. |
| **Testcriteria** | Baseline-rapport met ruwe data, versies en methodologie; alle community-bestanden aanwezig; CI lint groen. |
| **Definitie van voltooiing** | `architecture/decisions.md` bevat geaccepteerde ADR's; baseline is gereproduceerd op ≥ 2 dagen. |

### Fase 3 — Eerste minimale ISO

| | |
|---|---|
| **Doel** | Een bootbare, **niet-publieke** test-ISO: Debian 13 + Plasma + minimale SANORA-configuratie, zonder eigen desktopverfraaiing. |
| **Werkzaamheden** | `live-build`-config in `iso/`; pakketlijst; `SOURCE_DATE_EPOCH` [S55]; dubbele build + `diffoscope` [S54]; checksum + handtekening; SBOM-skelet. |
| **Afhankelijkheden** | Fase 2; buildrunner met voldoende ruimte [S54]. |
| **Risico's** | Trixie-images niet volledig reproduceerbaar [S54]; firmware/licenties [S38]; live vs. installed-verschil. |
| **Testcriteria** | Boot in UEFI (VM + ≥ 1 fysiek systeem); Wayland-sessie actief; netwerk/audio/opslag functioneel; twee builds vergeleken; afwijkingen gedocumenteerd. |
| **Definitie van voltooiing** | ISO bootbaar in de testmatrix, build reproduceerbaar óf afwijking gedocumenteerd als bekend issue; **geen publieke download**. |

### Fase 4 — Installatie en hardwarecompatibiliteit

| | |
|---|---|
| **Doel** | Betrouwbare offline-installatie en een eerste HCL. |
| **Werkzaamheden** | Calamares-branding/modules [S61][S62]; één partitiescenario + LUKS2-optie [S62]; firmware in image [S13][S38]; hardwaretests per §10.3; foutmeldingen F-06; fwupd/LVFS [S39]. |
| **Afhankelijkheden** | Fase 3; beschikbaarheid van testsystemen (Intel/AMD/NVIDIA, Wi-Fi, laptops). |
| **Risico's** | Debian 6.12-kernel te oud voor nieuwe hardware [S11][S33]; NVIDIA-module-ondertekening [S36][S40]; firmware-licenties. |
| **Testcriteria** | Installatie op elk testsysteem offline geslaagd; herstart; suspend/resume; alle apparaten uit de matrix gedetecteerd; rollback van een mislukte installatie getest. |
| **Definitie van voltooiing** | HCL met ≥ 1 systeem per GPU-/Wi-Fi-klasse, inclusief exacte versies en bekende beperkingen; juridische toets firmware afgerond. |

### Fase 5 — SANORA-desktopervaring

| | |
|---|---|
| **Doel** | Eigen, consistente identiteit zonder fork. |
| **Werkzaamheden** | Global Theme [S23], iconen, wallpapers, geluiden, KWin-scripts/effects [S24][S25], panel/dock/starter, light/dark, animatie- en toegankelijkheidsregels, eigen KCM-skelet. |
| **Afhankelijkheden** | Fase 4; licentie voor assets (Q-01); design-review. |
| **Risico's** | Contrast-/toegankelijkheidsregressies; thema breekt bij Plasma-rebase; eigen assets per ongeluk op Apple-ontwerp lijkend. |
| **Testcriteria** | Screenshot-review bij 100%/200% schaal, light/dark, reduced motion; schermlezer- en toetsenbordtest; KPI-1/2/8 niet slechter dan baseline binnen vastgestelde marge; design-review vastgelegd. |
| **Definitie van voltooiing** | Eén `sanora-desktop`-metapakket, volledig via de SANORA-repo bij te werken; geen enkele upstream-bron gewijzigd. |

### Fase 6 — Softwarecentrum en systeembeheer

| | |
|---|---|
| **Doel** | Eén plek voor apps, updates, firmware en systeeminstellingen. |
| **Werkzaamheden** | Discover-configuratie/backends [S26], AppStream-metainfo + validatie [S27][S28], Flatpak-curatie [S49], permissie-weergave [S48], SANORA-updatebeleid, eerste KCM voor systeembeheer. |
| **Afhankelijkheden** | Fase 5; beslissing Q-08 over PackageKit [S4]. |
| **Risico's** | Extra achtergrondservices; PackageKit-afhankelijkheid; onduidelijke herkomst van apps. |
| **Testcriteria** | Installeren/verwijderen/bijwerken via UI; firmware-update in testomgeving; herkomst en permissies zichtbaar; KPI-9 toont geen ongedocumenteerde services. |
| **Definitie van voltooiing** | Dagelijkse beheertaken zonder terminal uitvoerbaar in de testscenario's; documentatie in `docs/`. |

### Fase 7 — Beveiliging en updates

| | |
|---|---|
| **Doel** | Veilige standaardconfiguratie en betrouwbaar update-/herstelpad. |
| **Werkzaamheden** | `unattended-upgrades` [S47], eigen ondertekende repo, AppArmor-profielen [S44], firewallbeleid [S45], polkit-acties [S46], LUKS2 + herstelsleutel, TPM2-opt-in [S42], Btrfs/snapper-rollback [S52], Secure Boot-documentatie [S40][S41], SBOM + provenance [S50][S51], `SECURITY.md`. |
| **Afhankelijkheden** | Fase 4–6; sleutelbeheer; juridische toets. |
| **Risico's** | R-01 Secure Boot; update-regressies; TPM-PCR-brittleheid [S42]; rollback dekt `/home` niet [S52]. |
| **Testcriteria** | Security-update automatisch toegepast; geforceerde mislukte update herstelbaar; reboot na kernel- en firmware-update met TPM-opt-in; ondertekende repo met vervalste `Release` geweigerd; geen telemetrie in netwerkcapture. |
| **Definitie van voltooiing** | Threat model + `SECURITY.md` gepubliceerd; herstelprocedure aantoonbaar getest op ≥ 2 systemen. |

### Fase 8 — Performance-optimalisatie

| | |
|---|---|
| **Doel** | Aantoonbare, stabiele verbetering t.o.v. de baseline — geen willekeurige tweaks. |
| **Werkzaamheden** | KPI-harness (§11), service-audit, animatie-/compositor-metingen, I/O-metingen met `fio`, energiemetingen; elke wijziging met ADR + voor/na-meting. |
| **Afhankelijkheden** | Fase 2-baseline, fase 5/6/7-stabiele build. |
| **Risico's** | Meetfouten; optimalisatie ten koste van stabiliteit; VM-metingen ten onrechte als bewijs gebruikt. |
| **Testcriteria** | Elke optimalisatie: ≥ 3 herhaalde metingen, mediaan + spreiding, functionele tests groen, geen regressie in andere KPI's. |
| **Definitie van voltooiing** | `PERFORMANCE.md` met ruwe data en eerlijke "geen verbetering"-vermeldingen waar van toepassing; niet-bewezen tweaks verwijderd. |

### Fase 9 — Uitgebreide hardwaretests

| | |
|---|---|
| **Doel** | Breedte en diepte van hardwareondersteuning aantonen. |
| **Werkzaamheden** | Uitbreiding HCL over de volledige §10.3-matrix; regressietests bij kernel/Mesa/firmware-updates; laptop-specifieke tests (suspend, accu, dock, hotplug); multi-monitor/VRR/HDR; NVIDIA open vs. propriëtair [S36]; community-testprogramma met gestandaardiseerd rapportageformaat. |
| **Afhankelijkheden** | Fase 4/8; testapparaten en vrijwilligers. |
| **Risico's** | Onvolledige dekking; driverregressies; firmware-afhankelijkheden die niet offline leverbaar zijn. |
| **Testcriteria** | Elke HCL-regel bevat datum, versies, testscript-uitvoer en bekende beperkingen; regressies zijn reproduceerbaar en aan upstream gerapporteerd. |
| **Definitie van voltooiing** | Publiceerbare HCL met een expliciete lijst "niet ondersteund / niet getest"; geen ongefundeerde ondersteuningsclaims. |

### Fase 10 — Eerste publieke release

| | |
|---|---|
| **Doel** | Een stabiele, gedocumenteerde, reproduceerbare eerste release voor dagelijks gebruik. |
| **Werkzaamheden** | Release-candidate, release notes, changelog [S63], checksums + handtekeningen, SBOM, installatiegids, HCL, `PERFORMANCE.md`, `THIRD_PARTY.md`, bekende beperkingen, updatepad naar de volgende release, ondersteuningsbeleid, mirror/download, security-meldpunt. |
| **Afhankelijkheden** | Alle eerdere gates geslaagd; licentie en juridische toetsen afgerond; goedgekeurde basisarchitectuur. |
| **Risico's** | Te vroege release; onderschatte ondersteuningslast; ontbrekend rollback- of updatepad; supply-chain-claim zonder bewijs. |
| **Testcriteria** | Volledige regressiesuite groen; dubbele reproduceerbare build; installatie + upgrade + rollback getest; documentatie-review; expliciete "known issues"-lijst. |
| **Definitie van voltooiing** | Ondertekende publieke release met reproduceerbare build, SBOM, release notes, ondersteuningsvenster en een benoemde maintainer voor security-meldingen. **Geen release zonder expliciete goedkeuring van de architectuur.** |

---

## 20. Technische risico's

| ID | Risico | Kans / Impact | Mitigatie | Fase |
|---|---|---|---|---|
| R-01 | Eigen Secure Boot-/shim-ondertekening is organisatorisch en technisch zwaar [S40][S41] | Hoog / Hoog | Geen eigen shim in v1; gefaseerd beleid §12.2; duidelijke documentatie; later aparte ADR | 7 |
| R-02 | NVIDIA: propriëtaire userspace, GSP-firmware, module-ondertekening, Wayland-sync, licentiebeperkingen [S34][S36][S37] | Hoog / Hoog | Opt-in ná installatie; open kernelmodules aanbevolen [S36]; licentietekst meegeleverd [S37]; juridische toets; testmatrix §10 | 4/9 |
| R-03 | Debian 6.12-kernel te oud voor nieuwe Intel/AMD/Arc/Wi-Fi-hardware [S11][S33] | Middel–Hoog / Hoog | Hardwarematrix vroeg meten; selectieve, gedocumenteerde backports [S15]; rebaseplan naar Debian 14 | 2/4/9 |
| R-04 | Backports hebben geen reguliere security-dekking en zijn "as-is" [S15] | Middel / Hoog | Alleen per uitzondering; pinning; actieve monitoring; alternatief: wachten op next-stable | 4/7 |
| R-05 | Plasma-versiekloof: Debian 13 heeft 6.3.6, LTS is 6.6, actueel is 6.8 [S11][S17][S19] | Hoog / Middel | Geen backportage in v1; thema/scripts regressietesten; rebase naar Debian 14; ADR bij afwijking | 2/5 |
| R-06 | Calamares-upstream migratie naar Codeberg (GitHub-repo gearchiveerd in 2025), historische LUKS-documentatie en eigen module-onderhoud [S61][S62] | Middel / Middel | Volg Codeberg als canonical upstream; minimale modules; LUKS-keten vroeg en tegen actuele docs testen | 4 |
| R-07 | ISO-reproduceerbaarheid regresseert (trixie 13.2 niet reproduceerbaar) [S54] | Middel / Middel | Verplichte dubbele build + `diffoscope`/`reprotest`; eerlijke rapportage; `SOURCE_DATE_EPOCH` [S55][S56] | 3/10 |
| R-08 | Firmware-/driverlicenties bij herdistributie [S13][S37][S38][S39] | Middel / Hoog | `firmware-inventory.md`, SPDX [S51], juridische toets vóór publieke ISO, opt-in NVIDIA | 3/4/10 |
| R-09 | Te kleine maintainercapaciteit voor eigen repo, CI, CVE-opvolging en release-engineering | Hoog / Hoog | Minimalistische architectuur; maximaal upstream hergebruik; kleine eigen repo; geen eigen kernel/compositor/store-server; gates in roadmap | Alle |
| R-10 | "Premium design" ten koste van toegankelijkheid of performance | Middel / Hoog | Harde release-gates: contrast, schermlezer, reduced motion, KPI-regressie [S17][S20] | 5/8 |
| R-11 | Automatische updates veroorzaken regressies; apt/dpkg niet atomair [S47] | Middel / Hoog | Alleen security-updates automatisch; snapshots/rollback [S52]; accu-uitsluiting [S47]; notificatie | 7 |
| R-12 | TPM2-binding breekt na firmware/kernel-update [S42] | Middel / Middel | TPM opt-in; herstelsleutel verplicht; PCR-keuze 7/11/14; regressietest | 7 |
| R-13 | AppStream/PackageKit-laag (Ubuntu verwijderde `pkcon`) [S4][S26][S28] | Middel / Middel | Backend-keuze als ADR (Q-08); eigen validatie in CI | 6 |
| R-14 | Scope-creep: toch "even" een ISO of thema bouwen vóór goedkeuring | Middel / Hoog | Expliciete goedkeuringsgate in dit document en in fase 1/2; alleen dit bestand toegevoegd | 1/2 |
| R-15 | Ongefundeerde performance-claims of verzonnen benchmarks | Middel / Hoog | §11 verbiedt cijfers zonder meetprotocol; ruwe data verplicht; reviews door ChatGPT/gebruiker | 2/8 |

---

## 21. Openstaande onderzoeksvragen

> **[AANBEVELING]** Onderstaande vragen zijn **bewust niet als aanname dichtgetimmerd**. De antwoorden zijn nodig vóór of in fase 2. Ze zijn ook geschikt voor onafhankelijke review door ChatGPT.

| ID | Vraag | Waarom het uitmaakt | Voorgestelde beslisser |
|---|---|---|---|
| Q-01 | Welke licentie(s)? Voorstel: eigen code GPL-2.0-or-later óf Apache-2.0; documentatie CC-BY-SA-4.0; eigen assets CC-BY-SA-4.0 of CC-BY-4.0 [S51] | Bepaalt branding, bijdragen, compatibiliteit met Debian-pakketten en SBOM | Gebruiker + juridische toets |
| Q-02 | Wordt ADR-0001 (Debian 13) én ADR-0002 (KDE Plasma/Wayland) goedgekeurd? | Blokkeert alle implementatie | Gebruiker |
| Q-03 | Wat is de minimumhardware en de officiële ondersteunde hardwaregrens? (Ubuntu 26.04 hanteert 6 GB / 25 GB [S3]) | Bepaalt KPI's, RAM-doel, ISO-omvang, HCL | Gebruiker + fase 2-meting |
| Q-04 | Hoeveel maintainers, uren, budget en infrastructuur zijn beschikbaar (buildrunner, mirror, sleutelbeheer, testhardware)? | Bepaalt of eigen shim/repo/CI haalbaar is; R-09 | Gebruiker |
| Q-05 | Blijven we bij Debian 13 Plasma 6.3.6, of wordt Plasma 6.6 LTS [S19] zelf teruggepackaget? | Grote, meerjarige packaginglast vs. langere upstream-ondersteuning | Gebruiker + ChatGPT-review |
| Q-06 | Komt NVIDIA in de default-ISO, of uitsluitend opt-in ná installatie? [S36][S37] | Juridisch, Secure Boot, image-omvang, eerste indruk op NVIDIA-laptops | Gebruiker + juridische toets |
| Q-07 | Wordt een image-based/immutable updatepad (bootc/rpm-ostree-achtig, `mkosi` [S57], osbuild [S59]) later overwogen? | Verandert update-, rollback- en ISO-architectuur fundamenteel | Gebruiker (ná fase 3) |
| Q-08 | Welke Discover-backend voor systeempakketten: PackageKit of een directe apt-integratie? [S4][S26] | Extra daemon en onderhoud vs. mindere integratie | Fase 6 |
| Q-09 | Welke talen/localisatie en welke standaardapplicaties (browser, office, mail)? | Beïnvloedt ISO-omvang, AppStream-curatie en documentatie | Gebruiker |
| Q-10 | Wanneer ARM64, en onder welke voorwaarden? | Projectvisie noemt ARM64 als latere fase; nu expliciet buiten scope | Gebruiker (ná fase 10) |
| Q-11 | Wat is het release- en ondersteuningsbeleid van SANORA zelf (punktreleases, EOL, upgrade-pad)? | Moet aansluiten op Debian's 5-jaarcyclus [S8][S9] | Gebruiker |
| Q-12 | Hoe wordt omgegaan met optionele, anonieme statistieken — nooit, of opt-in met lokaal inzagemoment? | Privacy-eis §13 | Gebruiker |
| Q-13 | Is er een gewenste samenwerkingsvorm met ChatGPT (reviewfrequentie, ADR-medeondertekening, checklist)? | Sector 9 van de opdracht: beslissingen moeten onafhankelijk beoordeelbaar zijn | Gebruiker |

---

## 22. Eerste concrete ontwikkeltaken

> **[AANBEVELING]** **Niets hiervan wordt uitgevoerd vóór goedkeuring.** Elke taak is klein, afzonderlijk reviewbaar en laat bestaande bestanden intact (met uitzondering van een bewuste, kleine PR voor `README.md`).

| # | Taak | Type | Omvang | Acceptatiecriterium |
|---|---|---|---|---|
| T-01 | Dit document voorleggen aan gebruiker én ChatGPT, met expliciete vraag om goedkeuring/bezwaar per ADR | Review | 1 PR / 1 reviewronde | Per ADR: `accepted`, `rejected` of `needs discussion` genoteerd in `architecture/decisions.md` |
| T-02 | Beslissen over Q-01 t/m Q-04 en Q-06 | Besluit | 1 discussie | Antwoorden vastgelegd als ADR's |
| T-03 | `architecture/adr/0001-basis-debian.md` + `0002-desktop-plasma.md` aanmaken met status, argumenten, nadelen | Docs | 2 bestanden | ADR-formaat §18.2; verwijzingen naar `[S#]` |
| T-04 | `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` in **vier afzonderlijke PR's** | Community | 4 PR's | Conform GitHub-documentatie voor templates/security policy [S63] |
| T-05 | Issue- en PR-templates incl. een hardware-rapportageformulier (HCL-velden) | Community | 1 PR | YAML-forms valideren; `config.yml` aanwezig [S63] |
| T-06 | `README.md` uitbreiden (projectstatus, fase, link naar dit document, geen claims over werkende software) | Docs | 1 PR | Bestaande titelregel behouden; geen overschrijven van inhoud zonder review |
| T-07 | Hardware-inventaris opstellen: beschikbare testsystemen met exacte hardware-ID's, kernel/Mesa/firmware-versies | Onderzoek | 1 bestand | Minimaal 3 systemen; sjabloon voor HCL-rapportage |
| T-08 | Baseline-meetharness voor KPI-1/2/3/4/9 opstellen (alleen scripts + documentatie, nog geen optimalisaties) | Tests | 1 PR | Herhaalbaar, versies gelogd, geen drempelwaarden verzonnen; `systemd-analyze`-beperkingen gedocumenteerd [S43] |
| T-09 | `THIRD_PARTY.md`-skelet met SPDX-kolommen en een eerste inventaris van Debian/Plasma/Calamares/Flatpak [S51] | Docs | 1 PR | Elke rij heeft herkomst + licentie + "eigen werk: ja/nee" |
| T-10 | CI-skelet: markdown-linkcheck, `[S#]`-referentiecontrole, YAML-lint (geen builds) | CI | 1 PR | CI slaagt op de huidige repo; geen extra services op het eindsysteem |

**[FEIT]** Van bovenstaande is in deze opdracht **alleen dit document** gerealiseerd (§1.2). **[NIET GETEST]** T-01 t/m T-10 zijn niet uitgevoerd.

---

## 23. Bronnen en officiële documentatie

> Alle bronnen zijn geraadpleegd op **2026-11-01** (UTC). Waar een pagina naar een nieuwere versie verwijst, is dat in de tekst aangegeven. Officiële documentatie van de betreffende projecten heeft voorrang; secundaire bronnen zijn alleen gebruikt om officiële pagina's te lokaliseren en zijn niet als bewijs geciteerd.

### Linux-bases, levenscycli en juridisch

- **[S1]** Ubuntu — *Ubuntu release cycle*. https://ubuntu.com/about/release-cycle — Geraadpleegd: 2026-11-01.
- **[S2]** Ubuntu — *Ubuntu kernel lifecycle and enablement stack*. https://ubuntu.com/kernel/lifecycle — Geraadpleegd: 2026-11-01.
- **[S3]** Ubuntu — *Ubuntu 26.04 LTS release notes*. https://documentation.ubuntu.com/release-notes/26.04/ — Geraadpleegd: 2026-11-01.
- **[S4]** Ubuntu — *Ubuntu 26.04 LTS summary (for LTS users)*. https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/ — Geraadpleegd: 2026-11-01.
- **[S5]** Canonical — *Intellectual property rights policy*. https://canonical.com/legal/intellectual-property-policy — Geraadpleegd: 2026-11-01.
- **[S6]** Fedora Project — *Fedora Linux Release Life Cycle*. https://docs.fedoraproject.org/en-US/releases/lifecycle/ — Geraadpleegd: 2026-11-01.
- **[S7]** Fedora Project Wiki — *Remix*. https://fedoraproject.org/wiki/Remix — Geraadpleegd: 2026-11-01.
- **[S8]** Debian — *Debian Releases*. https://www.debian.org/releases/ — Geraadpleegd: 2026-11-01.
- **[S9]** Debian Wiki — *LTS (Long Term Support)*. https://wiki.debian.org/LTS — Geraadpleegd: 2026-11-01.
- **[S10]** Debian — *Debian 13 (trixie) Release Notes — overzicht/vertalingen*. https://www.debian.org/releases/trixie/releasenotes — Geraadpleegd: 2026-11-01.
- **[S11]** Debian — *Release Notes for Debian 13, hoofdstuk 2 "What's new"*. https://www.debian.org/releases/trixie/release-notes/whats-new.en.html — Geraadpleegd: 2026-11-01.
- **[S12]** Debian — *Debian derivatives*. https://www.debian.org/derivatives/ — Geraadpleegd: 2026-11-01.
- **[S13]** Debian — *Debian Social Contract (v1.2)*. https://www.debian.org/social_contract — Geraadpleegd: 2026-11-01.
- **[S14]** Debian — *Debian security FAQ*. https://www.debian.org/security/faq — Geraadpleegd: 2026-11-01.
- **[S15]** Debian — *Debian Backports*. https://backports.debian.org/ — Geraadpleegd: 2026-11-01.
- **[S16]** Debian — *APT User's Guide*. https://www.debian.org/doc/manuals/apt-guide/index.en.html — Geraadpleegd: 2026-11-01.
- **[S64]** Debian — *Release Notes for Debian 13 — documentindex/licentie*. https://www.debian.org/releases/trixie/release-notes/index.en.html — Geraadpleegd: 2026-11-01.

### Desktopomgevingen en softwarecentrum

- **[S17]** KDE — *Plasma 6.8 release-aankondiging*. https://kde.org/announcements/plasma/6/6.8.0/ — Geraadpleegd: 2026-11-01.
- **[S18]** KDE Plasma Team — *Going all-in on a Wayland future*. https://blogs.kde.org/2025/11/26/going-all-in-on-a-wayland-future/ — Geraadpleegd: 2026-11-01.
- **[S19]** KDE Community Wiki — *Schedules/Plasma 6 (LTS, cadans, versies)*. https://community.kde.org/Schedules/Plasma_6 — Geraadpleegd: 2026-11-01.
- **[S20]** GNOME — *Introducing GNOME 50 "Tokyo"*. https://release.gnome.org/50/ — Geraadpleegd: 2026-11-01.
- **[S21]** Xfce — *Xfce 4.20 tour (Wayland-status)*. https://www.xfce.org/about/tour420/ — Geraadpleegd: 2026-11-01.
- **[S22]** Xfce — *Xfce 4.20 released*. https://www.xfce.org/about/news/1734220800/ — Geraadpleegd: 2026-11-01.
- **[S23]** KDE UserBase — *System Settings / Appearance (Global Theme)*. https://userbase.kde.org/System_Settings/Appearance/en — Geraadpleegd: 2026-11-01.
- **[S24]** KDE Developers — *KWin scripting tutorial*. https://develop.kde.org/docs/plasma/kwin/ — Geraadpleegd: 2026-11-01.
- **[S25]** KDE Developers — *KWin Effects*. https://develop.kde.org/docs/plasma/kwineffect/ — Geraadpleegd: 2026-11-01.
- **[S26]** KDE — *Discover (applicatiepagina met backends)*. https://apps.kde.org/discover/ — Geraadpleegd: 2026-11-01.
- **[S27]** freedesktop.org — *AppStream 1.2 specificatie*. https://www.freedesktop.org/software/appstream/docs/ — Geraadpleegd: 2026-11-01.
- **[S28]** Debian Wiki — *AppStream*. https://wiki.debian.org/AppStream — Geraadpleegd: 2026-11-01.
- **[S65]** Fedora Project Wiki — *Changes/KDE Plasma 6 (Wayland-only voor Fedora KDE)*. https://fedoraproject.org/wiki/Changes/KDE_Plasma_6 — Geraadpleegd: 2026-11-01.

### Wayland, kernel, GPU, drivers en firmware

- **[S29]** Wayland — *Wayland (protocol/architectuur)*. https://wayland.freedesktop.org/ — Geraadpleegd: 2026-11-01.
- **[S30]** Linux Kernel — *GPU Driver Developer's Guide (DRM/KMS, amdgpu, i915, xe, nouveau)*. https://docs.kernel.org/gpu/index.html — Geraadpleegd: 2026-11-01.
- **[S31]** Linux Kernel — *drm/xe Intel GFX Driver*. https://docs.kernel.org/gpu/xe/ — Geraadpleegd: 2026-11-01.
- **[S32]** kernel.org — *The Linux Kernel Archives*. https://www.kernel.org/ — Geraadpleegd: 2026-11-01.
- **[S33]** kernel.org — *finger_banner (actuele stable/longterm-versies)*. https://origin.kernel.org/finger_banner — Geraadpleegd: 2026-11-01.
- **[S34]** NVIDIA — *open-gpu-kernel-modules (GitHub)*. https://github.com/NVIDIA/open-gpu-kernel-modules — Geraadpleegd: 2026-11-01.
- **[S35]** NVIDIA Developer — *NVIDIA Releases Open-Source GPU Kernel Modules*. https://developer.nvidia.com/blog/nvidia-releases-open-source-gpu-kernel-modules/ — Geraadpleegd: 2026-11-01.
- **[S36]** NVIDIA — *README, Chapter 44: Open Linux Kernel Modules (driver 615.78.08)*. https://download.nvidia.com/XFree86/Linux-x86_64/615.78.08/README/kernel_open.html — Geraadpleegd: 2026-11-01.
- **[S37]** NVIDIA — *NVIDIA Driver License Agreement (Linux)*. https://www.nvidia.com/en-us/drivers/nvidia-license/linux/ — Geraadpleegd: 2026-11-01.
- **[S38]** kernel.org — *linux-firmware repository (LICENSE, LICENSES/, LICENSE-CRITERIA.md)*. https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/ — Geraadpleegd: 2026-11-01.
- **[S39]** LVFS — *Offline Firmware documentatie (fwupd/LVFS)*. https://lvfs.readthedocs.io/en/latest/offline.html — Geraadpleegd: 2026-11-01.

### Beveiliging, privacy, updates en prestaties

- **[S40]** Debian Wiki — *SecureBoot (shim, MOK, DKMS, beperkingen)*. https://wiki.debian.org/SecureBoot — Geraadpleegd: 2026-11-01.
- **[S41]** rhboot — *shim (UEFI shim loader, SBAT, MOK)*. https://github.com/rhboot/shim — Geraadpleegd: 2026-11-01.
- **[S42]** systemd — *systemd-cryptenroll(1) (LUKS2, TPM2, PCR's, herstelsleutels)*. https://www.freedesktop.org/software/systemd/man/latest/systemd-cryptenroll.html — Geraadpleegd: 2026-11-01.
- **[S43]** systemd — *systemd-analyze(1)*. https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html — Geraadpleegd: 2026-11-01.
- **[S44]** AppArmor — *officiële documentatie*. https://apparmor.net/ — Geraadpleegd: 2026-11-01.
- **[S45]** firewalld — *officiële projectpagina*. https://firewalld.org/ — Geraadpleegd: 2026-11-01.
- **[S46]** freedesktop.org — *polkit Reference Manual*. https://www.freedesktop.org/software/polkit/docs/latest/ — Geraadpleegd: 2026-11-01.
- **[S47]** Debian Wiki — *UnattendedUpgrades / PeriodicUpdates*. https://wiki.debian.org/UnattendedUpgrades — Geraadpleegd: 2026-11-01.
- **[S48]** Flatpak — *Sandbox Permissions (documentatie)*. https://docs.flatpak.org/en/latest/sandbox-permissions.html — Geraadpleegd: 2026-11-01.
- **[S49]** Flatpak — *officiële projectpagina*. https://flatpak.org/ — Geraadpleegd: 2026-11-01.
- **[S50]** SLSA — *SLSA specification v1.0* (site meldt dat v1.2 actueel is: https://slsa.dev/spec/v1.2/). https://slsa.dev/spec/v1.0/ — Geraadpleegd: 2026-11-01.
- **[S51]** SPDX — *SPDX License List (versie 3.29.0)*. https://spdx.org/licenses/ — Geraadpleegd: 2026-11-01.
- **[S52]** openSUSE — *Snapper and Btrfs (rollback, uitsluiting van /home)*. https://doc.opensuse.org/documentation/tumbleweed/snapper/ — Geraadpleegd: 2026-11-01.

### ISO, installer en projectbeheer

- **[S53]** Debian Live Project — *Debian Live Manual*. https://live-team.pages.debian.net/live-manual/ — Geraadpleegd: 2026-11-01.
- **[S54]** Debian Wiki — *ReproducibleInstalls/LiveImages*. https://wiki.debian.org/ReproducibleInstalls/LiveImages — Geraadpleegd: 2026-11-01.
- **[S55]** Reproducible Builds — *SOURCE_DATE_EPOCH specificatie*. https://reproducible-builds.org/specs/source-date-epoch/ — Geraadpleegd: 2026-11-01.
- **[S56]** Reproducible Builds — *System images (ISO/squashfs/initramfs)*. https://reproducible-builds.org/docs/system-images/ — Geraadpleegd: 2026-11-01.
- **[S57]** systemd — *mkosi: Build Bespoke OS Images*. https://github.com/systemd/mkosi — Geraadpleegd: 2026-11-01.
- **[S58]** go-debos — *debos: Debian OS builder*. https://github.com/go-debos/debos — Geraadpleegd: 2026-11-01.
- **[S59]** OSBuild — *Image Builder (osbuild/Image Builder/bootc)*. https://osbuild.org/ — Geraadpleegd: 2026-11-01.
- **[S60]** Weldr — *lorax / livemedia-creator*. https://github.com/weldr/lorax — Geraadpleegd: 2026-11-01.
- **[S61]** Calamares — *officiële site (Codeberg, releases, modules)*. https://calamares.codeberg.page/ — Geraadpleegd: 2026-11-01.
- **[S62]** Calamares Wiki — *Deploy LUKS* (historische pagina; GitHub-repo op 18 aug 2025 gearchiveerd, pagina laatst bewerkt in 2021 — daarom alleen als vertrekpunt gebruikt). https://github.com/calamares/calamares/wiki/Deploy-LUKS — Geraadpleegd: 2026-11-01.
- **[S63]** GitHub Docs — *About issue and pull request templates* (incl. `SECURITY.md`-verwijzing). https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates — Geraadpleegd: 2026-11-01.

### Bronnen die bewust níet als bewijs zijn gebruikt

**[FEIT]** Tijdens het onderzoek zijn ook nieuwsartikelen, blogs en beantwoorde vragen gelezen om actuele versienummers en officiële URL's te vinden (bijvoorbeeld over Ubuntu 26.04, Fedora 44, Plasma-releases en desktop-RAM-metingen). Die bevatten onderling tegenstrijdige cijfers (o.a. over exacte EOL-data en RAM-verbruik) en zijn daarom **niet** als bron voor beslissingen opgenomen; waar mogelijk is elke bewering teruggevoerd op de hierboven genoemde officiële pagina's.

---

## Afsluiting — goedkeuring vereist

**[AANBEVELING]** Dit document is de volledige eerste oplevering: repository-inventarisatie, onderzoek naar bases en desktops, driver-/kernel-/Wayland-strategie, systeemarchitectuur, performance-, beveiligings-, privacy-, package-, softwarecentrum-, installer- en ISO-strategie, repositorystructuur, roadmap, risico's, open vragen, eerste taken en bronnen.

**[FEIT]** Er is géén distributie gebouwd, geen code gewijzigd, geen map aangemaakt en geen bestaand bestand overschreven. Alleen `SANORA_OS_ARCHITECTURE.md` is toegevoegd.

**[AANBEVELING]** **Wacht op goedkeuring.** De eerste vervolgstap is T-01: beoordeel ADR-0001 t/m ADR-0006 en beantwoord minimaal Q-01 t/m Q-04 en Q-06 (§21). Belangrijke wijzigingen in deze architectuur worden als nieuwe ADR voorgesteld, met uitleg waarom, en nooit stilzwijgend doorgevoerd.

**SANORA OS — kwaliteit boven snelheid.**
