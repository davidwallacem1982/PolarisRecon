import os
import time

import numpy as np
import polars as pl


def generate_mock_data(n_records=1000000):
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 16 + "POLARIS RECON - DATA GENERATOR" + " " * 12 + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"[*] Preparando geração de {n_records:,} registros...")

    start_time = time.time()

    # Gerar IDs únicos
    print("[>] Calculando chaves primárias (order_ids)...")
    order_ids = np.arange(1, n_records + 1)

    # Dados base (Internos)
    print("[>] Construindo DataFrame Interno (Base de Dados)...")
    internal_df = pl.DataFrame(
        {
            "external_id": [f"EXT_{i}" for i in order_ids],
            "order_id": order_ids,
            "order_datetime": ["2024-02-26 10:00:00"] * n_records,
            "asset_id": [
                f"ASSET_{np.random.randint(1, 100)}" for _ in range(n_records)
            ],
            "trading_account": [
                f"ACC_{np.random.randint(1000, 9999)}" for _ in range(n_records)
            ],
            "quantity": np.random.uniform(10, 1000, n_records).round(2),
            "unit_price": np.random.uniform(100, 150, n_records).round(2),
        }
    )

    # Criar DataFrame Externo (Cópia do Interno com divergências)
    print("[>] Injetando anomalias e divergências controladas...")
    external_df = internal_df.clone()

    # 1. Simular divergência de quantidade (em 10.000 registros)
    indices_qty = np.random.choice(n_records, 10000, replace=False)
    external_df[indices_qty, "quantity"] = external_df[indices_qty, "quantity"] * 1.05

    # 2. Simular divergência de preço (em 5.000 registros)
    indices_price = np.random.choice(n_records, 5000, replace=False)
    external_df[indices_price, "unit_price"] = (
        external_df[indices_price, "unit_price"] + 0.5
    )

    # 3. Simular registros faltantes (Remover 1.000 registros do externo)
    external_df = external_df.slice(0, n_records - 1000)

    # 4. Simular registros extras no externo (Adicionar 500 novos)
    extra_ids = np.arange(n_records + 1, n_records + 501)
    print("[>] Finalizando registros órfãos no arquivo externo...")
    extra_df = pl.DataFrame(
        {
            "external_id": [f"EXT_{i}" for i in extra_ids],
            "order_id": extra_ids,
            "order_datetime": ["2024-02-26 11:00:00"] * 500,
            "asset_id": ["ASSET_NEW"] * 500,
            "trading_account": ["ACC_NEW"] * 500,
            "quantity": [100.0] * 500,
            "unit_price": [150.0] * 500,
        }
    )
    external_df = pl.concat([external_df, extra_df])

    # Salvar em CSV
    print("[>] Serializando dados para a pasta /data...")
    if not os.path.exists("data"):
        os.makedirs("data")

    external_df.write_csv("data/external_file.csv")
    internal_df.write_csv("data/internal_base.csv")

    end_time = time.time()
    print("╚" + "═" * 58 + "╝")
    print(f"✅ GERAÇÃO CONCLUÍDA EM {end_time - start_time:.2f} segundos.")
    print(f"Local: {os.path.abspath('data')}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    generate_mock_data()
