import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from tqdm import tqdm  # para barra de progresso

class MarsRoverPhotos:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
        self.output_dir = "mars_rover_photos"
        
    def get_photos_for_date(self, date):
        params = {
            "api_key": self.api_key,
            "earth_date": date.strftime("%Y-%m-%d")
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()["photos"]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao coletar dados para {date}: {e}")
            return []

    def download_photo(self, url, filepath):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
            return False

    def collect_month_data(self, year, month):
        # Criar diretório base se não existir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Definir período
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        all_photos_data = []
        current_date = start_date

        # Coletar dados para cada dia do mês
        print("Coletando dados do Mars Rover...")
        while current_date <= end_date:
            photos = self.get_photos_for_date(current_date)
            
            for photo in photos:
                photo_data = {
                    'data': current_date.strftime("%Y-%m-%d"),
                    'id_foto': photo['id'],
                    'camera': photo['camera']['name'],
                    'rover': photo['rover']['name'],
                    'status_rover': photo['rover']['status'],
                    'sol': photo['sol'],
                    'url_imagem': photo['img_src']
                }
                all_photos_data.append(photo_data)
            
            time.sleep(0.1)  # Para não sobrecarregar a API
            current_date += timedelta(days=1)

        # Criar DataFrame e salvar CSV
        df = pd.DataFrame(all_photos_data)
        csv_filename = f"{self.output_dir}/mars_rover_photos_{year}_{month:02d}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Dados salvos em {csv_filename}")

        # Baixar fotos
        print("Baixando fotos...")
        for _, row in tqdm(df.iterrows(), total=len(df)):
            date_dir = os.path.join(self.output_dir, row['data'])
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
                
            photo_filename = f"{row['id_foto']}_{row['camera']}.jpg"
            photo_path = os.path.join(date_dir, photo_filename)
            
            if not os.path.exists(photo_path):
                self.download_photo(row['url_imagem'], photo_path)
                time.sleep(0.1)  # Para não sobrecarregar o servidor

def main():
    api_key = "XRdXTghORUOSAbD2K3sbqRc4miJYHdcIbAbhtjsA"
    
    # Criar instância da classe
    mars_rover = MarsRoverPhotos(api_key)
    
    # Coletar dados para um mês específico
    ano = 2023
    mes = 9
    
    mars_rover.collect_month_data(ano, mes)
    print("Processo concluído!")

if __name__ == "__main__":
    main()