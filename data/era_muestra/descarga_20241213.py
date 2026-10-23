import cdsapi

dataset = "reanalysis-era5-land"
request = {
    "variable": [
        "2m_temperature",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "total_precipitation"
    ],
    "year": "2024",
    "month": "12",
    "day": ["13"],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "data_format": "netcdf",
    "download_format": "zip",
    "area": [-18.5, -61.5, -39.5, -34.5]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
