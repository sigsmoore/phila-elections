# 2020_general-pivoted.csv is "By Vote Type" sheet of 2020_general.xlsx, saved as csv
# below is code to produce 2020_general.csv

party_affiliation = {
    # party affiliations gleaned from various wikipedia articles
    'AARON BASHIR': 'REPUBLICAN',
    'AMEN BROWN': 'DEMOCRATIC',
    'ANGEL CRUZ': 'DEMOCRATIC',
    'BRENDAN F BOYLE': 'DEMOCRATIC',
    'BRIAN SIMS': 'DEMOCRATIC',
    'CHRIS RABB': 'DEMOCRATIC',
    'DANIEL WASSMER': 'LIBERTARIAN',
    'DANILO BURGOS': 'DEMOCRATIC',
    'DARISHA K PARKER': 'DEMOCRATIC',
    'DASHA PRUETT': 'REPUBLICAN',
    'DAVID TORRES': 'REPUBLICAN',
    'DONALD J TRUMP AND MICHAEL R PENCE': 'REPUBLICAN',
    'DONNA BULLOCK': 'DEMOCRATIC',
    'DREW MURRAY': 'REPUBLICAN',
    'DWIGHT EVANS': 'DEMOCRATIC',
    'ED NEILSON': 'DEMOCRATIC',
    'ELIZABETH FIEDLER': 'DEMOCRATIC',
    'HEATHER HEIDELBAUGH': 'REPUBLICAN',
    'ISABELLA FITZGERALD': 'DEMOCRATIC',
    'JARED SOLOMON': 'DEMOCRATIC',
    'JASON DAWKINS': 'DEMOCRATIC',
    'JENNIFER MOORE': 'LIBERTARIAN',
    'JO JORGENSEN AND JEREMY SPIKE COHEN': 'LIBERTARIAN',
    'JOANNA E MCCLINTON': 'DEMOCRATIC',
    'JOE HOHENSTEIN': 'DEMOCRATIC',
    'JOE SOLOSKI': 'LIBERTARIAN',
    'JOE TORSELLA': 'DEMOCRATIC',
    'JOHN NUNGESSER': 'REPUBLICAN',
    'JOHN SABATINA': 'DEMOCRATIC',
    'JOHN WEINRICH': 'INDEPENDENT',
    'JORDAN A HARRIS': 'DEMOCRATIC',
    'JOSEPH R BIDEN AND KAMALA D HARRIS': 'DEMOCRATIC',
    'JOSH SHAPIRO': 'DEMOCRATIC',
    'KAREN HOUCK': 'REPUBLICAN',
    'KEVIN J BOYLE': 'DEMOCRATIC',
    'LISA GOLDMAN RILEY': 'REPUBLICAN',
    'LOU MENNA IV': 'REPUBLICAN',
    'MALCOLM KENYATTA': 'DEMOCRATIC',
    'MARTINA WHITE': 'REPUBLICAN',
    'MARY GAY SCANLON': 'DEMOCRATIC',
    'MARYLOUISE ISAACSON': 'DEMOCRATIC',
    'MATT BALTSAR': 'LIBERTARIAN',
    'MICHAEL HARVEY': 'REPUBLICAN',
    'MIKE DOYLE': 'DEMOCRATIC',
    'MIKE DRISCOLL': 'DEMOCRATIC',
    'MORGAN CEPHAS': 'DEMOCRATIC',
    'NANCY GUENST': 'DEMOCRATIC',
    'NIKIL SAVAL': 'DEMOCRATIC',
    'NINA AHMAD': 'DEMOCRATIC',
    'OLIVIA FAISON': 'GREEN',
    'PAMELA A DELISSIO': 'DEMOCRATIC',
    'REGINA YOUNG': 'DEMOCRATIC',
    'RICHARD L WEISS': 'GREEN',
    'RICK KRAJEWSKI': 'DEMOCRATIC',
    'SHARIF STREET': 'DEMOCRATIC',
    'STACY L GARRITY': 'REPUBLICAN',
    'STEPHEN KINSEY': 'DEMOCRATIC',
    'TIMOTHY DEFOOR': 'REPUBLICAN',
    'TIMOTHY RUNKLE': 'GREEN',
    'VINCENT HUGHES': 'DEMOCRATIC',
    'WANDA LOGAN': 'REPUBLICAN',
}

import pandas as pd

gen20_piv = pd.read_csv('2020_general-pivoted.csv')

# the 2020 spreadsheet includes DIVISIONs FED-2, FED3, and FED-5,
# which do not appear in other years.  discard them.
gen20_piv = gen20_piv.loc[gen20_piv.WARD.notna()].copy()

# WARD is created as a float column because the FED-? columns have no
# value for WARD.  Once we drop those columns, all WARD values are ints.
gen20_piv['WARD'] = gen20_piv.WARD.astype('int')

assert (gen20_piv['DIV'].str[:2].astype('int') == gen20_piv['WARD']).all()
gen20_piv['DIV'] = gen20_piv['DIV'].str[3:].astype('int')
gen20_piv.rename(columns={'DIV':'DIVISION'}, inplace=True)

# columns 3-6 give the congressional, senatorial, legistlative, and
# council district for each division.  we don't care about those, so
# discard them.  also reorder the first 3 columns.
gen20_piv = gen20_piv[['WARD','DIVISION','TYPE']+list(gen20_piv.columns[7:])]

# replace "VICE-PRESIDENT" with "VICE PRESIDENT" to be consistent with
# previous years
import re
gen20_piv.rename(columns=lambda s: re.sub('VICE-PRESIDENT', 'VICE PRESIDENT', s), inplace=True)

# now un-pivot
gen20 = gen20_piv.melt(id_vars=['WARD','DIVISION','TYPE'])

assert (gen20['variable'].str.split('\n').str.len()==2).all()
gen20[['OFFICE','CANDIDATE']] = gen20['variable'].str.split('\n',expand=True)
gen20['PARTY'] = gen20['CANDIDATE'].map(party_affiliation)
gen20['VOTES'] = gen20['value']
gen20.drop(columns=['variable','value'], inplace=True)

gen20.to_csv('2020_general.csv', index=False)

# shortcomings:
# - values in the TYPE column - E, M, and P - differ from previous years,
#   which have A, M, and P.  Maybe E is the same as A?  Fortunately for us,
#   we don't really care about TYPE; we sum the VOTES over all TYPEs.
