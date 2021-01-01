# Philadelphia Elections Data Visualization

## Data sources

### Election results

* <https://www.philadelphiavotes.com/en/resources-a-data/ballot-box-app.html>
* <https://github.com/openelections/openelections-data-pa>

### GeoJSON

* <https://www.opendataphilly.org/dataset/political-wards>
* <https://www.opendataphilly.org/dataset/political-ward-divisions>

## Data format

CSV files have the following columns:

1. **WARD** integer in the range 1-66
1. **DIVISION** integer in the range 1-52, a subdivision of a ward
1. **TYPE** or **VOTE TYPE** single character whose meaning is described below
1. **OFFICE** or **CATEGORY** capital letter string
1. **CANDIDATE**, **NAME**, or **SELECTION** capital letter string
1. **VOTES** or **VOTE COUNT** integer

N.B. some CSV files contain latin-1 characters

### Type codes

(The following are my guesses based on sources I don't remember o_o)

- **A** = absentee
- **L** = mail-in
- **M** = election day/in-person
- **P** = provisional

## Dependencies / Thanks to

* [Plotly / Dash](https://plotly.com/)
* [Mapbox](https://www.mapbox.com/)
* [pandas](https://pandas.pydata.org/)
* [Heroku](https://www.heroku.com/)
* [OpenDataPhilly](https://www.opendataphilly.org)
* [philadelphiavotes.com](https://philadelphiavotes.com)
* Inspired by: <https://gothamist.com/news/official-results-map-see-how-your-nyc-neighbors-voted-2020-election>
