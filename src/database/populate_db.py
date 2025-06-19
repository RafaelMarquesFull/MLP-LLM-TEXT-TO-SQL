import      sqlite3
import      random
from        pathlib import Path
from        faker   import Faker

DATA_DIR    = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH     = DATA_DIR / "automobiles.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
 
fake        = Faker('pt_BR')

brands = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Volkswagen', 'Nissan', 'Hyundai', 'BMW', 'Mercedes-Benz', 'Audi', 'Fiat']
models_by_brand = {
    'Audi':          ['A4', 'A6', 'Q5', 'A3', 'Q3'],
    'BMW':           ['Série 3', 'Série 5', 'X3', 'X1', 'X5'],
    'Fiat':          ['Uno', 'Mobi', 'Argo', 'Cronos', 'Toro'],
    'Ford':          ['Focus', 'Fusion', 'Explorer', 'Ranger', 'Ka'],
    'Honda':         ['Civic', 'Accord', 'CR-V', 'HR-V', 'Fit'],
    'Nissan':        ['Sentra', 'Altima', 'Rogue', 'Kicks', 'Versa'],
    'Toyota':        ['Corolla', 'Camry', 'RAV4', 'Hilux', 'Yaris'],
    'Hyundai':       ['Elantra', 'Sonata', 'Tucson', 'Creta', 'HB20'],
    'Chevrolet':     ['Cruze', 'Malibu', 'Equinox', 'Onix', 'S10'],
    'Volkswagen':    ['Golf', 'Jetta', 'Tiguan', 'Polo', 'Virtus'],
    'Mercedes-Benz': ['Classe C', 'Classe E', 'GLC', 'Classe A', 'GLE'],
}

colors          = ['Preto', 'Branco', 'Prata', 'Cinza', 'Azul', 'Vermelho', 'Marrom', 'Verde', 'Amarelo', 'Laranja']
categories      = ['Sedan', 'SUV', 'Hatchback', 'Picape', 'Cupê']
fuel_types      = ['Gasolina', 'Etanol', 'Diesel', 'Híbrido', 'Elétrico']
transmissions   = ['Automática', 'Manual']
steering_types  = ['Hidráulica', 'Mecânica', 'Elétrica']

def create_database():
    conn    = sqlite3.connect(DB_PATH)
    cursor  = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS automobiles')

    cursor.execute('''
    CREATE TABLE automobiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        license_plate TEXT NOT NULL,
        color TEXT,
        doors INTEGER,
        category TEXT,
        seats INTEGER,
        steering TEXT,
        air_conditioning INTEGER,
        power_windows INTEGER, 
        fuel_type TEXT,
        engine_power REAL,
        mileage INTEGER,
        transmission TEXT
    )
    ''')

    for _ in range(100):
        brand = random.choice(brands)
        model = random.choice(models_by_brand[brand])
        
        car_data = (
            brand,
            model,
            fake.license_plate(), 
            random.choice(colors),
            random.choice([2, 4]),
            random.choice(categories),
            random.choice([2, 5, 7]),
            random.choice(steering_types),
            random.choice([0, 1]), 
            random.choice([0, 1]), 
            random.choice(fuel_types),
            round(random.uniform(1.0, 4.0), 1),
            random.randint(0, 200000),
            random.choice(transmissions)
        )
        
        cursor.execute('''
        INSERT INTO automobiles (
                brand, 
                model, 
                license_plate, 
                color, doors, 
                category, 
                seats, 
                steering, 
                air_conditioning, 
                power_windows, 
                fuel_type, 
                engine_power, 
                mileage, 
                transmission
            )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', 
            car_data
        )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print(f"Banco de dados 'automobiles.db' criado e populado em '{DB_PATH}'!")
