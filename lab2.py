import urllib.request
import datetime
import os
import pandas as pd
import statistics

# Цикл для отримання даних з сайту
for i in range(1, 28):
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1=1981&year2=2024&type=Mean"
    wp = urllib.request.urlopen(url)
    text = wp.read()
    now = datetime.datetime.now()
    date_and_time = now.strftime("%d-%m-%Y__%H-%M-%S")

    with open(f'../../AD/df/id_{str(i)}_{date_and_time}.csv' , 'wb') as file:
        file.write(text)
print("VHI is downloaded...")

# Функція для считування csv файлів
def read_csv(directory):
    data_frames = []

    for file in os.listdir(directory):
        region = file.split("_")[1]
        file_path = os.path.join(directory, file)

        try:
            df = pd.read_csv(file_path, index_col=False, header=1)
            df.columns = [col.strip().lower().replace("<br>", "") for col in df.columns]
            df = df.replace(to_replace=r'<.*?>', value='', regex=True)
            df["region"] = region
            data_frames.append(df)
        except Exception as e:
            print(f"Error {file_path}: {e}")

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
    else:
        combined_df = pd.DataFrame()

    return combined_df

df = read_csv("df")
#print(df.head())


while (df[['vci', 'tci', 'vhi']] == -1).any().any():
    df = df.mask(df == -1, df.shift())

df = df.dropna(subset=['vci', 'tci', 'vhi'])


df.to_csv('df/whole_df.csv', index=False)
df = pd.read_csv('../../AD/df/whole_df.csv', index_col=False)

# Змінюємо індекси областей на назви
regions = {
    1: "Черкаська", 2: "Чернігівська", 3: "Чернівецька", 4: "АР Крим", 5: "Дніпропетровська", 6: "Донецька", 7: "Івано-Франківська", 8: "Харківська",
    9: "Херсонська", 10: "Хмельницька", 11: "Київська", 12: "м. Київ", 13: "Кіровоградська", 14: "Луганська", 15: "Львівська", 16: "Миколаївська",
    17: "Одеська", 18: "Полтавська", 19: "Рівненська", 20: "м. Севастополь", 21: "Сумська", 22: "Тернопільська", 23: "Закарпатська", 24: "Вінницька",
    25: "Волинська", 26: "Запорізька", 27: "Житомирська"
}

df["region"] = df["region"].astype(int).map(regions)

# Перетворюємо ствопчик років з рядка в ціле число
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")


# Функція для знаходження vhi для області за вказаний рік
# def vhi_year(region, year):
#     res = df[(df["region"] == region) & (df["year"] == year)]
#     res_vhi = list(res["vhi"])
#
#     print(f"vhi для {region} області на {year} рік склав: \n{res_vhi}")
#
#     print("\nMIN:", min(res_vhi))
#     print("MAX:", max(res_vhi))
#     print("AVG:", statistics.mean(res_vhi))
#     print("MED:", statistics.median(res_vhi))
#
# vhi_year("Київська", 2006)

# Функція для знаходження vhi для декількох області за діапазон років
# def vhi_years(region, min_year, max_year):
#     res = df[(df["region"].isin(region)) & (df["year"].between(min_year, max_year))]
#     res_vhi = list(res["vhi"])
#
#     print(f"vhi для {region} області на {min_year}-{max_year} має {len(res_vhi)} значень")
#
#     print("\nMIN:", min(res_vhi))
#     print("MAX:", max(res_vhi))
#     print("AVG:", statistics.mean(res_vhi))
#     print("MED:", statistics.median(res_vhi))
#
# vhi_years(["Київська", "Харківська", "Львівська"], 2000, 2010)

# # Функція для визначення років, коли було забагато посух
# def drought(percent=0):
#     drought_years = []
#     regions = df["region"].unique()
#     min_region_num = int(percent * len(regions) / 100)
#
#     for year in df["year"].unique():
#         droughts_num = 0
#         for region in regions:
#             res = df[(df["region"] == region) & (df["year"] == year)]
#             res_vhi = list(res["vhi"])
#             if len(res_vhi) != 0:
#                 if statistics.mean(res_vhi) < 35:
#                     droughts_num += 1
#
#         if droughts_num > min_region_num:
#             drought_years.append(int(year))
#
#     print(f"{len(drought_years)} років були посушливі")
#     print(drought_years)
#
# drought(20)