import pandas as pd

def load_data(file_path):
    #Wczytuje dane z pliku CSV
    return pd.read_csv(file_path)

def calculate_interventions_by_race(df):
    #Grupuje dane według rasy i liczy interwencje
    return df.groupby('race')['id'].count()

def create_pivot_table(df):
    #Tworzy tabelę przestawną z odsetkiem choroby psychicznej
    pivot_table = pd.pivot_table(df, values='name', index=['race'], columns=['signs_of_mental_illness'], aggfunc='count').fillna(0)
    pivot_table['percent_mental_illness'] = (pivot_table[True] / (pivot_table[True] + pivot_table[False]) * 100).round(2)
    return pivot_table

def merge_interventions(pivot_table, interventions_by_race):
    #Łączy tabelę przestawną z interwencjami według rasy
    pivot_table = pd.merge(pivot_table, interventions_by_race, on='race', how='left')
    pivot_table.rename(columns={'id': 'Interventions per race'}, inplace=True)
    new_order = ['Interventions per race'] + [col for col in pivot_table.columns if col != 'Interventions per race']
    return pivot_table[new_order]

def analyze_max_percent(pivot_table):
    #Znajduje rasę z największym odsetkiem znamion choroby psychicznej
    max_percent_race = pivot_table['percent_mental_illness'].idxmax()
    max_percent = pivot_table['percent_mental_illness'].max()
    print(f"Rasa o największym odsetku znamion choroby psychicznej podczas interwencji to {max_percent_race} z odsetkiem {max_percent:.2f}%")

def add_day_of_week(df):
    #Dodaje kolumnę z dniem tygodnia
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    return df

def count_days_of_week(df):
    #Zlicza interwencje według dnia tygodnia.
    day_of_week_counts = df['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    print("Interwencje według odpowiedniego dnia tygodnia:")
    print(day_of_week_counts)

def merge_population_data(df):
    #Łączy dane o populacji stanów z danymi o interwencjach.
    state_population = pd.read_html('https://simple.wikipedia.org/wiki/List_of_U.S._states_by_population')[0]
    state_abbreviations = pd.read_html('https://simple.wikipedia.org/wiki/List_of_U.S._state_abbreviations')[0]
    df = pd.merge(df, state_abbreviations, how='left', left_on='state', right_on=0)
    df = pd.merge(df, state_population, how='left', left_on=1, right_on='State')
    return df

def calculate_incidents_per_1000(df):
    #Oblicza liczbę interwencji na 1000 mieszkańców.
    df['incidents_per_1000'] = (df.groupby('State')['id'].transform('count') / df['Census population, April 1, 2020 [1][2]']) * 1000
    incidents_per_1000 = df[['State', 'incidents_per_1000']].drop_duplicates().set_index('State').sort_values('incidents_per_1000', ascending=False).round(3)
    print(f"Liczba interwencji na 1000 mieszkańców w poszczególnych stanach:\n{incidents_per_1000}")

# Wczytanie danych
df = load_data('fatal-police-shootings-data.csv')

# Analiza interwencji według rasy
interventions_by_race = calculate_interventions_by_race(df)
pivot_table = create_pivot_table(df)
pivot_table = merge_interventions(pivot_table, interventions_by_race)
print("Dane dotyczące liczby ofiar interwencji według rasy (interventions_by_race) oraz tego, czy wykazywały (True) czy nie wykazywały (False) one oznak choroby psychicznej, a także odsetek interwencji, w których ofiary wykazywały te oznaki (percent_mental_illness)")
print(pivot_table)
analyze_max_percent(pivot_table)

# Analiza interwencji według dnia tygodnia
df = add_day_of_week(df)
count_days_of_week(df)

# Analiza interwencji w przeliczeniu na 1000 mieszkańców
df = merge_population_data(df)
calculate_incidents_per_1000(df)
