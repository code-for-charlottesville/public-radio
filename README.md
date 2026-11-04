# public-radio

A Code for Charlottesville project in collaboration with SemiPublic.org to collect data on public radio and TV stations and store the data on Wikidata.

Our aims are:

1. Group public radio stations by top level ownership

2. Map the geographic reach of all public radio stations, grouped by top level owner

3. Produce a dashboard where demographic data is joined on public radio's geographic reach

4. Store data on wikidata for posterity

## Getting Started

You will need to download the following public FCC Database Files to the tables directory in order to generate the database locally via a script. An index of the files can be found here: [LMS Public Database Files](https://enterpriseefiling.fcc.gov/dataentry/public/tv/lmsDatabase.html#). Individual links to the tables relevant to this work are provided below.

- [application_facility](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/10-14-2026/application_facility.zip)
- [application](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/application.zip)
- [facility](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/facility.zip)
- [license_filing_version](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/license_filing_version.zip)
- [lkp_application_purpose](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/lkp_application_purpose.zip)
- [lkp_application_sub_purpose](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/lkp_application_sub_purpose.zip)
- [lkp_authorization_type](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/lkp_authorization_type.zip)
- [lkp_filing_status](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/lkp_filing_status.zip)
- [lkp_filing_type](https://enterpriseefiling.fcc.gov/dataentry/api/download/dbfile/11-03-2026/lkp_filing_type.zip)

We will also need the FM service contour data. Note that this does not include AM stations and a description on the data shape and method used by the FCC to determine these contours can be found [here](https://www.fcc.gov/media/radio/fm-service-contour-data-points).

- [FM_service_contour_current](https://transition.fcc.gov/bureaus/mb/databases/map/FM_service_contour_current.zip)

## Relevant FCC Radio Service Codes

https://wiki.radioreference.com/index.php/FCC_Radio_Service_Codes

Broadcast/Mass Media 	FB 	FM Booster
Broadcast/Mass Media 	FD 	FM Digital
Broadcast/Mass Media 	FL 	Low Power FM
Broadcast/Mass Media 	FM 	FM Station
Broadcast/Mass Media 	FS 	FM Auxiliary Transmitter
Broadcast/Mass Media 	FX 	FM Translator 

[FCC Public Inspection Files and Countour Search](https://publicfiles.fcc.gov/)
[FCC API Documentation for Developers](https://publicfiles.fcc.gov/developer)
[LMS Public Database Files](https://enterpriseefiling.fcc.gov/dataentry/public/tv/lmsDatabase.html#)
[FM Service Contour Data Points](https://www.fcc.gov/media/radio/fm-service-contour-data-points)
[FCCdata.org](https://fccdata.org/?)